# Measures.MD #

## Part A — Measure library

All measures live in the `_Measures` table. Patterns: **SUM** (additive across every dimension), **last balance** (semi-additive: additive across clients, never across dates), **recompute-and-weight** (non-additive: recalculated from its parts at every level, never summed or averaged).

### Total Fees
```dax
Total Fees = SUM ( fact_fees[amount] )
```
**Pattern:** SUM · **Format:** currency
**Meaning:** Total fee revenue Wildcat billed in the selected period and segment.

### Net Flows
```dax
Net Flows =
CALCULATE ( SUM ( fact_transactions[amount] ), fact_transactions[txn_type] = "Deposit" )
    - CALCULATE ( SUM ( fact_transactions[amount] ), fact_transactions[txn_type] = "Withdrawal" )
```
**Pattern:** SUM · **Format:** currency
**Meaning:** Client deposits minus withdrawals, showing whether new money is coming in or leaving.

### AUM (naive SUM) — ⚠ WRONG for a balance
```dax
AUM (naive SUM) = SUM ( fact_portfolio_snapshot[aum] )
```
**Pattern:** SUM (the wrong pattern for a balance) · **Format:** currency
**Meaning:** Kept only to show the double-counting trap. Summing a monthly balance across dates gives $566.68B instead of the true $12.73B ending AUM, so it is never used on the report.

### Ending AUM
```dax
Ending AUM =
CALCULATE (
    SUM ( fact_portfolio_snapshot[aum] ),
    LASTNONBLANK ( dim_date[date], CALCULATE ( COUNTROWS ( fact_portfolio_snapshot ) ) )
)
```
**Pattern:** last balance · **Format:** currency
**Meaning:** Assets Wildcat manages as of the last snapshot date in the selected period ($12.73B at December 2024).

### Ending Clients
```dax
Ending Clients =
CALCULATE (
    DISTINCTCOUNT ( fact_portfolio_snapshot[client_id] ),
    LASTNONBLANK ( dim_date[date], CALCULATE ( COUNTROWS ( fact_portfolio_snapshot ) ) )
)
```
**Pattern:** last balance · **Format:** whole number
**Meaning:** Number of clients with a balance on the last snapshot date (2,325 at December 2024).

### Avg AUM per Client
```dax
Avg AUM per Client = DIVIDE ( [Ending AUM], [Ending Clients] )
```
**Pattern:** recompute-and-weight · **Format:** currency
**Meaning:** Typical relationship size: Ending AUM divided by Ending Clients.

### Ending AUM LY
```dax
Ending AUM LY = CALCULATE ( [Ending AUM], SAMEPERIODLASTYEAR ( dim_date[date] ) )
```
**Pattern:** last balance (time-shifted) · **Format:** currency
**Meaning:** Ending AUM for the same period one year earlier, used as the growth baseline. Blank for 2020, the first year of data.

### AUM YoY %
```dax
AUM YoY % = DIVIDE ( [Ending AUM] - [Ending AUM LY], [Ending AUM LY] )
```
**Pattern:** recompute-and-weight · **Format:** %
**Meaning:** How much the book grew or shrank versus the same point last year. No alternate result in DIVIDE, so 2020 shows blank instead of a misleading 0%.

### Ending AUM PM
```dax
Ending AUM PM = CALCULATE ( [Ending AUM], DATEADD ( dim_date[date], -1, MONTH ) )
```
**Pattern:** last balance (time-shifted) · **Format:** currency
**Meaning:** Ending AUM one month earlier, used as the month-over-month baseline.

### AUM MoM %
```dax
AUM MoM % = DIVIDE ( [Ending AUM] - [Ending AUM PM], [Ending AUM PM] )
```
**Pattern:** recompute-and-weight · **Format:** %
**Meaning:** Short-term change in AUM versus the prior month (+4.25% in December 2024).

### Avg Monthly AUM
```dax
Avg Monthly AUM =
DIVIDE (
    SUM ( fact_portfolio_snapshot[aum] ),
    DISTINCTCOUNT ( fact_portfolio_snapshot[snapshot_date] )
)
```
**Pattern:** recompute-and-weight · **Format:** currency
**Meaning:** Average balance across the months in the period. It sits below Ending AUM in growth years and above it in 2022, when AUM fell.

### Fee Yield (bps)
```dax
Fee Yield (bps) =
DIVIDE ( [Total Fees] * 12 * 10000, SUM ( fact_portfolio_snapshot[aum] ) )
```
**Pattern:** recompute-and-weight (combines two fact tables) · **Format:** bps
**Meaning:** Annualized fees earned per dollar of AUM, i.e. how well Wildcat monetizes its assets (about 43 bps firm-wide).

### Organic Growth Rate
```dax
Organic Growth Rate = DIVIDE ( [Net Flows], [Ending AUM LY] )
```
**Pattern:** recompute-and-weight · **Format:** %
**Meaning:** Growth from net client money alone, excluding market performance. Only meaningful for a single year: the grand total divides several years of flows by one year's balance.

