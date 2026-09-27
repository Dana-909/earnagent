# Paradox Engine v0

Research prototype for detecting logical inconsistencies between related prediction-market contracts.

## Current detector
- Loads public active market metadata in the browser.
- Extracts YES prices and explicit calendar dates.
- Groups semantically similar questions after replacing dates.
- Tests date monotonicity (earlier-deadline event should not be priced above an otherwise equivalent later-deadline event).
- Shows candidates only; it does **not** execute trades.

## Important
A raw logical gap is not a guaranteed executable arbitrage. Resolution rules, market wording, liquidity, spread, fees, slippage, settlement and execution risk must be verified independently.

## Next validation gate
Add exact resolution-rule comparison and order-book executable prices before treating any candidate as economically meaningful.
