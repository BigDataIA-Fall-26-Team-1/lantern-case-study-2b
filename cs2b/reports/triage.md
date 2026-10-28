# Triage of non-admitted filings

89 of 171 attempted filings were not admitted ($333,975.1m of $538,863.9m filed fair value).

Evidence: `reports/p3_gap_evidence.csv` (simple causes), `reports/p3_gap_evidence2.csv` (extra axes, alternative totals), `reports/p3_gap_evidence3.csv` (NUM comparison, issuer subtotals). Scripts: `scripts/p3b_gap_evidence.py`, `scripts/p3c_deep_evidence.py`, `scripts/p3d_num_and_subtotals.py`, `scripts/p3e_triage.py`.

## Key finding

For 62 of the 80 excluded filings with a filed total and holdings, the filer's own identifier-level fair value facts in NUM sum to our parsed holdings within 1%, and every matched holding's SOI value equals its NUM value. The parse is faithful; most gaps come from what the filers tag, not from parsing.

## Category rules (applied in this order)

1. No filed total in NUM: `no_filed_total`.
2. No identified holdings: `no_identified_holdings`.
3. NUM identifier-level facts exceed our holdings by more than 1%: `custom_tags`.
4. Our holdings more than 10x the filed fact: `other` (the fact is not the portfolio total).
5. Issuer-level subtotals close the gap: `totals_counted`.
6. Removing negative fair values closes the gap: `unfunded_commitments`.
7. Adding back cash dropped by rule_cash closes the gap: `cash_lines`.
8. A single holding equals the gap: `totals_counted`.
9. Short of the total with missing fair values: `custom_tags`.
10. Over the total with subtotals explaining at least half the gap: `totals_counted`.
10b. Our total an exact multiple (2x or more) of the filed total: `totals_counted` (subtotal levels carrying identifiers).
11. Otherwise: `other`, with the NUM evidence stated.

## Summary

| Category | Filings | Filed fair value |
|---|---:|---:|
| other | 46.0 | $268,582.5m |
| custom_tags | 21.0 | $42,214.0m |
| totals_counted | 9.0 | $15,363.2m |
| no_filed_total | 7.0 | $0.0m |
| unfunded_commitments | 3.0 | $5,927.8m |
| no_identified_holdings | 2.0 | $683.9m |
| cash_lines | 1.0 | $1,203.6m |

## Filings

### BLACKSTONE PRIVATE CREDIT FUND (0001803498-26-000014, 10-K)

