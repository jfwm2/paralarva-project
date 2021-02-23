es-rally docker baseline
========================

Instead of using our proxy, we target directly members of the elasticsearch cluster

Test result
-----------
```
$ esrally race --track=percolator --target-hosts=localhost:9201,localhost:9202,localhost:9203 --pipeline=benchmark-only --user-tag="localhost:920x"

    ____        ____
   / __ \____ _/ / /_  __
  / /_/ / __ `/ / / / / /
 / _, _/ /_/ / / / /_/ /
/_/ |_|\__,_/_/_/\__, /
                /____/

[INFO] Racing on track [percolator], challenge [append-no-conflicts] and car ['external'] with version [7.11.0].

Running delete-index                                                           [100% done]
Running create-index                                                           [100% done]
Running check-cluster-health                                                   [100% done]
Running index                                                                  [100% done]
Running refresh-after-index                                                    [100% done]
Running force-merge                                                            [100% done]
Running refresh-after-force-merge                                              [100% done]
Running wait-until-merges-finish                                               [100% done]
Running percolator_with_content_president_bush                                 [100% done]
Running percolator_with_content_saddam_hussein                                 [100% done]
Running percolator_with_content_hurricane_katrina                              [100% done]
Running percolator_with_content_google                                         [100% done]
Running percolator_no_score_with_content_google                                [100% done]
Running percolator_with_highlighting                                           [100% done]
Running percolator_with_content_ignore_me                                      [100% done]
Running percolator_no_score_with_content_ignore_me                             [100% done]

