import os
import pytest


from paralarva.helper import get_response, get_header_info_from_string, \
    get_config_from_yaml_file, config_is_valid, section_exist_in_config, \
    valid_ip_port_dict, valid_service_list, valid_service

response_skeleton = '\r\nConnection: close\r\nContent-Encoding: identity' \
                    '\r\nContent-Type: text/html\r\nContent-Length: '

responses = {
    '100': 'HTTP/1.1 100 Continue\r\n\r\n',
    '200': f"HTTP/1.1 200 OK{response_skeleton}15\r\n\r\n<h1>200 OK</h1>",
    '200_msg': f"HTTP/1.1 200 OK{response_skeleton}30\r\n\r\n<h1>200 OK THIS_IS_A_TEST</h1>",
    '400': f"HTTP/1.1 400 Bad Request{response_skeleton}31\r\n\r\n<h1>Error 400: Bad Request</h1>",
    '400_msg': f"HTTP/1.1 400 Bad Request{response_skeleton}46\r\n\r\n<h1>Error 400: Bad Request THIS_IS_A_TEST</h1>",
    '413': f"HTTP/1.1 413 Request Entity Too Large{response_skeleton}44"
           f"\r\n\r\n<h1>Error 413: Request Entity Too Large</h1>",
    '413_msg': f"HTTP/1.1 413 Request Entity Too Large{response_skeleton}59"
               f"\r\n\r\n<h1>Error 413: Request Entity Too Large THIS_IS_A_TEST</h1>",
    '500': f"HTTP/1.1 500 Internal Server Error{response_skeleton}41\r\n\r\n<h1>Error 500: Internal Server Error</h1>",
    '500_msg': f"HTTP/1.1 500 Internal Server Error{response_skeleton}56"
               f"\r\n\r\n<h1>Error 500: Internal Server Error THIS_IS_A_TEST</h1>",
    '502': f"HTTP/1.1 502 Bad Gateway{response_skeleton}31\r\n\r\n<h1>Error 502: Bad Gateway</h1>",
    '502_msg': f"HTTP/1.1 502 Bad Gateway{response_skeleton}46\r\n\r\n<h1>Error 502: Bad Gateway THIS_IS_A_TEST</h1>",
    '504': f"HTTP/1.1 504 Gateway Timeout{response_skeleton}35\r\n\r\n<h1>Error 504: Gateway Timeout</h1>",
    '504_msg': f"HTTP/1.1 504 Gateway Timeout{response_skeleton}50"
               f"\r\n\r\n<h1>Error 504: Gateway Timeout THIS_IS_A_TEST</h1>",
}

header_1 = 'test1 test2 test3 test4'
header_2 = header_1 + '\r\n'
header_3 = header_2 + 'Field1:      \r\n  field2 :     Value2   \r\n '
header_4 = header_3 + 'Field3:\r\n   FIELD4 : VALUE4'

test_dir = os.environ.get('TESTS_DIR') if os.environ.get('TESTS_DIR') else '.'
config = get_config_from_yaml_file(
    os.path.abspath(f"{test_dir}/test_config.yaml"))
test_config = {'listen': {'address': '127.0.0.1', 'port': 8080},
               'services': [{'name': 'test-h1', 'domain': 'h1',
                             'hosts': [{'address': '127.0.0.1', 'port': 9200}]},
                            {'name': 'test-h2', 'domain': 'h2',
                             'hosts': [{'address': '127.0.0.1', 'port': 9200},
                                       {'address': '127.0.0.2', 'port': 9200}]},
                            {'name': 'test-h3', 'domain': 'h3',
                             'hosts': [{'address': '127.0.0.1', 'port': 9200},
                                       {'address': '127.0.0.2', 'port': 9200},
                                       {'address': '127.0.0.3', 'port': 9200}]}]}


