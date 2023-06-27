import pandas as pd

from reuselca import *
from math import isnan
from reuselca.utils_html import get_rating_dot

def generate_table(case_name):
    Building = utils.Building(case_name)

pd.options.display.float_format = '{0:.2f}'.format


if __name__ == "__main__":
    cfg = get_cfg()
    cases = cfg["cases"]
    # for case in cases:
    #     generate_table(case, nav_bar)
    Building = utils.Building("Faraday_cisbat")
    reused_data = Building.data[Building.data["Status"]=="Reused"]

    cols = ["Map_id", "Element", "Category", "Reuse_origin", "Age",
            "Reference_service_lifetime", "Service_life_extension",
            "Element_area", "Volume", "Mass", "Mass with loss", "Loss",
            "DIS - Operating time", "DIS - Operating unit", "DIS - Machine power",
            "DIS - Energy type", "DIS - Default dismantling", "GWP_DIS",
            "TR_A2 - Total distance", "TR_A2 - Data rating", "TR_A2 - Vehicle", "GWP_TR_A2",
            "ST - Storage place", "ST - Storage space", "ST - Unit of storage",
            "ST - Default space", "ST - Duration (years)", "ST - Default duration", "GWP_ST",
            "MOD - Data type", "MOD - LCA dataset name", "MOD - Ratio impact", "MOD - Operating time (hours)",
            "MOD - Operating unit", "MOD - Machine power", "MOD - Energy type", "GWP_MOD",
            "KBOB_dataset_name", "KBOB_dataset_id", "GWP_LOSSES",
            "TR_A4 - Total distance", "TR_A4 - Data rating", "TR_A4 - Vehicle", "GWP_TR_A4",
            "GWP_A1-A5", "GWP_New_A1-A5", "GWP_Avoided_prod", "GWP_Avoided_Waste", "GWP_Avoided_Total"]

    full_table = reused_data[cols]
    # convert to int
    for col in ["Map_id", "Age", "Reference_service_lifetime", "Service_life_extension",
                "DIS - Machine power", "TR_A2 - Total distance"
                ]:
        full_table[col] = full_table[col].fillna(0)
        full_table[col] = full_table[col].astype(int)

    def return_percentage(value):
        return '{:.0%}'.format(value)

    full_table["Loss"] = full_table["Loss"].apply(return_percentage)

    # dismantling
    def create_dis_col(row):
        dis_rating = row["DIS - Default dismantling"]
        if dis_rating == "Default (no data)":
            return get_rating_dot(dis_rating)+'UVEK DQRv2 2021: deconstruction, average/CH U'
        if dis_rating == "Estimate":
            return get_rating_dot(dis_rating)+'{} W, {} (CH), {} {} '.format(row["DIS - Machine power"],row["DIS - Energy type"],
                                             row["DIS - Operating time"],row["DIS - Operating unit"])
        if row["DIS - Default dismantling"] == "Not concerned":
            return get_rating_dot(dis_rating)+' -'

    def create_st_col(row):
        duration_rating = row["ST - Default duration"]
        space_rating = row["ST - Default space"]
        if pd.isna(row["ST - Storage place"]):
            return "No storage"
        if pd.isna(duration_rating):
            return "No storage"
        elif duration_rating == "Default (no data)":
            duration = get_rating_dot(duration_rating)+'{:.2f} years'.format(Building.hypotheses["Default storage duration (year)"].values[0])
        elif duration_rating == "Estimate":
            duration = get_rating_dot(duration_rating)+'{:.2f} years'.format(row["ST - Duration (years)"])
        if pd.isna(space_rating):
            return "No storage"
        elif space_rating == "Default (no data)":
            if row["ST - Unit of storage"] == "m2":
                space = get_rating_dot(space_rating)+'{:.3f} m2'.format(row["Element_area"])
            elif row["ST - Unit of storage"] == "m3":
                space = get_rating_dot(space_rating)+'{:.3f} m3'.format(row["Volume"])
        elif space_rating == "Estimate":
            if row["ST - Unit of storage"] == "m2":
                space = get_rating_dot(space_rating)+'{:.3f} m2'.format(row["ST - Storage space"])
            elif row["ST - Unit of storage"] == "m3":
                space = get_rating_dot(space_rating)+'{:.3f} m3'.format(row["ST - Storage space"])
        return duration+', '+space+' in {}'.format(row["ST - Storage place"])

    def create_mod_col(row):
        if pd.isna(row["MOD - Data type"]):
            return "-"
        elif row["MOD - Data type"] == "Reuse-LCA Modifications":
            return "Reuse-LCA dataset: {} ({:.2f})".format(row["MOD - LCA dataset name"], row["MOD - Ratio impact"])
        elif row["MOD - Data type"] == "Energy only":
            return "{} W, {} (CH), {} {} ".format(row["MOD - Machine power"],row["MOD - Energy type"],
                                             row["MOD - Operating time (hours)"],row["MOD - Operating unit"])
    def create_tr_a2_col(row):
        tr_rating = row["TR_A2 - Data rating"]
        return get_rating_dot(tr_rating)+"{:.0f} km, {}".format(row["TR_A2 - Total distance"], row["TR_A2 - Vehicle"])
    def create_tr_a4_col(row):
        tr_rating = row["TR_A4 - Data rating"]
        return get_rating_dot(tr_rating)+"{:.0f} km, {}".format(row["TR_A4 - Total distance"], row["TR_A4 - Vehicle"])

    full_table["Dismantling inventory"] = full_table.apply(lambda row: create_dis_col(row), axis=1)
    full_table["Storage inventory"] = full_table.apply(lambda row: create_st_col(row), axis=1)
    full_table["Modification inventory"] = full_table.apply(lambda row: create_mod_col(row), axis=1)
    full_table["Transport A2 inventory"] = full_table.apply(lambda row: create_tr_a2_col(row), axis=1)
    full_table["Transport A4 inventory"] = full_table.apply(lambda row: create_tr_a4_col(row), axis=1)

    cols2 = ["Map_id", "Element", "Category", "Reuse_origin", "Age",
             "Element_area", "Volume", "Mass", "Mass with loss", "Loss",
             "Service_life_extension",
             "Dismantling inventory", "DIS - Default dismantling", "GWP_DIS",
             "Transport A2 inventory", "TR_A2 - Data rating", "GWP_TR_A2",
             "Storage inventory", "GWP_ST",
             "Modification inventory", "GWP_MOD",
             "Transport A4 inventory", "TR_A4 - Data rating", "GWP_TR_A4",
             "KBOB_dataset_name", "KBOB_dataset_id","GWP_LOSSES",
             "GWP_A1-A5", "GWP_New_A1-A5", "GWP_Avoided_prod", "GWP_Avoided_Waste", "GWP_Avoided_Total"]

    filtered_table = full_table[cols2]

    mapping_names = {"Map_id": "n°",
                     "Element":"Element",
                     "Category":"Category",
                     "Reuse_origin":"Origin",
                     "Age":"Age",
                     "Element_area":"Area (m²)",
                     "Volume":"Volume (m3)",
                     "Mass":"Mass used (kg)",
                     "Mass with loss":"Mass before losses (kg)",
                     "Loss":"Losses",
                     "Service_life_extension":"Extension of service lifespan",
                     "Dismantling inventory":"Dismantling LCI",
                     "DIS - Default dismantling":"Dismantling data rating",
                     "GWP_DIS":"Dismantling GWP (kg CO2eq.)",
                     "Transport A2 inventory":"Transport A2 LCI",
                     "TR_A2 - Data rating": "Transport A2 data rating",
                     "GWP_TR_A2":"Transport A2 GWP (kg CO2eq.)",
                     "Storage inventory":"Storage LCI",
                     "GWP_ST":"Storage GWP (kg CO2eq.)",
                     "Modification inventory":"Modification LCI",
                     "GWP_MOD":"Modification GWP (kg CO2eq.)",
                     "Transport A4 inventory":"Transport A2 GWP (kg CO2eq.)",
                     "TR_A4 - Data rating":"Transport A4 data rating",
                     "GWP_TR_A4":"Transport A4 GWP (kg CO2eq.)",
                     "KBOB_dataset_name":"KBOB dataset (for new prod. and EoL)",
                     "KBOB_dataset_id": "KBOB dataset id",
                     "GWP_LOSSES":"Losses GWP (kg CO2eq.)",
                     "GWP_A1-A5":"Project A1-A4 GWP (kg CO2eq.)",
                     "GWP_New_A1-A5":"New prod. eq. A1-A4 GWP (kg CO2eq.)",
                     "GWP_Avoided_prod":"Avoided production GWP (kg CO2eq.)",
                    "GWP_Avoided_Waste":"Avoided waste treatment GWP (kg CO2eq.)",
                    "GWP_Avoided_Total":"Total avoided GWP (kg CO2eq.)"
                     }

    final_table = filtered_table.rename(columns=mapping_names)
    html = final_table.to_html(index=False)
    html = html.replace("&amp;","&")
    html = html.replace("&lt;","<")
    html = html.replace("&gt;",">")
    print(html)

    # map_dict = {"Map_id": "n°",
    #         "Element":"Element",
    #         "Category":"Category",
    #         "Reuse_origin":"Origin",
    #         "Age":"Age",
    #         "Reference_service_lifetime":"Reference service lifespan",
    #         "Service_life_extension":"Extension of service lifespan",
    #         "Element_area":"Area (m²)",
    #         "Volume":"Volume (m3)",
    #         "Mass":"Mass (kg)",
    #         "Mass with loss": "Mass before losses (kg)",
    #         "Loss":"Losses",
    #         "DIS - Operating time":, "DIS - Operating unit", "DIS - Machine power",
    #         "DIS - Energy type", "DIS - Default dismantling", "GWP_DIS",
    #         "TR_A2 - Total distance", "TR_A2 - Data rating", "TR_A2 - Vehicle", "GWP_TR_A2",
    #         "ST - Storage place", "ST - Storage space", "ST - Unit of storage",
    #         "ST - Default space", "ST - Duration (years)", "ST - Default duration", "GWP_ST",
    #         "MOD - Data type", "MOD - LCA dataset name", "MOD - Ratio impact", "MOD - Operating time (hours)",
    #         "MOD - Operating unit", "MOD - Machine power", "MOD - Energy type", "GWP_MOD",
    #         "KBOB_dataset_name", "KBOB_dataset_id",
    #         "TR_A4 - Total distance", "TR_A4 - Data rating", "TR_A4 - Vehicle", "GWP_TR_A4",
    #         "GWP_A1-A5", "GWP_New_A1-A5", "GWP_Avoided_prod", "GWP_Avoided_Waste", "GWP_Avoided_Total"]
