import os
from paralarva.proxy import Proxy

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

test_dir = os.environ.get('TESTS_DIR') if os.environ.get('TESTS_DIR') else '.'
proxy = Proxy(file_name=os.path.abspath(f"{test_dir}/test_config.yaml"))


def test_proxy():
    assert proxy


def test_proxy_config():
    assert proxy.config == test_config
