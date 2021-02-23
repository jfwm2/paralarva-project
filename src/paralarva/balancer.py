"""
The Balancer class forwards incoming requests to a member server of the
current instance and gather the response.
"""

import logging
import random
import socket
import uuid
from paralarva.helper import get_response, \
    get_header_info_from_string, CONTENT_LENGTH_HEADER, CONTINUE, DEFAULT_TIMEOUT
from prometheus_client import Histogram
from typing import Any, Optional, List, Tuple

# Default buffer size in bytes
BUFFER_SIZE = 4096

# Strategies
RROBIN = 10
RANDOM = 0

_strategy_to_name = {
    RROBIN: 'RROBIN',
    RANDOM: 'RANDOM',
}

_name_to_strategy = {
    'RROBIN': RROBIN,
    'RANDOM': RANDOM,
}

# Prometheus metric to track time spent and requests made.
request_time = Histogram('request_processing_seconds',
                         'Time spent processing requests', ['server', 'port'])
socket_latency = Histogram('socket_exchange_latency_seconds',
                           'Time spend between sending and receiving data on current socket'
                           'on a socket to server', ['order', 'server', 'port'])


class Balancer:
    def __init__(self, name: str, domain: str,
                 hosts: List[Tuple[str, int]], strategy: int = RANDOM,
                 socket_timeout: float = DEFAULT_TIMEOUT,
                 dry_run: bool = False) -> None:
        """
        create an instance of balancer for a given service identified by its
        domain

        :param name: name of the service pertaining to the balancer
        :param domain: domain of the service pertaining to the balancer
        :param hosts: list of member servers identified by ip_address and port)
        :param strategy: load balancing strategy only random is supported, but
        a minimal version of round robin was also implemented
        :param socket_timeout: time after which the query the a member server
        times out
        :param dry_run: if True, dry run mode: requests are not actually
        proxied, but a 200 OK response is returned
        """
        logging.debug(f"creating balancer {name} for domain {domain} with "
                      f"hosts {hosts} using {_strategy_to_name[strategy]} "
                      "strategy")
        self.name = name
        self.domain = domain
        self.hosts = hosts
        self.strategy = strategy
        self.dry_run = dry_run

        logging.info(f"default socket timeout set to {socket_timeout} seconds for balancer {name}")
        socket.setdefaulttimeout(socket_timeout)

        # initialize the random number generator used by the random strategy
        random.seed()

        # used to keep track of last choice using round robin strategy
        self.rr_last = 0

    def forward_and_get_response(self, data: Any, head: Any,
                                 request_id: Optional[uuid.uuid1] = None
                                 ) -> Tuple[Optional[int], Any]:
        """
        forward the request receive to one of the member servers of the
        balancer and return the response

        :param data: the request to forward (head + body or only body)
        :param head: the head of the request to forward if not included in
        the data parameter, otherwise it is zero length
        :param request_id: optional request id
        :return: a tuple containing an optional error code and the response
        (or error message) to send back;  if dry run
        mode is active (self.dry_run == True) 200 OK response is returned
        """
        error, response = None, None
        host_index = self.get_host_index(request_id)
        if self.dry_run:
            logging.error(f"{request_id} - 200 OK (dry run)")
            response = get_response(200, "(dry-run)")
        else:
            host = self.hosts[host_index]
            with request_time.labels(server=host[0], port=host[1]).time():
                error, response = self.send_request_and_get_response(
                    host, data, head, request_id)
        return error, response

    def get_host_index(self, request_id: Optional[uuid.uuid1] = None) -> int:
        """
        find the index in the member servers hosts list (according to the
        balancing strategy) of the hosts to which a request will be forwarded

        :param request_id: optional request id
        :return: an index of self.hosts chosen according to the current
        balancing strategy
        """
        if self.strategy == RANDOM:
            host_index = random.randrange(len(self.hosts))
        elif self.strategy == RROBIN:
            self.rr_last = (self.rr_last + 1) % len(self.hosts)
            host_index = self.rr_last
        else:
            raise ValueError(
                f"{request_id} - {self.strategy} is not a valid load "
                "balancing strategy identifier")
        logging.debug(
            f"{request_id} - balancer {self.name}: "
            f"choosing {self.hosts[host_index]}")
        return host_index

    @staticmethod
    def send_request_and_get_response(host: Tuple[str, int], data: Any, head: Any,
                                      request_id: Optional[uuid.uuid1] = None) -> Tuple[Optional[int], Any]:
        """
        send a request to given host (specified with ip address + port) and
        retrieve the response

        :param host: ip address + port of socket for sending the request
        :param data: the request to forward (head + body or only body)
        :param head: the head of the request to forward if not included in
        the data parameter, otherwise it is zero length
        :param request_id: optional request id
        :return: a tuple containing an optional error code and the response
        (or error message) to send back
        """
        error, response = None, None
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # order number of exchange on the socket with the server (use for SLx)
        # order is None for head and 1 for the first payload packet; if head
        # is with the data payload, we start at 0; this way packet with order
        # number 1 is the first one being sent without head data
        order = None

        logging.debug(
            f"{request_id} - processing request; head: {head} - data: {data} ")
        try:
            sock.connect(host)

            if head:
                logging.debug(f"{request_id} sending {head} to {host}")
                with socket_latency.labels(order=order, server=host[0],
                                           port=host[1]).time():
                    sock.send(head)
                    response = sock.recv(BUFFER_SIZE)
                order = 1
                logging.debug(f"{request_id} - response received from "
                              f"{host}: {response}")

                if response != get_response(CONTINUE):
                    sock.close()
                    return error, response

            logging.debug(f"{request_id}  sending {data} to {host}")
            if not order:
                order = 0
            with socket_latency.labels(order=order, server=host[0],
                                       port=host[1]).time():
                sock.sendall(data + "\r\n\r\n".encode())
                response = sock.recv(BUFFER_SIZE)
            headers_string = str(
                response, 'iso-8859-1').split('\r\n\r\n', 1)[0]
            _, headers = get_header_info_from_string(headers_string)
            length = len(headers_string) + int(headers[CONTENT_LENGTH_HEADER]) + 4

            logging.debug(f"{request_id} - response received from {host}: "
                          f"{response} - length: {len(response)}/{length}")

            while len(response) < length:
                order += 1
                with socket_latency.labels(order=order, server=host[0],
                                           port=host[1]).time():
                    incoming = sock.recv(BUFFER_SIZE)
                response += incoming
                logging.debug(f"{request_id} - response received from {host}: "
                              f"{response} - length: {len(response)}/{length}")
        except socket.timeout:
            logging.error(f"{request_id} - 504 Gateway Timeout")
            error, response = 504, get_response(504)
        except OSError:
            logging.error(f"{request_id} - 502 Bad Gateway")
            error, response = 502, get_response(502)
        finally:
            sock.close()

        return error, response
