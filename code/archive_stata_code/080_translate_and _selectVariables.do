** Setup
cls
clear all
macro drop _all
capture log close

set more off
version 15

** Change working directory
global suser = c(username)
    * at work
if(inlist("$suser", "carlosmendez")){
cd "/Users/carlosmendez/Documents/GitHub/project2021o/c00-transform_data"
}
    * at home
if(inlist("$suser", "carlos")){
cd "/Users/carlos/Github/QuaRCS-lab/project2021o/c00-transform_data"
}
    * windows collaborator
if(inlist("$suser", "satya")){
cd "D:\GitHub\project2021o/c00-transform_data"
}

log using "080_translate_and_add_labels_to_static_variables.txt", text replace
**=====================================================
** Program Name: Translate and add labels to static variables
** Author: Carlos Mendez
** Date: 21-Aug-2022
** --------------------------------------------------------------------------------------------
** Inputs/Ouputs:
* Data files used:
                    * ../data/GeoDS4Bolivia_allVariables.dta

* Data files created as final product:

                    * ../data/GeoDS4Bolivia

**=====================================================


**  Import data
use  "../data/GeoDS4Bolivia_allVariables.dta", clear

describe
summarize


** Translate labels and rename variables of the SDG database

*Change variables labels
label variable imds             "Municipal Sustainable Development Index"
label variable rank_imds        "Bolivia Index Ranking"
label variable poblacion_2020   "Population 2020"
label variable urbano_2012      "Urbanization rate, 2012 (% of population)"

label variable sdg1_1_ee        "Extreme energy poverty rate, 2016 (% of houses)"
label variable sdg1_1_nbi       "Unsatisfied basic needs, 2012 (% of population)"
label variable sdg1_2_pm        "Multidimensional poverty index, 2012"
label variable sdg1_4_ssb       "Access to the 3 basic services, 2012 (% of households)"

label variable sdg2_2_dm        "Chronic malnutrition in children (< 5 years), 2016 (%)"
label variable sdg2_2_smu       "Obesity in women (15-49 years), 2016 (%)"
label variable sdg2_4_su        "Average area per Production Unit Agriculture and Livestock, 2013 (ha)"
label variable sdg2_4_t         "Tractor density, 2013 (per 1,000 UPAs)"

label variable sdg3_1_p         "Institutional childbirth coverage, average 2008-2012 (%)"
label variable sdg3_2_mi        "Infant mortality rate (< 1 year), 2016 (per. 1,000 live births)"
label variable sdg3_2_mn        "Children mortality rate in (< 5 years), 2016 (per. 1,000 live births)"
label variable sdg3_3_c         "Chagas disease infestation rate, 2017 (% of households)"
label variable sdg3_3_d         "Dengue incidence, 2018 (per 10,000 population)"
label variable sdg3_3_m         "Malaria incidence, average 2014-17 (per 1,000 population)"
label variable sdg3_3_t         "Tuberculosis incidence, 2017 (per 100,000 population)"
label variable sdg3_3_vih       "HIV incidence, average 2014-17 (per 1,000,00 population)"
label variable sdg3_7_fa        "Adolescent fertility rate (15-19 years), 2012 (births per 1,000 women)"

label variable sdg4_1_ash       "Secondary school dropout rate, male, 2017 (% of enrolled)"
label variable sdg4_1_asm       "Secondary school dropout rate, females, 2017 (% of enrolled)"
label variable sdg4_4_es        "Population with higher education (>= 19 years), 2012 (%)"
label variable sdg4_6_alfab     "Literacy rate for (>= 15 years), 2012 (%)"
label variable sdg4_c_pci       "Qualified teachers at the initial level, 2016 (%)"
label variable sdg4_c_pcs       "Qualified teachers at the secondary level, 2016"

label variable sdg5_1_paes      "Gender parity in school dropouts in  secondary school, 2017"
label variable sdg5_1_pej       "Gender parity in years of education of young people (25-35 years old), 2012. (25-35 years), 2012"
label variable sdg5_1_ppm       "Gender Parity in the Multidimensional Poverty Index, 2012"
label variable sdg5_5_pp        "Gender parity in the overall participation rate (>=10 years), 2012"

label variable sdg6_1_ca        "Drinking water coverage, 2017 (% of population)"
label variable sdg6_2_cs        "Sanitation coverage, 2017 (% of population)"
label variable sdg6_3_tar       "Wastewater treatment, 2017 (% of wastewater) wastewater)"

