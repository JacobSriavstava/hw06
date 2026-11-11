# Part D — Verification of Claude's `Top 10 Client Share`

## Did it run as written?
No. I changed the variable name `LastDate` to `LastSnapDate` because `LASTDATE` is a built-in DAX time-intelligence function, and DAX names are not case-sensitive, so the variable name collided with the function and the measure would not parse. No logic was changed. (I also fixed a typo I introduced while retyping the `TREATAS` line.) Once those two fixes were made, the measure ran without errors and returned the expected values on the first try. Claude's test query returned, for 2024 by client tier: HNW 0.031397, Retail 0.018348,UHNW 0.081264, and 0.061589 at the total. The Ending AUM column in the same query matchedmy Part B values for every tier.

## Which reconciliation rows prove it?
`reports/measure_reconciliation.csv`: the `Top 10 Client Share` rows for `Total`,
`Tier HNW 2024`, `Tier Retail 2024`, `Tier UHNW 2024`, and `Year 2020`–`Year 2024`.
All 9 match the independent pandas calculation within 0.0001; the largest difference
is about 5e-13 (88/88 rows overall).

## Edge cases checked
1. **Tier table, 2024:** every tier is well under 100% (3.14%, 1.83%, 8.13%), so the
   measure ranks the top 10 *within* each tier. If it ranked across all clients
   (the `ALL ( dim_client )` mistake), every tier's numerator would be the firm-wide
   top 10 ($784M): Retail would show about 147% ($784M ÷ $533M) and HNW about 31%.
2. **Grand total vs. UHNW:** top-10 dollars at the total (6.16% × $12.73B) and in UHNW
   (8.13% × $9.65B) are both exactly $784,005,019.49. The firm's 10 largest clients
   are all UHNW, so both levels pick the same clients. This only works if the measure
   respects the filter at each level.
3. **Year 2022:** 5.53%, the lowest year. December 2022 had the most clients of any
   year-end (2,500, vs. 2,157 in 2021 and 2,325 in 2023), and Ending AUM fell from 2021.
   More clients sharing a smaller base means less concentration at the top. The pandas
   match confirms the measure reads only the December 2022 snapshot instead of summing
   balances across months.
4. **Year 2024 = Total** (0.061589…), as expected, since both read the December 2024 snapshot.

## What I changed and why
Renamed the variable `LastDate` → `LastSnapDate` so it no longer collides with the DAX
`LASTDATE` function. The calculation itself is unchanged, and it matched pandas on
every slice.

## A claim Claude made, confirmed or refuted
Claude claimed TOPN could return more than 10 clients if several are tied at 10th
place, and added `dim_client[client_id]` as a second sort key so the measure always
returns exactly 10. I checked this with the same ranking the measure uses (AUM at the
last snapshot date), and the query returned exactly 10. The claim is correct in
principle: TOPN keeps every row tied at the cutoff. In this data, though, no slice has
a tie between its 10th and 11th client, so the tie-breaker never changes a result.