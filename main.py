import argparse
import logging
import os
import prometheus_client
from paralarva.helper import DEFAULT_TIMEOUT
from paralarva.proxy import Proxy

DEFAULT_CONFIG_FILE = 'config.yaml'
DEFAULT_PROMETHEUS_PORT = 8000
DEFAULT_LOG_LEVEL = 'info'
LOG_NAME_TO_LEVEL = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARN,
    'error': logging.ERROR,
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Paralarva little proxy launcher')
    parser.add_argument('-f', '--file',
                        type=str,
                        default=DEFAULT_CONFIG_FILE,
                        help=f"yaml configuration file (default: {DEFAULT_CONFIG_FILE})")
    parser.add_argument('-l', '--log-level',
                        choices=LOG_NAME_TO_LEVEL.keys(),
                        default=DEFAULT_LOG_LEVEL,
                        help=f"Log level (default: {DEFAULT_LOG_LEVEL})")
    parser.add_argument('-p', '--prometheus-port',
                        type=int,
                        default=DEFAULT_PROMETHEUS_PORT,
                        help=f"Log level (default: {DEFAULT_PROMETHEUS_PORT})")
    parser.add_argument('-n', '--next-port',
                        action='store_true',
                        help='If listening port already used increment it until a free port is found')
    parser.add_argument('-d', '--dry-run',
                        action='store_true',
                        help='Dry run flag')
    parser.add_argument('-a', '--listen-all-addr',
                        action='store_true',
                        help='Use when running in a container so proxy will listen on 0.0.0.0')
    parser.add_argument('-t', '--timeout',
                        type=int,
                        default=round(DEFAULT_TIMEOUT),
                        help='Default timeout in seconds for connection to remote services')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                        level=LOG_NAME_TO_LEVEL[args.log_level])
    # start prometheus
    logging.info(
        f"starting prometheus exporter on port {args.prometheus_port}")
    try:
        prometheus_client.start_http_server(args.prometheus_port)
    except Exception as e:
        logging.warning(f"error: prometheus exception: {repr(e)}")

    # instantiate proxy and launch it
    proxy = Proxy(file_name=os.path.abspath(args.file),
                  next_port=args.next_port,
                  timeout=float(args.timeout),
                  listen_all_addr=args.listen_all_addr,
                  dry_run=args.dry_run)
    proxy.run()