label variable sdg7_1_cee       "Electricity coverage, 2012 (% of population) population)"
label variable sdg7_1_cep       "Residential electricity consumption per capita, 2016 (kWh/person/year)"
label variable sdg7_1_elc       "Clean cooking energy, 2012 (% of households)"
label variable sdg7_3_ecep      "CO2 emissions per capita by energy, 2016. (tCO2/person/year)"

label variable sdg8_4_mcc       "Residential electric meters with zero consumption, 2016 (%)"
label variable sdg8_5_ph        "Overall participation rate males (>= 10 years), 2012 (%)"
label variable sdg8_5_pm        "Overall female participation rate (>= 10 years), 2012 (%)"
label variable sdg8_6_hnn       "Men who do not study or participate in the labor market (15-24 years), 2012 (%)"
label variable sdg8_6_mnn       "Women who do not study or participate in the labor market (15-24 years),2012 (%),2012 (%)"
label variable sdg8_10_b        "Density of bank branches, 2018 (per 100,000 inhabitants)"
label variable sdg8_11_mm       "Index of the degree of intermediation in migration, 2012"

label variable sdg9_1_rutas     "Number of railways/primary roads entering/leaving the municipality, 2019"
label variable sdg9_5_c         "Kuaa computers delivered, 2016 (per 100 school-age population, 6-19 years)"
label variable sdg9_5_pt        "Educational units with technological floors, 2016 (%)"
label variable sdg9_c_crdm      "Fixed and mobile network coverage, 2012 (% of households)"
label variable sdg9_c_rb        "Density of radio bases, 2016 (number of radio bases per 1000 inhabitants)"

label variable sdg10_2_egini    "GINI coefficient of years of education, 2012"
label variable sdg10_2_ge       "Inequality in electricity consumption, 2016"
label variable sdg10_2_nhe      "Non-Spanish speaking population (>= 3 years), 2012 (%)"

label variable sdg11_1_h        "Overcrowding rate, 2012 (% of households)"
label variable sdg11_1_sss      "Households that do not have a toilet, bathroom or latrine, 2012 (%) latrine, 2012 (%)"
label variable sdg11_2_atc      "Seats available for mass transit, 2017 (per 1,000 inhabitants)"

label variable sdg13_1_vcc      "Climate change vulnerability Index, 2015"
label variable sdg13_2_ectp     "Total CO2 emissions per capita, 2016 (tCO2/person/year)"
label variable sdg13_2_td       "Deforestation rate, average 2016-2018 (% of forest area 2015)"
label variable sdg15_1_ap       "Protected areas, 2019 (% of the municipality's land area) municipality)"
label variable sdg15_5_pb       "Biodiversity loss rate due to deforestation deforestation, average 2016-2018"

label variable sdg16_1_vh       "Registered homicide rate, average 2015-2017. (per 100,000 inhabitants)"
label variable sdg16_6_ce       "Programmed budget execution capacity, 2017 (%)"
label variable sdg16_9_nrc      "Children registered in the civil registry (< 5 years), 2012 (%)"

label variable sdg17_1_il       "Proportion of municipal revenues that come from local taxes, 2017 (%)"
label variable sdg17_5_ip       "Public investment per capita, 2017 (Bs./person)"

label variable sdg1_1_ee_abs    "Number of homes consuming <25% of the Dignity Tariff limit (210 kWh/year), 2016."
label variable sdg1_1_nbi_abs   "Population with unsatisfied basic needs, 2012"
label variable sdg1_2_pm_abs    "Number of households with deficiencies in 4 or more dimensions (out of 9)"
label variable sdg1_4_ssb_abs   "Number of households lacking 1/3 basic services (electricity, water and sanitation),2012"

label variable sdg2_2_dm_abs    "Num.children <5years with chronic malnutrition,2016(weighted by dept. and poverty)"
label variable sdg2_2_smu_abs   "Num.women aged 15-49 years, overweight (BMI>=30), 2016 (by dept. and poverty)"
label variable sdg2_4_su_abs    "Total area of agricultural production units, 2013 (ha)"
label variable sdg2_4_t_abs     "Number of tractors in the municipality, 2013"

