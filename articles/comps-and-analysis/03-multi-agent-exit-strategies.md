## Help Content

**Title:** Multi-Agent Exit Strategies
**Format:** Help article
**Audience:** All
**Slug:** multi-agent-exit-strategies
**Purpose:** Run comps across multiple exit strategies to see how each approach changes the numbers.

**Content:**

ReiSearch's multi-agent comps let you evaluate a property under different exit strategies at the same time. Instead of running separate analyses for each approach, the AI runs them in parallel and presents the results side by side.

### What Multi-Agent Comps Are

Each "agent" in the analysis represents an exit strategy. When you run a multi-agent comp, the AI evaluates the property from the perspective of each strategy and adjusts the comparable selection and calculations accordingly.

The result is a comparison table showing how the same property performs under different scenarios.

### Available Exit Strategies

**Retail** — Market-rate sale to an owner-occupant. Comps focus on recently sold homes in similar condition. This is the baseline analysis for standard resale.

**Wholesale** — Below-market acquisition for assignment. Comps emphasize distressed sales, days on market, and discount-to-ARV. The AI looks for the spread between current condition value and after-repair value.

**BRRRR** — Buy, Rehab, Rent, Refinance, Repeat. Comps include both rental comparables (for refinance valuation) and recent sales in the area. The AI estimates ARV after rehab and projected rental income.

**Subject-To** — Acquiring the property subject to the existing financing. The analysis focuses on loan terms, equity capture, and monthly cash flow with the existing mortgage in place.

**Short-Term Rental (STR)** — Vacation rental or Airbnb strategy. Comps include nearby STR properties with occupancy rates, nightly rates, and seasonal trends. The AI projects annual revenue based on local STR data.

**Rental** — Long-term buy-and-hold. Comps focus on rental properties: rent per square foot, cap rates, gross rent multiplier, and expense ratios in the area.

### How Results Differ Per Strategy

The same subject property can produce very different numbers depending on the strategy you select:

- **ARV** — Retail and BRRRR may show higher ARV than wholesale.
- **Comparable selection** — Each strategy pulls different property types. STR looks at nearby vacation rentals. Rental looks at multifamily and SFR rentals.
- **Key metrics** — Retail emphasizes price per square foot. STR emphasizes revenue potential. Rental emphasizes cash flow and cap rate.

### Running a Multi-Agent Comp

Open any property and click "Run Comps." Select "Multi-Agent" mode. Check the strategies you want to evaluate. The AI runs all selected strategies simultaneously.

Results are displayed in a tabbed or column layout so you can compare across strategies at a glance.

[SCREENSHOT: Multi-agent comp results showing the same property evaluated under Retail, Wholesale, and BRRRR strategies side by side]

### When to Use Multi-Agent

- **Evaluating a property with multiple exit options.** Not sure whether to flip or hold? Run both strategies.
- **Pitching to different buyers.** Show a wholesaler the wholesale numbers and an investor the rental numbers from the same analysis.
- **Testing your assumptions.** If the numbers only work under one strategy and not others, you know the risk.

### Token Cost

Multi-agent comps cost [MULTI_AGENT_COMP_COST] tokens per run. This covers all selected strategies in a single run rather than charging per strategy.

**Next steps:**
- How AI Comps Work
- Reading a Comp Result
- Underwriting Tools
- Repair Estimator

**Status:** Draft v0.1

### Notes for Neo
- Specific agent names for each exit strategy were assumed from positioning per the session recap. Actual available strategies may differ. Confirm which are live in production.
