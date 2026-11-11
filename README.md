# HW06: DAX Measure Library #
### Jacob Srivastava ###

## Structure
- README.md
- claude
        - dax_dession.md
        - model_metadata.md
        - verification.mc
- powerbi
        - hw06.pbix
        - measures.md
- reports
        - measure_reconciliation.csv
        - powerbi_values.csv
- scripts
        - 01_reconcile_measures.py


Something to note: The card on the measures tab in the powerbi did not display the numbers because of an error with apporto. The numbers were verified when it was viewed in table view. 


## How to Run ##

Set up Environment 
- python3 -m venv .venv & source .venv/bin/activate (Activate Environment)
- pip install --upgrade pip & pip install pandas (Install pandas)
- python scripts/01_reconcile_measures.py (Run 01_reconcile_measures.py)

- Claude Cowork drafted script and helped build the Part A documentation
- I ran the script in VS Code
- Claude Code reviewed the code before commit
- Claude code made fixes to any errors
- Claude helped draft the DAX and DAX verification codes 
- Claude helped draft the DAX for the Top 10 Client Share

## Claude Code Findings ##
| Finding | Severity | What I did |
|---|---|---|
| 5a: Power BI rows with no pandas match only printed a warning, so the summary could report success with rows missing | High | **Fixed.** Missing rows now appear in the output with `match = False` and count as failures |
| 5b: Script always exited with code 0 | Med | **Fixed.** Exits with code 1 on any mismatch or missing row |
| 2a: Top 10 Client Share was never checked against Power BI | High | **Fixed.** The script lists measures with no Power BI rows. After Part D, I exported the 9 Top 10 rows and reran: 88/88 match, and the warning is gone |
| 4a / 4b: Tolerances looked up by name with a silent default; Ending Clients used the currency tolerance | Med / Low | **Fixed.** One explicit `TOLERANCES` dict covering all measures, checked against the measure list; Ending Clients = 0 |
| 2d: Slices are hardcoded | Low | **Kept on purpose.** They match the Power BI export exactly; a comment in the code explains this |
| 3a: Pandas drops null-alpha rows from numerator and denominator, but "typical" DAX would keep their AUM in the denominator | Med | **No change; the review was wrong here.** Claude Code couldn't see my DAX. My measure filters `NOT ISBLANK ( active_alpha_ytd )` inside CALCULATE, which removes those rows from both, the same as pandas |
| 3b: `ne(1)` keeps NaN suspect flags | Low | **No change.** My DAX uses `<> 1`, which behaves the same way |
| 2b: Fee Yield's ×12 assumes one snapshot per month | Med | **No change.** ×12 is the assignment's definition, and the data has exactly one snapshot per month (60 dates, all on the 1st) |
| 2c, 3c–3e, 5c–5e: edge cases the data never hits, and code tidy-ups | Low | **Not changed;** none affect results |

Claude Code also added a `status` column to the reconciliation CSV. I removed it so the file has exactly the required columns (`measure, slice, powerbi_value, pandas_value, abs_diff, match`); status still appears in the console summary.

** The output above is from Claude Code based on info from the project and what I did througout it. I verified it. 


## Mismatches and Fixes ##
All 88 rows match. One issue was caught **before** reconciliation: in my first export, the `Ending AUM, Total` row showed **2325** (the Ending Clients value) because of a typo in my export query, where the row referenced the wrong measure. `Avg AUM per Client` (5,475,084.77) only works out if Ending AUM is $12.73B, which showed the model was right and the query was wrong. I fixed the query, and the corrected value (12,729,572,078.86) is in `powerbi_values.csv`.

## Notes

- **Measures page cards:** the Card visual rendered blank on Apporto, although "Show as a table" confirmed it received the correct value. The four KPIs (Ending AUM, Ending Clients, Avg AUM per Client, Top 10 Client Share) are therefore shown in a single-row table visual at the top of the page.
- **Relationships:** the model shows 12 relationships rather than the 11 in the instructions. The extra one is `dim_security[benchmark_id] → dim_benchmark[benchmark_id]`, which no HW6 measure uses, so it was left as is.
- **Measure names:** two measures were first created as `Ending Client` and `AUM MoM%`. Both were renamed to the assignment's names before the metadata export.
- **Part D:** I chose measure 11 (`Top 10 Client Share`), because measure 10 (`Alpha Signal`) depends on measure 9.
- **`hw06.pbix` size:** [under 100 MB, committed to the repo / over 100 MB, uploaded to Brightspace instead].

** Output above was made with the assistance of Claude and then I verified it. 
** Used claude code and claude cowork to assist with the creation of files and documents. Claude cowork helped create the DAX syntax. I then verified it with different checks to validate the information was correct. 