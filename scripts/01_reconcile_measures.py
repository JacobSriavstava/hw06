"""
HW06 - Step 1: Reconcile Power BI measures against an independent pandas rebuild.

1. Rebuild every Wildcat Capital measure from the clean CSVs in hw06/Data.
   (Nothing on the pandas side reads powerbi_values.csv.)
2. Only after that, load hw06/reports/powerbi_values.csv and merge on
   measure + slice.
3. Write hw06/reports/measure_reconciliation.csv and print a summary.

Time-intelligence notes (mirroring DAX):
  * A slice's filter context is a set of calendar months (+ an optional tier).
  * "LY" shifts that month set back 1 year (SAMEPERIODLASTYEAR / DATEADD -1 YEAR).
  * "PM" shifts it back 1 month (DATEADD -1 MONTH).
  * "Ending" measures evaluate on the latest snapshot_date that has rows in
    the (possibly shifted) context (LASTNONBLANK-style).
  * DIVIDE semantics: a blank or zero denominator returns blank.

Run from anywhere:  python hw06/scripts/01_reconcile_measures.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd

# --------------------------------------------------------------------------
# Paths (relative to this file)
# --------------------------------------------------------------------------
HW06_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = HW06_DIR / "Data"
REPORTS_DIR = HW06_DIR / "reports"
PBI_VALUES_CSV = REPORTS_DIR / "powerbi_values.csv"
OUTPUT_CSV = REPORTS_DIR / "measure_reconciliation.csv"
OUTPUT_COLUMNS = ["measure", "slice", "powerbi_value", "pandas_value", "abs_diff", "match"]

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
# Slice definitions are fixed on purpose to mirror the slices exported from
# Power BI into powerbi_values.csv (Total, Year 2020-2024, Tier x 2024, Dec 2024).
# They are not derived from the data, so if the export changes (new years, a new
# latest month, new tiers), update these to match or the labels won't line up.
YEARS = range(2020, 2025)
TIERS = ["HNW", "Retail", "UHNW"]
TIER_YEAR = 2024
DEC_2024 = pd.Timestamp("2024-12-01")

CURRENCY_TOL = 0.01      # currency measures
COUNT_TOL = 0            # counts must match exactly
RATIO_TOL = 0.0001       # ratios, percentages, bps
TEXT_EXACT = None        # text measures: exact string match

# Every measure in Measures.registry() must appear here (checked at runtime).
TOLERANCES: dict[str, float | None] = {
    "AUM (naive SUM)": CURRENCY_TOL,
    "Ending AUM": CURRENCY_TOL,
    "Ending Clients": COUNT_TOL,
    "Avg AUM per Client": CURRENCY_TOL,
    "Ending AUM LY": CURRENCY_TOL,
    "AUM YoY %": RATIO_TOL,
    "Ending AUM PM": CURRENCY_TOL,
    "AUM MoM %": RATIO_TOL,
    "Avg Monthly AUM": CURRENCY_TOL,
    "Fee Yield (bps)": RATIO_TOL,
    "Organic Growth Rate": RATIO_TOL,
    "AUM-Weighted Alpha": RATIO_TOL,
    "Alpha Signal": TEXT_EXACT,
    "Top 10 Client Share": RATIO_TOL,
}

ALPHA_UPPER = 0.02
ALPHA_LOWER = -0.02

BLANK = None  # DAX BLANK()


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------
def _month_start(dates: pd.Series) -> pd.Series:
    return dates.dt.to_period("M").dt.to_timestamp()


def _load_fact(file_name: str, columns: list[str], date_col: str,
               clients: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / file_name, usecols=columns)
    df[date_col] = pd.to_datetime(df[date_col], format="%Y-%m-%d")
    df = df.rename(columns={date_col: "date"})
    df["month"] = _month_start(df["date"])
    # Relationship fact[client_id] -> dim_client[client_id] (many-to-one).
    # Left join: unmatched clients stay in Total/Year slices but drop out of tier slices,
    # same as a blank tier in Power BI.
    return df.merge(clients, on="client_id", how="left", validate="many_to_one")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    clients = pd.read_csv(DATA_DIR / "dim_client.csv", usecols=["client_id", "client_tier"])
    if clients["client_id"].duplicated().any():
        raise ValueError("dim_client.client_id is not unique")

    snap = _load_fact(
        "fact_portfolio_snapshot.csv",
        ["snapshot_date", "client_id", "aum", "active_alpha_ytd", "is_return_suspect"],
        "snapshot_date",
        clients,
    )
    fees = _load_fact("fact_fees.csv", ["fee_date", "client_id", "amount"], "fee_date", clients)
    txns = _load_fact(
        "fact_transactions.csv",
        ["txn_date", "client_id", "amount", "txn_type"],
        "txn_date",
        clients,
    )
    return snap, fees, txns


# --------------------------------------------------------------------------
# Slices
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Slice:
    label: str
    months: frozenset          # set of month-start Timestamps in the filter context
    tier: str | None = None

    def shifted(self, *, years: int = 0, months: int = 0) -> "Slice":
        offset = pd.DateOffset(years=years, months=months)
        return Slice(self.label, frozenset(m - offset for m in self.months), self.tier)

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        mask = df["month"].isin(list(self.months))
        if self.tier is not None:
            mask &= df["client_tier"].eq(self.tier)
        return df.loc[mask]


def build_slices(*facts: pd.DataFrame) -> list[Slice]:
    # Labels and month sets are fixed to match the Power BI export (see Config).
    first = min(f["month"].min() for f in facts)
    last = max(f["month"].max() for f in facts)
    all_months = frozenset(pd.date_range(first, last, freq="MS"))

    def year_months(y: int) -> frozenset:
        return frozenset(pd.date_range(f"{y}-01-01", f"{y}-12-01", freq="MS"))

    slices = [Slice("Total", all_months)]
    slices += [Slice(f"Year {y}", year_months(y)) for y in YEARS]
    slices += [Slice(f"Tier {t} {TIER_YEAR}", year_months(TIER_YEAR), tier=t) for t in TIERS]
    slices.append(Slice("Dec 2024", frozenset([DEC_2024])))
    return slices


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def divide(numerator, denominator):
    """DAX DIVIDE: blank if either side is blank or the denominator is 0."""
    if numerator is BLANK or denominator is BLANK or denominator == 0:
        return BLANK
    return numerator / denominator


def sum_or_blank(values: pd.Series):
    """DAX SUM over no rows returns BLANK, not 0."""
    return BLANK if values.empty else float(values.sum())


def rows_on_last_date(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows
    return rows.loc[rows["date"].eq(rows["date"].max())]


# --------------------------------------------------------------------------
# Measures
# --------------------------------------------------------------------------
class Measures:
    def __init__(self, snap: pd.DataFrame, fees: pd.DataFrame, txns: pd.DataFrame):
        self.snap = snap
        self.fees = fees
        self.txns = txns

    # --- AUM -------------------------------------------------------------
    def aum_naive_sum(self, s: Slice):
        return sum_or_blank(s.filter(self.snap)["aum"])

    def ending_aum(self, s: Slice):
        last = rows_on_last_date(s.filter(self.snap))
        return sum_or_blank(last["aum"])

    def ending_clients(self, s: Slice):
        last = rows_on_last_date(s.filter(self.snap))
        return BLANK if last.empty else int(last["client_id"].nunique())

    def avg_aum_per_client(self, s: Slice):
        return divide(self.ending_aum(s), self.ending_clients(s))

    def ending_aum_ly(self, s: Slice):
        return self.ending_aum(s.shifted(years=1))

    def aum_yoy_pct(self, s: Slice):
        ly = self.ending_aum_ly(s)
        cur = self.ending_aum(s)
        if ly is BLANK or cur is BLANK:
            return BLANK
        return divide(cur - ly, ly)

    def ending_aum_pm(self, s: Slice):
        return self.ending_aum(s.shifted(months=1))

    def aum_mom_pct(self, s: Slice):
        pm = self.ending_aum_pm(s)
        cur = self.ending_aum(s)
        if pm is BLANK or cur is BLANK:
            return BLANK
        return divide(cur - pm, pm)

    def avg_monthly_aum(self, s: Slice):
        rows = s.filter(self.snap)
        return divide(sum_or_blank(rows["aum"]), rows["date"].nunique())

    # --- Fees & flows ----------------------------------------------------
    def fee_yield_bps(self, s: Slice):
        fee_total = sum_or_blank(s.filter(self.fees)["amount"])
        aum_total = sum_or_blank(s.filter(self.snap)["aum"])
        if fee_total is BLANK:
            return BLANK
        return divide(fee_total * 12 * 10_000, aum_total)

    def organic_growth_rate(self, s: Slice):
        rows = s.filter(self.txns)
        deposits = sum_or_blank(rows.loc[rows["txn_type"].eq("Deposit"), "amount"])
        withdrawals = sum_or_blank(rows.loc[rows["txn_type"].eq("Withdrawal"), "amount"])
        if deposits is BLANK and withdrawals is BLANK:
            net_flows = BLANK
        else:
            net_flows = (deposits or 0.0) - (withdrawals or 0.0)  # BLANK - x = -x in DAX
        return divide(net_flows, self.ending_aum_ly(s))

    # --- Alpha -----------------------------------------------------------
    def aum_weighted_alpha(self, s: Slice):
        # Last date is picked from ALL slice rows, before any exclusions.
        last = rows_on_last_date(s.filter(self.snap))
        keep = last.loc[last["is_return_suspect"].ne(1) & last["active_alpha_ytd"].notna()]
        if keep.empty:
            return BLANK
        weighted = float((keep["aum"] * keep["active_alpha_ytd"]).sum())
        return divide(weighted, float(keep["aum"].sum()))

    def alpha_signal(self, s: Slice):
        alpha = self.aum_weighted_alpha(s)
        if alpha is BLANK:
            return BLANK
        if alpha >= ALPHA_UPPER:
            return "Outperforming"
        if alpha <= ALPHA_LOWER:
            return "Lagging"
        return "In line"

    # --- Concentration ---------------------------------------------------
    def top10_client_share(self, s: Slice):
        last = rows_on_last_date(s.filter(self.snap))
        if last.empty:
            return BLANK
        top10 = last.groupby("client_id")["aum"].sum().nlargest(10).sum()
        return divide(float(top10), self.ending_aum(s))

    def registry(self) -> dict[str, Callable[[Slice], object]]:
        return {
            "AUM (naive SUM)": self.aum_naive_sum,
            "Ending AUM": self.ending_aum,
            "Ending Clients": self.ending_clients,
            "Avg AUM per Client": self.avg_aum_per_client,
            "Ending AUM LY": self.ending_aum_ly,
            "AUM YoY %": self.aum_yoy_pct,
            "Ending AUM PM": self.ending_aum_pm,
            "AUM MoM %": self.aum_mom_pct,
            "Avg Monthly AUM": self.avg_monthly_aum,
            "Fee Yield (bps)": self.fee_yield_bps,
            "Organic Growth Rate": self.organic_growth_rate,
            "AUM-Weighted Alpha": self.aum_weighted_alpha,
            "Alpha Signal": self.alpha_signal,
            "Top 10 Client Share": self.top10_client_share,
        }


def compute_pandas_values() -> pd.DataFrame:
    snap, fees, txns = load_data()
    measures = Measures(snap, fees, txns)
    slices = build_slices(snap, fees, txns)

    registry = measures.registry()
    if set(registry) != set(TOLERANCES):
        raise ValueError(
            "TOLERANCES keys must match the measure registry. "
            f"Missing tolerance: {sorted(set(registry) - set(TOLERANCES))}; "
            f"unknown in TOLERANCES: {sorted(set(TOLERANCES) - set(registry))}"
        )

    records = [
        {"measure": name, "slice": s.label, "pandas_value": fn(s)}
        for name, fn in registry.items()
        for s in slices
    ]
    return pd.DataFrame(records)


# --------------------------------------------------------------------------
# Comparison (powerbi_values.csv is read only here)
# --------------------------------------------------------------------------
def parse_pbi_value(raw: str):
    text = str(raw).strip()
    if text == "":
        return BLANK
    try:
        return float(text)
    except ValueError:
        return text


def load_powerbi_values() -> pd.DataFrame:
    pbi = pd.read_csv(PBI_VALUES_CSV, dtype=str, keep_default_na=False)
    pbi["measure"] = pbi["measure"].str.strip()
    pbi["slice"] = pbi["slice"].str.strip()
    pbi["powerbi_value"] = pbi["value"].map(parse_pbi_value)
    return pbi[["measure", "slice", "powerbi_value"]]


def _is_blank(v) -> bool:
    return v is BLANK or (isinstance(v, float) and pd.isna(v))


def compare(measure: str, pbi_val, pd_val) -> tuple[float | None, bool]:
    pbi_blank, pd_blank = _is_blank(pbi_val), _is_blank(pd_val)
    if pbi_blank and pd_blank:
        return None, True
    if pbi_blank or pd_blank:
        return None, False
    tol = TOLERANCES[measure]
    if tol is TEXT_EXACT or isinstance(pbi_val, str) or isinstance(pd_val, str):
        return None, str(pbi_val) == str(pd_val)
    diff = abs(float(pbi_val) - float(pd_val))
    return diff, diff <= tol


def reconcile(pandas_values: pd.DataFrame, pbi_values: pd.DataFrame) -> pd.DataFrame:
    """One row per Power BI row, in Power BI order.

    status is "match", "mismatch", or "missing_in_pandas" (a Power BI row with
    no pandas counterpart, which counts as a failure).
    """
    merged = pbi_values.merge(pandas_values, on=["measure", "slice"], how="left", indicator=True)
    missing = merged["_merge"].eq("left_only")

    results = [
        (None, False) if miss else compare(m, a, b)
        for m, a, b, miss in zip(merged["measure"], merged["powerbi_value"],
                                 merged["pandas_value"], missing)
    ]
    merged["abs_diff"] = [r[0] for r in results]
    merged["match"] = pd.Series([r[1] for r in results], index=merged.index, dtype=bool)
    merged["status"] = "mismatch"
    merged.loc[merged["match"], "status"] = "match"
    merged.loc[missing, "status"] = "missing_in_pandas"
    return merged[["measure", "slice", "powerbi_value", "pandas_value",
                   "abs_diff", "match", "status"]]


def report_unchecked(pandas_values: pd.DataFrame, pbi_values: pd.DataFrame) -> None:
    """Warn (not fail) about pandas results that Power BI never exported."""
    pbi_keys = set(zip(pbi_values["measure"], pbi_values["slice"]))
    pandas_only = [k for k in zip(pandas_values["measure"], pandas_values["slice"])
                   if k not in pbi_keys]
    unchecked_measures = sorted(set(pandas_values["measure"]) - set(pbi_values["measure"]))

    print(f"Pandas-only rows not in powerbi_values.csv (not checked): {len(pandas_only)}")
    if unchecked_measures:
        print("WARNING: measures computed in pandas with no Power BI rows at all "
              "(not verified):")
        for name in unchecked_measures:
            print(f"  - {name}")


def print_summary(recon: pd.DataFrame) -> int:
    """Print the summary and return the number of failing rows."""
    mismatches = recon.loc[recon["status"].eq("mismatch")]
    missing = recon.loc[recon["status"].eq("missing_in_pandas")]
    failures = recon.loc[~recon["match"]]

    print("\n" + "=" * 60)
    print("MEASURE RECONCILIATION SUMMARY")
    print("=" * 60)
    print(f"Power BI rows      : {len(recon)}")
    print(f"Matches            : {int(recon['match'].sum())}")
    print(f"Mismatches         : {len(mismatches)}")
    print(f"Missing in pandas  : {len(missing)}")
    if failures.empty:
        print("All Power BI measures reconcile to pandas within tolerance.")
    else:
        print("\nFailing rows:")
        with pd.option_context("display.max_rows", None, "display.width", 200,
                               "display.float_format", "{:,.6f}".format):
            print(failures.to_string(index=False))
    print(f"\nWrote {OUTPUT_CSV.relative_to(HW06_DIR.parent)}")
    return len(failures)


def main() -> None:
    # 1) Independent pandas rebuild - no Power BI inputs.
    pandas_values = compute_pandas_values()

    # 2) Only now bring in Power BI's exported values.
    pbi_values = load_powerbi_values()

    # 3) Compare, write, summarise.
    report_unchecked(pandas_values, pbi_values)
    recon = reconcile(pandas_values, pbi_values)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    # status is for the console summary only; the CSV keeps the fixed schema.
    recon[OUTPUT_COLUMNS].to_csv(OUTPUT_CSV, index=False)
    failures = print_summary(recon)
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