def test_get_response():
    assert get_response(100) == responses['100'].encode()
    assert get_response(200) == responses['200'].encode()
    assert get_response(200, 'THIS_IS_A_TEST') == responses['200_msg'].encode()
    assert get_response(400) == responses['400'].encode()
    assert get_response(400, 'THIS_IS_A_TEST') == responses['400_msg'].encode()
    assert get_response(413) == responses['413'].encode()
    assert get_response(413, 'THIS_IS_A_TEST') == responses['413_msg'].encode()
    assert get_response(500) == responses['500'].encode()
    assert get_response(500, 'THIS_IS_A_TEST') == responses['500_msg'].encode()
    assert get_response(502) == responses['502'].encode()
    assert get_response(502, 'THIS_IS_A_TEST') == responses['502_msg'].encode()
    assert get_response(504) == responses['504'].encode()
    assert get_response(504, 'THIS_IS_A_TEST') == responses['504_msg'].encode()

    # unknown status code defaults to 500
    assert get_response(0) == responses['500'].encode()
    assert get_response(0, 'THIS_IS_A_TEST') == responses['500_msg'].encode()


def test_get_header_info_from_string():
    assert get_header_info_from_string('') == ('', {})
    assert get_header_info_from_string('Test') == ('TEST', {})
    assert get_header_info_from_string(header_1) == ('TEST1', {})
    assert get_header_info_from_string(header_2) == ('TEST1', {})
    assert get_header_info_from_string(header_3) == (
        'TEST1', {'field1': '', 'field2': 'Value2'})
    assert get_header_info_from_string(header_4) == ('TEST1', {'field1': '', 'field2': 'Value2',
                                                               'field3': '', 'field4': 'VALUE4'})


def test_get_config_from_yaml_file():
    assert config == test_config
    with pytest.raises(Exception):
        get_config_from_yaml_file('fake_config_file.yaml')


def test_config_is_valid():
    assert config_is_valid(config)
    # two services cannot have the same domain
    assert not config_is_valid({'listen': {'address': '127.0.0.1', 'port': 8080},
                                'services': [{'name': 'test-h1', 'domain': 'SAME_DOMAIN',
                                              'hosts': [{'address': '127.0.0.1', 'port': 9200}]},
                                             {'name': 'test-h2', 'domain': 'SAME_DOMAIN',
                                              'hosts': [{'address': '127.0.0.1', 'port': 9200}]}]})
    # two services cannot have the same name
    assert not config_is_valid({'listen': {'address': '127.0.0.1', 'port': 8080},
                                'services': [{'name': 'SAME_NAME', 'domain': 'h1',
                                              'hosts': [{'address': '127.0.0.1', 'port': 9200}]},
                                             {'name': 'SAME_NAME', 'domain': 'h2',
                                              'hosts': [{'address': '127.0.0.1', 'port': 9200}]}]})


def test_section_exist_in_config():
    assert not section_exist_in_config([], {})
    assert not section_exist_in_config(['test'], [])
    assert not section_exist_in_config(['test'], {})
    assert not section_exist_in_config(['test'], {'not_test': None})
    assert section_exist_in_config(['test'], {'test': None})


def test_valid_ip_port_dict():
    assert valid_ip_port_dict({'address': '127.0.0.1', 'port': 1})
    assert not valid_ip_port_dict([None])
    assert not valid_ip_port_dict({'wrong': '127.0.0.1', 'port': 1})
    assert not valid_ip_port_dict({'address': '127.0.0.1', 'wrong': 1})
    assert not valid_ip_port_dict({'address': 1, 'port': 1})
    assert not valid_ip_port_dict({'address': '127.0.0.1', 'port': '1'})
    assert not valid_ip_port_dict({'address': '256.0.0.1', 'port': 1})


def test_valid_service_list():
    assert not valid_service_list({})
    assert not valid_service_list([])


def test_valid_service():
    assert valid_service({'name': 'test-h1', 'domain': 'h1',
                          'hosts': [{'address': '127.0.0.1', 'port': 9200}]})
    assert not valid_service([])
    assert not valid_service({'not_name': 'test-h1', 'domain': 'h1',
                              'hosts': [{'address': '127.0.0.1', 'port': 9200}]})
    assert not valid_service({'name': 'test-h1', 'not_domain': 'h1',
                              'hosts': [{'address': '127.0.0.1', 'port': 9200}]})
    assert not valid_service({'name': 'test-h1', 'domain': 'h1',
                              'not_hosts': [{'address': '127.0.0.1', 'port': 9200}]})
    assert not valid_service({'name': 'test-h1', 'domain': 'h1', 'hosts': []})
    assert not valid_service({'name': 'test-h1', 'domain': 'h1', 'hosts': [0]})
