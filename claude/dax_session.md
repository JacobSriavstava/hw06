# Dax Session #

Prompt:
I’m adding a DAX measure to a Power BI model. My model metadata, exported with the three INFO.VIEW queries (columns, relationships, measures), is in hw06/claude/model_metadata.md. Read it first. Ignore the DateTableTemplate_… and LocalDateTable_… tables; they’re hidden auto date tables.

What the metadata doesn’t say:

fact_portfolio_snapshot has one row per client per month. snapshot_date is always the 1st of the month.
aum is a balance, so it must never be summed across dates. active_alpha_ytd is a year-to-date rate.
dim_date is marked as the date table; all relationships are many-to-one and single-direction.
The existing measure [Ending AUM] returns the AUM balance at the last snapshot date in the current filter, using LASTNONBLANK.

Measure to write: Top 10 Client Share = the share of Ending AUM held by the 10 largest clients within the current filter. For example, in a table by dim_client[client_tier] filtered to 2024, each tier’s row should use the top 10 clients within that tier, divided by that tier’s Ending AUM. It must never exceed 100%.

Please give me:

The measure’s DAX, reusing existing measures where possible
An explanation of its filter context: how it behaves at the grand total, by dim_date[year], and by client tier filtered to 2024
A DAX test query I can run in DAX query view to check it
Any assumptions you made, such as how ties are handled

Don’t edit any files.
**This code was made with Claude

## Response
The Measure: 
Top 10 Client Share =
VAR LastDate =
    MAX ( fact_portfolio_snapshot[snapshot_date] )   -- same date [Ending AUM] lands on
VAR EndingAUM = [Ending AUM]
VAR ClientAUM =
    CALCULATETABLE (
        ADDCOLUMNS (
            SUMMARIZE ( fact_portfolio_snapshot, dim_client[client_id] ),
            "@AUM", CALCULATE ( SUM ( fact_portfolio_snapshot[aum] ) )
        ),
        KEEPFILTERS ( TREATAS ( { LastDate }, dim_date[date] ) )
    )
VAR Top10 =
    TOPN ( 10, ClientAUM, [@AUM], DESC, dim_client[client_id], ASC )
VAR Top10AUM =
    SUMX ( Top10, [@AUM] )
RETURN
    IF ( NOT ISBLANK ( LastDate ), DIVIDE ( Top10AUM, EndingAUM ) )
---

 Testing the Measure:
 // Total + by tier, 2024
EVALUATE
SUMMARIZECOLUMNS (
    ROLLUPADDISSUBTOTAL ( dim_client[client_tier], "IsTotal" ),
    TREATAS ( { 2024 }, dim_date[year] ),
    "Last Date",   MAX ( fact_portfolio_snapshot[snapshot_date] ),
    "Clients",     CALCULATE ( DISTINCTCOUNT ( fact_portfolio_snapshot[client_id] ),
                       fact_portfolio_snapshot[snapshot_date]
                           = MAX ( fact_portfolio_snapshot[snapshot_date] ) ),
    "Ending AUM",  [Ending AUM],
    "Top10 Share", [Top 10 Client Share]
)

// By year
EVALUATE
SUMMARIZECOLUMNS (
    dim_date[year],
    "Ending AUM",  [Ending AUM],
    "Top10 Share", [Top 10 Client Share]
)
ORDER BY dim_date[year]

---

Test Result