- Gap: +8.42%; holdings $89,123.7m (2005); filed $82,199.3m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +2.8%), but exceed its reported total by $6,924.4m (+8.4%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `BCRED Emerald JV LP - LP Interest`, fair value $1,678.7m, SOI rows 96758
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### BLUE OWL CREDIT INCOME CORP. (0001812554-26-000011, 10-K)

- Gap: +4.30%; holdings $37,464.3m (558); filed $35,918.9m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $1,545.4m (+4.3%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Associations, Inc. | First lien senior secured loan | Non-Affiliated Issuer`, fair value $535.8m, SOI rows 95510
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### HPS CORPORATE LENDING FUND (0001628280-26-020206, 10-K)

- Gap: +5.95%; holdings $26,844.9m (1092); filed $25,337.4m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $1,507.5m (+5.9%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Blazing Star Shields Direct Parent, LLC 1 | Non-Affiliated Issuer`, fair value $485.9m, SOI rows 97204
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### BLUE OWL CAPITAL CORP (0001655888-26-000010, 10-K)

- Gap: +11.18%; holdings $18,312.0m (634); filed $16,470.9m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +4.2%), but exceed its reported total by $1,841.1m (+11.2%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Wingspire Capital Holdings LLC | Specialty finance equity investment | Affiliated`, fair value $607.3m, SOI rows 66757
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### GOLDMAN SACHS PRIVATE CREDIT CORP. (0001193125-26-088668, 10-K)

- Gap: -5.87%; holdings $14,753.8m (732); filed $15,674.5m
- **Category:** `custom_tags`
- **Evidence:** NUM has $252.9m of identifier-level fair value the SOI lacks: $252.9m on identifiers absent from the SOI, and $0.0m for 26 SOI holdings with no fair value.
- **Example:** `Equity and Other - 0.7% United States - 0.1% Common Stock - 0.1% SDB HOLDCO, LLC (dba Spec`, fair value n/a, SOI rows 108319;108320
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### BLUE OWL TECHNOLOGY FINANCE CORP. (0001747777-26-000012, 10-K)

- Gap: +8.92%; holdings $15,560.1m (491); filed $14,286.0m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference -0.1%), but exceed its reported total by $1,274.1m (+8.9%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Certinia Inc. | First lien senior secured loan | Non-Affiliated Issuer`, fair value $231.0m, SOI rows 21193
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### FS KKR CAPITAL CORP (0001628280-26-011734, 10-K)

- Gap: +48.11%; holdings $19,267.0m (733); filed $13,008.6m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.2%), but exceed its reported total by $6,258.4m (+48.1%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Credit Opportunities Partners JV, LLC | Credit Opportunities Partners JV, LLC`, fair value $1,967.9m, SOI rows 23780
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### NORTH HAVEN PRIVATE INCOME FUND LLC (0001193125-26-096532, 10-K/A)

- Gap: +5.36%; holdings $6,965.1m (1082); filed $6,610.6m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $354.5m (+5.4%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Investments-non-controlled/non-affiliated Debt Investments Insurance Services Integrity Ma`, fair value $111.2m, SOI rows 132258
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### PROSPECT CAPITAL CORP (0001287032-26-000045, 10-Q)

- Gap: +5.73%; holdings $6,810.4m (260); filed $6,441.5m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +52.0%), but exceed its reported total by $368.9m (+5.7%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `National Property REIT Corp. | Residential Real Estate Investment Trusts (REITs) / Consume`, fair value $652.6m, SOI rows 49560
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### BLUE OWL TECHNOLOGY INCOME CORP. (0001869453-26-000017, 10-K)

- Gap: +1.29%; holdings $6,286.9m (451); filed $6,207.1m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.9%), but exceed its reported total by $79.8m (+1.3%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `IRI Group Holdings, Inc. (f/k/a Circana Group, L.P. (f/k/a The NPD Group, L.P.)), First li`, fair value $145.4m, SOI rows 135030
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### MONROE CAPITAL INCOME PLUS CORP (0001742313-26-000013, 10-K)

- Gap: +5.30%; holdings $6,127.9m (978); filed $5,819.8m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $308.2m (+5.3%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `ZI Intermediate II, Inc. | Senior Secured Loans`, fair value $82.3m, SOI rows 166670
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### MAIN STREET CAPITAL CORP (0001396440-26-000016, 10-K)

- Gap: +7.94%; holdings $5,956.3m (737); filed $5,518.1m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +5.7%), but exceed its reported total by $438.1m (+7.9%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `MSC Adviser I, LLC | Member Units`, fair value $255.0m, SOI rows 49266
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### BARINGS PRIVATE CREDIT CORP (0001859919-26-000022, 10-K)

- Gap: +4.87%; holdings $5,114.4m (807); filed $4,877.0m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.2%), but exceed its reported total by $237.4m (+4.9%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Rocade Holdings LLC | Preferred LP Units`, fair value $141.2m, SOI rows 59320;59321
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### HERCULES CAPITAL, INC. (0001280784-26-000009, 10-K)

- Gap: +21.02%; holdings $5,405.5m (365); filed $4,466.6m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $938.8m (+21.0%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Debt Investments Healthcare Services, Other and Total Marathon Health, LLC`, fair value $181.3m, SOI rows 25896
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### TPG TWIN BROOK CAPITAL INCOME FUND (0001913724-26-000007, 10-K)

- Gap: +2.42%; holdings $4,381.4m (796); filed $4,277.7m
- **Category:** `totals_counted`
- **Evidence:** A single holding ($103.7m) equals the gap of $103.7m.
- **Example:** `Twin Brook Equity Holdings, LLC , Equity interest, Affiliated`, fair value $103.7m, SOI rows 162014
- **Fix or reason:** None yet: one filing, verify before writing a rule.

### FRANKLIN BSP CAPITAL CORP (0001825248-26-000007, 10-K)

- Gap: +31.36%; holdings $5,347.9m (536); filed $4,071.0m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $1,276.9m (+31.4%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `FBLC Senior Loan Fund, LLC | Investment in Joint Ventures`, fair value $225.0m, SOI rows 109201
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### SIXTH STREET SPECIALTY LENDING, INC. (0001193125-26-048664, 10-K)

- Gap: +1.75%; holdings $3,406.0m (223); filed $3,347.3m
- **Category:** `totals_counted`
- **Evidence:** A single holding ($76.7m) equals the gap of $58.7m.
- **Example:** `Debt Investments Internet Services EDB Parent, LLC Investment First-lien loan ($76,729 par`, fair value $76.7m, SOI rows 26115;26116
- **Fix or reason:** None yet: one filing, verify before writing a rule.

### GOLDMAN SACHS BDC, INC. (0001193125-26-077458, 10-K)

- Gap: -6.65%; holdings $3,044.8m (526); filed $3,261.7m
- **Category:** `custom_tags`
- **Evidence:** NUM has $71.4m of identifier-level fair value the SOI lacks: $71.4m on identifiers absent from the SOI, and $0.0m for 3 SOI holdings with no fair value.
- **Example:** `Investment Debt Investments - 226.3% United Kingdom - 3.5% 1st Lien/Senior Secured Debt - `, fair value n/a, SOI rows 37569
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### MIDCAP FINANCIAL INVESTMENT CORP (0001193125-26-076499, 10-K)

- Gap: +11.00%; holdings $3,516.2m (683); filed $3,167.8m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $348.3m (+11.0%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Controlled Investments ChyronHego US Holding Corporation, Term Loan`, fair value $105.9m, SOI rows 23172;23173
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### ARES CORE INFRASTRUCTURE FUND (0002031750-26-000015, 10-K)

- Gap: +108.10%; holdings $6,493.7m (79); filed $3,120.4m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $3,373.3m (+108.1%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Denali Equity Holdings LLC`, fair value $2,522.5m, SOI rows 106233
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### STEPSTONE PRIVATE CREDIT FUND LLC (0001193125-26-128890, 10-K)

- Gap: +28.43%; holdings $3,864.1m (1037); filed $3,008.6m
- **Category:** `custom_tags`
- **Evidence:** NUM has $334.3m of identifier-level fair value the SOI lacks: $334.3m on identifiers absent from the SOI, and $0.0m for 9 SOI holdings with no fair value.
- **Example:** `on-Controlled, Non-Affiliated Debt Investments | First Lien Senior Secured | Insurance Bro`, fair value n/a, SOI rows 143012
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### DIAMETER CREDIT CO (0001193125-26-104439, 10-K)

- Gap: -1.87%; holdings $2,731.6m (247); filed $2,783.5m
- **Category:** `unfunded_commitments`
- **Evidence:** Negative fair values ($-28.5m) close the gap of $-51.9m.
- **Example:** `Investments Non-Controlled/Non-Affiliated First Lien Debt Interactive Media & Services Twi`, fair value $94.6m, SOI rows 128768;128769
- **Fix or reason:** None: the filer nets unfunded commitments differently; most filers keep them.

### CARLYLE CREDIT SOLUTIONS, INC. (0001702510-26-000021, 10-K)

- Gap: +1.08%; holdings $2,679.9m (260); filed $2,651.3m
- **Category:** `totals_counted`
- **Evidence:** A single holding ($45.5m) equals the gap of $28.6m.
- **Example:** `Investment | Non-Affiliated Issuer | First Lien Debt | Deerfield Dakota Holding, LLC | Div`, fair value $45.5m, SOI rows 115553
- **Fix or reason:** None yet: one filing, verify before writing a rule.

### KKR FS INCOME TRUST (0001628280-26-017326, 10-K)

- Gap: +23.11%; holdings $3,231.7m (463); filed $2,625.1m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $606.6m (+23.1%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Apex Service Partners LLC | Commercial & Professional Services 3`, fair value $55.3m, SOI rows 94603
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### CARLYLE SECURED LENDING, INC. (0001544206-26-000013, 10-K)

- Gap: +49.70%; holdings $3,688.4m (298); filed $2,463.9m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $1,224.5m (+49.7%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Investment | Affiliated Issuer | Investment Funds | Middle Market Credit Fund, LLC, Subord`, fair value $123.1m, SOI rows 36491
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### TRINITY CAPITAL INC. (0001193125-26-068600, 10-K)

- Gap: +21.62%; holdings $2,940.8m (542); filed $2,418.1m
- **Category:** `custom_tags`
- **Evidence:** NUM has $218.1m of identifier-level fair value the SOI lacks: $218.1m on identifiers absent from the SOI, and $0.0m for 86 SOI holdings with no fair value.
- **Example:** `Affiliate Investments Autonomy Data Services, Inc.`, fair value n/a, SOI rows 15017
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### BARINGS BDC, INC. (0001379785-26-000009, 10-K)

- Gap: +11.93%; holdings $2,684.7m (681); filed $2,398.5m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $286.1m (+11.9%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Eclipse Business Capital, LLC | LLC units`, fair value $139.5m, SOI rows 28650;28651
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### FIDELITY PRIVATE CREDIT FUND (0001193125-26-119488, 10-K)

- Gap: -8.34%; holdings $2,101.4m (345); filed $2,292.6m
- **Category:** `custom_tags`
- **Evidence:** We are short by $191.2m; 31 holdings have no SOI fair value and NUM has 0 custom-tag fair value facts.
- **Example:** `Investments -- non-controlled/ non-affiliate Equity Air Freight & Logistics SCP 3PL Topco,`, fair value n/a, SOI rows 118541
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### T SERIES MIDDLE MARKET LOAN FUND LLC (0001193125-26-085572, 10-K)

- Gap: +1.33%; holdings $2,215.0m (804); filed $2,185.9m
- **Category:** `totals_counted`
- **Evidence:** A single holding ($34.7m) equals the gap of $29.1m.
- **Example:** `Debt Investments - non-controlled/non-affiliated Industrial Conglomerates Excelitas Techno`, fair value $34.7m, SOI rows 103665
- **Fix or reason:** None yet: one filing, verify before writing a rule.

### SLR INVESTMENT CORP. (0001193125-26-066979, 10-K)

- Gap: +8.54%; holdings $2,306.2m (132); filed $2,124.8m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $181.4m (+8.5%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Common Equity/Equity Interests/Warrants | SLR Credit Solutions | Financial Services | 12/2`, fair value $281.0m, SOI rows 22432;22433
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### CAPITAL SOUTHWEST CORP (0000017313-26-000011, 10-Q)

- Gap: +19.46%; holdings $2,404.9m (531); filed $2,013.2m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $391.7m (+19.5%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `CITYVET INC. | First Lien`, fair value $45.0m, SOI rows 21720
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### CION INVESTMENT CORP (0001534254-26-000003, 10-K)

- Gap: +39.10%; holdings $2,522.0m (358); filed $1,813.0m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $709.0m (+39.1%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `First American Treasury Obligations Fund, Class Z Shares, Short Term Investments`, fair value $116.0m, SOI rows 109647
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### BAIN CAPITAL PRIVATE CREDIT (0001193125-26-104390, 10-K)

- Gap: -3.04%; holdings $1,630.1m (352); filed $1,681.3m
- **Category:** `custom_tags`
- **Evidence:** We are short by $51.2m; 46 holdings have no SOI fair value and NUM has 80 custom-tag fair value facts.
- **Example:** `Non Controlled/Non Affiliate Investments Aerospace & Defense ATS First Lien Senior Secured`, fair value n/a, SOI rows 141197
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### FIDELITY PRIVATE CREDIT CO LLC (0001193125-26-119504, 10-K)

- Gap: -1.16%; holdings $1,620.6m (349); filed $1,639.7m
- **Category:** `custom_tags`
- **Evidence:** We are short by $19.1m; 23 holdings have no SOI fair value and NUM has 3 custom-tag fair value facts.
- **Example:** `Investments -- non-controlled/ non-affiliate First Lien Debt Application Software ACP Aven`, fair value n/a, SOI rows 118749
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### BLUE OWL CAPITAL CORP II (0001655887-26-000010, 10-K)

- Gap: +5.22%; holdings $1,658.8m (288); filed $1,576.5m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.1%), but exceed its reported total by $82.3m (+5.2%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Associations, Inc. | First lien senior secured loan | Non Affiliated`, fair value $47.2m, SOI rows 95508
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### JEFFERIES CREDIT PARTNERS BDC INC. (0001193125-26-116342, 10-K)

- Gap: -1.15%; holdings $1,556.8m (454); filed $1,574.9m
- **Category:** `unfunded_commitments`
- **Evidence:** Negative fair values ($-3.4m) close the gap of $-18.1m.
- **Example:** `Non-Controlled/Non-Affiliated Portfolio Company Investments First Lien Debt Investments Pr`, fair value $35.5m, SOI rows 147764
- **Fix or reason:** None: the filer nets unfunded commitments differently; most filers keep them.

### CRESCENT CAPITAL BDC, INC. (0001193125-26-071922, 10-K)

- Gap: -1.02%; holdings $1,553.4m (617); filed $1,569.4m
- **Category:** `unfunded_commitments`
- **Evidence:** Negative fair values ($-1.6m) close the gap of $-16.0m.
- **Example:** `Investments United States Equity Investments Diversified Financials First Eagle Logan JV, `, fair value $33.4m, SOI rows 43800
- **Fix or reason:** None: the filer nets unfunded commitments differently; most filers keep them.

### KKR FS INCOME TRUST SELECT (0001628280-26-017328, 10-K)

- Gap: +21.97%; holdings $1,874.0m (395); filed $1,536.4m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $337.6m (+22.0%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Bonterra LLC | Software & Services 1`, fair value $34.0m, SOI rows 97509
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### GOLDMAN SACHS PRIVATE MIDDLE MARKET CREDIT II LLC (0001193125-26-088646, 10-K)

- Gap: +4.95%; holdings $1,610.2m (161); filed $1,534.3m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $75.9m (+4.9%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Non-Controlled Affiliates Goldman Sachs Financial Square Government Fund`, fair value $125.0m, SOI rows 141983
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### BLACKROCK TCP CAPITAL CORP. (0001193125-26-079299, 10-K)

- Gap: +11.25%; holdings $1,705.8m (363); filed $1,533.3m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $172.5m (+11.3%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Debt Investments Internet Software and Services Domo, Inc. First Lien Delayed Draw Term Lo`, fair value $63.0m, SOI rows 26247
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### OVERLAND ADVANTAGE (0001193125-26-117368, 10-K)

- Gap: -11.47%; holdings $1,334.0m (46); filed $1,506.9m
- **Category:** `custom_tags`
- **Evidence:** We are short by $172.9m; 0 holdings have no SOI fair value and NUM has 30 custom-tag fair value facts.
- **Example:** `Investments Non-controlled/non-affiliated Debt investments Hotels, Restaurants & Leisure C`, fair value $97.8m, SOI rows 128136
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### FORTRESS PRIVATE LENDING FUND (0001193125-26-128496, 10-K)

- Gap: +5.02%; holdings $1,563.6m (131); filed $1,488.9m
- **Category:** `totals_counted`
- **Evidence:** A single holding ($67.8m) equals the gap of $74.7m.
- **Example:** `Investments Non-controlled, Non-affiliated Investments Debt Investments Health Care Equipm`, fair value $67.8m, SOI rows 128047
- **Fix or reason:** None yet: one filing, verify before writing a rule.

### VISTA CREDIT STRATEGIC LENDING CORP. (0001193125-26-101986, 10-K)

- Gap: -2.26%; holdings $1,435.0m (106); filed $1,468.2m
- **Category:** `custom_tags`
- **Evidence:** We are short by $33.2m; 49 holdings have no SOI fair value and NUM has 68 custom-tag fair value facts.
- **Example:** `Investments  Non-controlled/non-affiliated Aptean, Inc. Commitment Type Delayed Draw Commi`, fair value n/a, SOI rows 119858
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### 26NORTH BDC, INC. (0001193125-26-091756, 10-K)

- Gap: -4.59%; holdings $1,352.7m (123); filed $1,417.8m
- **Category:** `custom_tags`
- **Evidence:** We are short by $65.1m; 0 holdings have no SOI fair value and NUM has 34 custom-tag fair value facts.
- **Example:** `Debt Investments | Alegeus Technologies Holdings Corp. |First Lien Senior Secured Term Loa`, fair value $67.4m, SOI rows 104247;104248
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### AGL PRIVATE CREDIT INCOME FUND (0001193125-26-103932, 10-K)

- Gap: +1.77%; holdings $1,379.7m (157); filed $1,355.6m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $24.0m (+1.8%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Investments Non-controlled/Non-affiliated Debt investments Industry Electrical Equipment M`, fair value $64.0m, SOI rows 128194;128195
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### BARINGS CAPITAL INVESTMENT CORP (0001811972-26-000004, 10-K)

- Gap: +2.18%; holdings $1,366.1m (608); filed $1,337.0m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $29.1m (+2.2%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Eclipse Business Capital, LLC, LLC Units`, fair value $68.9m, SOI rows 28678;28679
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### MSC INCOME FUND, INC. (0001535778-26-000026, 10-K)

- Gap: +4.69%; holdings $1,398.0m (505); filed $1,335.4m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.8%), but exceed its reported total by $62.7m (+4.7%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `South Coast Terminals Holdings, LLC | Secured Debt 2`, fair value $33.2m, SOI rows 62000
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### LORD ABBETT PRIVATE CREDIT FUND (0000930413-26-000841, 10-K)

- Gap: -97.70%; holdings $30.1m (5); filed $1,309.9m
- **Category:** `custom_tags`
- **Evidence:** We are short by $1,279.9m; 4 holdings have no SOI fair value and NUM has 0 custom-tag fair value facts.
- **Example:** `First Lien Secured Debt`, fair value n/a, SOI rows 109703
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### PENNANTPARK INVESTMENT CORP (0001193125-26-042780, 10-Q)

- Gap: +30.07%; holdings $1,584.9m (471); filed $1,218.5m
- **Category:** `custom_tags`
- **Evidence:** NUM has $205.4m of identifier-level fair value the SOI lacks: $205.4m on identifiers absent from the SOI, and $0.0m for 3 SOI holdings with no fair value.
- **Example:** `Investments in Non-Controlled, Non-Affiliated Portfolio Companies Common Equity/Partnershi`, fair value n/a, SOI rows 39176;39177
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### PALMER SQUARE CAPITAL BDC INC. (0001193125-26-073362, 10-K)

- Gap: -3.65%; holdings $1,159.7m (264); filed $1,203.6m
- **Category:** `cash_lines`
- **Evidence:** Cash rows dropped by rule_cash ($43.9m) close the gap of $-43.9m.
- **Example:** `Short-Term Investments Morgan Stanley Liquidity Funds US Dollar Treasury Liquidity Fund - `, fair value $28.8m, SOI rows 61410
- **Fix or reason:** None: this filer's total includes cash; rule_cash is right for most filers.

### SILVER POINT SPECIALTY LENDING FUND (0001193125-26-114381, 10-K)

- Gap: +4.23%; holdings $1,233.8m (215); filed $1,183.7m
- **Category:** `custom_tags`
- **Evidence:** NUM has $189.0m of identifier-level fair value the SOI lacks: $189.0m on identifiers absent from the SOI, and $0.0m for 3 SOI holdings with no fair value.
- **Example:** `Non-Controlled/Non-Affiliated Investments 1st Lien/Secured Loans Canada 1261229 BC LTD Ins`, fair value n/a, SOI rows 144082
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### SARATOGA INVESTMENT CORP. (0001213900-26-002153, 10-Q)

- Gap: +239.17%; holdings $3,445.8m (456); filed $1,016.0m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference -11.5%), but exceed its reported total by $2,429.8m (+239.2%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Sub Total Non-control/Non-affiliate investments`, fair value $921.1m, SOI rows 2172
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### AUDAX PRIVATE CREDIT FUND, LLC (0001193125-26-120299, 10-K)

- Gap: +2.18%; holdings $970.5m (418); filed $949.8m
- **Category:** `custom_tags`
- **Evidence:** NUM has $63.5m of identifier-level fair value the SOI lacks: $63.5m on identifiers absent from the SOI, and $0.0m for 131 SOI holdings with no fair value.
- **Example:** `80/20 Senior Secured Delayed Draw Term Loan Maturity 12/13/2032`, fair value n/a, SOI rows 92353
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### JOHN HANCOCK COMVEST PRIVATE INCOME FUND (0001193125-26-124287, 10-K)

- Gap: +1.70%; holdings $953.7m (207); filed $937.7m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $16.0m (+1.7%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `First Lien Senior Secured CRA Funding 1, LLC - Term Loan Financial Services Spread Above I`, fair value $26.9m, SOI rows 109769
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### RUNWAY GROWTH FINANCE CORP. (0001193125-26-104117, 10-K)

- Gap: +1.59%; holdings $942.1m (117); filed $927.4m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $14.7m (+1.6%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Non-Control/Non-Affiliate Investments Debt Investments Systems Software 3PL Central LLC (d`, fair value $69.5m, SOI rows 141626;141627
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### GLADSTONE CAPITAL CORP (0001143513-26-000004, 10-Q)

- Gap: -5.95%; holdings $849.2m (119); filed $902.9m
- **Category:** `custom_tags`
- **Evidence:** We are short by $53.7m; 0 holdings have no SOI fair value and NUM has 17 custom-tag fair value facts.
- **Example:** `RPM Freight Systems, LLC   Term Debt`, fair value $50.0m, SOI rows 59578
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### PHILLIP STREET MIDDLE MARKET LENDING FUND LLC (0001193125-26-088656, 10-K)

- Gap: -4.57%; holdings $860.4m (266); filed $901.5m
- **Category:** `custom_tags`
- **Evidence:** NUM has $22.0m of identifier-level fair value the SOI lacks: $22.0m on identifiers absent from the SOI, and $0.0m for 10 SOI holdings with no fair value.
- **Example:** `Investment Debt Investments - 188.7% United States - 188.7% 1st Lien/Senior Secured Debt -`, fair value n/a, SOI rows 117551
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### VARAGON CAPITAL CORP (0001193125-26-114266, 10-K)

- Gap: -6.59%; holdings $793.4m (342); filed $849.4m
- **Category:** `custom_tags`
- **Evidence:** NUM has $70.4m of identifier-level fair value the SOI lacks: $70.4m on identifiers absent from the SOI, and $0.0m for 0 SOI holdings with no fair value.
- **Example:** `Controlled Investments, Industry Investment Funds and Vehicles, Company Senior Direct Lend`, fair value $165.7m, SOI rows 101687
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### LAFAYETTE SQUARE USA, INC. (0001628280-26-020991, 10-K)

- Gap: +6.66%; holdings $841.8m (125); filed $789.2m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $52.6m (+6.7%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Flatworld Intermediate Corporation | First lien senior secured loan 2`, fair value $39.8m, SOI rows 110128
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### COMMONWEALTH CREDIT PARTNERS BDC I, INC. (0001193125-26-104454, 10-K)

- Gap: +1.27%; holdings $656.3m (174); filed $648.1m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $8.2m (+1.3%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Debt Investments, First Lien Senior Secured, AIDC IntermediateCo 2, LLC - Term Loan, Softw`, fair value $27.9m, SOI rows 105723
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### APOLLO ORIGINATION II (UL) CAPITAL TRUST (0001193125-26-104513, 10-K)

- Gap: +82.17%; holdings $1,166.0m (141); filed $640.1m
- **Category:** `totals_counted`
- **Evidence:** A single holding ($526.0m) equals the gap of $526.0m.
- **Example:** `Co-investment`, fair value $526.0m, SOI rows 100394
- **Fix or reason:** None yet: one filing, verify before writing a rule.

### WHITEHORSE FINANCE, INC. (0001104659-26-024735, 10-K)

- Gap: +61.23%; holdings $932.9m (254); filed $578.6m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $354.3m (+61.2%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `WHF STRS Ohio Senior Loan Fund LLC Subordinated Note`, fair value $84.4m, SOI rows 165907;165908
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### BCP INVESTMENT CORP (0001193125-26-093918, 10-K)

- Gap: +18.21%; holdings $592.2m (214); filed $501.0m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +30.8%), but exceed its reported total by $91.2m (+18.2%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Investments in Affiliate Portfolio Companies Joint Ventures Series B-Great Lakes Funding I`, fair value $37.5m, SOI rows 126276
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### PARTNERS GROUP LENDING FUND, LLC (0001398344-26-005654, 10-K)

- Gap: n/a; holdings n/a (0); filed $458.3m
- **Category:** `no_identified_holdings`
- **Evidence:** 386 current SOI rows, none with an identifier.
- **Example:** Rows only on a custom axis (dropped from the SOI) or subtotals.
- **Fix or reason:** None in Part 3: identifiers on a custom axis are not in the SOI.

### STAR MOUNTAIN LOWER MIDDLE-MARKET CAPITAL CORP (0001140361-26-012276, 10-K)

- Gap: +300.00%; holdings $1,500.2m (253); filed $375.0m
- **Category:** `totals_counted`
- **Evidence:** Our holdings are exactly 4.000x the filed total ($375.0m). Holdings and subtotal rows at several levels (industry, investment type, affiliation category) all carry identifiers, and each level sums to the full portfolio, so 4 levels give 4x. For Star Mountain (0001140361-26-012276) the schedule's total ($375.0m) was confirmed by hand, and UJP Acquisition's warrants (SOI rows 162550;162551, 29,787) reappear as the Food Products subtotal (row 110409) and the warrants-category subtotal (row 165467).
- **Example:** `Non-Affiliate Investments`, fair value $312.2m, SOI rows 141475
- **Fix or reason:** Not fixed: these subtotal identifiers share no common word such as 'Total'; separating them needs the schedule's hierarchy, which the SOI does not carry.

### TRIPLEPOINT PRIVATE VENTURE CREDIT INC. (0001792509-26-000003, 10-K)

- Gap: +4.70%; holdings $376.3m (461); filed $359.4m
- **Category:** `totals_counted`
- **Evidence:** A single holding ($16.9m) equals the gap of $16.9m.
- **Example:** `Federated Government Obligations Fund | Non-Affiliated Issuer`, fair value $16.9m, SOI rows 109272
- **Fix or reason:** None yet: one filing, verify before writing a rule.

### OFS CAPITAL CORP (0001487918-26-000021, 10-K)

- Gap: +28.04%; holdings $437.9m (119); filed $342.0m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $95.9m (+28.0%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Pfanstiehl Holdings, Inc. | Common Equity`, fair value $79.4m, SOI rows 150290
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### MONROE CAPITAL CORP (0001512931-26-000011, 10-K)

- Gap: +23.45%; holdings $413.4m (306); filed $334.9m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $78.5m (+23.4%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `MC Asset Management (Corporate), LLC 1 | Senior Secured Loans | Affiliated`, fair value $14.0m, SOI rows 138583
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### GREAT ELM CAPITAL CORP. (0001193125-26-085697, 10-K)

- Gap: +15.94%; holdings $383.9m (102); filed $331.1m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.8%), but exceed its reported total by $52.8m (+15.9%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `CLO Formation JV, LLC Industry Structured Finance Security Common Equity Initial Acquisiti`, fair value $41.4m, SOI rows 100041;100042
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### SILVER CAPITAL HOLDINGS LLC (0001193125-26-088636, 10-K)

- Gap: +43.49%; holdings $472.5m (52); filed $329.3m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $143.2m (+43.5%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Non-Controlled Affiliated Investments Goldman Sachs Financial Square Government Fund`, fair value $139.8m, SOI rows 141925
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### LORD ABBETT PRIVATE CREDIT FUND S (0000930413-26-000842, 10-K)

- Gap: -100.00%; holdings $0.0m (55); filed $318.6m
- **Category:** `custom_tags`
- **Evidence:** We are short by $318.6m; 55 holdings have no SOI fair value and NUM has 0 custom-tag fair value facts.
- **Example:** `Accel International Holdings, Inc. (Revolver) [Member]`, fair value n/a, SOI rows 92537
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### REMORA CAPITAL CORP (0001213900-26-035841, 10-K)

- Gap: +213.84%; holdings $797.1m (149); filed $254.0m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +60.5%), but exceed its reported total by $543.1m (+213.8%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Investments - non-controlled/non-affiliated - First Lien Senior Secured Loan`, fair value $254.0m, SOI rows 119854
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### SURO CAPITAL CORP. (0001493152-26-009641, 10-K)

- Gap: n/a; holdings n/a (0); filed $225.5m
- **Category:** `no_identified_holdings`
- **Evidence:** 117 current SOI rows, none with an identifier.
- **Example:** Rows only on a custom axis (dropped from the SOI) or subtotals.
- **Fix or reason:** None in Part 3: identifiers on a custom axis are not in the SOI.

### BC PARTNERS LENDING CORP (0001193125-26-094381, 10-K)

- Gap: -1.76%; holdings $187.5m (131); filed $190.9m
- **Category:** `custom_tags`
- **Evidence:** We are short by $3.4m; 4 holdings have no SOI fair value and NUM has 44 custom-tag fair value facts.
- **Example:** `Investment in Derivatives - 0.0%, Princeton Medspa Partners LLC, Professional Services, Ma`, fair value n/a, SOI rows 117917
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### INVESTCORP CREDIT MANAGEMENT BDC, INC. (0001193125-26-132860, 10-K)

- Gap: +7.34%; holdings $185.3m (65); filed $172.7m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +6.8%), but exceed its reported total by $12.7m (+7.3%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Non-Controlled/Non-Affiliated Investments, Senior Secured First Lien Debt Investments, Pro`, fair value $10.1m, SOI rows 145944
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### STEELE CREEK CAPITAL CORP (0001213900-26-034052, 10-K)

- Gap: +210.06%; holdings $357.6m (253); filed $115.3m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +29.0%), but exceed its reported total by $242.2m (+210.1%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Non-controlled/Non-Affiliated Investments -215.8% of Shareholder's Equity`, fair value $115.3m, SOI rows 144977
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### PROSPECT FLOATING RATE & ALTERNATIVE INCOME FUND, INC. (0001521945-26-000013, 10-Q)

- Gap: +5.51%; holdings $67.4m (74); filed $63.9m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $3.5m (+5.5%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `Credit Central Loan Company, LLC | Consumer Finance | First Brands Group - First Lien Term`, fair value $4.9m, SOI rows 23642
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### RAND CAPITAL CORP (0001193125-26-133767, 10-K/A)

- Gap: +36.61%; holdings $66.2m (99); filed $48.5m
- **Category:** `other`
- **Evidence:** Our holdings match the filer's own identifier-level NUM facts (difference +0.0%), but exceed its reported total by $17.8m (+36.6%): the filer tags holdings its total does not include, for example a second schedule or joint venture we could not attribute.
- **Example:** `BMP Food Service Supply Holdco, LLC - $6,835,000 Third Amended and Restated Term Note, $4,`, fair value $3.9m, SOI rows 97376;97377
- **Fix or reason:** None: no evidenced rule exists, and a rule only to force a match is not allowed.

### NEXPOINT CAPITAL, INC. (0001193125-26-134282, 10-K)

- Gap: +97.73%; holdings $74.3m (24); filed $37.6m
- **Category:** `totals_counted`
- **Evidence:** A single holding ($36.7m) equals the gap of $36.7m.
- **Example:** `Net Assets`, fair value $36.7m, SOI rows 140809
- **Fix or reason:** None yet: one filing, verify before writing a rule.

### MUZINICH BDC, INC. (0001213900-26-035730, 10-K)

- Gap: +2509.61%; holdings $641.4m (55); filed $24.6m
- **Category:** `other`
- **Evidence:** Our holdings are 26.1x the filed fact ($24.6m), and match the filer's own identifier-level NUM facts: the undimensioned fact is not the portfolio total.
- **Example:** `Investments`, fair value $217.3m, SOI rows 129826
- **Fix or reason:** None possible from the data set: the filing's total is not tagged as expected.

### PRINCETON CAPITAL CORP (0001213900-26-036469, 10-K)

- Gap: -14.54%; holdings $12.2m (31); filed $14.3m
- **Category:** `custom_tags`
- **Evidence:** We are short by $2.1m; 26 holdings have no SOI fair value and NUM has 0 custom-tag fair value facts.
- **Example:** `Control investments - Advantis Certified Staffing Solutions, Inc. - Common Stock - Series `, fair value n/a, SOI rows 101544;101545
- **Fix or reason:** Not fixed: recovering custom-tag values from NUM is the stretch goal.

### KAYNE DL 2021, INC. (0001213900-26-022449, 10-K)

- Gap: +7408.06%; holdings $386.7m (227); filed $5.2m
- **Category:** `custom_tags`
- **Evidence:** NUM has $38.7m of identifier-level fair value the SOI lacks: $38.7m on identifiers absent from the SOI, and $0.0m for 41 SOI holdings with no fair value.
- **Example:** `Building products-Ruff Roofers Buyer, LLC-First lien senior secured delayed draw loan-SOFR`, fair value n/a, SOI rows 98032
- **Fix or reason:** Not fixed: recovering these values from NUM is the stretch goal.

### KAYNE ANDERSON BDC, INC. (0001213900-26-022392, 10-K)

- Gap: n/a; holdings $2,691.2m (293); filed n/a
- **Category:** `no_filed_total`
- **Evidence:** NUM has no undimensioned InvestmentOwnedAtFairValue fact at the period end.
- **Example:** 293 holdings parsed, nothing to reconcile against.
- **Fix or reason:** None possible: the filer reports no total under the standard tag.

### OXFORD SQUARE CAPITAL CORP. (0001213900-26-024280, 10-K)

- Gap: n/a; holdings $1,188.8m (73); filed n/a
- **Category:** `no_filed_total`
- **Evidence:** NUM has no undimensioned InvestmentOwnedAtFairValue fact at the period end.
- **Example:** 73 holdings parsed, nothing to reconcile against.
- **Fix or reason:** None possible: the filer reports no total under the standard tag.

### PHENIXFIN CORP (0001213900-26-013689, 10-Q)

- Gap: n/a; holdings $1,006.6m (96); filed n/a
- **Category:** `no_filed_total`
- **Evidence:** NUM has no undimensioned InvestmentOwnedAtFairValue fact at the period end.
- **Example:** 96 holdings parsed, nothing to reconcile against.
- **Fix or reason:** None possible: the filer reports no total under the standard tag.

### FIRST EAGLE PRIVATE CREDIT FUND (0001193125-26-108556, 10-K)

- Gap: n/a; holdings $567.1m (199); filed n/a
- **Category:** `no_filed_total`
- **Evidence:** NUM has no undimensioned InvestmentOwnedAtFairValue fact at the period end.
- **Example:** 199 holdings parsed, nothing to reconcile against.
- **Fix or reason:** None possible: the filer reports no total under the standard tag.

### MUZINICH CORPORATE LENDING INCOME FUND, INC. (0001213900-26-035737, 10-K)

- Gap: n/a; holdings $514.2m (103); filed n/a
- **Category:** `no_filed_total`
- **Evidence:** NUM has no undimensioned InvestmentOwnedAtFairValue fact at the period end.
- **Example:** 103 holdings parsed, nothing to reconcile against.
- **Fix or reason:** None possible: the filer reports no total under the standard tag.

### SCP PRIVATE CREDIT INCOME BDC LLC (0001193125-26-066960, 10-K)

- Gap: n/a; holdings $184.5m (23); filed n/a
- **Category:** `no_filed_total`
- **Evidence:** NUM has no undimensioned InvestmentOwnedAtFairValue fact at the period end.
- **Example:** 23 holdings parsed, nothing to reconcile against.
- **Fix or reason:** None possible: the filer reports no total under the standard tag.

### SLR HC BDC LLC (0001193125-26-066954, 10-K)

- Gap: n/a; holdings $85.8m (35); filed n/a
- **Category:** `no_filed_total`
- **Evidence:** NUM has no undimensioned InvestmentOwnedAtFairValue fact at the period end.
- **Example:** 35 holdings parsed, nothing to reconcile against.
- **Fix or reason:** None possible: the filer reports no total under the standard tag.