label variable sdg3_1_p_abs     "Number of unattended deliveries in a health facility, 2012"
label variable sdg3_2_mi_abs    "Number of children who died before their first birthday, 2016"
label variable sdg3_2_mn_abs    "Number of children who died before their fifth birthday, 2016"
label variable sdg3_3_c_abs     "Number of households infested with Chagas disease, 2017"
label variable sdg3_3_d_abs     "Population with dengue, 2018"
label variable sdg3_3_m_abs     "Number of reported malaria cases, average 2014-2017"
label variable sdg3_3_t_abs     "Number of cases of tuberculosis in all forms, new and relapsed, 2017"
label variable sdg3_3_vih_abs   "Number of HIV cases, 2014-2017"
label variable sdg3_7_fa_abs    "Number of births per women aged 15-19 years, annual average, 2008-2012"

label variable sdg4_1_ash_abs   "Number of male high school dropouts, 2017"
label variable sdg4_1_asm_abs   "Number of female high school dropouts, 2017"
label variable sdg4_4_es_abs    "Population aged 19 years and older with higher education attained, 2012"
label variable sdg4_6_alfab_~s  "Population aged 15 and over who are not literate, 2012"
label variable sdg4_c_pci_abs   "Number of unqualified teachers at the initial level, 2016"
label variable sdg4_c_pcs_abs   "Number of unqualified teachers at the secondary level, 2016"

label variable sdg6_1_ca_abs    "Population without drinking water coverage, 2017"
label variable sdg6_2_cs_abs    "Population without basic sanitation coverage, 2017"

label variable sdg7_1_cee_abs   "Population without electricity coverage, 2012"
label variable sdg7_1_cep_abs   "Residential electricity consumption, 2016 (kWh)"
label variable sdg7_1_elc_abs   "Number of households without clean energy for cooking, 2012"
label variable sdg7_3_ecep_abs  "Total CO2 emissions by energy, 2016 (tCO2/year)"

label variable sdg8_4_mcc_abs   "Residential electric meters with zero consumption, 2016 (%)"
label variable sdg8_5_ph_abs    "Overall male participation rate (>= 10 years), 2012 (%)"
label variable sdg8_5_pm_abs    "Overall female participation rate (>= 10 years), 2012 (%)"
label variable sdg8_6_hnn_abs   "Men neither studying nor participating in the labor market (15-24 years), 2012(%)"
label variable sdg8_6_mnn_abs   "Women neither studying nor participating in the labor market(15-24 years), 2012(%)"
label variable sdg8_10_b_abs    "Density of bank branches, 2018 (per 100,000 inhabitants)"

label variable sdg9_1_rutas_~s  "Number of railways/primary roads entering/leaving the municipality, 2019"
label variable sdg9_5_c_abs     "Number of Kuaa computers delivered, 2016"
label variable sdg9_5_pt_abs    "Number of educational units with technological floors, 2016"
label variable sdg9_c_crdm_abs  "Number of households without fixed or cellular telephony coverage, 2012"
label variable sdg9_c_rb_abs    "Total number of radio bases (ATT and Prontis), 2016"

label variable sdg10_2_nhe_abs  "Population>=3 years old, do not speak Spanish (as mother tongue,1st,2nd language), 2012."

label variable sdg11_1_h_abs    "Number of households with overcrowding (more than 2 persons per room), 2012"
label variable sdg11_1_sss_abs  "Number of households without sanitation services, 2012"
label variable sdg11_2_atc_abs  "Number of seats available in mass transit vehicles, 2017."

label variable sdg13_2_ectp_~s  "Total CO2 emissions, 2016 (tCO2/year)"
label variable sdg13_2_td_abs   "Annual deforestation, 2016-2018 (ha)"

label variable sdg15_1_ap_abs   "Legally declared protected area(Municipal,Departmental, National),2019(km2)"
label variable sdg15_5_pb_abs   "Absolute Species Richness Loss, 2016-2018 (% of national loss)"

label variable sdg16_1_vh_abs   "Number of registered homicides, 2015-2017"
label variable sdg16_6_ce_abs   "Annual Operating Budget (POA) in Bs., 2017"
label variable sdg16_9_nrc_abs  "Number of children under 5 years of age not registered in a civil registry, 2012"

label variable sdg17_5_ip_abs   "Total public investment, 2017 (Bs.)"

label variable sdg1_1_ee_norm   "Normalized (0-100): sdg1_1_eepr"
label variable sdg1_1_nbi_norm  "Normalized (0-100): sdg1_1_ubn"
label variable sdg1_2_pm_norm   "Normalized (0-100): sdg1_2_mpi"
label variable sdg1_4_ssb_norm  "Normalized (0-100): sdg1_4_abs"

