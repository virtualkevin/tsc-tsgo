# Page-owned compact graph measurement results

Capture completed successfully; independent raw readback verified all 276 observations and the 27 validation records. Sources and executable match the preparation checkpoint. These are standalone model measurements, not compiler performance.

Ratios below are pointer time / compact time: values below 1 mean the compact representation is slower. Both summaries and every observation are preserved; there is no outlier filtering.

| Records | Operation | Ratio of medians | Median paired ratio | Paired range | Pointer ns/op | Compact ns/op | Pointer B/op | Compact B/op | Pointer allocs/op | Compact allocs/op |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 4096 | linked/construct | 0.505399 | 0.518829 | 0.466246–0.598462 | 252635 | 499872 | 258061 | 235797 | 17 | 131 |
| 4096 | linked/internal | 0.440629 | 0.440629 | 0.283749–0.603199 | 20929 | 47498 | 0 | 0 | 0 | 0 |
| 4096 | linked/public | 0.067335 | 0.062840 | 0.046325–0.078218 | 31212 | 463530 | 0 | 0 | 0 | 0 |
| 4096 | local/construct | 0.681036 | 0.691439 | 0.645432–0.764595 | 192524 | 282693 | 258053 | 228408 | 17 | 63 |
| 4096 | local/internal | 0.481844 | 0.502141 | 0.286390–0.751594 | 17927 | 37205 | 0 | 0 | 0 | 0 |
| 4096 | local/public | 0.061674 | 0.063379 | 0.049810–0.082363 | 24554 | 398127 | 0 | 0 | 0 | 0 |
| 262144 | linked/construct | 0.320761 | 0.333415 | 0.243510–0.381908 | 3.09467e+07 | 9.64791e+07 | 1.60005e+07 | 3.26729e+07 | 1026 | 23029 |
| 262144 | linked/internal | 0.486630 | 0.469131 | 0.370736–0.713264 | 1.2603e+07 | 2.58985e+07 | 0 | 0 | 0 | 0 |
| 262144 | linked/public | 0.128163 | 0.130204 | 0.089281–0.196403 | 1.11822e+07 | 8.72496e+07 | 0 | 0 | 0 | 0 |
| 262144 | local/construct | 0.850370 | 0.841903 | 0.761788–0.904408 | 1.72227e+07 | 2.02531e+07 | 1.59998e+07 | 1.41157e+07 | 1026 | 4096 |
| 262144 | local/internal | 0.792429 | 0.811546 | 0.613092–0.984990 | 3.62081e+06 | 4.56926e+06 | 0 | 0 | 0 | 0 |
| 262144 | local/public | 0.134791 | 0.133150 | 0.116122–0.151916 | 4.09476e+06 | 3.03786e+07 | 0 | 0 | 0 | 0 |

Retention endpoints are median HeapAlloc deltas after two GCs with only the final root held. They include runtime accounting variation and are neither peak RSS nor exact payload sizes.

| Records | Shape | Pointer retained bytes | Compact retained bytes | Compact pages | Remote entries | Remote capacity |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 4096 | linked | 227728 | 169272 | 16 | 120 | 155 |
| 4096 | local | 222424 | 160248 | 16 | 15 | 15 |
| 4096 | sparse | 19016 | 14824 | 1 | 0 | 0 |
| 262144 | linked | 1.39149e+07 | 1.94309e+07 | 1024 | 185334 | 271284 |
| 262144 | local | 1.39096e+07 | 9.92277e+06 | 1024 | 1023 | 1023 |
| 262144 | sparse | 29656 | 20144 | 1 | 0 | 0 |

The sparse fixture retains exactly one compact page at both sizes, addressing the prior global-owner design's whole-graph retention. Local edges reduce retained heap at 262144 records from 13909608 to 9922768 bytes, but all construction and traversal timing summaries favor pointers. Distant edges reverse even the memory advantage: 185334 remote entries (capacity 271284), plus indexing maps, raise retained heap from 13914928 to 19430936 bytes and construction allocation from about 16 MB to 32.7 MB.

Decision: do not integrate this representation into the compiler. Smaller pointer-free records alone do not justify remote metadata, decoding, and public adaptation costs. This experiment establishes a reachability option and its costs, not an end-to-end optimization. Real compiler edge locality, payloads and APIs remain outside this fixture. Production and PERF.md remain unchanged; the 10× native-relative goal remains unmet.
