"""
This module provides constant variables and helper static functions
"""

import logging
import ipaddress
import yaml
from typing import Dict, List, Optional, Tuple

# Default timeout in seconds
DEFAULT_TIMEOUT = 10.0

# Status codes handled
GATEWAY_TIMEOUT = 504
BAD_GATEWAY = 502
SERVER_ERROR = 500
ENTITY_TOO_LARGE = 413
BAD_REQUEST = 400
OK = 200
CONTINUE = 100

_status_to_text = {
    CONTINUE: 'Continue',
    OK: 'OK',
    BAD_REQUEST: 'Bad Request',
    ENTITY_TOO_LARGE: 'Request Entity Too Large',
    SERVER_ERROR: 'Internal Server Error',
    BAD_GATEWAY: 'Bad Gateway',
    GATEWAY_TIMEOUT: 'Gateway Timeout',
}

# http header fields handled
CONTENT_LENGTH_HEADER = 'content-length'
TRANSFER_ENCODING_HEADER = 'transfer-encoding'
EXPECT_HEADER = 'expect'

# all http Methods
METHODS = ['CONNECT', 'DELETE', 'GET', 'HEAD',
           'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE']

# Host field in http header
HOST = 'host'


def get_response(code: int, additional_text: str = None) -> bytes:
    """
    Format a basic http 1.1 response mostly used for errors and for dry runs

    :param code: http status code
    :param additional_text: optional additional text to be added in the body of
    the response
    :return: an array of bytes containing the response
    """
    if code not in _status_to_text:
        logging.debug(f"unknown or unhandled status code {code} "
                      f"(additional text: \"{additional_text}\") - "
                      "changing status code to 500")
        code = SERVER_ERROR
    message_text = f"{code} {_status_to_text[code]}" if code < 400 else \
        f"Error {code}: {_status_to_text[code]}"
    if additional_text:
        message_text += f" {additional_text}"
    elif code < 200:
        return f"HTTP/1.1 {code} {_status_to_text[code]}\r\n\r\n".encode()
    body_text = f"<h1>{message_text}</h1>"
    return f"HTTP/1.1 {code} {_status_to_text[code]}\r\n" \
           "Connection: close\r\n" \
           "Content-Encoding: identity\r\n" \
           "Content-Type: text/html\r\n" \
           f"Content-Length: {len(body_text)}\r\n\r\n" \
           f"{body_text}".encode()


def get_header_info_from_string(
        header_string: str) -> Tuple[Optional[str], Dict[str, Optional[str]]]:
    """
    Return http method and dict with headers field of an http request

    :param header_string: string containing the header of an http request
    :return: a tuple formed with (1) am uppercase string containing the http
    method of the request and (2) a dict having as keys strings containing http
    header fields and as values None or strings containing such fields values
    """
    headers = {}
    method = header_string.split(' ', 1)[0].upper()
    lines = [line for line in header_string.split('\r\n')]
    for i in range(1, len(lines)):
        line_split = lines[i].split(':', 1)
        key = line_split[0].strip()
        if len(key) == 0:
            continue
        else:
            headers[key.lower()] = line_split[1].strip() if len(
                line_split) == 2 else None
    return method, headers


def get_config_from_yaml_file(file_name: str) -> Dict:
    """
    Parse a yaml configuration file and return dict

    :param file_name: yaml configuration file
    :return: a dict with the following structure (with possibly more services
    and hosts in services)
    {'listen': {'address': '127.0.0.1', 'port': 8080},
     'services': [{'name': 'test-h1',
                   'domain': 'h1',
                   'hosts': [{'address': '127.0.0.1', 'port': 9200}]}
    """
    logging.info(f"retrieving configuration from {file_name}")
    with open(file_name) as file:
        documents = yaml.full_load(file)
    config = documents['proxy']
    logging.debug(f"configuration retrieved: {config}")
    return config


def config_is_valid(config: Dict) -> bool:
    """
    Check if a configuration is valid

    :param config: dict containing a configuration
    :return: True is the config is valid, False otherwise
    """
    return section_exist_in_config(['listen', 'services'], config) \
           and section_exist_in_config(['address', 'port'], config['listen']) \
           and valid_ip_port_dict(config['listen']) \
           and valid_service_list(config['services'])


def section_exist_in_config(section_list: List[str], config: Dict) -> bool:
    """
    Check if the all keys of a list are also keys of a dict

    :param section_list: list of keys
    :param config: dict to be check
    :return: True if all keys of the list are top level keys of the dict,
    False otherwise
    """
    if len(section_list) == 0:
        logging.error(f"unexpected empty section list")
        return False
    if not isinstance(config, dict):
        logging.error(f"expected a dict, instead got {config}")
        return False
    for section_name in section_list:
        if section_name not in config:
            logging.error(f"no section {section_name} in {config}")
            return False
    return True


def valid_ip_port_dict(ip_port_dict: Dict) -> bool:
    """
    check if a dict respect the format
    {'address': '<VALID_IP>', 'port': <PORT_NUMBER>}

    :param ip_port_dict: Dict to be checked
    :return: True if the format is respected and the ip address is valid,
    False otherwise
    """
    if not isinstance(ip_port_dict, dict):
        logging.error(f"expected a dict, instead got {ip_port_dict}")
        return False
    for name in ['address', 'port']:
        if name not in ip_port_dict:
            logging.error(f"no section {name} in {ip_port_dict}")
            return False
    if not isinstance(ip_port_dict['address'], str):
        logging.error(f"{ip_port_dict['address']} type is not str")
        return False
    if not isinstance(ip_port_dict['port'], int):
        logging.error(f"{ip_port_dict['port']} type is not int")
        return False
    try:
        ipaddress.ip_address(ip_port_dict['address'])
    except ValueError:
        logging.error(f"{ip_port_dict['address']} is not a valid ip address")
        return False
    return True


def valid_service_list(service_list: List) -> bool:
    """
    check if a list if non empty and contains valid services

    :param service_list: list to be checked
    :return: True if the list is conform, False otherwise
    """
    if not isinstance(service_list, list):
        logging.error(f"expected a list, instead got {service_list}")
        return False
    if len(service_list) == 0:
        logging.error(f"service list is empty")
        return False

    domain_list, name_list = [], []
    for service in service_list:
        if not valid_service(service):
            return False
        domain, name = service['domain'], service['name']

        if domain in domain_list:
            logging.error(f"duplicate service domain: \"{domain}\"")
            return False
        elif name in name_list:
            logging.error(f"duplicate service name: \"{name}\"")
            return False
        else:
            domain_list.append(domain)
            name_list.append(name)
    return True


def valid_service(service: Dict) -> bool:
    """
    Check if a dict is a valid service

    :param service: dict containing a service
    :return: True if the service is valid, False otherwise
    """
    if not isinstance(service, Dict):
        logging.error(f"expected a dict, instead got {service}")
        return False
    for item in ['name', 'domain', 'hosts']:
        if item not in service:
            logging.error(f"no section {item} in {service}")
            return False
    for item in ['name', 'domain']:
        if not isinstance(service[item], str):
            logging.error(f"expected a str, instead got {service[item]}")
            return False
    if not isinstance(service['hosts'], list):
        logging.error("expected a list of host for service "
                      f"{service['name']}, instead got {service['hosts']}")
        return False
    if len(service['hosts']) == 0:
        logging.error(f"hosts list of service {service['name']} is empty")
        return False
    for host in service['hosts']:
        if not valid_ip_port_dict(host):
            return False
    return True
