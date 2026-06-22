cls
**=====================================================
** Program Name: Compute NTL per capita
** Author: Carlos Mendez
** Date: 2022-04-26
** --------------------------------------------------------------------------------------------
** Inputs/Ouputs:
* Data files used:
                 * ../data/NTL_trends.dta
                 * ../data/Population_trends.dta

* Data files created as intermediate product:

* Data files created as final product:

**=====================================================

** 0. Change working directory
cd "/Users/carlosmendez/Documents/GitHub/project2021o/c00-transform_data"

** 1. Setup
clear all
macro drop _all
capture log close
set more off
version 15

** 2. Open log file
log using "060_compute_NTL_pc.txt", text replace

** 3. Install modules
*ssc install estout, replace all
*ssc install outreg2, replace all
*ssc install reghdfe, replace all * INFO: http://scorreia.com/software/reghdfe/
*net install gr0009_1, from (http://www.stata-journal.com/software/sj10-1) replace all
*net install tsg_schemes, from("https://raw.githubusercontent.com/asjadnaqvi/Stata-schemes/main/schemes/") replace all
*set scheme white_tableau, permanently
*set scheme gg_tableau, permanently


** 4. Import data
use "../data/Population_trends.dta", clear

describe
summarize

** Select observations from 2012-2020
keep if year > 2011

** Merge with NTL dataset
sort asdf_id year
merge 1:1 asdf_id year using "../data/NTL_trends.dta"
drop _merge

** Rescale NTL by 100,000,000 to be able to compute log (NTL/pop)
gen NTL     = 100000000*ntl
gen t6NTL   = 100000000*tr6_ntl
gen t100NTL = 100000000*tr100_ntl
gen t400NTL = 100000000*tr400_ntl

label variable     NTL "NTL (Sum of NTL) rescaled by 100,000,000"
label variable   t6NTL "Trend of NTL (HP 6.25)"
label variable t100NTL "Trend of NTL (HP 100)"
label variable t400NTL "Trend of NTL (HP 400)"

** Compute log of NTL/POP
gen ln_NTLpc = ln(NTL/pop)
gen ln_t6NTLpc = ln(t6NTL/tr6_pop) 
gen ln_t100NTLpc = ln(t100NTL/tr100_pop) 
gen ln_t400NTLpc = ln(t400NTL/tr400_pop)

label variable ln_NTLpc      "Log sum of lights per capita"
label variable ln_t6NTLpc    "Log sum of lights per capita (Trend HP 6.25)"
label variable ln_t100NTLpc  "Log sum of lights per capita (Trend HP 100)"
label variable ln_t400NTLpc  "Log sum of lights per capita (Trend HP 400)"

des ln_NTLpc ln_t6NTLpc ln_t100NTLpc ln_t400NTLpc
sum ln_NTLpc ln_t6NTLpc ln_t100NTLpc ln_t400NTLpc

** Save long-form panel dataset
save             "../data/lnNTLpc.dta", replace
export delimited "../data/lnNTLpc.csv", replace

** Save wide-form panel dataset
keep asdf_id shapeName year ln_NTLpc ln_t6NTLpc ln_t100NTLpc ln_t400NTLpc
reshape wide ln_NTLpc ln_t6NTLpc ln_t100NTLpc ln_t400NTLpc, i(asdf_id shapeName)  j(year)  
order _all, alphabetic
order shapeName, after(asdf_id)
save             "../data/lnNTLpc_trends-wide.dta", replace
export delimited "../data/lnNTLpc_trends-wide.csv", replace



** 99. Close log file
log close

**====================END==============================
 