label variable sdg2_2_dm_norm   "Normalized (0-100): sdg2_2_cmc"
label variable sdg2_2_smu_norm  "Normalized (0-100): sdg2_2_oww"
label variable sdg2_4_su_norm   "Normalized (0-100): sdg2_4_pual"
label variable sdg2_4_t_norm    "Normalized (0-100): sdg2_2_td"

label variable sdg3_1_p_norm    "Normalized (0-100): sdg3_1_idca"
label variable sdg3_2_mi_norm   "Normalized (0-100): sdg3_2_imr"
label variable sdg3_2_mn_norm   "Normalized (0-100): sdg3_2_mrc"
label variable sdg3_3_c_norm    "Normalized (0-100): sdg3_3_cdir"
label variable sdg3_3_d_norm    "Normalized (0-100): sdg3_3_di"
label variable sdg3_3_m_norm    "Normalized (0-100): sdg3_3_imr"
label variable sdg3_3_t_norm    "Normalized (0-100): sdg3_3_ti"
label variable sdg3_3_vih_norm  "Normalized (0-100): sdg3_3_hivi"
label variable sdg3_7_fa_norm   "Normalized (0-100): sdg3_7_afr"

label variable sdg4_1_ash_norm  "Normalized (0-100): sdg4_1_ssdrm"
label variable sdg4_1_asm_norm  "Normalized (0-100): sdg4_1_ssdrf"
label variable sdg4_4_es_norm   "Normalized (0-100): sdg4_4_phe"
label variable sdg4_6_alfab_~m  "Normalized (0-100): sdg4_6_lr"
label variable sdg4_c_pci_norm  "Normalized (0-100): sdg4_c_qti"
label variable sdg4_c_pcs_norm  "Normalized (0-100): sdg4_c_qts"

label variable sdg5_1_paes_n~m  "Normalized (0-100): sdg5_1_gpsd"
label variable sdg5_1_pej_norm  "Normalized (0-100): sdg5_1_gpyp"
label variable sdg5_1_ppm_norm  "Normalized (0-100): sdg5_1_gpmpi"
label variable sdg5_5_pp_norm   "Normalized (0-100): sdg5_5_gpop"

label variable sdg6_1_ca_norm   "Normalized (0-100): sdg6_1_dwc"
label variable sdg6_2_cs_norm   "Normalized (0-100): sdg6_2_sc"
label variable sdg6_3_tar_norm  "Normalized (0-100): sdg6_3_wwt"

label variable sdg7_1_cee_norm "Normalized (0-100): sdg7_1_ec"
label variable sdg7_1_cep_norm "Normalized (0-100): sdg7_1_rec"
label variable sdg7_1_elc_norm "Normalized (0-100): sdg7_1_cce"
label variable sdg7_3_ecep_n~m "Normalized (0-100): sdg7_3_co2epc"  

label variable sdg8_4_mcc_norm  "Normalized (0-100): sdg8_4_rem"
label variable sdg8_5_ph_norm   "Normalized (0-100): sdg8_5_oprm"
label variable sdg8_5_pm_norm   "Normalized (0-100): sdg8_5_ofrm"
label variable sdg8_6_hnn_norm  "Normalized (0-100): sdg8_6_mlm"
label variable sdg8_6_mnn_norm  "Normalized (0-100): sdg8_6_mlw"
label variable sdg8_10_b_norm   "Normalized (0-100): sdg8_10_dbb"
label variable sdg8_11_mm_norm  "Normalized (0-100): sdg8_11_idi"

label variable sdg9_1_rutas_~m  "Normalized (0-100): sdg9_1_routes"
label variable sdg9_5_c_norm    "Normalized (0-100): sdg9_5_cd"
label variable sdg9_5_pt_norm   "Normalized (0-100): sdg9_5_eutf"
label variable sdg9_c_crdm_n~m  "Normalized (0-100): sdg9_5_mnc"
label variable sdg9_c_rb_norm   "Normalized (0-100): sdg9_c_drb"

label variable sdg10_2_egini~m "Normalized (0-100): sdg10_2_gyce"
label variable sdg10_2_ge_norm "Normalized (0-100): sdg10_2_iec"
label variable sdg10_2_nhe_n~m "Normalized (0-100): sdg10_2_nssp" 

label variable sdg11_1_h_norm "Normalized (0-100): sdg11_1_hocr"
label variable sdg11_1_sss_n~m "Normalized (0-100): sdg11_1_hno"
label variable sdg11_2_atc_n~m "Normalized (0-100): sdg11_2_samt"

