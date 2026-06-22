cls
**=====================================================
** Program Name: Create regional indentifiers dataset
** Author: Carlos Mendez
** Date: 2022-04-04
** --------------------------------------------------------------------------------------------
** Inputs/Ouputs:
* Data files used: ../data/rawData/bd_atlasmunicipalodsbolivia2020_Stata15_full.dta

* Data files created as intermediate product:

* Data files created as final product: ../data/regional_indentifiers

**=====================================================

** 0. Change working directory
*cd "/Users/carlos/Github/QuaRCS-lab/project2021o/c00-transform_data"
cd "/Users/carlosmendez/Documents/GitHub/project2021o/c00-transform_data"

** 1. Setup
clear all
macro drop _all
capture log close
set more off
version 15

** 2. Open log file
log using "020_create_regional_identifiers_dataset.txt", text replace

** 3. Install modules
*ssc install estout, replace all
*ssc install outreg2, replace all
*ssc install reghdfe, replace all * INFO: http://scorreia.com/software/reghdfe/
*net install gr0009_1, from (http://www.stata-journal.com/software/sj10-1) replace all
*net install tsg_schemes, from("https://raw.githubusercontent.com/asjadnaqvi/Stata-schemes/main/schemes/") replace all
*set scheme white_tableau, permanently
*set scheme gg_tableau, permanently


** 4. Import data
use "../data/rawData/bd_atlasmunicipalodsbolivia2020_Stata15_full.dta", clear
sort poly_id

** Select variables
keep id municipio dep depmun poly_id asdf_id

** Rename and label variables
rename id mun_id
label variable mun_id "Municipality ID"

rename municipio mun
label variable mun "Municipality"

label variable dep "Department"
egen dep_id = group(dep)
label variable dep_id "Department ID"

rename depmun dep_mun
label variable dep_mun "Department-municipality"

label variable poly_id "Polygon ID"
label variable asdf_id "ASDF ID"

** Order variables
order poly_id, first
order asdf_id, after(poly_id)
order dep_id, after(dep)
order mun_id, after(mun)

list poly_id asdf_id mun dep

** Merge with dataset: shapeID
merge 1:1 asdf_id using "../data/shapeID.dta"
drop _merge

** X. Save dataset
save             "../data/regional_identifiers.dta", replace
export delimited "../data/regional_identifiers.csv", replace

** 99. Close log file
log close

**====================END==============================
 