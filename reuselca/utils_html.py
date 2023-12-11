import pandas as pd

def get_rating_dot(rating):
    # From https://www.color-hex.com/color-palette/30630
    if rating == "Project specific":
        return '<span style="color: #57e32c;" class="data-rating-dot"><b>&bull;</b></span>'
    elif rating == "Not concerned":
        return '<span style="color: #57e32c;" class="data-rating-dot"><b>&bull;</b></span>'
    elif rating == "Estimate":
        return '<span style="color: #b7dd29;" class="data-rating-dot"><b>&bull;</b></span>'
    elif rating == "Hypothesis":
        return '<span style="color: #ffe234;" class="data-rating-dot"><b>&bull;</b></span>'
    elif rating == "Default (no data)":
        return '<span style="color: #ffa534;" class="data-rating-dot"><b>&bull;</b></span>'
    elif rating == "Not modelled (no data)":
        return '<span style="color: #ff4545;" class="data-rating-dot"><b>&bull;</b></span>'

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

def create_losses_col(row):
    los_rating = row["Loss data rating"]

    return get_rating_dot(los_rating)+format_float(return_percentage(row["Loss"]))

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

def create_st_col(row, default_storage):
    place_rating = row["ST - Data rating storage place"]
    duration_rating = row["ST - Default duration"]
    space_rating = row["ST - Default space"]

    if place_rating == "Not concerned" or duration_rating == "Not concerned" or space_rating == "Not concerned":
        return get_rating_dot("Not concerned")+"No storage"
    elif pd.isna(row["ST - Storage place"]) or row["ST - Storage place"]=='nan' or place_rating == "Not modelled (no data)":
        return get_rating_dot("Not modelled (no data)")+"No information"
    else:
        place = get_rating_dot(place_rating)+'{}'.format(row["ST - Storage place"])

    if duration_rating == "Default (no data)":
        duration = get_rating_dot(duration_rating)+'{:.2f} a'.format(default_storage)
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
                                             row["MOD - Operating time"],row["MOD - Operating unit"])

def create_tr_a2_col(row):
    dist_rating = row["TR_A2 - Data rating distance"]
    veh_rating = row["TR_A2 - Data rating vehicle"]
    try:
        if pd.isna(dist_rating) or dist_rating == 'nan':
            return get_rating_dot("Not modelled (no data)") + "No information"
        if dist_rating == "Not concerned" and veh_rating == "Not concerned":
            return get_rating_dot("Not concerned")+"No intermediate transport"
        elif dist_rating == "Not concerned" or veh_rating == "Not concerned":
            return get_rating_dot("Not modelled (no data)") + "No complete information"
        elif dist_rating == "Not modelled (no data)" or veh_rating == "Not modelled (no data)":
            return get_rating_dot("Not modelled (no data)")
        else:
            return get_rating_dot(dist_rating)+'{:.0f} km, '.format(row["TR_A2 - Total distance"])+get_rating_dot(veh_rating)+row["TR_A2 - Vehicle"]
    except TypeError:
        print("Error - Element concerned: ", row['Element'])
        raise

def create_tr_a4_col(row):
    dist_rating = row["TR_A4 - Data rating distance"]
    veh_rating = row["TR_A4 - Data rating vehicle"]
    if pd.isna(dist_rating) or dist_rating == 'nan':
        return get_rating_dot("Not modelled (no data)") + "No information"
    if dist_rating == "Not concerned" and veh_rating == "Not concerned":
        return get_rating_dot("Not concerned")+"No intermediate transport"
    elif dist_rating == "Not concerned" or veh_rating == "Not concerned":
        return get_rating_dot("Not modelled (no data)") + "No complete information"
    elif dist_rating == "Not modelled (no data)" or veh_rating == "Not modelled (no data)":
        return get_rating_dot("Not modelled (no data)")
    else:
        return get_rating_dot(dist_rating)+'{:.0f} km, '.format(row["TR_A4 - Total distance"])+get_rating_dot(veh_rating)+row["TR_A4 - Vehicle"]

def create_neweq_col(row):
    function_rating = row["Function_quality_data_rating"]
    try:
        if "Reuse-LCA" in row["KBOB_group"]:
            prefix = "Reuse-LCA: "
        else:
            prefix = "KBOB: "
        if function_rating == "Default (no data)":
            percent = "(" + get_rating_dot(function_rating) + "100%)"
        else:
            percent = "("+get_rating_dot(function_rating)+return_percentage(row["Function_quality"])+")"
        return prefix+row["KBOB_dataset_name"]+" "+percent
    except TypeError:
        print("Error - Element concerned: ", row['Element'])
        raise

def create_lifespan_ext(row):
    return get_rating_dot("Hypothesis")+"{}".format(row["Service_life_extension"])

def create_reduction_col(row):
    value = (row["GWP_A1-A5"]-row["GWP_New_A1-A5"])/row["GWP_New_A1-A5"]
    return return_percentage(format_float(value))