label variable sdg13_1_vcc_n~m "Normalized (0-100): sdg13_1_ccvi"
label variable sdg13_2_ectp_~m "Normalized (0-100): sdg13_2_tco2e"
label variable sdg13_2_td_norm "Normalized (0-100): sdg13_2_dra"

label variable sdg15_1_ap_norm "Normalized (0-100): sdg15_1_pa"
label variable sdg15_5_pb_norm "Normalized (0-100): sdg15_5_blr"

label variable sdg16_1_vh_norm "Normalized (0-100): sdg16_1_rhr"
label variable sdg16_6_ce_norm "Normalized (0-100): sdg16_6_pbec"
label variable sdg16_9_nrc_n~m "Normalized (0-100): sdg16_9_cr"

label variable sdg17_1_il_norm "Normalized (0-100): sdg17_1_pmtax"
label variable sdg17_5_ip_norm "Normalized (0-100): sdg17_5_pipc"

label variable indice_ods1 "SDG1 Index"
label variable indice_ods2 "SDG2 Index"
label variable indice_ods3 "SDG3 Index"
label variable indice_ods4 "SDG4 Index"
label variable indice_ods5 "SDG5 Index"
label variable indice_ods6 "SDG6 Index"
label variable indice_ods7 "SDG7 Index"
label variable indice_ods8 "SDG8 Index"
label variable indice_ods9 "SDG9 Index"
label variable indice_ods10 "SDG10 Index"
label variable indice_ods11 "SDG11 Index"
label variable indice_ods13 "SDG13 Index"
label variable indice_ods15 "SDG15 Index"
label variable indice_ods16 "SDG16 Index"
label variable indice_ods17 "SDG17 Index" 

*Rename variables name
rename poblacion_2020 population_2020

rename sdg1_1_ee    sdg1_1_eepr
rename sdg1_1_nbi   sdg1_1_ubn
rename sdg1_2_pm    sdg1_2_mpi
rename sdg1_4_ssb   sdg1_4_abs

rename sdg2_2_dm    sdg2_2_cmc
rename sdg2_2_smu   sdg2_2_oww
rename sdg2_4_su    sdg2_4_pual
rename sdg2_4_t     sdg2_4_td

rename sdg3_1_p     sdg3_1_idca
rename sdg3_2_mi    sdg3_2_imr
rename sdg3_2_mn    sdg3_2_mrc
rename sdg3_3_c     sdg3_3_cdir
rename sdg3_3_d     sdg3_3_di
rename sdg3_3_m     sdg3_3_imr
rename sdg3_3_t     sdg3_3_ti 
rename sdg3_3_vih   sdg3_3_hivi
rename sdg3_7_fa    sdg3_7_afr 

rename sdg4_1_ash   sdg4_1_ssdrm
rename sdg4_1_asm   sdg4_1_ssdrf
rename sdg4_4_es    sdg4_4_phe
rename sdg4_6_alfab sdg4_6_lr
rename sdg4_c_pci   sdg4_c_qti
rename sdg4_c_pcs   sdg4_c_qts

rename sdg5_1_paes  sdg5_1_gpsd
rename sdg5_1_pej   sdg5_1_gpyp
rename sdg5_1_ppm   sdg5_1_gpmpi
rename sdg5_5_pp    sdg5_5_gpop
rename sdg6_1_ca    sdg6_1_dwc
rename sdg6_2_cs    sdg6_2_sc
rename sdg6_3_tar   sdg6_3_wwt

rename sdg7_1_cee   sdg7_1_ec
rename sdg7_1_cep   sdg7_1_rec
rename sdg7_1_elc   sdg7_1_cce
rename sdg7_3_ecep  sdg7_3_co2epc 

rename sdg8_4_mcc   sdg8_4_rem
rename sdg8_5_ph    sdg8_5_oprm
rename sdg8_5_pm    sdg8_5_ofrm
rename sdg8_6_hnn   sdg8_6_mlm
rename sdg8_6_mnn   sdg8_6_wlm
rename sdg8_10_b    sdg8_10_dbb
rename sdg8_11_mm   sdg8_11_idi

rename sdg9_1_rutas  sdg9_1_routes
rename sdg9_5_c      sdg9_5_cd
rename sdg9_5_pt     sdg9_5_eutf
rename sdg9_c_crdm   sdg9_c_mnc
rename sdg9_c_rb     sdg9_c_drb

rename sdg10_2_egini sdg10_2_gcye 
rename sdg10_2_ge    sdg10_2_iec
rename sdg10_2_nhe   sdg10_2_nssp 

