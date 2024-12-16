import pandas as pd
from reuselca.utils import *

# Paramètres fixes à renseigner ou charger depuis un fichier
project_SRE = 723.9
faraday_path = "C:/Users/gauthier.demonchy/PycharmProjects/20221216_Faraday_Reuse_LCA_calculation_v9_lots_Margot.xlsx"

# Chargement des données
faraday_pd = pd.read_excel(faraday_path, sheet_name="LCI+LCIA", header=2)
new_inventory = faraday_pd[faraday_pd["Status"] == "New"]
reuse_inventory = faraday_pd[faraday_pd["Status"] == "Reused"]

# Afficher les noms des colonnes pour vérifier les noms exacts
print("Colonnes dans reuse_inventory:")
print(reuse_inventory.columns)

# Préparation des données de sortie
table_features = ["Element", "Category", "e-BKP_category", "Material type", "Reuse_origin", "FU_quantity", "FU_unit", "Mass"]
output_table = reuse_inventory[table_features].copy()
output_table["FU_unit"] = output_table["FU_unit"].apply(lambda unit: f"{unit}/m² SRE")
output_table["Mass"] = output_table["Mass"] / 1000  # Conversion en tonnes
output_table = output_table.sort_values(by="Mass", ascending=False)

# Calculs des masses réutilisées
reused_mass = output_table["Mass"].sum()  # tonnes
reused_mass_percent = 100 * reused_mass / (faraday_pd["Mass"].sum() / 1000)
reused_mass_area = 1000 * reused_mass / project_SRE

# Calcul des GWP pour les scénarios tout neuf et réutilisé
GWP_A1A5_allnew = faraday_pd[["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A1-A5"]].sum().sum()  # kgCO2/m²
GWP_A1A5_reuse = faraday_pd[["GWP_A1-A3", "GWP_A4", "GWP_A1-A5"]].sum().sum()  # kgCO2/m²
GWP_A1A5_diff = (GWP_A1A5_allnew - GWP_A1A5_reuse) * project_SRE / 1000  # tCO2 A1-A5
GWP_A1A5_var = 100 * (GWP_A1A5_reuse - GWP_A1A5_allnew) / GWP_A1A5_allnew

# Évitement des émissions de GWP par la réutilisation
GWP_avoided_disposal = reuse_inventory["GWP_New_C1-C4"] * reuse_inventory["Service_life_extension"]
GWP_avoided_disposal_total = GWP_avoided_disposal.fillna(0).sum() * project_SRE / 1000  # tCO2 avoided disposal

# Produits biosourcés neufs et réemployés
biogenic_inventory = faraday_pd[faraday_pd["Material type"] == "Biogenic"].copy()

# Fonction hypothétique pour calculer le CO2 stocké
def calc_stored_bio_co2(inventory):
    stored_co2 = inventory["Biogenic_carbon_content"] * inventory["Service_life_extension"]
    return stored_co2.fillna(0)

# Calculer le CO2 stocké
stored_co2_reuse = calc_stored_bio_co2(reuse_inventory)
stored_co2_new = calc_stored_bio_co2(new_inventory)

# Créer un DataFrame avec les bonnes valeurs
comp_co2 = pd.DataFrame({
    "Element": reuse_inventory["Element"],
    "Stored CO2": stored_co2_reuse,
    "C1C4": reuse_inventory["GWP_New_C1-C4"]
})

# Assurez-vous que les index sont alignés
comp_co2 = comp_co2.reset_index(drop=True)


# Utilisation de ressources non renouvelables
PENR_feedstock_col = "PE-NR_use_feedstock"  # Nom de colonne corrigé
if PENR_feedstock_col in reuse_inventory.columns:
    PENR_feedstock = reuse_inventory[PENR_feedstock_col].sum() * project_SRE
else:
    print(f"Colonne {PENR_feedstock_col} non trouvée dans reuse_inventory.")

# Tableau de résultats
results_actual_reuse = faraday_pd[["GWP_A1-A3", "GWP_A4", "GWP_A1-A5", "UBP_A1-A3", "UBP_A4", "UBP_A1-A5", "PE-NR_A1-A3", "PE-NR_A4", "PE-NR_A1-A5"]].fillna(0).sum()
results_actual_reuse_reuse = reuse_inventory[["GWP_A1-A3", "GWP_A4", "GWP_A1-A5", "UBP_A1-A3", "UBP_A4", "UBP_A1-A5", "PE-NR_A1-A3", "PE-NR_A4", "PE-NR_A1-A5"]].fillna(0).sum()
results_actual_reuse_new = new_inventory[["GWP_A1-A3", "GWP_A4", "GWP_A1-A5", "UBP_A1-A3", "UBP_A4", "UBP_A1-A5", "PE-NR_A1-A3", "PE-NR_A4", "PE-NR_A1-A5"]].fillna(0).sum()
results_all_new = faraday_pd[["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A1-A5", "UBP_New_A1-A3", "UBP_New_A4", "UBP_New_A1-A5", "PE-NR_New_A1-A3", "PE-NR_New_A4", "PE-NR_New_A1-A5"]].fillna(0).sum()

results = pd.DataFrame([results_actual_reuse, results_actual_reuse_reuse / results_actual_reuse, results_actual_reuse_new / results_actual_reuse])

diff = results_actual_reuse.values - results_all_new.values

var = []
for i in range(len(diff)):
    var.append(diff[i] / results_all_new.values[i])

results_var_gwp = (faraday_pd[["GWP_A1-A3", "GWP_A4", "GWP_A1-A5"]].sum().sum() - faraday_pd[["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A1-A5"]].sum().sum()) / faraday_pd[["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A1-A5"]].sum().sum()

# Périmètre GWP
reuse_inventory[["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A1-A5"]].sum().sum() / faraday_pd[["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A1-A5"]].sum().sum()
(reuse_inventory[["GWP_A1-A3", "GWP_A4", "GWP_A1-A5"]].sum().sum() - reuse_inventory[["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A1-A5"]].sum().sum()) / reuse_inventory[["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A1-A5"]].sum().sum()