### AUM-Weighted Alpha
```dax
AUM-Weighted Alpha =
CALCULATE (
    DIVIDE (
        SUMX (
            fact_portfolio_snapshot,
            fact_portfolio_snapshot[aum] * fact_portfolio_snapshot[active_alpha_ytd]
        ),
        SUM ( fact_portfolio_snapshot[aum] )
    ),
    LASTNONBLANK ( dim_date[date], CALCULATE ( COUNTROWS ( fact_portfolio_snapshot ) ) ),
    fact_portfolio_snapshot[is_return_suspect] <> 1,
    NOT ISBLANK ( fact_portfolio_snapshot[active_alpha_ytd] )
)
```
**Pattern:** recompute-and-weight · **Format:** %
**Meaning:** Year-to-date return versus benchmark, weighted by client AUM, read at the last snapshot with suspect returns excluded. Null-alpha rows are dropped from both numerator and denominator.

### Alpha Signal
```dax
Alpha Signal =
VAR a = [AUM-Weighted Alpha]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( a ), BLANK (),
        a >= 0.02, "Outperforming",
        a <= -0.02, "Lagging",
        "In line"
    )
```
**Pattern:** text label derived from AUM-Weighted Alpha · **Format:** text
**Meaning:** A quick verdict: "Outperforming" (≥ +2%), "Lagging" (≤ −2%), or "In line"; blank when alpha is blank. Alpha is stored as a decimal, so ±2% is written as ±0.02.

### Top 10 Client Share
```dax
Top 10 Client Share =
VAR LastSnapDate = MAX ( fact_portfolio_snapshot[snapshot_date] )
VAR EndingAUM = [Ending AUM]
VAR ClientAUM =
    CALCULATETABLE (
        ADDCOLUMNS (
            SUMMARIZE ( fact_portfolio_snapshot, dim_client[client_id] ),
            "@AUM", CALCULATE ( SUM ( fact_portfolio_snapshot[aum] ) )
        ),
        KEEPFILTERS ( TREATAS ( { LastSnapDate }, dim_date[date] ) )
    )
VAR Top10 = TOPN ( 10, ClientAUM, [@AUM], DESC, dim_client[client_id], ASC )
VAR Top10AUM = SUMX ( Top10, [@AUM] )
RETURN
    IF ( NOT ISBLANK ( LastSnapDate ), DIVIDE ( Top10AUM, EndingAUM ) )
```
**Pattern:** recompute-and-weight (at the last balance) · **Format:** %
**Meaning:** Share of AUM held by the 10 largest clients within the current filter, showing how exposed the book is to losing a few relationships. Drafted with Claude in Part D; see `claude/verification.md`.

## Part C ##
(a) With no filters, Ending AUM shows one total. SUMX ( VALUES ( dim_client[client_id] ), [Ending AUM] ) shows a larger one. Compute both, explain the difference in dollars, and say which answers "How much do we manage today?"

With no filters, Ending AUM is $12,729,572,078.86, while SUMX (VALUES(dim_client[client_id]), [Ending AUM]) is #13,149,297713.80. This is $419,725,634.94 higher. 

Ending AUM finds one last snapshot date for the whole model and sums the balances on that date. SUMX evaluates Ending AUM once per client. 

Ending AUm answers the question how much do we manage today. The SUMX version overstates it by counting departed clients stranded balances. 


(b) For 2024, Fee Yield (bps) is lower than the ICE 9 Effective Fee Rate (bps). Both are fees per dollar. Use pandas to find the cause, and say which data limitation it reveals

In 2024, Fee Yield (bps) is 43.15 and the ICE 9 Effective Fee Rate (bps) is 45.53. Both of these measures use the same fees but the difference is from what they are divided by. Fee Yield divides by all AUM in fact_portfolio_snapshot: $135.46 B. The Effective Fee Rate divides by the AUM in fact_fees: $128.39 B. This comes out to a $7.07B difference. 

Using pandas I matched the two tables by client and month. Wherever both tables have a row, the amounts match exactly.

Data limitations: The fee table is missing records for about 5% of client-months. The data can't tell us whether those months were never billed or just weren't recorded. Fee Yield shows revenue recorded per dollar managed while Elevated Fee Rate shows the price charged on billed AUM. 


(c) Why must AUM-Weighted Alpha be read at the last snapshot only, and why exclude is_return_suspect = 1? Report the simple mean of active_alpha_ytd for the same rows, and the weighted value with suspects included

It must be last snapshot only because active_alpha_ytd is a year to date number. January's values cover one month, and decembers cover the full year. Only the last snaoshot shows the whole period. If we average across all 2024 months, alpha drops to 0.32% because the early-year values are short partial year figures. At the last snaoshot, the answer is 1.45%. 

We exclude suspicious rows with is_return_suspect =1 because they contain impossinble values of up to +9,457% alpha, while clean rows stay between -50% and +50%. There are a total of 3,875 suspicious rows and 148 at the December 2024 snapshot, Including them would raise weighted alpha. 

The simple unweighted mean of active_alpha_ytd for the same rows is 0.88%, lower than the weighted 1.45%. This means larger accounts earned more alpha than smaler ones. The weighted version is the right one to use because it reflects how the firms actual dollars performed. 


(d) Compare Organic Growth Rate by client tier in 2024. What does it say about where Wildcat's growth comes from, and what does it not tell you? (Hint: compare it with AUM YoY %)

All three tiers grew AUM by about the same amount (19.13-19.64% YoY)but for different reasons. 
- Retain grew 9.87% from new client money
- HNW grew only 1.18% organically
- UHNW grew just 0.10% organically. 
New money mostly comes from retail. 
This does not tell us: 
- Why the non-organic growth happened
- Who is behind the flows
- Profitability of the growth
