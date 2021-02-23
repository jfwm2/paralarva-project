es-rally docker tests
=====================

The idea of these tests is to use a docker three nodes elasticsearch cluster that we will bench with and without our proxy.  

Prerequisite
------------

Install [es-rally], the elasticsearch official benchmark tool

Make sure `vm.max_map_count` is at least `262144`.
```
$ sudo sysctl -w vm.max_map_count=262144
vm.max_map_count = 262144
```

Launch docker elasticsearch containers and create/upgrade helm chart
```
./tests/docker/create_es_clusters_and_build_minkube_chart.sh
removing container es0n1 if it exits
1fbb8f72c75e
container es0n1 created with ID 34b470d3b8b7a1a89dce604dd737f7848572cf4ef263b1abeed0f5ddd6728740
Error response from daemon: network with name elastic already exists
removing container es1n1 if it exits
9e206ff451e9
container es1n1 created with ID e10124d25ffbd45dbaf7269db6971231852da56a1955a544b42fe4f03dff856e
removing container es1n2 if it exits
8bf945d610c9
container es1n2 created with ID 433add78350c1ed7ac55d4345b404c5f06bb2317cf148d5d8eb5b54b166baf92
removing container es1n3 if it exits
67dbcb076ee5
container es1n3 created with ID a2a7cb0ecfcabb008bbb66175d20998b8029e2588dbce6ab147664268822d978
using /dev/fd/63 as config file
installing paralarva helm release...
Error: cannot re-use a name that is still in use
helm release paralarva already installed; upgrading it...
Release "paralarva" has been upgraded. Happy Helming!
NAME: paralarva
LAST DEPLOYED: Sun Feb 21 19:49:30 2021
NAMESPACE: default
STATUS: deployed
REVISION: 64
TEST SUITE: None
```

Launch prometheus container
```
$ prometheus/scrape_paralarva_on_minikube.sh 
removing container paralarva-prometheus if it already exits
container paralarva-prometheus created with ID 187bc23006c2b5d4f44494a3a000a4e33c505296887b58e686800e13cc8660ad
```

Tests result
------------

- [es-rally-es1]: Test result using the proxy (including metrics recorded during the benchmark)
- [es-rally-localhost]: Result of same test targeting directly elasticsearch containers
- [es-rally-comparison]: Comparison and analysis

[es-rally]: https://esrally.readthedocs.io/en/stable/
[es-rally-es1]: esrally-es1.md
[es-rally-localhost]: esrally-localhost.md
[es-rally-comparison]: esrally-comparison.md