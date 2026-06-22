cls
**=====================================================
** Program Name: Clean data and estimate population trends
** Author: Carlos Mendez
** Date: 2022-04-04
** --------------------------------------------------------------------------------------------
** Inputs/Ouputs:
* Data files used:  ../data/rawData/CO2/CO2.csv

* Data files created as intermediate product:

* Data files created as final product: ../data/CO2_trends.dta

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
log using "050_clean_and_estimate_CO2_trends.txt", text replace

** 3. Install modules
*ssc install estout, replace all
*ssc install outreg2, replace all
*ssc install reghdfe, replace all * INFO: http://scorreia.com/software/reghdfe/
*net install gr0009_1, from (http://www.stata-journal.com/software/sj10-1) replace all
*net install tsg_schemes, from("https://raw.githubusercontent.com/asjadnaqvi/Stata-schemes/main/schemes/") replace all
*set scheme white_tableau, permanently
*set scheme gg_tableau, permanently

** 4. Import data
import delimited "../data/rawData/CO2/CO2.csv", case(preserve) clear

describe
summarize

** Drop unnecesary variables
drop Level gqid id shapeGroup shapeType
describe
sum

** Raname variables
rename oco2_v10r_xco2_yearly2015mean co2015
rename oco2_v10r_xco2_yearly2017mean co2017
rename oco2_v10r_xco2_yearly2019mean co2019
rename oco2_v10r_xco2_yearly2020mean co2020
rename oco2_v10r_xco2_yearly2018mean co2018
rename oco2_v10r_xco2_yearly2016mean co2016

** Order variables
order co2016, after(co2015)
order co2018, after(co2017)
order shapeName, after(asdf_id)
order shapeID, after(shapeName)
des
sum


** Reshape data from wide to long
reshape long co, i(asdf_id shapeName shapeID) j(year)

** Compute long-run trends: HP filter with parameters 6.25, 100, 400
gen ln_co = ln(co)

xtset asdf_id year
pfilter ln_co, method(hp) trend(tr6_ln_y)   smooth(6.25)
pfilter ln_co, method(hp) trend(tr100_ln_y) smooth(100)
pfilter ln_co, method(hp) trend(tr400_ln_y) smooth(400)


** Re-express NTL in its original scale
gen   tr6_co = exp(tr6_ln_y)
gen tr100_co = exp(tr100_ln_y)
gen tr400_co = exp(tr400_ln_y)

** Label variables
label variable shapeName "Municipality name"
label variable shapeID   "Municipality Geoquery Polygon ID"

label variable co "Carbon dioxide (average concentration)"
notes co: The average concentration of carbon dioxide in a column of dry air extending from Earth's surface to the top of the atmosphere. The raster used is the result of aggregating one year of data to a 10km grid and then using a linear interpolation to fill gaps. The underlying data were produced by NASA's OCO-2 project, and obtained from the OCO-2 data archive maintained at the NASA Goddard Earth Science Data and Information Services Center.  >>>Download link: http://geo.aiddata.org/query/#!/status/624f0a2423ecef1a9a52c4a2

label variable tr6_co "Trend of CO2 concentration (HP 6.25)"
notes tr6_co: The trend is based on the HP filter with a smoothing parameter of 6.25
label variable tr100_co "Trend of CO2 concentration (HP 100)"
notes tr100_co: The trend is based on the HP filter with a smoothing parameter of 100
label variable tr400_co "Trend of CO2 concentration (HP 400)"
notes tr400_co: The trend is based on the HP filter with a smoothing parameter of 400

** Verify similarity with the original series
reg co tr6_co, robust
reg co tr100_co, robust
reg co tr400_co, robust

tw (sc co tr6_co)   (lfit co tr6_co),   name(fig1, replace)
tw (sc co tr100_co) (lfit co tr100_co), name(fig2, replace)
tw (sc co tr400_co) (lfit co tr400_co), name(fig3, replace)

tsline tr6_co co if asdf_id == 91, name(fig4, replace)
*tsline tr6_co co if asdf_id == 93, name(fig5, replace)
*tsline tr6_co co if asdf_id == 109, name(fig6, replace)
*tsline tr6_co co if asdf_id == 217, name(fig7, replace)
*tsline tr6_co co if asdf_id == 218, name(fig8, replace)
*tsline tr6_co co if asdf_id == 225, name(fig9, replace)
*tsline tr6_co co if asdf_id == 228, name(fig10, replace)
*tsline tr6_co co if asdf_id == 218, name(fig11, replace)
*tsline tr6_co co if asdf_id == 160, name(ElAlto, replace)
*
*tsline tr400_co co if asdf_id == 91, name(ffig4, replace)
*tsline tr400_co co if asdf_id == 93, name(ffig5, replace)
*tsline tr400_co co if asdf_id == 109, name(ffig6, replace)
*tsline tr400_co co if asdf_id == 217, name(ffig7, replace)
*tsline tr400_co co if asdf_id == 218, name(ffig8, replace)
*tsline tr400_co co if asdf_id == 225, name(ffig9, replace)
*tsline tr400_co co if asdf_id == 228, name(ffig10, replace)
*tsline tr400_co co if asdf_id == 218, name(ffig11, replace)
*tsline tr400_co co if asdf_id == 160, name(fElAlto, replace)



** Drop unnecesary variables
drop tr6_ln_y tr100_ln_y tr400_ln_y ln_co 

describe
sum

** Save long-form panel dataset
save             "../data/CO2_trends.dta", replace
export delimited "../data/CO2_trends.csv", replace

** Save wide-form panel dataset
reshape wide co tr6_co tr100_co tr400_co, i(asdf_id shapeName)  j(year)  
order _all, alphabetic
order shapeName, after(asdf_id)
save             "../data/CO2_trends-wide.dta", replace
export delimited "../data/CO2_trends-wide.csv", replace
drop shapeID
** 99. Close log file
log close

**====================END==============================
 