rename sdg11_1_h     sdg11_1_hocr
rename sdg11_1_sss   sdg11_1_hno
rename sdg11_2_atc   sdg11_2_samt

rename sdg13_1_vcc   sdg13_1_ccvi
rename sdg13_2_ectp  sdg13_2_tco2e
rename sdg13_2_td    sdg13_2_dra

rename sdg15_1_ap    sdg15_1_pa
rename sdg15_5_pb    sdg15_5_blr

rename sdg16_1_vh    sdg16_1_rhr
rename sdg16_6_ce    sdg16_6_pbec
rename sdg16_9_nrc   sdg16_9_cr

rename sdg17_1_il    sdg17_1_pmtax
rename sdg17_5_ip    sdg17_5_pipc

** Variables in absolute terms

rename sdg1_1_ee_abs sdg1_1_dtl_abs
rename sdg1_1_nbi_abs sdg1_1_pubn_abs
rename sdg1_2_pm_abs sdg1_2_dd_abs
rename sdg1_4_ssb_abs sdg1_4_ebs_abs

rename sdg2_2_dm_abs sdg2_2_cm_abs
rename sdg2_2_smu_abs sdg2_2_wow_abs
rename sdg2_4_su_abs sdg2_4_apu_abs
rename sdg2_4_t_abs sdg2_4_tm_abs

rename sdg3_1_p_ab sdg3_1_udhf_ab
rename sdg3_2_mi_abs sdg3_2_fb_abs
rename sdg3_2_mn_abs sdg3_2_ffb_abs
rename sdg3_3_c_abs sdg3_3_cd_abs
rename sdg3_3_d_abs sdg3_3_pd_abs
rename sdg3_3_m_abs sdg3_3_mc_abs
rename sdg3_3_t_abs sdg3_3_tc_abs
rename sdg3_3_vih_abs sdg3_3_vih_abs 
rename sdg3_7_fa_abs sdg3_7_bpw_abs
rename sdg4_1_ash_abs sdg4_1_mhs_abs
rename sdg4_1_asm_abs sdg4_1_fhs_abs
rename sdg4_4_es_abs sdg4_4_heu_abs
rename sdg4_6_alfab_~s sdg4_6_pnl_abs
rename sdg4_c_pci_abs sdg4_c_uti_abs
rename sdg4_c_pcs_abs sdg4_c_uts_abs

rename sdg6_1_ca_abs sdg6_1_wdc_abs
rename sdg6_2_cs_abs sdg6_2_bsc_abs

rename sdg7_1_cee_abs sdg7_1_wec_abs
rename sdg7_1_cep_abs sdg7_1_rec_abs
rename sdg7_1_elc_abs sdg7_1_cec_abs
rename sdg7_3_ecep_abs sdg7_3_tee_abs

rename sdg8_4_mcc_abs sdg8_4_rem_abs
rename sdg8_5_ph_abs sdg8_5_ompr_abs
rename sdg8_5_pm_abs sdg8_5_ofpr_abs
rename sdg8_6_hnn_abs sdg8_6_mlm_abs
rename sdg8_6_mnn_abs sdg8_6_wlm_abs
rename sdg8_10_b_abs sdg8_10_dbb_abs

rename sdg9_1_rutas_~s sdg9_1_rmun_abs
rename sdg9_5_c_abs sdg9_5_kcd_abs
rename sdg9_5_pt_abs sdg9_5_eutf_abs
rename sdg9_c_crdm_abs sdg9_c_hf_abs
rename sdg9_c_rb_abs sdg9_c_tr_abs

rename sdg10_2_nhe_abs sdg10_2_dss_abs 

rename sdg11_1_h_abs sdg11_1_ho_abs
rename sdg11_1_sss_abs sdg11_1_wos_abs
rename sdg11_2_atc_abs sdg11_2_mtv_abs

rename sdg13_2_ectp_~s sdg13_2_tco2_abs
rename sdg13_2_td_abs sdg13_2_ad_abs

rename sdg15_1_ap_abs sdg15_1_pa_abs
rename sdg15_5_pb_abs sdg15_5_rl_abs

rename sdg16_1_vh_abs sdg16_1_rh_abs 
rename sdg16_6_ce_abs sdg16_6_aob_abs
rename sdg16_9_nrc_abs sdg16_9_ncr_abs

rename sdg17_5_ip_abs sdg17_5_tpi_abs

* Variables in normalized scale

