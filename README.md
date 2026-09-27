# EarnAgent

Autonomous earning experiment. The current production agent scans public sources for explicitly paid digital tasks, rejects vague/non-numeric reward claims, ranks candidates, and publishes an auditable dashboard. It never counts an advertised bounty as revenue.

## Truthful accounting
- **opportunity** = externally posted task with explicit numeric reward;
- **completed** = work actually produced and submitted through an allowed channel;
- **verified revenue** = external payment confirmation only.

The agent does not impersonate the owner, accept third-party legal terms, bypass KYC, create payout identities, spend the owner's money, or fabricate traffic/completions/revenue. Those constraints mean fully unattended cash receipt is possible only on channels that permit autonomous participation and already have a valid payout route.

## Automation
GitHub Actions runs the scout hourly and deploys the resulting `data/earnagent.json` to Pages. Paradox Engine source has been superseded in the main product; its history remains available in Git.

## Deployment note
Each scheduled run creates a fresh Pages artifact; failed deployment attempts are recovered with a fresh workflow run rather than reusing an artifact-bearing attempt.
