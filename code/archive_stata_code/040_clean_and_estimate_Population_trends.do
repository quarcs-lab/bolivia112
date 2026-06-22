cls
**=====================================================
** Program Name: Clean data and estimate population trends
** Author: Carlos Mendez
** Date: 2022-04-04
** --------------------------------------------------------------------------------------------
** Inputs/Ouputs:
* Data files used:  ../data/rawData/Pop/622081a016cfcc2a7a4e3ab2_results.csv

* Data files created as intermediate product:

* Data files created as final product: ../data/POP_trends.dta

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
log using "040_clean_and_estimate_Population_trends.txt", text replace

** 3. Install modules
*ssc install estout, replace all
*ssc install outreg2, replace all
*ssc install reghdfe, replace all * INFO: http://scorreia.com/software/reghdfe/
*net install gr0009_1, from (http://www.stata-journal.com/software/sj10-1) replace all
*net install tsg_schemes, from("https://raw.githubusercontent.com/asjadnaqvi/Stata-schemes/main/schemes/") replace all
*set scheme white_tableau, permanently
*set scheme gg_tableau, permanently

** 4. Import data
import delimited "../data/rawData/Pop/622081a016cfcc2a7a4e3ab2_results.csv", case(preserve) clear

describe
summarize

** Drop unnecesary variables
drop worldpop_pop_count_1km_mosaic200 v4 v6 v8 v10 v12 v14 v16 v18 v20 worldpop_pop_count_1km_mosaic201 v24 v26 v28 v30 v32 v34 v36 v38 v40 worldpop_pop_count_1km_mosaic202 Level gqid id shapeType shapeGroup
describe
sum

** Raname variables
rename v3 pop2000
rename v5 pop2001
rename v7 pop2003
rename v9 pop2002
rename v11 pop2005
rename v13 pop2004
rename v15 pop2006
rename v17 pop2008
rename v19 pop2007
rename v21 pop2009
rename v23 pop2010
rename v25 pop2011
rename v27 pop2012
rename v29 pop2013
rename v31 pop2014
rename v33 pop2015
rename v35 pop2016
rename v37 pop2017
rename v39 pop2018
rename v41 pop2019
rename v43 pop2020

** Order variables
order pop2002, after(pop2001)
order pop2004, after(pop2003)
order pop2007, after(pop2006)
order shapeName, after(asdf_id)
des
sum

** Remove inf in string variables
ds pop*, has(type string)  
foreach v in `r(varlist)' {
      replace `v' = "" if `v' == "inf"
}

** Convert string variables to numeric
destring , replace
describe
sum

** Drop observations for the year 2000 as they contain huge outliers
drop pop2000 

** Reshape data from wide to long
reshape long pop, i(asdf_id shapeName shapeID) j(year)

** Linear interpolation of missing values
xtset asdf_id year
gen ln_pop = ln(pop) // multiply by 1 million to avoid negative numbers

ipolate ln_pop year, gen(ln_pop_ip) epolate by (asdf_id)

des
sum


** Compute long-run trends: HP filter with parameters 6.25, 100, 400
pfilter ln_pop_ip, method(hp) trend(tr6_ln_y)   smooth(6.25)
pfilter ln_pop_ip, method(hp) trend(tr100_ln_y) smooth(100)
pfilter ln_pop_ip, method(hp) trend(tr400_ln_y) smooth(400)

** Re-express NTL in its original scale
gen   tr6_pop = exp(tr6_ln_y)
gen tr100_pop = exp(tr100_ln_y)
gen tr400_pop = exp(tr400_ln_y)

** Label variables
label variable shapeName "Municipality name"
label variable shapeID   "Municipality Geoquery Polygon ID"

label variable pop "Estimated population count"
notes pop: Estimated population count from WorldPop. Underlying dataset provides number of people per 1km pixel. The mapping approach is Random Forest-based dasymetric redistribution  >>>Download link: http://geo.aiddata.org/query/#!/status/622081a016cfcc2a7a4e3ab2

label variable tr6_pop "Trend of population (HP 6.25)"
notes tr6_pop: The trend is based on the HP filter with a smoothing parameter of 6.25
label variable tr100_pop "Trend of population (HP 100)"
notes tr100_pop: The trend is based on the HP filter with a smoothing parameter of 100
label variable tr400_pop "Trend of population (HP 400)"
notes tr400_pop: The trend is based on the HP filter with a smoothing parameter of 400


** Verify similarity with the original series
reg pop tr6_pop, robust
reg pop tr100_pop, robust
reg pop tr400_pop, robust

tw (sc pop tr6_pop)   (lfit pop tr6_pop),   name(fig1, replace)
tw (sc pop tr100_pop) (lfit pop tr100_pop), name(fig2, replace)
tw (sc pop tr400_pop) (lfit pop tr400_pop), name(fig3, replace)

tsline tr6_pop pop if asdf_id == 91, name(fig4, replace)
tsline tr6_pop pop if asdf_id == 93, name(fig5, replace)
tsline tr6_pop pop if asdf_id == 109, name(fig6, replace)
tsline tr6_pop pop if asdf_id == 217, name(fig7, replace)
tsline tr6_pop pop if asdf_id == 218, name(fig8, replace)
tsline tr6_pop pop if asdf_id == 225, name(fig9, replace)
tsline tr6_pop pop if asdf_id == 228, name(fig10, replace)
tsline tr6_pop pop if asdf_id == 218, name(fig11, replace)
tsline tr6_pop pop if asdf_id == 160, name(ElAlto, replace)

tsline tr400_pop pop if asdf_id == 91, name(ffig4, replace)
tsline tr400_pop pop if asdf_id == 93, name(ffig5, replace)
tsline tr400_pop pop if asdf_id == 109, name(ffig6, replace)
tsline tr400_pop pop if asdf_id == 217, name(ffig7, replace)
tsline tr400_pop pop if asdf_id == 218, name(ffig8, replace)
tsline tr400_pop pop if asdf_id == 225, name(ffig9, replace)
tsline tr400_pop pop if asdf_id == 228, name(ffig10, replace)
tsline tr400_pop pop if asdf_id == 218, name(ffig11, replace)
tsline tr400_pop pop if asdf_id == 160, name(fElAlto, replace)


** Drop unnecesary variables
drop tr6_ln_y tr100_ln_y tr400_ln_y ln_pop ln_pop_ip

describe
sum



** Save long-form panel dataset
save             "../data/Population_trends.dta", replace
export delimited "../data/Population_trends.csv", replace


** Save wide-form panel dataset
reshape wide pop tr6_pop tr100_pop tr400_pop, i(asdf_id shapeName)  j(year)  
order _all, alphabetic
order shapeName, after(asdf_id)
drop shapeID
save             "../data/Population_trends-wide.dta", replace
export delimited "../data/Population_trends-wide.csv", replace


** 99. Close log file
log close

**====================END==============================
 