rename sdg1_1_ee_norm sdg1_1_eepr_norm
rename sdg1_1_nbi_norm sdg1_1_ubn_norm
rename sdg1_2_pm_norm sdg1_2_mpi_norm
rename sdg1_4_ssb_norm sdg1_4_abs_norm

rename sdg2_2_dm_norm sdg2_2_cmc_norm
rename sdg2_2_smu_norm sdg2_2_oww_norm
rename sdg2_4_su_norm sdg2_4_pual_norm
rename sdg2_4_t_norm sdg2_4_td_norm

rename sdg3_1_p_norm sdg3_1_idca_norm
rename sdg3_2_mi_norm sdg3_2_imr_norm
rename sdg3_2_mn_norm sdg3_2_mrc_norm
rename sdg3_3_c_norm sdg3_3_cdir_norm
rename sdg3_3_d_norm sdg3_3_di_norm
rename sdg3_3_m_norm sdg3_3_imr_norm
rename sdg3_3_t_norm sdg3_3_ti_norm
rename sdg3_3_vih_norm sdg3_3_hivi_norm
rename sdg3_7_fa_norm sdg3_7_afr_norm

rename sdg4_1_ash_norm sdg4_1_ssdrm_norm 
rename sdg4_4_es_norm sdg4_4_ssdrf_norm
rename sdg4_6_alfab_~m sdg4_6_lr_norm
rename sdg4_c_pci_norm sdg4_c_qti_norm
rename sdg4_c_pcs_norm sdg4_c_qts_norm

rename sdg5_1_paes_n~m sdg5_1_gpsd_norm
rename sdg5_1_pej_norm sdg5_1_gpyd_norm
rename sdg5_1_ppm_norm sdg5_1_gpmpi_norm
rename sdg5_5_pp_norm sdg5_5_gpop_norm

rename sdg6_1_ca_norm sdg6_1_dwc_norm
rename sdg6_2_cs_norm sdg6_2_sc_norm
rename sdg6_3_tar_norm sdg6_3_wwt_norm

rename sdg7_1_cee_norm sdg7_1_ec_norm
rename sdg7_1_cep_norm sdg7_1_rec_norm
rename sdg7_1_elc_norm sdg7_1_cce_norm
rename sdg7_3_ecep_n~m sdg7_3_co2epc_norm

rename sdg8_4_mcc_norm sdg8_4_rem_norm
rename sdg8_5_ph_norm sdg8_5_oprm_norm
rename sdg8_5_pm_norm sdg8_5_ofrm_norm
rename sdg8_6_hnn_norm sdg8_6_mlm_norm
rename sdg8_6_mnn_norm sdg8_6_wlm_norm
rename sdg8_10_b_norm sdg8_10_dbb_norm
rename sdg8_11_mm_norm sdg8_11_idi_norm

rename sdg9_1_rutas_norm sdg9_1_routes_norm 
rename sdg9_5_c_norm sdg9_5_cd_norm
rename sdg9_5_pt_norm sdg9_5_eutf_norm
rename sdg9_c_crdm_n~m sdg9_c_mnc_norm
rename sdg9_c_rb_norm sdg9_c_drb_norm

rename sdg10_2_egini~m sdg10_2_gcye_norm
rename sdg10_2_ge_norm sdg10_2_iec_norm
rename sdg10_2_nhe_n~m sdg10_2_nssp_norm

rename sdg11_1_h_norm sdg11_1_hocr_norm
rename sdg11_1_sss_n~m sdg11_1_hno_norm
rename sdg11_2_atc_n~m sdg11_2_samt_norm

rename sdg13_1_vcc_n~m sdg13_1_ccvi_norm
rename sdg13_2_ectp_~m sdg13_2_tco2e_norm
rename sdg13_2_td_norm sdg13_2_dra_norm

rename sdg15_1_ap_norm sdg15_1_pa_norm
rename sdg15_5_pb_norm sdg15_5_blr_norm

rename sdg16_1_vh_norm sdg16_1_rhr_norm
rename sdg16_6_ce_norm sdg16_6_pbec_norm
rename sdg16_9_nrc_n~m sdg16_9_cr_norm

rename sdg17_1_il_norm sdg17_1_pmtax_norm
rename sdg17_5_ip_norm sdg17_5_pipc_norm

* SDG index

rename indice_ods1 index_sdg1
rename indice_ods2 index_sdg2
rename indice_ods3 index_sdg3
rename indice_ods4 index_sdg4
rename indice_ods5 index_sdg5
rename indice_ods6 index_sdg6
rename indice_ods7 index_sdg7
rename indice_ods8 index_sdg8
rename indice_ods9 index_sdg9
rename indice_ods10 index_sdg10
rename indice_ods11 index_sdg11
rename indice_ods13 index_sdg13
rename indice_ods15 index_sdg15
rename indice_ods16 index_sdg16
rename indice_ods17 index_sdg17



