cls
**=====================================================
** Program Name: Clean data and estimate nighttime lights (NTL) trends
** Author: Carlos Mendez
** Date: 2022-04-04
** --------------------------------------------------------------------------------------------
** Inputs/Ouputs:
* Data files used:  ../data/rawData/NTL/61556172109a8645cf7aca33_results.csv

* Data files created as intermediate product:

* Data files created as final product: ../data/NTL_trends.dta

**=====================================================

** 0. Change working directory
* cd " "

** 1. Setup
clear all
macro drop _all
capture log close
set more off
version 15

** 2. Open log file
log using "030_clean_and_estimate_NTL_trends.txt", text replace

** 3. Install modules
*ssc install estout, replace all
*ssc install outreg2, replace all
*ssc install reghdfe, replace all * INFO: http://scorreia.com/software/reghdfe/
*net install gr0009_1, from (http://www.stata-journal.com/software/sj10-1) replace all
*net install tsg_schemes, from("https://raw.githubusercontent.com/asjadnaqvi/Stata-schemes/main/schemes/") replace all
*set scheme white_tableau, permanently
*set scheme gg_tableau, permanently

** 4. Import data
import delimited "../data/rawData/NTL/61556172109a8645cf7aca33_results.csv", case(preserve) clear

describe
summarize

** Rename variables
rename viirs_ntl_annual_v20_avg_masked2 ntl2019
rename v3 ntl2014
rename v4 ntl2012
rename v5 ntl2016
rename v6 ntl2015
rename v7 ntl2013
rename v8 ntl2017
rename v9 ntl2020
rename v10 ntl2018

** Order variables
order ntl2012, after(asdf_id)
order ntl2013, after(ntl2012)
order ntl2014, after(ntl2013)
order ntl2015, after(ntl2014)
order ntl2016, after(ntl2015)
order ntl2017, after(ntl2016)
order ntl2018, after(ntl2017)
order ntl2019, after(ntl2018)
order ntl2020, after(ntl2019)
order shapeName, after(asdf_id)

** Keep relevant variables
keep asdf_id shapeName ntl2012-ntl2020

describe
sum


** Remove NAs in string variables
ds ntl*, has(type string)  
foreach v in `r(varlist)' {
      replace `v' = "" if `v' == "NA"
}

** Convert string variables to numeric
destring , replace
describe
sum

** Replace 0 values as missing
foreach v of varlist ntl* {
replace `v' = . if `v' == 0
}

sum

** Reshape data from wide to long
reshape long ntl, i(asdf_id shapeName) j(year)


** Linear interpolation of missing values
xtset asdf_id year
gen ln_1000000ntl = ln(1000000*ntl) // multiply by 1 million to avoid negative numbers

ipolate ln_1000000ntl year, gen(ln_1000000ntl_ip) epolate by (asdf_id)
sum

** Predict the missing values
xtreg ln_1000000ntl_ip year, fe
predict ln_1000000ntl_ip_pr
label variable ln_1000000ntl_ip_pr "Predicted ln_1000000ntl_ip on year"
sum

** Replace the remaining missing values with the prediction
gen ln_1000000ntl_ip2 = ln_1000000ntl_ip
replace ln_1000000ntl_ip2 = ln_1000000ntl_ip_pr if ln_1000000ntl_ip == .
sum

** Compute long-run trends: HP filter with parameters 6.25, 100, 400
pfilter ln_1000000ntl_ip2, method(hp) trend(tr6_ln_y)   smooth(6.25)
pfilter ln_1000000ntl_ip2, method(hp) trend(tr100_ln_y) smooth(100)
pfilter ln_1000000ntl_ip2, method(hp) trend(tr400_ln_y) smooth(400)

** Re-express NTL in its original scale
gen tr6_ntl = (exp(tr6_ln_y))/1000000
gen tr100_ntl = (exp(tr100_ln_y))/1000000
gen tr400_ntl = (exp(tr400_ln_y))/1000000

** Label variables
label variable shapeName "Municipality name"
label variable ntl "NTL (Sum of nighttime lights)"
notes ntl: viirs_ntl_annual_v20_avg_masked_sum  >>> Annual VIIRS nighttime lights product Version 2. Average value with background pixels masked.  >>>Download link: geo.aiddata.org/query/#!/status/61556172109a8645cf7aca33 
label variable ln_1000000ntl "Log (1million * NTL)"
label variable ln_1000000ntl_ip "Interpolation of Log (1million * NTL) on year"
label variable ln_1000000ntl_ip_pr "Prediction of  iterpolated Log (1million * NTL) on year"
label variable ln_1000000ntl_ip2 "Interpolation of Log (1million * NTL) on year"
notes ln_1000000ntl_ip2: There were missing values even after interpolation. Predicted values were used to fill in these missing values
label variable tr6_ntl "Trend of NTL (HP 6.25)"
notes tr6_ntl: The trend is based on the HP filter with a smoothing parameter of 6.25
label variable tr100_ntl "Trend of NTL (HP 100)"
notes tr100_ntl: The trend is based on the HP filter with a smoothing parameter of 100
label variable tr400_ntl "Trend of NTL (HP 400)"
notes tr400_ntl: The trend is based on the HP filter with a smoothing parameter of 400


** Verify similarity with the original series
reg ntl tr6_ntl, robust
reg ntl tr100_ntl, robust
reg ntl tr400_ntl, robust

tw (sc ntl tr6_ntl) (lfit ntl tr6_ntl), name(fig1, replace)
tw (sc ntl tr100_ntl) (lfit ntl tr100_ntl), name(fig2, replace)
tw (sc ntl tr400_ntl) (lfit ntl tr400_ntl), name(fig3, replace)

tsline tr6_ntl ntl if asdf_id == 91, name(fig4, replace)
tsline tr6_ntl ntl if asdf_id == 93, name(fig5, replace)
tsline tr6_ntl ntl if asdf_id == 109, name(fig6, replace)
tsline tr6_ntl ntl if asdf_id == 217, name(fig7, replace)
tsline tr6_ntl ntl if asdf_id == 218, name(fig8, replace)
tsline tr6_ntl ntl if asdf_id == 225, name(fig9, replace)
tsline tr6_ntl ntl if asdf_id == 228, name(fig10, replace)
tsline tr6_ntl ntl if asdf_id == 218, name(fig11, replace)
tsline tr6_ntl ntl if asdf_id == 160, name(ElAlto, replace)


** Drop unnecesary variables
drop ln_1000000ntl ln_1000000ntl_ip ln_1000000ntl_ip_pr ln_1000000ntl_ip2 tr6_ln_y tr100_ln_y tr400_ln_y

describe
sum

** Save long-form panel dataset
save             "../data/NTL_trends.dta", replace
export delimited "../data/NTL_trends.csv", replace

** Save wide-form panel dataset
reshape wide ntl tr6_ntl tr100_ntl tr400_ntl, i(asdf_id shapeName)  j(year)  
order _all, alphabetic
order shapeName, after(asdf_id)
save             "../data/NTL_trends-wide.dta", replace
export delimited "../data/NTL_trends-wide.csv", replace

** 99. Close log file
log close

**====================END==============================
 