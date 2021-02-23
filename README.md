Paralarva
=========
This is paralarva ([paralarvae] are baby [squids]), my little proxy.

Overview
========

Implementation
--------------
The core of the implementation is made of 3 classes:
- Proxy ([proxy.py]) that accepts incoming connections and process them using an event loop.
  This class contains methods to parse and validate the proxy configuration (e.g., [config.yaml]) that is used to
  build a dictionary of Balancer objects (see below) to forward incoming requests to the right service.
  Such requests are stored within a [selector].
- Request ([request.py]) handles individual client requests to forward them to the right balancer and send back the
  response or an error.
- Balancer ([balancer.py]) forwards incoming requests to a member server of the current instance and gather the
  response.

In addition, there is a helper module ([helper.py]) which provides constants and helper static functions

Automation
----------
The [helm_chart] directory contains a chart with values ([values.yaml]) and a [templates] directory that contains
the following files (other files in the same directory have not been changed after `helm create` command):

- [configmap.yaml] defines a config map to hold the application configuration.
- [deployment.yaml] contains information about ports, commands options, and configuration.
- [service-app.yaml] and [service-data.yaml] describe services respectively exposing the application, and the monitoring 
  endpoints. Note that to make things compatible with minikube, we specified `NodePort` service types in the
  [values.yaml] file in order be able to reach the application service with ` $(minikube ip):30303` and the monitoring
  endpoint with ` $(minikube ip):30300`.

This chart can be deployed by running `helm install paralarva helm_chart --values helm_chart/values.yaml` at the root
of the project (or `helm upgrade paralarva helm_chart --values helm_chart/values.yaml` if the chart is already
installed). Note that corresponding pods may need to be restarted for some changes to be taken into account. 

The `values` file can also be generated to reflect a proxy configuration provided in a file having the same format as
[config.yaml]. Please, see below ([how to deploy on kubernetes]) for more information.

Monitoring
----------

To guarantee the reliability, performance, and scalability of the service we can define the 3 following SLIs:
- **availability** (over time) to make sure instances of the service are up. We define availability of a service as the 
  ratio of time duration the service responds correctly to a check over the time elapsed since the beginning of the
  monitoring period. Here are two examples:
  - We check a service every minute and 6 checks failed during the last hour. Therefore, we conclude that the 
    service was down 6 minutes for the last 60 minutes which makes the availability at 90%.
  - We can implement an availability SLI using only a counter that is incremented with the time
    in seconds (in most TSDB) since the last check only if the current checks succeeds. To obtain the value of the
    availability over the last 10 minutes (600 seconds), we divide the time derivative of our counter by this 600:
    - if all (resp. none of the) checks were successful during the last 10 minutes, our counter increased by 600
      (resp. 0), so the availability over time is 100% (resp. 0%).
    - if a few checks failed with the sum of durations between a (first) failure (possibly of a series of failures)
      and the next success (or the end of the monitoring period) being 30 seconds, our counter would increase by 570
      seconds during a 10 minutes period, leading to an availability rate of 95% (`570 / 600 = 0.95`).
- **latency** to guarantee that requests are served in an acceptable time. Using the average of latency may lead to
  counter-intuitive views. For example, few requests can be processed very fast (possibly due to errors),
  making slow requests undetectable since the average value could be acceptable because it is just being artificially
  lowered. Therefore, we prefer to use percentiles; for example, a given value of the 95th percentile means that 95% of
  requests had a latency less than this value. To compute such values, we can just keep track of bucketed time values
  and [derive percentiles from binned data] or use a TSDB build-in function (like [histogram_quantile] if we use
  [prometheus]).
- **error rate** to ensure that proper responses are served. We can compute the number of errors over time, but it would
  not be meaningful if we do not take into account the total number of requests. Therefore, we should use the ratio of
  errors over the total number of requests. To do so, we just need to keep track of the total number of requests, and 
  the number errors. If we use counters, we can easily compute this indicator for a time range using the ratio of the
  derivatives of the error counter over the requests one.

We used [prometheus] to define some related metrics (see [prometheus metrics]).

Future improvements
===================
- support the [transfer-encoding] http header (at the present time only payload 
  pertaining to message having a [content-length] header are supported)
- use a proper health check for liveliness/readiness probes instead of the metrics
  endpoint  
- use multithreading/processing to handle requests in an asynchronous way
- when some request to a service fails because of a faulty server
  - blacklist the server for a while
  - retry with another member of the service
- use a builder and a slim image in docker file for better isolation
- extensive testing (as of now only content of [helper.py] and [proxy.py] are extensively tested)

