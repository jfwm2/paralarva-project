import random
from paralarva.balancer import Balancer, RROBIN, RANDOM

default_strategy_balancer = Balancer(name='default_balancer', domain='default',
                                     hosts=[('host0', 0), ('host1', 0), ('host2', 0), ('host3', 0), ('host4', 0)])

random_strategy_balancer = Balancer(name='random_balancer', domain='domain', strategy=RANDOM,
                                    hosts=[('host0', 0), ('host1', 0), ('host2', 0), ('host3', 0), ('host4', 0)])

rrobin_strategy_balancer = Balancer(name='rrobin_balancer', domain='rrobin',strategy=RROBIN,
                                    hosts=[('host0', 0), ('host1', 0), ('host2', 0), ('host3', 0), ('host4', 0)])

minimal_rrobin_strategy_balancer_balancer = Balancer(name='minimal_rrobin_balancer', domain='minimal_rrobin',
                                                     strategy=RROBIN, hosts=[('host0', 0)])


def test_default_strategy_is_random():
    assert default_strategy_balancer.strategy == RANDOM


def test_random_strategy_get_host_index():
    random.seed(0)
    assert random_strategy_balancer.get_host_index() == 3
    assert random_strategy_balancer.get_host_index() == 3
    assert random_strategy_balancer.get_host_index() == 0
    assert random_strategy_balancer.get_host_index() == 2
    assert random_strategy_balancer.get_host_index() == 4
    assert random_strategy_balancer.get_host_index() == 3
    assert random_strategy_balancer.get_host_index() == 3
    assert random_strategy_balancer.get_host_index() == 2
    assert random_strategy_balancer.get_host_index() == 3


def test_rrobin_strategy_get_host_index():
    assert rrobin_strategy_balancer.get_host_index() == 1
    assert rrobin_strategy_balancer.get_host_index() == 2
    assert rrobin_strategy_balancer.get_host_index() == 3
    assert rrobin_strategy_balancer.get_host_index() == 4
    assert rrobin_strategy_balancer.get_host_index() == 0
    assert rrobin_strategy_balancer.get_host_index() == 1
    assert rrobin_strategy_balancer.get_host_index() == 2


def test_minimal_rrobin_strategy_get_host_index():
    assert minimal_rrobin_strategy_balancer_balancer.get_host_index() == 0
    assert minimal_rrobin_strategy_balancer_balancer.get_host_index() == 0

