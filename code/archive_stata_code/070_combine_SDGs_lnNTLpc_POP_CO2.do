cls
**=====================================================
** Program Name: Combine datasets to build GeoDS4Bolivia dataset
** Author: Carlos Mendez
** Date: 2022-04-27
** --------------------------------------------------------------------------------------------
** Inputs/Ouputs:
* Data files used:
                    * ../data/regional_identifiers.dta
                    * ../data/SDGs.dta
                    * ../data/Population_trends-wide.dta
                    * ../data/lnNTLpc_trends-wide.dta
                    * ../data/CO2_trends-wide.dta


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
log using "070_combine_SDGs_lnNTLpc_POP_CO2.txt", text replace

** 3. Install modules
*ssc install estout, replace all
*ssc install outreg2, replace all
*ssc install reghdfe, replace all * INFO: http://scorreia.com/software/reghdfe/
*net install gr0009_1, from (http://www.stata-journal.com/software/sj10-1) replace all
*net install tsg_schemes, from("https://raw.githubusercontent.com/asjadnaqvi/Stata-schemes/main/schemes/") replace all
*set scheme white_tableau, permanently
*set scheme gg_tableau, permanently


** 4. Import data
use  "../data/regional_identifiers.dta", clear

describe
summarize

** Merge with SDGs database
sort asdf_id
merge 1:1 asdf_id using "../data/SDGs.dta"
drop _merge

** Merge with Population database
merge 1:1 asdf_id using "../data/Population_trends-wide.dta"
drop _merge

** Merge with NTL database
merge 1:1 asdf_id using "../data/lnNTLpc_trends-wide.dta"
drop _merge

** Merge with CO2 database
merge 1:1 asdf_id using "../data/CO2_trends-wide.dta"
drop _merge


** X. Save dataset
save             "../data/GeoDS4Bolivia_allVariables.dta", replace
export delimited "../data/GeoDS4Bolivia_allVariables.csv", replace

** 99. Close log file
log close

**====================END==============================
 