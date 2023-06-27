import pandas as pd
from reuselca.utils import *

# Paramètres fixes à renseinger ou charger depuis un fichier
project_SRE = 723.9
faraday_path = "C:/Users/mija.frossard/Documents/OneDrive - HESSO/RaD/Projet_Reuse-LCA/Cas études/Faraday/Faraday_Reuse_LCA_calculation_v2.xlsx"

# Code
faraday_pd = pd.read_excel(faraday_path, sheet_name="LCI+LCIA", header=2)
new_inventory = faraday_pd[faraday_pd["Status"]=="New"]
reuse_inventory = faraday_pd[faraday_pd["Status"]=="Reused"]

table_features = ["Element", "Category", "e-BKP_category", "Material type", "Reuse_origin", "FU_quantity", "FU_unit", "Mass"]
output_table = reuse_inventory[table_features].copy()
units_list = output_table["FU_unit"]
units_list = [unit+"/m² SRE" for unit in units_list]
output_table["FU_unit"] = units_list
output_table["Mass"] = output_table["Mass"].divide(1000)
output_table.sort_values(by="Mass", ascending=False)

reused_mass = output_table["Mass"].sum() # tonnes
reused_mass_percent = 100*reused_mass/(faraday_pd["Mass"].sum()/1000)
reused_mass_area =1000*reused_mass/project_SRE

GWP_A1A5_allnew = faraday_pd[["GWP_M1_A1A3", "GWP_M1_A4","GWP_M1_A5"]].sum().sum() # kgCO2/m2
GWP_A1A5_reuse = faraday_pd[["GWP_M3_A1A3", "GWP_M3_A4","GWP_M3_A5"]].sum().sum() # kgCO2/m2
GWP_A1A5_diff = (GWP_A1A5_allnew-GWP_A1A5_reuse)*project_SRE/1000 # tCO2 A1-A5
GWP_A1A5_var = 100*(GWP_A1A5_reuse-GWP_A1A5_allnew)/GWP_A1A5_allnew

GWP_avoided_disposal = reuse_inventory["GWP_M1_C1C4"]*reuse_inventory["Extension_rate"]
GWP_avoided_disposal_total = GWP_avoided_disposal.fillna(0).sum()*project_SRE/1000 # tCO2 avoided disposal

# Produits biosourcés neufs et réemployés

biogenic_inventory = faraday_pd[faraday_pd["Material type"]=="Biogenic"].copy()

calc_stored_bio_co2(reuse_inventory, project_SRE)
calc_stored_bio_co2(new_inventory, project_SRE)

cc_reuse = reuse_inventory["RR_Biogenic_carbon_content"]*reuse_inventory["Extension_rate"]
cc_reuse = cc_reuse.fillna(0).sum()*project_SRE
cc_new = new_inventory["RR_Biogenic_carbon_content"]*new_inventory["Extension_rate"]
cc_new=cc_new.fillna(0).sum()*project_SRE
comp_co2 = pd.DataFrame([reuse_inventory["Element"], calc_stored_bio_co2(reuse_inventory, project_SRE, total=False), reuse_inventory["GWP_M1_C1C4"]])
comp_co2 = comp_co2.transpose()
comp_co2.columns=["Element", "Stored CO2", "C1C4"]

# Feedstock NRPE

PENR_feedstock = reuse_inventory["RR_PE-NR_use_feedstock"].sum()*project_SRE
faraday_pd["RR_PE-NR_use_feedstock"].sum()*project_SRE

faraday_pd["RR_Biogenic_carbon_content"]*faraday_pd["Extension_rate"]*3.67

# Results table

results_actual_reuse = faraday_pd[["GWP_M3_A1A3", "GWP_M3_A4","GWP_M3_A5","UBP_M3_A1A3", "UBP_M3_A4","UBP_M3_A5","PE-NR_M3_A1A3", "PE-NR_M3_A4","PE-NR_M3_A5"]].fillna(0).sum()
results_actual_reuse_reuse = reuse_inventory[["GWP_M3_A1A3", "GWP_M3_A4","GWP_M3_A5","UBP_M3_A1A3", "UBP_M3_A4","UBP_M3_A5","PE-NR_M3_A1A3", "PE-NR_M3_A4","PE-NR_M3_A5"]].fillna(0).sum()
results_actual_reuse_new = new_inventory[["GWP_M3_A1A3", "GWP_M3_A4","GWP_M3_A5","UBP_M3_A1A3", "UBP_M3_A4","UBP_M3_A5","PE-NR_M3_A1A3", "PE-NR_M3_A4","PE-NR_M3_A5"]].fillna(0).sum()
results_all_new = faraday_pd[["GWP_M1_A1A3", "GWP_M1_A4","GWP_M1_A5","UBP_M1_A1A3", "UBP_M1_A4","UBP_M1_A5","PE-NR_M1_A1A3", "PE-NR_M1_A4","PE-NR_M1_A5"]].fillna(0).sum()

results = pd.DataFrame([results_actual_reuse,results_actual_reuse_reuse/results_actual_reuse,results_actual_reuse_new/results_actual_reuse])

diff = results_actual_reuse.values-results_all_new.values

var = []
for i in range(0,len(diff)):
    var.append(diff[i]/results_all_new.values[i])

results_var_gwp = (faraday_pd[["GWP_M3_A1A3", "GWP_M3_A4","GWP_M3_A5"]].sum().sum()-faraday_pd[["GWP_M1_A1A3", "GWP_M1_A4","GWP_M1_A5"]].sum().sum())/faraday_pd[["GWP_M1_A1A3", "GWP_M1_A4","GWP_M1_A5"]].sum().sum()

# périmètre gwp

reuse_inventory[["GWP_M1_A1A3", "GWP_M1_A4","GWP_M1_A5"]].sum().sum()/faraday_pd[["GWP_M1_A1A3", "GWP_M1_A4","GWP_M1_A5"]].sum().sum()
(reuse_inventory[["GWP_M3_A1A3", "GWP_M3_A4","GWP_M3_A5"]].sum().sum()-reuse_inventory[["GWP_M1_A1A3", "GWP_M1_A4","GWP_M1_A5"]].sum().sum())/reuse_inventory[["GWP_M1_A1A3", "GWP_M1_A4","GWP_M1_A5"]].sum().sum()
