# Paradox Engine v1

Public research scanner for logical inconsistencies between related prediction-market contracts.

## Production flow
GitHub Actions runs `scanner.py` on deploy and hourly. The scanner fetches active public market metadata server-side, groups date-nested contracts, tests monotonicity, checks available best bid/ask, minimum pair liquidity and resolution-wording similarity, then publishes a static `data/results.json`. The browser only renders that generated snapshot, avoiding direct API/CORS dependence.

## Candidate gates
A **qualified paper candidate** currently requires:
- raw date-monotonicity violation > 0.5 percentage points;
- positive executable proxy: earlier YES best bid > later YES best ask;
- minimum reported liquidity of $1,000 on both sides;
- resolution wording similarity > 70%.

This is deliberately a research/paper signal, not a guaranteed arbitrage or trade instruction. Order-book depth, fees, slippage, settlement semantics and simultaneous execution can still remove the apparent edge.

## Reliability
If the upstream market fetch fails, the build fails rather than silently publishing invented fresh data. The UI displays the timestamp of the latest successfully deployed server scan.

## Next research frontier
Full depth-aware CLOB simulation, explicit fee/slippage models, stronger semantic rule equivalence, and additional deterministic relation classes (threshold nesting, mutually exclusive/exhaustive partitions and implication).
