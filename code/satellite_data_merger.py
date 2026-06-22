# %%

# NOTE (bolivia112): This is the PROVINCE-level twin of the DS4Bolivia satellite
# data merger. The unit of analysis is now 112 Bolivian provinces (keyed by
# prov_id, the 3-digit INE code) instead of 339 municipalities (asdf_id). The
# base province values are POPULATION-WEIGHTED AGGREGATIONS of the municipal data
# (intensive variables = weighted mean, extensive variables = sum); see
# ../province_aggregation_report.md. With only 112 observations the sample is
# small for ML, so treat downstream models accordingly. The external satellite
# layers below are merged onto the province base via prov_id.

import pandas as pd
from datetime import datetime

# %%
db = pd.read_csv("../bolivia112_v20260622.csv") # province master (112 provinces)
desc = pd.read_csv("../definitions_bolivia112_v20260622.csv")
# %%

# Air temperature =============================================================

#Adding new values to the dataset
airTempMean_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/air_tem_mean_2012-17.csv"

airTempMean = pd.read_csv(airTempMean_url)
db = db.merge(airTempMean, left_on="prov_id", right_on="id", right_index=False)
db.drop(columns="id", inplace=True)
# %%
vName = airTempMean.columns[~airTempMean.columns.str.contains("id")].to_list()

# Creating variable names and labels
vLabel = []
years = range(2012,2018)
for year in years:
    vLabel.append(f"Mean Air Temperature in Celcius in {year}")

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc, rows], ignore_index=True)

# %%

airTempMin_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/air_temp_min_2012-2017.csv"

airTempMin = pd.read_csv(airTempMin_url)
db = db.merge(airTempMin, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)


# %%

vName = airTempMin.columns[~airTempMin.columns.str.contains("id")].tolist()

vLabel = []
for year in years:
    vLabel.append(f"Minimum Air Temperature in Celcius in {year}")
    
rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)

# %%
airTempMax_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/air_temp_max_2012-2017.csv"

airTempMax = pd.read_csv(airTempMax_url)
db = db.merge(airTempMax, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)


# %%

vName = airTempMax.columns[~airTempMax.columns.str.contains("id")].tolist()

vLabel = []
for year in years:
    vLabel.append(f"Maximum Air Temperature in Celcius in {year}")
    
rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)


# ============================================================= Air temperature
# %%

# def nameLabelCreation(desc_db, db, label="no Label", range=False, year=0, ):
#     vName = db.colums[~db.columns.str.contains("id")].to_list()
    
#     if range != False:
#         vLabel = []
#         for year in range:
#             vLabel.append(f"{label} in {year}")
    
#     elif year != 0: 
#         vLabel = f"{label} in {year}" 
    
#     else: 
#         print("missing arguments")
        
#     rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})  
#     return rows
    

# %%

 # Coast Distance ===============================================================
coastDistance_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/coast_distance_2017.csv"

coastDistance = pd.read_csv(coastDistance_url)

