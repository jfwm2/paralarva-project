"""
The Proxy class represents a proxy that accepts incoming requests that are
stored in and selector and processed thereafter
"""

import logging
import selectors
import socket
from paralarva.balancer import Balancer
from paralarva.helper import config_is_valid, get_config_from_yaml_file, DEFAULT_TIMEOUT
from paralarva.request import Request
from typing import Any, Dict, NoReturn


class Proxy:
    def __init__(self, file_name: str, next_port: bool = False, timeout: float = DEFAULT_TIMEOUT,
                 listen_all_addr: bool = False, dry_run: bool = False) -> None:
        """
        Create a new proxy object

        :param file_name: file containing the config file to use
        :param next_port: when the port chosen to listen is not free, try the
        next one if this parameter is True, otherwise the exception is not
        caught (useful for debug)
        :param listen_all_addr: if True will listen on all ip addresses instead
        of only the one specified in the configuration
        :param timeout: time after which the query the a member server times out
        :param dry_run: if True, dry run mode: requests are not actually
        proxied, but a 200 OK response is returned to the client
        """
        config = get_config_from_yaml_file(file_name)
        if config_is_valid(config):
            self.config = config
        else:
            raise Exception("invalid configuration")

        if listen_all_addr:
            logging.info("listening on all ip addresses instead of only "
                         f"{self.config['listen']['address']}")
            self.config['listen']['address'] = '0.0.0.0'

        self.dry_run = dry_run
        self.next_port = next_port
        self.balancers = self.generate_balancers(timeout)
        self.selector = selectors.DefaultSelector()
        self.test_counter = 0

    def run(self) -> NoReturn:
        """
        run the proxy but creating a listen socket registered to a selector,
        thereafter incoming requests are accepted and processed in an event
        loop

        :return: no return
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.config['listen']['address'],
                          self.config['listen']['port'])
        if self.next_port:
            while True:
                try:
                    sock.bind(server_address)
                except OSError as ose:
                    if ose.args[0] != 48 and ose.args[0] != 98:
                        raise
                    logging.info(f"port {server_address[1]} already in use")
                    server_address = server_address[0], server_address[1] + 1
                else:
                    break
        else:
            sock.bind(server_address)
        sock.listen()
        logging.info(f"proxy listening on {server_address}")
        sock.setblocking(False)
        self.selector.register(sock, selectors.EVENT_READ, data=None)

        while True:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_connection(key)
                else:
                    try:
                        key.data.process_connection(mask)
                    except Exception as e:
                        logging.warning(
                            f"error: connection processing exception for "
                            f"{key.data.address}: {repr(e)}")
                        key.data.close()

    def accept_connection(self, key: Any) -> None:
        """
        accept an incoming connection that is register in the selector instance
        attribute

        :param key: selector key for the current incoming connection
        :return: None
        """
        sock = key.fileobj
        connection, address = sock.accept()
        logging.info(f"accepting connection from {address}")
        connection.setblocking(False)
        self.selector.register(connection,
                               selectors.EVENT_READ | selectors.EVENT_WRITE,
                               data=Request(address, self.balancers,
                                            self.selector, connection))

    def generate_balancers(self, timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Balancer]:
        """
        generate a dict container balancers associated to services

        :param timeout: time after which the query the a member server times out
        :return: a dict having services' domain as keys and pertaining
        balancers' abjects as values
        """
        balancers = {}
        for s in self.config['services']:
            name = s['name']
            domain = s['domain']
            hosts = [(h['address'], h['port']) for h in s['hosts']]
            balancers[domain] = Balancer(
                name=name, domain=domain, hosts=hosts, socket_timeout=timeout, dry_run=self.dry_run)
        return balancers
