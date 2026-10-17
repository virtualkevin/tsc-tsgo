# Predeclared tRPC reversed-role confirmation

NEW guard is baseline; OLD PointerLinkStore is candidate. A baseline/candidate ratio above1 favors OLD pointer. Exactly9 alternating pairs and1 warmup, matching default runtime settings, GNU time RSS on both sides.

| Metric | Result |
| --- | ---: |
| Old pointer median | 467.05 ms |
| New guard median | 503.62 ms |
| New / old ratio (above1 favors OLD) | 1.078 |
| Old / new ratio (above1 favors NEW) | 0.927 |
| Old pointer wins | 7/9 |
| New guard wins | 2/9 |
| Old / new median command peak RSS | 242.8 / 234.0 MiB |

Per-pair order/times/RSS and first-order strata are in confirmation.json. This is one predeclared confirmation, not repeated-until-favorable sampling. No repository docs were written and no acceptance conclusion is automatic.
