# EarnAgent

Autonomous earning engine. It continuously discovers paid digital work, prioritizes routes whose payment and execution are actually configured, produces deliverables, submits them when the route is free to enter, and records only verified settlements as revenue.

## Active execution loop
- **discover** — scans Taskmarket plus additional public earning sources;
- **action-first** — checks the Taskmarket action queue and inbox, not only the public task list;
- **execute** — free bounty/claim routes can be claimed and submitted automatically;
- **produce** — the AI worker creates bounded self-contained digital deliverables when the task is safely executable;
- **verify** — re-fetches task state and checks escrow/action preconditions before submission;
- **learn** — records submissions, pending settlements and verified payouts for later prioritization.

## Payment truth
Taskmarket is the primary live execution rail because the configured agent wallet can use its free claim and submit routes. Taskmarket's paid pitch/bid actions remain disabled so the agent does not spend the owner's funds. Advertised rewards are never counted as income; revenue is counted only after a canonical settlement/award is observed.

## Safety
The agent does not impersonate the owner, bypass KYC, create payout identities, expose secrets, spend owner funds, or fabricate traffic/completions/revenue. Third-party sources may be discovered and ranked, but they are not promoted to autonomous execution until their payout, authentication and submission semantics are verified.

## Automation
GitHub Actions runs approximately every 5 minutes. Each cycle runs the action-first worker, the existing deterministic worker, safety tests, the earning scanner and the Pages deployment. A slow AI provider is bounded so it cannot consume the whole cycle.

## Deployment note
Each scheduled run creates a fresh Pages artifact. Verified revenue and execution state are persisted in `data/taskmarket.json`, `data/taskmarket_active.json` and `data/earnagent.json`.

## Autonomous sales layer
The sales engine now runs every cycle and generates a small catalog of original digital goods (offline tools, templates and SVG assets). It publishes the catalog through GitHub Pages and probes a configured Lemon Squeezy store when `LEMONSQUEEZY_API_KEY` is available. Lemon Squeezy supports programmatic store/product management and checkout links; live payouts still require an activated seller account and payout method. The engine never counts listings or simulated orders as revenue.