** Drop unnecesary variables 
*** Form SDG databse: variables in absolute terms and normalized variables
*** From QuaRCS database:  6.25 HP trends, 400 HP trends

drop sdg1_1_dtl_abs-sdg17_5_tpi_abs
drop sdg1_1_eepr_norm-sdg17_5_pipc_norm

drop tr6_pop2001-tr6_pop2020
drop tr100_pop2001-tr100_pop2020
drop tr400_pop2001-tr400_pop2020

drop ln_t6NTLpc2012-ln_t6NTLpc2020
drop ln_t100NTLpc2012-ln_t100NTLpc2020

drop tr6_co2015-tr6_co2020
drop tr100_co2015-tr100_co2020


drop shapeName

* Add lables to population variables 
label variable pop2001 "Estimated population in 2001"
label variable pop2002 "Estimated population in 2002"
label variable pop2003 "Estimated population in 2003"
label variable pop2004 "Estimated population in 2004"
label variable pop2005 "Estimated population in 2005"
label variable pop2006 "Estimated population in 2006"
label variable pop2007 "Estimated population in 2007"
label variable pop2008 "Estimated population in 2008"
label variable pop2009 "Estimated population in 2009"
label variable pop2010 "Estimated population in 2010"
label variable pop2011 "Estimated population in 2011"
label variable pop2012 "Estimated population in 2012"
label variable pop2013 "Estimated population in 2013"
label variable pop2014 "Estimated population in 2014"
label variable pop2015 "Estimated population in 2015"
label variable pop2016 "Estimated population in 2016"
label variable pop2017 "Estimated population in 2017"
label variable pop2018 "Estimated population in 2018"
label variable pop2019 "Estimated population in 2019"
label variable pop2020 "Estimated population in 2020"


* Add labels to NTL variables
label variable ln_NTLpc2012 "Log NTL per capita in 2012"
label variable ln_NTLpc2013 "Log NTL per capita in 2013"
label variable ln_NTLpc2014 "Log NTL per capita in 2014"
label variable ln_NTLpc2015 "Log NTL per capita in 2015"
label variable ln_NTLpc2016 "Log NTL per capita in 2016"
label variable ln_NTLpc2017 "Log NTL per capita in 2017"
label variable ln_NTLpc2018 "Log NTL per capita in 2018"
label variable ln_NTLpc2019 "Log NTL per capita in 2019"
label variable ln_NTLpc2020 "Log NTL per capita in 2020"



label variable ln_t400NTLpc2012 "Trend log NTL per capita in 2012"
label variable ln_t400NTLpc2013 "Trend log NTL per capita in 2013"
label variable ln_t400NTLpc2014 "Trend log NTL per capita in 2014"
label variable ln_t400NTLpc2015 "Trend log NTL per capita in 2015"
label variable ln_t400NTLpc2016 "Trend log NTL per capita in 2016"
label variable ln_t400NTLpc2017 "Trend log NTL per capita in 2017"
label variable ln_t400NTLpc2018 "Trend log NTL per capita in 2018"
label variable ln_t400NTLpc2019 "Trend log NTL per capita in 2019"
label variable ln_t400NTLpc2020 "Trend log NTL per capita in 2020"


* Add labels to CO2 variables
label variable co2015 "Estimated carbon dioxide in 2015"
label variable co2016 "Estimated carbon dioxide in 2016"
label variable co2017 "Estimated carbon dioxide in 2017"
label variable co2018 "Estimated carbon dioxide in 2018"
label variable co2019 "Estimated carbon dioxide in 2019"
label variable co2020 "Estimated carbon dioxide in 2020"

label variable tr400_co2015 "Trend estimated carbon dioxide in 2015"
label variable tr400_co2016 "Trend estimated carbon dioxide in 2016"
label variable tr400_co2017 "Trend estimated carbon dioxide in 2017"
label variable tr400_co2018 "Trend estimated carbon dioxide in 2018"
label variable tr400_co2019 "Trend estimated carbon dioxide in 2019"
label variable tr400_co2020 "Trend estimated carbon dioxide in 2020"




save              "../data/GeoDS4Bolivia.dta", replace
export delimited  "../data/GeoDS4Bolivia.csv", replace
