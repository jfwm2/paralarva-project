"""
The Request class receives incoming requests, forwards then to the appropriate
balancer and responds with the response from the balancer if there is no error,
otherwise the response contains an error code
"""

import logging
import selectors
import uuid
from paralarva.balancer import Balancer
from paralarva.helper import get_response, get_header_info_from_string, \
    CONTENT_LENGTH_HEADER, TRANSFER_ENCODING_HEADER, EXPECT_HEADER, HOST, \
    METHODS
from typing import Any, Dict, Tuple
from prometheus_client import Counter

BUFFER_SIZE = 4096  # Default buffer size in bytes
MAX_HEADER_SIZE = BUFFER_SIZE - 128  # Max supported header size

# Prometheus status counter
status_counter = Counter('status', 'incoming requests status by host',
                         ['error', 'host', 'client'])


class Request:
    def __init__(self, address: Tuple[str, int],
                 balancers: Dict[str, Balancer],
                 selector: selectors, connection: Any) -> None:
        """
        create a request object to process an incoming connection, forward the
        request to the right balancer, and send back the response or an error

        :param address: address (ip address + port) of the incoming connection
        :param balancers: dict of balancers to chose from according to the HOST
        field of the incoming request
        :param selector: selector containing the incoming request
        :param connection: incoming connection socket
        """
        self.address = address

        self.incoming = b''  # incoming buffer
        self.outgoing = b''  # outgoing buffer
        # buffer for the head of the request if not in incoming buffer
        self.head = b''

        self.balancers = balancers
        self.selector = selector
        self.sock = connection

        self.headers = {}
        self.method = None
        self.content_length = None
        self.header_length = None
        self.received_so_far = 0
        self.error = None
        self.host = None
        self.request_id = None

    def process_connection(self, mask: int) -> None:
        """
        this method is called from the proxy.py event loop
        If the read bit is set and the instance error attribute is not,
        incoming bytes (if any) are read from the client socket, otherwise the
        connection is closed.
        If the write bit is set and the outgoing buffer (self.outgoing) is not
        empty part or all of it (depending of its size) is sent back to the
        client; if the outgoing buffer is empty, and some data is in the
        incoming buffer (self.incoming) a reply to the client is performed (if
        ready).

        :param mask: mask to bit-compare to selectors.EVENT_READ and
        selectors.EVENT_WRITE
        :return: None
        """
        if mask & selectors.EVENT_READ and self.error is None:
            incoming_data = self.sock.recv(BUFFER_SIZE)
            if incoming_data:
                self.received_so_far += len(incoming_data)
                self.incoming += incoming_data
            else:
                logging.info(f"closing connection to {self.address}")
                self.close()
        if mask & selectors.EVENT_WRITE:
            if self.outgoing and len(self.outgoing) > 0:
                logging.debug(f"sending {self.outgoing} (length: "
                              f"len(self.outgoing) {len(self.outgoing)}) {self.address}")
                sent = self.sock.send(self.outgoing)
                self.outgoing = self.outgoing[sent:]
            elif self.incoming and self.ready_to_reply():
                self.reply()

    def reply(self) -> None:
        """
        if no error is detected so far the request is processed and a reply to
        the client (with a response from a member server or an error message)
        with the content of the outgoing buffer.
        If the whole buffer is not fully sent, it is truncated so the remaining
        will be sent the next time the process_connection (above method) is
        called from the proxy.py event loop.

        :return: None
        """
        if self.error is None:
            self.process_complete_request()

        # since outgoing buffer is begin sent, we do not need data from
        # incoming or head buffer anymore
        self.incoming = b''
        self.head = b''
        if self.outgoing and len(self.outgoing) > 0:
            logging.debug(f"sending {self.outgoing} (length "
                          f"{len(self.outgoing)}) to {self.address}")
        else:
            logging.error(f"outgoing buffer supposed to be send to {self.address} "
                          f"is null or zero-length: {self.outgoing} -> "
                          f"502 Bad Gateway (empty response)")
            self.error, self.outgoing = 502, get_response(502)

        sent = self.sock.send(self.outgoing)
        self.outgoing = self.outgoing[sent:]

        if self.error:
            logging.info(f"closing connection to {self.address} because of "
                         f"error {self.error}")
            self.close()

        self.record_status()
        self.reset_request_info()

    def close(self) -> None:
        """
        close the connection pertaining to the current request

        :return: None
        """
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            logging.warning("error: socket.unregister() exception for "
                            f"{self.address}: {repr(e)}")
        try:
            self.sock.close()
        except OSError as e:
            logging.warning(f"error: socket.close() exception for "
                            f"{self.address}: {repr(e)}")
        finally:
            self.sock = None

    def ready_to_reply(self) -> bool:
        """
        check whether a response is ready to be sent back to the client

        :return: True if the current request is erroneous or not supported, the
        incoming request does not have a body, or it has body that was fully
        retrieved; False otherwise
        """
        logging.debug(
            f"receiving {self.incoming} from {self.address} with "
            f"content-length {self.content_length}")
        if self.content_length is None:
            self.populate_request_info()
            if self.error or CONTENT_LENGTH_HEADER not in self.headers:
                return True
            elif TRANSFER_ENCODING_HEADER is self.headers:
                self.error = 400
                self.outgoing = get_response(400,
                                             f"(method {self.method} should"
                                             f" have a {CONTENT_LENGTH_HEADER} "
                                             f"header; "
                                             f"{TRANSFER_ENCODING_HEADER} is "
                                             "not supported)")
                self.host = None
            else:
                self.content_length = int(self.headers[CONTENT_LENGTH_HEADER])
                logging.debug(f"received {self.incoming} from {self.address} "
                              f"with content-length {self.content_length}")

        if self.received_so_far < self.header_length + self.content_length + 4:
            if EXPECT_HEADER in self.headers \
                    and self.headers[EXPECT_HEADER] == '100-continue' \
                    and not self.head:
                reply_continue = get_response(100)
                logging.debug(f"sending {reply_continue} to {self.address}")
                self.sock.send(reply_continue)
                self.head = self.incoming
                self.incoming = b''
            return False
        else:
            return True

    def process_complete_request(self) -> None:
        """
        forward the request to the balancer with id matching the self.host
        instance attribute and populate the outgoing buffer with response; if a
        correct balancer cannot be determined, a error is recorded

        :return: None
        """

        logging.debug(
            f"{self.request_id} - processing complete request; head: "
            f"{self.head} - data: {self.incoming} ")

        if self.host and self.host in self.balancers:
            balancer = self.balancers[self.host]
            self.error, self.outgoing = balancer.forward_and_get_response(
                self.incoming, self.head, self.request_id)
        else:
            # Invalid or non-existent host, send error 400 (see link below)
            # https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.23
            self.error, self.outgoing = 400, get_response(400)
            if self.host:
                logging.warning(f"{self.request_id} - host {self.host} "
                                f"found in headers from {self.address} does "
                                "not match any load balancer")
            else:
                logging.warning(f"{self.request_id} - could not find Host "
                                f"field in headers from {self.address}")

    def record_status(self) -> None:
        """
        Update prometheus status counter

        :return: None
        """
        if self.error:
            logging.debug(f"{self.request_id} - recording error {self.error}")
        status_counter.labels(
            error=self.error, host=self.host, client=self.address[0]).inc()

    def reset_request_info(self):
        """
        reset request-specific instance attributes their default value

        :return: None
        """
        self.headers = {}
        self.method = None
        self.content_length = None
        self.header_length = None
        self.received_so_far = 0
        self.error = None
        self.host = None
        self.request_id = None

    def populate_request_info(self) -> None:
        """
        set request-specific instance attributes according the current
        incoming request

        :return: None
        """
        self.request_id = uuid.uuid1()
        logging.debug(
            f"{self.request_id} - retrieving request from {self.address}")
        headers_string = str(
            self.incoming, 'iso-8859-1').split('\r\n\r\n', 1)[0]
        self.header_length = len(headers_string)
        if self.header_length > MAX_HEADER_SIZE:
            self.error = 413
            self.outgoing = get_response(
                413, f"(header size must not exceed {MAX_HEADER_SIZE} bytes)")
            self.host = None
        else:
            self.method, self.headers = get_header_info_from_string(
                headers_string)
            if self.method not in METHODS:
                self.error = 400
                self.outgoing = get_response(
                    400, f"(unsupported method \"{self.method}\")")
            self.host = self.headers[HOST].split(':', 1)[0] \
                if HOST in self.headers and self.headers[HOST] else None