How to build
============

  1) Init environment `source ./bootstrap.sh`

  2) Check help `python main.py --help`

  3) Run your program `python main.py [options]`

How to test
===========

  1) Init environment `source ./bootstrap.sh`

  2) `TESTS_DIR=tests python -m pytest`

  3) `python main.py -f tests/test_config.yaml`

  4) `docker run -d --name "test-es" -p 9200:9200 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.11.0`
 
  5) run the command below (make sure to run `source ./bootstrap.sh` again if you are in another terminal, so the correct environment is being used)
     ```
     while true; do
       python tests/docker/fake_doc.py | curl -i -X POST "localhost:8080/my-index/_doc/?pretty" \
       -H 'Host: h1' -H 'Content-Type: application/json' --data-binary @-
     done
     ```

How to build/push docker image
==============================

  1) `docker login --username=xxxxxxxx`

  2) `docker build -t /paralarva:$(cat VERSION) --rm --force-rm .`

  3) `docker push xxxxxxxx/paralarva:$(cat VERSION)`

How to deploy on kubernetes
===========================

  1) Make any change to [chart_base_values.yaml] (this is the basis for the
  values of the chart to be deployed) and [config.yaml] (or another configuration
  file)

  2) run `./build_and_deploy_chart.sh [config_file.yaml]` 
     Note that corresponding pods may need to be restarted for some changes to be taken into account.

  3) the service is reachable on node port 30303 (see below example with `minikube`)

```
$ curl $(minikube ip):30303
<h1>Error 400: Bad Request</h1>
$ curl $(minikube ip):30303 -H 'Host: my-service.my-company.com'
<h1>200 OK (dry-run)</h1>
```

How to test minikube setup
==========================

Using only docker
-----------------

prerequisite:
 - 8 gb memory available
 - [Set vm.max_map_count to at least 262144] 
   **This is important! Elasticsearch containers in a cluster may fail without this setting**.

launch a prometheus container (optional)
```
$ prometheus/scrape_paralarva_on_minikube.sh 
removing container paralarva-prometheus if it already exits
container paralarva-prometheus created with ID 187bc23006c2b5d4f44494a3a000a4e33c505296887b58e686800e13cc8660ad
```

launch two docker elasticsearch clusters (`es0` with 1 node and `es1` with 3 nodes)
and install/upgrade helm chart accordingly. Note that corresponding pods may need to be restarted
for some changes to be taken into account. 
```
$ ./tests/docker/create_es_clusters_and_build_minkube_chart.sh
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

Send random data to `es1` or `es0` (change the host header accordingly). Before running the command below, make sure
the correct python virtual environment is activated (run `source ./bootstrap.sh` if needed)
```
while true; do
  python tests/docker/fake_doc.py | curl -i -X POST "$(minikube ip):30303/my-index/_doc/?pretty" \
  -H 'Host: es1' -H 'Content-Type: application/json' --data-binary @-
done
```

Check what is going on in prometheus (http://localhost:9090)

Using docker and the official elasticsearch benchmark tool
----------------------------------------------------------

The full test is summarized here: [es-rally]

[balancer.py]: src/paralarva/balancer.py
[chart_base_values.yaml]: chart_base_values.yaml
[configmap.yaml]: helm_chart/templates/configmap.yaml
[config.yaml]: config.yaml
[content-length]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Length
[deployment.yaml]: helm_chart/templates/deployment.yaml
[derive percentiles from binned data]: https://stats.stackexchange.com/questions/65710/derive-percentiles-from-binned-data?newreg=9159840caa9548dc8322ca7addf17a03
[es-rally]: tests/docker/esrally.md
[helm_chart]: helm_chart
[helper.py]: src/paralarva/helper.py
[histogram_quantile]: https://prometheus.io/docs/prometheus/latest/querying/functions/#histogram_quantile
[how to deploy on kubernetes]: #how-to-deploy-on-kubernetes
[paralarvae]: https://en.wikipedia.org/wiki/Paralarva
[prometheus]: https://prometheus.io/
[prometheus metrics]: prometheus/prom.md
[proxy.py]: src/paralarva/proxy.py
[request.py]: src/paralarva/request.py
[selector]: https://docs.python.org/3/library/selectors.html
[set vm.max_map_count to at least 262144]: https://www.elastic.co/guide/en/elasticsearch/reference/7.5/docker.html#_set_vm_max_map_count_to_at_least_262144
[service-app.yaml]: helm_chart/templates/service-app.yaml
[service-data.yaml]: helm_chart/templates/service-data.yaml
[squids]: https://en.wikipedia.org/wiki/Squid_(software)
[templates]:  helm_chart/templates
[transfer-encoding]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding
[values.yaml]: helm_chart/values.yaml