db = db.merge(coastDistance, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%

vName = coastDistance.columns[~coastDistance.columns.str.contains("id")].to_list()

vLabel =["Mean distance to coast in meters in 2017",
         "Max distance to coast in meters in 2017",
         "Min distance to coast in meters in 2017"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== Coast Distance

# %%
# Diamond Distance ===============================================================
diaDistance_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/diamond_distance_2017.csv"

diaDistance = pd.read_csv(diaDistance_url)

db = db.merge(diaDistance, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %% 

vName = diaDistance.columns[~diaDistance.columns.str.contains("id")].tolist()
vLabel =["Min distance to diamond deposits in meters in 2017",
         "Mean distance to diamond deposits in meters in 2017",
         "Max distance to diamond deposits in meters in 2017"
         ]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)

# =============================================================== Diamond Distance

# %%
# Drug cultivation  ===============================================================

drugCult_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/drug_cultivation_2017.csv"
drugCult = pd.read_csv(drugCult_url)
drugCult.drop(columns=['drugCult_cannabis2017',
                       'drugCult_opium2017',
                       'drugCult_mix2017'],
              inplace=True)
db = db.merge(drugCult, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%
vName = drugCult.columns[~drugCult.columns.str.contains("id")].to_list()
vLabel = ["Total area in polygons in 2017",
         "Area without drug cultivation in polygons in 2017",
         "Area with coca bush cultivation in polygons in 2017"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== Drug Cultivation

# %%
# Drug Cult Distance ===============================================================
drugDistance_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/drug_cultivation_distance_2017.csv"
drugDistance = pd.read_csv(drugDistance_url)

db = db.merge(drugDistance, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)
# %%
vName = drugDistance.columns[~drugDistance.columns.str.contains("id")].tolist()
vLabel = ["Mean distance to drug cultivation sites in meters in 2017",
         "Max distance to drug cultivation sites in meters in 2017",
         "Min distance to drug cultivation sites in meters in 2017"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)

# =============================================================== Drug Cult Distance

# %%

# esa_landcover ===============================================================
esa_landcover_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/esa_landcover_2012-2016.csv"

esa_landcover = pd.read_csv(esa_landcover_url)

db = db.merge(esa_landcover, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%

vName = esa_landcover.columns[~esa_landcover.columns.str.contains("id")].to_list()

vLabel = []
for col in vName: 
    year = col.split("esaLandCover",1)[1].split("_")[0]
    category = col.split("_",1)[1].replace("_", " ")
    
    label = f"{category} ESA land cover classification in polygons in {year}"
    vLabel.append(label)
    #print(label)

rows = pd.DataFrame({"varname":vName,"varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== esa_landcover

# %%

# Modis Landcover ===============================================================
modisLandcover_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/gee_modis_landcover_2012-2016.csv"

modisLandcover = pd.read_csv(modisLandcover_url)
db = db.merge(modisLandcover, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%
vName = modisLandcover.columns[~modisLandcover.columns.str.contains("id")].to_list()

labels = ["agricultural land MODIS, total pixels divided by green Pixels",
          "total pixels",
          "urban land MODIS, total pixels divided by gray Pixels"]
years = range(2012,2017)
vLabel = []
for year in years: 
    for label in labels:
        label = label +" in "+str(year)
        print(label)
        vLabel.append(label)

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== Modis Landcover
# %%

# GHSL ===============================================================
ghsl_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/ghsl_2015.csv"

ghsl = pd.read_csv(ghsl_url)
db = db.merge(ghsl, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%
vName = ghsl.columns[~ghsl.columns.str.contains("id")].tolist()
vLabel = ["pixel sum of the Global Human Settlement Layer population count in 2015"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== GHSL

# %%
# GISA ===============================================================

gisa_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/gisa_2012-2019.csv"

gisa = pd.read_csv(gisa_url)
db = db.merge(gisa, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%

vName = gisa.columns[~gisa.columns.str.contains("id")].tolist()

vLabel = []
for name in vName:
    year = name.split("gisa")[1]
    #print(year)
    vLabel.append(f"Global Impervious Surface area by pixel in {year}")
    print()
    
rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== GISA

# %%

# time to city ===============================================================
timeCity_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/distance_city_2016.csv"

timeCity = pd.read_csv(timeCity_url)
db = db.merge(timeCity, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%
vName = timeCity.columns[~timeCity.columns.str.contains("id")].tolist()

vLabel = ["mean distance to major city in minutes in 2016",
          "max distance to major city in minutes in 2016",
          "min distance to major city in minutes in 2016"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== time to city 

# %%

# Malaria ===============================================================
malaria_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/malaria_max_incidence_rate_2012-2019.csv"

malaria = pd.read_csv(malaria_url)
db = db.merge(malaria, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%
vName = [col for col in malaria.columns if col != "id"]
vLabel = []

for col in vName: 
    year = col.split(".",2)[1]
    type = col.split(".",2)[2]
    vLabel.append(f"{type} malaria rate per 1000 people in {year}")

vLabel

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# ***************************************************************************
# %%

malariaMean_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/malaria_mean_incidence_rate_2012-2019.csv"

malariaMean = pd.read_csv(malariaMean_url)
db = db.merge(malariaMean, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%
vName = [col for col in malariaMean.columns if col != "id"]
vLabel = []

for col in vName: 
    year = col.split(".",2)[1]
    type = col.split(".",2)[2]
    vLabel.append(f"{type} malaria rate per 1000 people in {year}")

vLabel

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)

# %%

malariaMin_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/malaria_min_incidence_rate_2012-2019.csv"

malariaMin = pd.read_csv(malariaMin_url)
db = db.merge(malariaMin, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%
vName = [col for col in malariaMin.columns if col != "id"]
vLabel = []

for col in vName: 
    year = col.split(".",2)[1]
    type = col.split(".",2)[2]
    vLabel.append(f"{type} malaria rate per 1000 people in {year}")

vLabel

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)


# =============================================================== Malaria
# %%

# Precipitation ===============================================================
pre_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/mean_precipitation_cru_ts_2012-2020.csv"

pre = pd.read_csv(pre_url)
db = db.merge(pre, left_on="prov_id", right_on="id").drop(columns="id")

# %%

vName = pre.columns[~pre.columns.str.contains("id")].tolist()
vLabel = []

for col in vName:
    year = col.split(".",2)[1]
    type = col.split(".",2)[2]
    vLabel.append(f"{type} precipitation in millimeters in {year}")

rows = pd.DataFrame({"varname": vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== Precipitation
# %%

# modis ===============================================================
modis_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/modis_landcover_2012.csv"

modis = pd.read_csv(modis_url)
# modis.reset_index(inplace=True)
# modis.rename(columns={"index":"id"})
db = db.merge(modis, left_on="prov_id", right_on="id")
db.drop(columns="id", inplace=True)

# %%
vName = [col for col in modis.columns if col != "id"]

vLabel = []

for col in vName:
    year = col.split(".",2)[1]
    type = col.split("_",3)[3].replace("_", " ")
    # print(year, type)
    
    vLabel.append(f"{type} categorical MODIS in {year}")
    
rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc, rows], ignore_index=True)
# =============================================================== modis
# %%

# Photovoltaic Potential ===============================================================
photovoltaic_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/photovoltaic_potential.csv"

photovoltaic = pd.read_csv(photovoltaic_url)

db = db.merge(photovoltaic, left_on="prov_id", right_on="id").drop(columns="id")

# %%

vName = photovoltaic.columns[~photovoltaic.columns.str.contains("id")].tolist()

vLabel = ["mean photovoltaic potential in kWh/kWp in 2019",
          "max photovoltaic potential in kWh/kWp in 2019",
          "min photovoltaic potential in kWh/kWp in 2019"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== Photovoltaic Potential
# %%
# Elevation ===============================================================
elevation_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/physical_elevation_2017.csv"

elevation = pd.read_csv(elevation_url)
db = db.merge(elevation, left_on="prov_id", right_on="id").drop(columns="id")

#%%
vName = elevation.columns[~elevation.columns.str.contains("id")].tolist()

vLabel = ["Mean elevation in meters in 2017",
          "Max elevation in meters in 2017",
          "Min elevation in meters in 2017"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc= pd.concat([desc,rows], ignore_index=True)
# =============================================================== Elevation
# %%
# Distance road ===============================================================

distanceRoad_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/road_distance_2017.csv"
distanceRoad = pd.read_csv(distanceRoad_url)
db = db.merge(distanceRoad, left_on="prov_id", right_on="id").drop(columns="id")

# %%

vName = distanceRoad.columns[~distanceRoad.columns.str.contains("id")].tolist()
vLabel = ["mean distance to road in meters in 2017",
          "max distance to road in meters in 2017",
          "min distance to road in meters in 2017"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== Distance road
# %%
# Slope ===============================================================
slope_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/slope_2017.csv"

slope = pd.read_csv(slope_url)

db = db.merge(slope, left_on="prov_id", right_on="id").drop(columns="id")

# %%
vName = slope.columns[~slope.columns.str.contains("id")].tolist()
vLabel = ["mean slope in degrees in 2017",
          "max slope in degrees in 2017",
          "min slope in degrees in 2017"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== Slope
# %%

#  Water distance ===============================================================
distanceWater_url = "https://raw.githubusercontent.com/HendrixPeralta/bol_hdi_prediction/refs/heads/main/data/satellite/collab_satellite_data/water_distance_2017.csv"

distanceWater = pd.read_csv(distanceWater_url)

db = db.merge(distanceWater, left_on="prov_id", right_on="id").drop(columns="id")

# %%
vName = distanceWater.columns[~distanceWater.columns.str.contains("id")].tolist()

vLabel = ["mean distance to water in meters in 2017",
          "max distance to water in meters in 2017",
          "min distance to water in meters in 2017"]

rows = pd.DataFrame({"varname":vName, "varlabel":vLabel})
desc = pd.concat([desc,rows], ignore_index=True)
# =============================================================== Water Distance


# GHSL ===============================================================

# =============================================================== GHSL
# GHSL ===============================================================
# =============================================================== GHSL

# GHSL ===============================================================
# =============================================================== GHSL
# %%
# Export ===============================================================
# Exporting final version
today = datetime.now().strftime("%Y%m%d")

db_filename = f"bolivia112_v{today}.csv"
db.to_csv(f"../{db_filename}", index=False)

desc_filename = f"definitions_bolivia112_v{today}.csv"
desc.to_csv(f"../{desc_filename}", index=False)

 # ============================================================== Exoport
# %%
