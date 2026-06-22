cls
* 1. Make sure your data is loaded
use GeoDS4Bolivia_v20250512.dta, clear

* 2. Set up a postfile to collect variable info
tempfile meta
postfile handle str32 varname str12 vartype str32 varformat str80 varlabel using `meta'

* 3. Loop through variables and collect info
ds
foreach v of varlist `r(varlist)' {
    local type : type `v'
    local format : format `v'
    local label : variable label `v'
    post handle ("`v'") ("`type'") ("`format'") ("`label'")
}

postclose handle

* 4. Use the collected data and export to CSV
use `meta', clear
drop vartype varformat

export delimited using "Definitions_GeoDS4Bolivia_v20250512.csv", replace
