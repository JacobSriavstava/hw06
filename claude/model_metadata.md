## Columns
[Table]	[Column]	[DataType]	[DAX formula]	[IsHidden]
DateTableTemplate_b50879b8-a09d-4fd7-b9a6-7a34995295aa	Date	Date		true
DateTableTemplate_b50879b8-a09d-4fd7-b9a6-7a34995295aa	Day	Integer	DAY([Date])	true
DateTableTemplate_b50879b8-a09d-4fd7-b9a6-7a34995295aa	Quarter	Text	"Qtr " & [QuarterNo]	true
DateTableTemplate_b50879b8-a09d-4fd7-b9a6-7a34995295aa	QuarterNo	Integer	INT(([MonthNo] + 2) / 3)	true
DateTableTemplate_b50879b8-a09d-4fd7-b9a6-7a34995295aa	Month	Text	FORMAT([Date], "MMMM")	true
DateTableTemplate_b50879b8-a09d-4fd7-b9a6-7a34995295aa	MonthNo	Integer	MONTH([Date])	true
DateTableTemplate_b50879b8-a09d-4fd7-b9a6-7a34995295aa	Year	Integer	YEAR([Date])	true
dim_advisor	years_experience	Integer		false
dim_advisor	certifications	Text		false
dim_advisor	advisor_id	Integer		false
dim_advisor	first_name	Text		false
dim_advisor	last_name	Text		false
dim_advisor	region	Text		false
dim_advisor	aum_target_mm	Integer		false
dim_benchmark	ticker_proxy	Text		false
dim_benchmark	asset_class	Text		false
dim_benchmark	name	Text		false
dim_benchmark	benchmark_id	Integer		false
dim_client	client_since	Date		false
dim_client	first_name	Text		false
dim_client	primary_account_type	Text		false
dim_client	client_tier	Text		false
dim_client	risk_profile	Text		false
dim_client	zip_code	Text		false
dim_client	state	Text		false
dim_client	city	Text		false
dim_client	age	Integer		false
dim_client	last_name	Text		false
dim_client	initial_aum	Number		false
dim_client	client_id	Integer		false
dim_client	is_active	True/False		false
dim_client	advisor_id	Integer		false
dim_date	is_quarter_end	Integer		false
dim_date	is_year_end	Integer		false
dim_date	is_trading_day	Integer		false
dim_date	Year	Integer		false
dim_date	Date	Date		false
dim_date	date_id	Integer		false
dim_date	Month	Integer		false
dim_date	Quarter	Integer		false
dim_date	month_name	Text		false
dim_date	week_of_year	Integer		false
dim_date	day_of_week	Text		false
dim_date	is_month_end	Integer		false
dim_security	expense_ratio_bps	Integer		false
dim_security	security_id	Integer		false
dim_security	ticker	Text		false
dim_security	name	Text		false
dim_security	asset_class	Text		false
dim_security	sector	Text		false
dim_security	benchmark_id	Integer		false
dim_security	is_etf	True/False		false
fact_fees	client_id	Integer		false
fact_fees	amount	Number		false
fact_fees	bps_charged	Number		false
fact_fees	aum_basis	Number		false
fact_fees	fee_type	Text		false
fact_fees	fee_date	Date		false
fact_fees	advisor_id	Integer		false
fact_fees	fee_id	Integer		false
fact_portfolio_snapshot	aum	Number		false
fact_portfolio_snapshot	Year	Integer		false
fact_portfolio_snapshot	snapshot_date	Date		false
fact_portfolio_snapshot	benchmark_id	Integer		false
fact_portfolio_snapshot	advisor_id	Integer		false
fact_portfolio_snapshot	client_id	Integer		false
fact_portfolio_snapshot	snapshot_id	Integer		false
fact_portfolio_snapshot	is_return_suspect	Integer		false
fact_portfolio_snapshot	account_type	Text		false
fact_portfolio_snapshot	cash_pct	Number		false
fact_portfolio_snapshot	active_alpha_ytd	Number		false
fact_portfolio_snapshot	benchmark_return_ytd	Number		false
fact_portfolio_snapshot	return_ytd	Number		false
fact_portfolio_snapshot	Month	Integer		false
fact_transactions	txn_id	Integer		false
fact_transactions	amount	Number		false
fact_transactions	price	Number		false
fact_transactions	shares	Number		false
fact_transactions	txn_type	Text		false
fact_transactions	txn_date	Date		false
fact_transactions	security_id	Integer		false
fact_transactions	advisor_id	Integer		false
fact_transactions	client_id	Integer		false
fact_transactions	is_post_departure_txn	Integer		false
LocalDateTable_976ce71a-eea0-49bb-b089-dd421adaa4b8	Month	Text	FORMAT([Date], "MMMM")	true
LocalDateTable_976ce71a-eea0-49bb-b089-dd421adaa4b8	QuarterNo	Integer	INT(([MonthNo] + 2) / 3)	true
LocalDateTable_976ce71a-eea0-49bb-b089-dd421adaa4b8	Quarter	Text	"Qtr " & [QuarterNo]	true
LocalDateTable_976ce71a-eea0-49bb-b089-dd421adaa4b8	Day	Integer	DAY([Date])	true
LocalDateTable_976ce71a-eea0-49bb-b089-dd421adaa4b8	Date	Date		true
LocalDateTable_976ce71a-eea0-49bb-b089-dd421adaa4b8	Year	Integer	YEAR([Date])	true
LocalDateTable_976ce71a-eea0-49bb-b089-dd421adaa4b8	MonthNo	Integer	MONTH([Date])	true