------------------------------------------------------
    _______             __   _____
   / ____(_)___  ____ _/ /  / ___/_________  ________
  / /_  / / __ \/ __ `/ /   \__ \/ ___/ __ \/ ___/ _ \
 / __/ / / / / / /_/ / /   ___/ / /__/ /_/ / /  /  __/
/_/   /_/_/ /_/\__,_/_/   /____/\___/\____/_/   \___/
------------------------------------------------------
            
|                                                         Metric |                                       Task |       Value |   Unit |
|---------------------------------------------------------------:|-------------------------------------------:|------------:|-------:|
|                     Cumulative indexing time of primary shards |                                            |     10.8044 |    min |
|             Min cumulative indexing time across primary shards |                                            |     1.35195 |    min |
|          Median cumulative indexing time across primary shards |                                            |     2.02483 |    min |
|             Max cumulative indexing time across primary shards |                                            |     2.76745 |    min |
|            Cumulative indexing throttle time of primary shards |                                            |           0 |    min |
|    Min cumulative indexing throttle time across primary shards |                                            |           0 |    min |
| Median cumulative indexing throttle time across primary shards |                                            |           0 |    min |
|    Max cumulative indexing throttle time across primary shards |                                            |           0 |    min |
|                        Cumulative merge time of primary shards |                                            |    0.448833 |    min |
|                       Cumulative merge count of primary shards |                                            |          15 |        |
|                Min cumulative merge time across primary shards |                                            |   0.0441333 |    min |
|             Median cumulative merge time across primary shards |                                            |   0.0837833 |    min |
|                Max cumulative merge time across primary shards |                                            |     0.17135 |    min |
|               Cumulative merge throttle time of primary shards |                                            |           0 |    min |
|       Min cumulative merge throttle time across primary shards |                                            |           0 |    min |
|    Median cumulative merge throttle time across primary shards |                                            |           0 |    min |
|       Max cumulative merge throttle time across primary shards |                                            |           0 |    min |
|                      Cumulative refresh time of primary shards |                                            |     0.87695 |    min |
|                     Cumulative refresh count of primary shards |                                            |          85 |        |
|              Min cumulative refresh time across primary shards |                                            |    0.155317 |    min |
|           Median cumulative refresh time across primary shards |                                            |    0.173833 |    min |
|              Max cumulative refresh time across primary shards |                                            |    0.202583 |    min |
|                        Cumulative flush time of primary shards |                                            |           0 |    min |
|                       Cumulative flush count of primary shards |                                            |           5 |        |
|                Min cumulative flush time across primary shards |                                            |           0 |    min |
|             Median cumulative flush time across primary shards |                                            |           0 |    min |
|                Max cumulative flush time across primary shards |                                            |           0 |    min |
|                                        Total Young Gen GC time |                                            |      62.335 |      s |
|                                       Total Young Gen GC count |                                            |        7960 |        |
|                                          Total Old Gen GC time |                                            |           0 |      s |
|                                         Total Old Gen GC count |                                            |           0 |        |
|                                                     Store size |                                            |   0.0473203 |     GB |
|                                                  Translog size |                                            | 2.56114e-07 |     GB |
|                                         Heap used for segments |                                            |   0.0451202 |     MB |
|                                       Heap used for doc values |                                            |  0.00566101 |     MB |
|                                            Heap used for terms |                                            |   0.0256348 |     MB |
|                                            Heap used for norms |                                            |           0 |     MB |
|                                           Heap used for points |                                            |           0 |     MB |
|                                    Heap used for stored fields |                                            |   0.0138245 |     MB |
|                                                  Segment count |                                            |          28 |        |
|                                                 Min Throughput |                                      index |     4834.48 | docs/s |
|                                                Mean Throughput |                                      index |     13172.6 | docs/s |
|                                              Median Throughput |                                      index |     13015.6 | docs/s |
|                                                 Max Throughput |                                      index |     20415.7 | docs/s |
|                                        50th percentile latency |                                      index |     1177.38 |     ms |
|                                        90th percentile latency |                                      index |     3115.16 |     ms |
|                                        99th percentile latency |                                      index |     5812.07 |     ms |
|                                       100th percentile latency |                                      index |     6357.44 |     ms |
|                                   50th percentile service time |                                      index |     1177.38 |     ms |
|                                   90th percentile service time |                                      index |     3115.16 |     ms |
|                                   99th percentile service time |                                      index |     5812.07 |     ms |
|                                  100th percentile service time |                                      index |     6357.44 |     ms |
|                                                     error rate |                                      index |           0 |      % |
|                                                 Min Throughput |     percolator_with_content_president_bush |       10.16 |  ops/s |
|                                                Mean Throughput |     percolator_with_content_president_bush |       11.34 |  ops/s |
|                                              Median Throughput |     percolator_with_content_president_bush |       11.37 |  ops/s |
|                                                 Max Throughput |     percolator_with_content_president_bush |       12.59 |  ops/s |
|                                        50th percentile latency |     percolator_with_content_president_bush |     10177.4 |     ms |
|                                        90th percentile latency |     percolator_with_content_president_bush |     11279.9 |     ms |
|                                        99th percentile latency |     percolator_with_content_president_bush |     11530.4 |     ms |
|                                       100th percentile latency |     percolator_with_content_president_bush |     11563.9 |     ms |
|                                   50th percentile service time |     percolator_with_content_president_bush |     52.5607 |     ms |
|                                   90th percentile service time |     percolator_with_content_president_bush |     69.8574 |     ms |
|                                   99th percentile service time |     percolator_with_content_president_bush |     84.9698 |     ms |
|                                  100th percentile service time |     percolator_with_content_president_bush |     86.8688 |     ms |
|                                                     error rate |     percolator_with_content_president_bush |           0 |      % |
|                                                 Min Throughput |     percolator_with_content_saddam_hussein |       29.18 |  ops/s |
|                                                Mean Throughput |     percolator_with_content_saddam_hussein |       29.61 |  ops/s |
|                                              Median Throughput |     percolator_with_content_saddam_hussein |       29.62 |  ops/s |
|                                                 Max Throughput |     percolator_with_content_saddam_hussein |       30.04 |  ops/s |
|                                        50th percentile latency |     percolator_with_content_saddam_hussein |     2095.94 |     ms |
|                                        90th percentile latency |     percolator_with_content_saddam_hussein |     2554.42 |     ms |
|                                        99th percentile latency |     percolator_with_content_saddam_hussein |     2608.29 |     ms |
|                                       100th percentile latency |     percolator_with_content_saddam_hussein |      2609.1 |     ms |
|                                   50th percentile service time |     percolator_with_content_saddam_hussein |      32.569 |     ms |
|                                   90th percentile service time |     percolator_with_content_saddam_hussein |     43.9783 |     ms |
|                                   99th percentile service time |     percolator_with_content_saddam_hussein |     64.1918 |     ms |
|                                  100th percentile service time |     percolator_with_content_saddam_hussein |     71.7447 |     ms |
|                                                     error rate |     percolator_with_content_saddam_hussein |           0 |      % |
|                                                 Min Throughput |  percolator_with_content_hurricane_katrina |       29.21 |  ops/s |
|                                                Mean Throughput |  percolator_with_content_hurricane_katrina |       30.79 |  ops/s |
|                                              Median Throughput |  percolator_with_content_hurricane_katrina |       31.41 |  ops/s |
|                                                 Max Throughput |  percolator_with_content_hurricane_katrina |       31.77 |  ops/s |
|                                        50th percentile latency |  percolator_with_content_hurricane_katrina |     1739.83 |     ms |
|                                        90th percentile latency |  percolator_with_content_hurricane_katrina |      2271.5 |     ms |
|                                        99th percentile latency |  percolator_with_content_hurricane_katrina |     2389.71 |     ms |
|                                       100th percentile latency |  percolator_with_content_hurricane_katrina |     2399.26 |     ms |
|                                   50th percentile service time |  percolator_with_content_hurricane_katrina |     28.1924 |     ms |
|                                   90th percentile service time |  percolator_with_content_hurricane_katrina |     41.1843 |     ms |
|                                   99th percentile service time |  percolator_with_content_hurricane_katrina |      70.029 |     ms |
|                                  100th percentile service time |  percolator_with_content_hurricane_katrina |     76.8598 |     ms |
|                                                     error rate |  percolator_with_content_hurricane_katrina |           0 |      % |
|                                                 Min Throughput |             percolator_with_content_google |        9.12 |  ops/s |
|                                                Mean Throughput |             percolator_with_content_google |        9.47 |  ops/s |
|                                              Median Throughput |             percolator_with_content_google |        9.48 |  ops/s |
|                                                 Max Throughput |             percolator_with_content_google |        9.78 |  ops/s |
|                                        50th percentile latency |             percolator_with_content_google |     10374.3 |     ms |
|                                        90th percentile latency |             percolator_with_content_google |     12471.1 |     ms |
|                                        99th percentile latency |             percolator_with_content_google |     12947.5 |     ms |
|                                       100th percentile latency |             percolator_with_content_google |     12992.5 |     ms |
|                                   50th percentile service time |             percolator_with_content_google |     88.1096 |     ms |
|                                   90th percentile service time |             percolator_with_content_google |     113.172 |     ms |
|                                   99th percentile service time |             percolator_with_content_google |     129.758 |     ms |
|                                  100th percentile service time |             percolator_with_content_google |     149.256 |     ms |
|                                                     error rate |             percolator_with_content_google |           0 |      % |
|                                                 Min Throughput |    percolator_no_score_with_content_google |        48.6 |  ops/s |
|                                                Mean Throughput |    percolator_no_score_with_content_google |        48.6 |  ops/s |
|                                              Median Throughput |    percolator_no_score_with_content_google |        48.6 |  ops/s |
|                                                 Max Throughput |    percolator_no_score_with_content_google |        48.6 |  ops/s |
|                                        50th percentile latency |    percolator_no_score_with_content_google |     1597.66 |     ms |
|                                        90th percentile latency |    percolator_no_score_with_content_google |      1709.6 |     ms |
|                                        99th percentile latency |    percolator_no_score_with_content_google |     1742.05 |     ms |
|                                       100th percentile latency |    percolator_no_score_with_content_google |     1754.32 |     ms |
|                                   50th percentile service time |    percolator_no_score_with_content_google |      13.072 |     ms |
|                                   90th percentile service time |    percolator_no_score_with_content_google |     18.7613 |     ms |
|                                   99th percentile service time |    percolator_no_score_with_content_google |     25.0557 |     ms |
|                                  100th percentile service time |    percolator_no_score_with_content_google |     29.9364 |     ms |
|                                                     error rate |    percolator_no_score_with_content_google |           0 |      % |
|                                                 Min Throughput |               percolator_with_highlighting |       34.17 |  ops/s |
|                                                Mean Throughput |               percolator_with_highlighting |       35.65 |  ops/s |
|                                              Median Throughput |               percolator_with_highlighting |       35.24 |  ops/s |
|                                                 Max Throughput |               percolator_with_highlighting |       37.55 |  ops/s |
|                                        50th percentile latency |               percolator_with_highlighting |     1218.73 |     ms |
|                                        90th percentile latency |               percolator_with_highlighting |     1286.58 |     ms |
|                                        99th percentile latency |               percolator_with_highlighting |     1292.84 |     ms |
|                                       100th percentile latency |               percolator_with_highlighting |     1293.08 |     ms |
|                                   50th percentile service time |               percolator_with_highlighting |     20.0169 |     ms |
|                                   90th percentile service time |               percolator_with_highlighting |      35.968 |     ms |
|                                   99th percentile service time |               percolator_with_highlighting |     43.9403 |     ms |
|                                  100th percentile service time |               percolator_with_highlighting |     58.4253 |     ms |
|                                                     error rate |               percolator_with_highlighting |           0 |      % |
|                                                 Min Throughput |          percolator_with_content_ignore_me |        0.07 |  ops/s |
|                                                Mean Throughput |          percolator_with_content_ignore_me |        0.07 |  ops/s |
|                                              Median Throughput |          percolator_with_content_ignore_me |        0.07 |  ops/s |
|                                                 Max Throughput |          percolator_with_content_ignore_me |        0.08 |  ops/s |
|                                        50th percentile latency |          percolator_with_content_ignore_me |      121653 |     ms |
|                                        90th percentile latency |          percolator_with_content_ignore_me |      194437 |     ms |
|                                        99th percentile latency |          percolator_with_content_ignore_me |      200296 |     ms |
|                                       100th percentile latency |          percolator_with_content_ignore_me |      201093 |     ms |
|                                   50th percentile service time |          percolator_with_content_ignore_me |     13939.3 |     ms |
|                                   90th percentile service time |          percolator_with_content_ignore_me |     14178.2 |     ms |
|                                   99th percentile service time |          percolator_with_content_ignore_me |     14368.1 |     ms |
|                                  100th percentile service time |          percolator_with_content_ignore_me |     14792.3 |     ms |
|                                                     error rate |          percolator_with_content_ignore_me |           0 |      % |
|                                                 Min Throughput | percolator_no_score_with_content_ignore_me |       15.07 |  ops/s |
|                                                Mean Throughput | percolator_no_score_with_content_ignore_me |       15.09 |  ops/s |
|                                              Median Throughput | percolator_no_score_with_content_ignore_me |       15.09 |  ops/s |
|                                                 Max Throughput | percolator_no_score_with_content_ignore_me |       15.13 |  ops/s |
|                                        50th percentile latency | percolator_no_score_with_content_ignore_me |     9.30115 |     ms |
|                                        90th percentile latency | percolator_no_score_with_content_ignore_me |      11.791 |     ms |
|                                        99th percentile latency | percolator_no_score_with_content_ignore_me |     16.4913 |     ms |
|                                       100th percentile latency | percolator_no_score_with_content_ignore_me |     17.2961 |     ms |
|                                   50th percentile service time | percolator_no_score_with_content_ignore_me |      8.2169 |     ms |
|                                   90th percentile service time | percolator_no_score_with_content_ignore_me |     11.2185 |     ms |
|                                   99th percentile service time | percolator_no_score_with_content_ignore_me |     15.3238 |     ms |
|                                  100th percentile service time | percolator_no_score_with_content_ignore_me |     16.1542 |     ms |
|                                                     error rate | percolator_no_score_with_content_ignore_me |           0 |      % |


----------------------------------
[INFO] SUCCESS (took 1773 seconds)
----------------------------------
```
