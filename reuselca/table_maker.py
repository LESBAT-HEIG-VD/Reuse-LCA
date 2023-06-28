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
            "Element_area", "Volume", "Mass", "Mass with loss", "Loss", "Loss data rating",
            "DIS - Operating time", "DIS - Operating unit", "DIS - Machine power",
            "DIS - Energy type", "DIS - Default dismantling", "GWP_DIS",
            "TR_A2 - Total distance", "TR_A2 - Data rating distance", "TR_A2 - Vehicle", "TR_A2 - Data rating vehicle", "GWP_TR_A2",
            "ST - Storage place", "ST - Data rating storage place", "ST - Storage space", "ST - Unit of storage",
            "ST - Default space", "ST - Duration (years)", "ST - Default duration", "GWP_ST",
            "MOD - Data type", "MOD - LCA dataset name", "MOD - Ratio impact", "MOD - Operating time",
            "MOD - Operating unit", "MOD - Machine power", "MOD - Energy type", "MOD - Data rating", "GWP_MOD",
            "KBOB_group", "KBOB_dataset_name", "KBOB_dataset_id", "Function_quality", "Function_quality_data_rating",
            "GWP_LOSSES", "TR_A4 - Total distance", "TR_A4 - Data rating distance", "TR_A4 - Vehicle", "TR_A4 - Data rating vehicle", "GWP_TR_A4",
            "GWP_A1-A5", "GWP_New_A1-A5", "GWP_Avoided_prod", "GWP_Avoided_Waste", "GWP_Avoided_Total"]

    full_table = reused_data[cols]
    # convert to int
    int_cols = ["Map_id", "Age", "Reference_service_lifetime", "Service_life_extension",
                "DIS - Machine power", "TR_A2 - Total distance"
                ]
    full_table[int_cols] = full_table[int_cols].fillna(0)
    full_table[int_cols] = full_table[int_cols].astype(int)

    float_cols = ["Element_area", "Volume", "Mass", "Mass with loss", "Loss",
                "DIS - Operating time", "GWP_DIS", "GWP_TR_A2", "ST - Storage space",
                "ST - Duration (years)", "GWP_ST", "MOD - Ratio impact",
                "MOD - Operating time", "GWP_MOD", "GWP_LOSSES","GWP_TR_A4",
                "GWP_A1-A5", "GWP_New_A1-A5", "GWP_Avoided_prod", "GWP_Avoided_Waste", "GWP_Avoided_Total"
                ]
    full_table[float_cols] = full_table[float_cols].fillna(0)
    # full_table[float_cols] = full_table[float_cols].astype(float)
    full_table[float_cols] = full_table[float_cols].apply(pd.to_numeric, errors='coerce')

    def format_float(num):
        if isinstance(num, float):
            if num == 0:
                return '{:.0f}'.format(num)
            if -0.01 < num < 0.01:
                return '{:.4f}'.format(num)  # Two digits after decimal for numbers between -1 and 1
            if -1 < num < 1:
                return '{:.3f}'.format(num)  # Two digits after decimal for numbers between -1 and 1
            if -10< num < 10:
                return '{:.2f}'.format(num)  # Two digits after decimal for numbers between -1 and 1
            if -100 < num < 100:
                return '{:.1f}'.format(num)  # Two digits after decimal for numbers between -1 and 1
            else:
                return '{:.0f}'.format(num)
        else:
            return num

    def return_percentage(value):
        if isinstance(value,str):
            return '{:.0%}'.format(float(value))
        else:
            return '{:.0%}'.format(value)

    full_table["Loss"] = full_table["Loss"].apply(return_percentage)

    # dismantling
    def create_losses_col(row):
        los_rating = row["Loss data rating"]
        return get_rating_dot(los_rating)+row["Loss"]

    def create_dis_col(row):
        dis_rating = row["DIS - Default dismantling"]
        if pd.isna(dis_rating):
            return get_rating_dot("Not modelled (no data)")+"No information"
        elif dis_rating == "Default (no data)":
            return get_rating_dot(dis_rating)+'UVEK DQRv2 2021: deconstruction, average/CH U'
        elif dis_rating == "Not concerned":
            if "surplus" in row["Reuse_origin"]:
                return get_rating_dot(dis_rating)+"Surplus, no dismantling"
            else:
                return get_rating_dot(dis_rating)+"No dismantling"
        else:
            return get_rating_dot(dis_rating)+'{} W, {} (CH), {} {} '.format(row["DIS - Machine power"],row["DIS - Energy type"],
                                             row["DIS - Operating time"],row["DIS - Operating unit"])

    def create_st_col(row):
        place_rating = row["ST - Data rating storage place"]
        duration_rating = row["ST - Default duration"]
        space_rating = row["ST - Default space"]

        if place_rating == "Not concerned" or duration_rating == "Not concerned" or space_rating == "Not concerned":
            return get_rating_dot("Not concerned")+"No storage"
        elif pd.isna(row["ST - Storage place"]) or row["ST - Storage place"]=='nan':
            return get_rating_dot("Not modelled (no data)")+"No information"
        else:
            place = get_rating_dot(place_rating)+'{}'.format(row["ST - Storage place"])

        if duration_rating == "Default (no data)":
            duration = get_rating_dot(duration_rating)+'{:.2f} a'.format(Building.hypotheses["Default storage duration (year)"].values[0])
        else:
            duration = get_rating_dot(duration_rating)+'{:.2f} a'.format(row["ST - Duration (years)"])

        if space_rating == "Default (no data)":
            if row["ST - Unit of storage"] == "m2":
                space = get_rating_dot(space_rating)+'{:.3f} m2'.format(row["Element_area"])
            elif row["ST - Unit of storage"] == "m3":
                space = get_rating_dot(space_rating)+'{:.3f} m3'.format(row["Volume"])
        else:
            space = get_rating_dot(space_rating)+'{:.3f}'.format(row["ST - Storage space"])+' '+row["ST - Unit of storage"]
        return duration+', '+space+', '+place

    def create_mod_col(row):
        mod_rating = row["MOD - Data rating"]
        if mod_rating == "Not concerned":
            return get_rating_dot(mod_rating)+'No modification'
        elif mod_rating == "Not modelled (no data)":
            return get_rating_dot(mod_rating)+row["MOD - LCA dataset name"]
        else:
            if pd.isna(row["MOD - Data type"]) or row["MOD - Data type"]=='nan':
                return get_rating_dot("Not modelled (no data)") + "No information"
            elif row["MOD - Data type"] == "Reuse-LCA Modifications":
                return get_rating_dot(mod_rating)+"Reuse-LCA: {}".format(row["MOD - LCA dataset name"])
            elif row["MOD - Data type"] == "Energy only":
                return get_rating_dot(mod_rating)+"{} W, {} (CH), {} {} ".format(row["MOD - Machine power"],row["MOD - Energy type"],
                                                 row["MOD - Operating time (hours)"],row["MOD - Operating unit"])

    def create_tr_a2_col(row):
        dist_rating = row["TR_A2 - Data rating distance"]
        veh_rating = row["TR_A2 - Data rating vehicle"]
        if pd.isna(dist_rating) or dist_rating == 'nan':
            return get_rating_dot("Not modelled (no data)") + "No information"
        if dist_rating == "Not concerned" and veh_rating == "Not concerned":
            return get_rating_dot("Not concerned")+"No intermediate transport"
        elif dist_rating == "Not concerned" or veh_rating == "Not concerned":
            return get_rating_dot("Not modelled (no data)") + "No complete information"
        else:
            return get_rating_dot(dist_rating)+'{:.0f} km, '.format(row["TR_A2 - Total distance"])+get_rating_dot(veh_rating)+row["TR_A2 - Vehicle"]

    def create_tr_a4_col(row):
        dist_rating = row["TR_A4 - Data rating distance"]
        veh_rating = row["TR_A4 - Data rating vehicle"]
        if pd.isna(dist_rating) or dist_rating == 'nan':
            return get_rating_dot("Not modelled (no data)") + "No information"
        if dist_rating == "Not concerned" and veh_rating == "Not concerned":
            return get_rating_dot("Not concerned")+"No intermediate transport"
        elif dist_rating == "Not concerned" or veh_rating == "Not concerned":
            return get_rating_dot("Not modelled (no data)") + "No complete information"
        else:
            return get_rating_dot(dist_rating)+'{:.0f} km, '.format(row["TR_A4 - Total distance"])+get_rating_dot(veh_rating)+row["TR_A4 - Vehicle"]

    def create_neweq_col(row):
        function_rating = row["Function_quality_data_rating"]
        if "Reuse-LCA" in row["KBOB_group"]:
            prefix = "Reuse-LCA: "
        else:
            prefix = "KBOB: "
        if function_rating == "Default (no data)":
            percent = "(" + get_rating_dot(function_rating) + "100%)"
        else:
            percent = "("+get_rating_dot(function_rating)+return_percentage(row["Function_quality"])+")"
        return prefix+row["KBOB_dataset_name"]+" "+percent

    def create_lifespan_ext(row):
        return get_rating_dot("Hypothesis")+"{}".format(row["Service_life_extension"])

    def create_reduction_col(row):
        value = (row["GWP_A1-A5"]-row["GWP_New_A1-A5"])/row["GWP_New_A1-A5"]
        return return_percentage(format_float(value))

    full_table["Losses"] = full_table.apply(lambda row: create_losses_col(row), axis=1)
    full_table["Dismantling"] = full_table.apply(lambda row: create_dis_col(row), axis=1)
    full_table["Storage"] = full_table.apply(lambda row: create_st_col(row), axis=1)
    full_table["Modification"] = full_table.apply(lambda row: create_mod_col(row), axis=1)
    full_table["Transport A2"] = full_table.apply(lambda row: create_tr_a2_col(row), axis=1)
    full_table["Transport A4"] = full_table.apply(lambda row: create_tr_a4_col(row), axis=1)
    full_table["Conventional product and end-of-life"] = full_table.apply(lambda row: create_neweq_col(row), axis=1)
    full_table["Service lifespan extension"] = full_table.apply(lambda row: create_lifespan_ext(row), axis=1)
    full_table["Difference of production's GWP (%)"] = full_table.apply(lambda row: create_reduction_col(row), axis=1)

    cols2 = ["Map_id", "Element", "Category",
             "Reuse_origin", "Age", "Service lifespan extension",
             "Element_area", "Volume", "Mass", "Mass with loss",
             "Conventional product and end-of-life", "KBOB_dataset_id",
             "Losses","Dismantling","Storage","Modification",
             "Transport A2","Transport A4",
             "GWP_LOSSES","GWP_DIS","GWP_ST","GWP_MOD","GWP_TR_A2","GWP_TR_A4",
             "GWP_A1-A5", "GWP_New_A1-A5", "GWP_Avoided_prod", "GWP_Avoided_Waste", "GWP_Avoided_Total", "Difference of production's GWP (%)"]

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
                     "Losses":"Losses",
                     "Service_life_extension":"Service lifespan extension",
                     "Dismantling inventory":"Dismantling",
                     "GWP_DIS":"GWP: Dismantling",
                     "Transport A2 inventory":"Transport A2",
                     "TR_A2 - Data rating": "Transport A2 data rating",
                     "GWP_TR_A2":"GWP: Transport A2",
                     "Storage inventory":"Storage",
                     "GWP_ST":"GWP: Storage",
                     "Modification inventory":"Modification",
                     "GWP_MOD":"GWP: Modification",
                     "Transport A4 inventory":"Transport A4",
                     "TR_A4 - Data rating":"Transport A4 data rating",
                     "GWP_TR_A4":"GWP: Transport A4",
                     "KBOB_dataset_name":"KBOB dataset (for new prod. and EoL)",
                     "KBOB_dataset_id": "KBOB dataset id",
                     "GWP_LOSSES":"GWP: Losses",
                     "GWP_A1-A5":"GWP: Total A1-A4",
                     "GWP_New_A1-A5":"GWP: Conventional equivalent A1-A4",
                     "GWP_Avoided_prod":"GWP: Avoided, production",
                    "GWP_Avoided_Waste":"GWP: Avoided, waste treatment",
                    "GWP_Avoided_Total":"GWP: Avoided, total",
                     "Difference of production's GWP (%)":"GWP: difference in production (%)"
                     }

    final_table = filtered_table.rename(columns=mapping_names)
    # # Apply formatting to DataFrame
    final_table = final_table.applymap(format_float)
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