## Relationships
[ID]	[Name]	[Relationship]	[Model]	[IsActive]	[CrossFilteringBehavior]	[RelyOnReferentialIntegrity]	[FromTable]	[FromColumn]	[FromCardinality]	[ToTable]	[ToColumn]	[ToCardinality]	[State]	[SecurityFilteringBehavior]
2450	AutoDetected_47d2c78f-3915-4351-b30d-fc5f654a65f4	'fact_transactions'[advisor_id] *[<-]1 'dim_advisor'[advisor_id]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_transactions	advisor_id	Many	dim_advisor	advisor_id	One	Ready	Single
3424	AutoDetected_080dc0c9-a847-4102-8fe6-5527ad4e80b2	'fact_transactions'[client_id] *[<-]1 'dim_client'[client_id]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_transactions	client_id	Many	dim_client	client_id	One	Ready	Single
4453	AutoDetected_2f815d05-ddf4-42b9-bf11-303f56a168d6	'fact_transactions'[security_id] *[<-]1 'dim_security'[security_id]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_transactions	security_id	Many	dim_security	security_id	One	Ready	Single
4712	6deec966-5197-f019-8717-87cd3326e62d	'fact_transactions'[txn_date] *[<-]1 'dim_date'[date]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_transactions	txn_date	Many	dim_date	date	One	Ready	Single
2451	AutoDetected_515f758c-a4c4-4e3e-8414-fe1239270ac5	'fact_portfolio_snapshot'[advisor_id] *[<-]1 'dim_advisor'[advisor_id]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_portfolio_snapshot	advisor_id	Many	dim_advisor	advisor_id	One	Ready	Single
2639	AutoDetected_27290db9-48a2-4230-a18e-ac5fca16ab64	'fact_portfolio_snapshot'[benchmark_id] *[<-]1 'dim_benchmark'[benchmark_id]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_portfolio_snapshot	benchmark_id	Many	dim_benchmark	benchmark_id	One	Ready	Single
3425	AutoDetected_8da07bbb-379a-44b4-8620-2cb9df480b79	'fact_portfolio_snapshot'[client_id] *[<-]1 'dim_client'[client_id]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_portfolio_snapshot	client_id	Many	dim_client	client_id	One	Ready	Single
4695	aa81e5e4-13d7-2473-c80b-1050d4fb268e	'fact_portfolio_snapshot'[snapshot_date] *[<-]1 'dim_date'[date]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_portfolio_snapshot	snapshot_date	Many	dim_date	date	One	Ready	Single
2452	AutoDetected_13cb45f8-9f1d-42c6-9326-a4402ef86ceb	'fact_fees'[advisor_id] *[<-]1 'dim_advisor'[advisor_id]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_fees	advisor_id	Many	dim_advisor	advisor_id	One	Ready	Single
3426	AutoDetected_6b7ee019-ebcc-4ab0-a5f6-23016186f549	'fact_fees'[client_id] *[<-]1 'dim_client'[client_id]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_fees	client_id	Many	dim_client	client_id	One	Ready	Single
4678	fbd94a81-c893-0c31-c79a-9a0f84f664a0	'fact_fees'[fee_date] *[<-]1 'dim_date'[date]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	fact_fees	fee_date	Many	dim_date	date	One	Ready	Single
2662	371030ed-f05a-47f6-a233-06998810b983	'dim_client'[client_since] *[<-]1 'LocalDateTable_976ce71a-eea0-49bb-b089-dd421adaa4b8'[Date]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	dim_client	client_since	Many	LocalDateTable_976ce71a-eea0-49bb-b089-dd421adaa4b8	date	One	Ready	Single
4454	AutoDetected_031cb484-3962-4004-9c23-08d705a8563e	'dim_security'[benchmark_id] *[<-]1 'dim_benchmark'[benchmark_id]	ca34a054-9d2c-4746-aa82-054222ad4fc1	true	OneDirection	false	dim_security	benchmark_id	Many	dim_benchmark	benchmark_id	One	Ready	Single

