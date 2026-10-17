# Frozen indexed-symbol screening configurations

Prepared after same-binary calibration and before candidate timing. No screening result exists yet. The comparison policy is ../../results/indexed-symbol-aa/COMPARISON_POLICY.md; its exact hash is required by every configuration and checked by the screening controller before/after groups. All three configurations pin source/binary/sidecar identities and complete source differences.

The executed A/A controller remains unchanged in the calibration archive. These screening copies additionally freeze the policy file and use stage-appropriate output names. They retain the same input, diagnostic, wrapper, environment, sample and build-provenance gates. Preparation preflight verifies identities but performs no timed workload invocations.

Original execution paths are /tmp/tsc-indexed-bench/{run-screen,common-screen,preflight-screen}.mjs and the three JSON configurations. To use those paths, copy these files into that directory; invoke node run-screen.mjs with a fresh output directory followed by the configuration path. Absolute workspace paths require adjustment on another machine. No builds/tests/profiles or concurrent benchmark suites may overlap timing. No subagents are used.