## Measures

[Table]	[Measure]	[DAX formula]	[FormatString]	[State]
_Measures	Total Fees	SUM( fact_fees[amount])		Valid
_Measures	Net Flows	CALCULATE(SUM( fact_transactions[amount]), fact_transactions[txn_type] = "Deposit") - CALCULATE(SUM( fact_transactions[amount]), fact_transactions[txn_type] = "Withdrawal")		Valid
_Measures	AUM (naive SUM)	SUM( fact_portfolio_snapshot[aum])		Valid
_Measures	Ending AUM	CALCULATE( SUM(fact_portfolio_snapshot[aum]),LASTNONBLANK( dim_date[date], CALCULATE( COUNTROWS(fact_portfolio_snapshot))))		Valid
_Measures	Ending Clients	CALCULATE(DISTINCTCOUNT(fact_portfolio_snapshot[client_id]), LASTNONBLANK( dim_date[date], CALCULATE( COUNTROWS(fact_portfolio_snapshot))))		Valid
_Measures	Avg AUM per Client	DIVIDE([Ending AUM], [Ending Clients])		Valid
_Measures	Ending AUM LY	CALCULATE([Ending AUM], SAMEPERIODLASTYEAR(dim_date[date]))		Valid
_Measures	AUM YoY %	DIVIDE( [Ending AUM] - [Ending AUM LY], [Ending AUM LY])		Valid
_Measures	Ending AUM PM	CALCULATE( [Ending AUM], DATEADD(dim_date[date], -1, MONTH))		Valid
_Measures	AUM MoM %	DIVIDE([Ending AUM]-[Ending AUM PM],[Ending AUM PM])		Valid
_Measures	Avg Monthly AUM	DIVIDE(SUM(fact_portfolio_snapshot[aum]), DISTINCTCOUNT(fact_portfolio_snapshot[snapshot_date]))		Valid
_Measures	Fee Yield (bps)	DIVIDE([Total Fees] * 12 * 10000, SUM(fact_portfolio_snapshot[aum]))		Valid
_Measures	Organic Growth Rate	DIVIDE([Net Flows],[Ending AUM LY])		Valid
_Measures	AUM-Weighted Alpha	CALCULATE(DIVIDE(SUMX(fact_portfolio_snapshot, fact_portfolio_snapshot[aum]*fact_portfolio_snapshot[active_alpha_ytd]), SUM(fact_portfolio_snapshot[aum])), LASTNONBLANK(dim_date[date], CALCULATE(COUNTROWS(fact_portfolio_snapshot))), fact_portfolio_snapshot[is_return_suspect] <> 1, NOT ISBLANK(fact_portfolio_snapshot[active_alpha_ytd]))		Valid
_Measures	Alpha Signal	VAR a = [AUM-Weighted Alpha] RETURN SWITCH( TRUE(), ISBLANK(a), BLANK(), a>=0.02, "Outperforming", a<= -0.02, "Lagging", "In line")		Valid