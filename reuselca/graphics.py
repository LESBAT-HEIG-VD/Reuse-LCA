import plotly.graph_objects as go
import plotly.express as px
import os
from reuselca.utils import Building, get_cfg, ROOT_DIR
from reuselca.utils_html import *
import pandas as pd

cfg = get_cfg()

scope = ["A1-A3", "A4", "B4", "C1-C4", "Total"]
impact_names = ["GWP", "UBP", "PE-NR"]
imp_labels = [impact+"_"+module for module in scope for impact in impact_names]
imp_labels_new = [impact+"_"+"New"+"_"+module for module in scope for impact in impact_names]

impact_name = {"GWP":"GHG emission (kg CO2eq./kg)",
               "UBP":"Ecological Scarcity 2021 (UBP/kg)",
               "PE-NR":"Primary energy, non renewable (kWh/kg)"
               }

def building_impacts_table(Building, variant="Actual"):
    if variant == "Actual":
        impacts = Building.impacts
        title = "Table 1: Building LCA impacts - Actual design with reuse"
        html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.case+cfg['figures_suffix']['impacts_table'])
    elif variant == "New":
        impacts = Building.impacts_new
        title = 'Table 1: Building LCA impacts - "Only new" variant'
        html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.case+cfg['figures_suffix']['impacts_table_new'])

    ordered_cols = ["Impact category","A1-A3","A4","B4","C1-C4","Total"]

    results_sqm = impacts.div(Building.sqm).round(1)
    results_sqm["Impact category"] = impacts.index
    results_sqm = results_sqm[ordered_cols]

    results_sqm_year = impacts.div(Building.sqm).div(Building.lifespan).round(1)
    results_sqm_year["Impact category"] = impacts.index
    results_sqm_year = results_sqm_year[ordered_cols]

    fig = go.Figure()
    fig.add_trace(
        go.Table(
            header=dict(values=ordered_cols),
            cells=dict(values= [results_sqm[col] for col in ordered_cols])
        )
    )
    fig.update_layout(
        updatemenus = [dict(
            buttons=[
                dict(label='[Impact]/m²',
                     method='restyle',
                     args=[{'cells': {'values': results_sqm.values.T}}]),
    dict(label='[Impact]/m²/year',
                     method='restyle',
                     args=[{'cells': {'values': results_sqm_year.values.T}}]),

    ],
            showactive = True,
            direction = 'down',
            x = 0,
            y = 1,

        ),
        ],
        title=title
        )


    fig.show()
    fig.write_html(html_path)
    return fig

def material_sunburst(Building):
    data = Building.data
    title = "Mass-share of Reused and New Components by Material Type"
    html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.case+cfg['figures_suffix']['material_sunburst'])
    # Aggregate the data by reuse, material type, and component
    agg_data = data.groupby(["Status", "Material type", "Element"]).agg({"Mass": "sum"}).reset_index()

    agg_data["Mass"] = agg_data["Mass"] / 1000
    # Calculate the share of each row as a percentage of the total mass
    agg_data["Share"] = agg_data["Mass"] / Building.total_mass * 100 * 1000

    agg_data["Share text"] = agg_data["Share"].apply(lambda x: "{:.1f}%".format(x) if x < 0.1 else "{:.2f}%".format(x))

    # Create a sunburst chart
    fig = px.sunburst(
        agg_data,
        path=["Status", "Material type", "Element"],
        values="Share",
    )

    fig.update_traces(
        hovertemplate = "<b>%{label}</b><br>" +
                      "Share: %{value:.2f}%<br>"
    )

    fig.update_layout(title_text=title)
    fig.show()
    fig.write_html(html_path)
    return agg_data

def material_sunburst_ebkp(Building):
    data = Building.data
    title = "Share of Reused and New Components by e-BKP category"
    html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.case+cfg['figures_suffix']['material_sunburst_ebkp'])
    ebkp = pd.read_csv(os.path.join(ROOT_DIR,cfg['data_folder'],"e-bkp-classification_EN.csv"),
        delimiter=";", encoding='latin-1', header=None, names=["Category", "Description"])

    # Aggregate the data by reuse, material type, and component


    agg_data = data.groupby(["Status", "e-BKP_0", "e-BKP_1", "e-BKP_category"]).agg({"Mass": "sum"}).reset_index()

    total_mass_df = data.groupby("Status").agg({"Mass": "sum"}).reset_index()
    agg_data["Mass"] = agg_data["Mass"] / 1000
    # Calculate the share of each row as a percentage of the total mass
    agg_data["Share"] = agg_data["Mass"] / Building.total_mass * 100 * 1000

    agg_data["Share text"] = agg_data["Share"].apply(lambda x: "{:.1f}%".format(x) if x < 0.1 else "{:.2f}%".format(x))

    agg_data["desc 0"] = agg_data["e-BKP_0"].apply(lambda x: ebkp[ebkp["Category"]==x]["Description"].values[0])
    agg_data["desc 1"] = agg_data["e-BKP_1"].apply(lambda x: ebkp[ebkp["Category"]==x]["Description"].values[0])
    agg_data["desc 2"] = agg_data["e-BKP_category"].apply(lambda x: ebkp[ebkp["Category"]==x]["Description"].values[0])

    # Create a sunburst chart
    fig = px.sunburst(
        agg_data,
        path=["Status", "e-BKP_0", "e-BKP_1", "e-BKP_category"],
        values="Share",
        # hover_data=["Mass"],
        custom_data=["desc 0", "desc 1", "desc 2"]

    )

    fig.update_traces(
        hovertemplate = "<b>%{label}</b><br>" +
                      "Share: %{value:.2f}%<br>"+
                      "%{customdata[0]}<br>"+
                        "%{customdata[1]}<br>" +
                        "%{customdata[2]}<br>"
    )

    fig.update_layout(title_text=title)
    fig.show()
    fig.write_html(html_path)
    return agg_data

def co2_sunburst(Building):
    # CO2 emissions for A1-A4 by material types and elements
    data = Building.data
    title = "GHG emissions over A1-A4 of Reused and New Components by Material Type"
    html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.case+cfg['figures_suffix']['co2_sunburst'])
    # Aggregate the data by reuse, material type, and component
    agg_data = data.groupby(["Status", "Material type", "Element"]).agg({"GWP_A1-A5": "sum"}).reset_index()

    # Calculate the share of each row as a percentage of the total mass
    agg_data["Share"] = agg_data["GWP_A1-A5"]*100 / agg_data["GWP_A1-A5"].sum()

    agg_data["Share text"] = agg_data["Share"].apply(lambda x: "{:.1f}%".format(x) if x < 0.1 else "{:.2f}%".format(x))

    # Create a sunburst chart
    fig = px.sunburst(
        agg_data,
        path=["Status", "Material type", "Element"],
        values="Share",
    )

    fig.update_traces(
        hovertemplate = "<b>%{label}</b><br>" +
                      "Share: %{value:.2f}%<br>"
    )

    fig.update_layout(title_text=title)
    fig.show()
    fig.write_html(html_path)
    return agg_data


def bar_reused_comp(Building, impact_label):
    import plotly.graph_objects as go
    import matplotlib as plt
    data = Building.data
    title = 'Comparison of the reused components with their "new" equivalent'
    html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.case+"_"+impact_label+cfg['figures_suffix']['reused_comp_bar'])
    if impact_label == "GWP":
        Building.case_bar_GWP_reused_components_html = html_path
    if impact_label == "UBP":
        Building.case_bar_UBP_reused_components_html = html_path
    if impact_label == "PE-NR":
        Building.case_bar_PE_NR_reused_components_html = html_path

    cmapping = plt.cm.get_cmap('Set2')
    colors = [plt.colors.rgb2hex(cmapping(i)) for i in range(4)]

    reuse_inventory = data[data["Status"] == "Reused"]
    reuse_components = reuse_inventory.groupby("Element")

    filter_imp = [i for i in imp_labels if impact_label in i]
    filter_imp_new = [i for i in imp_labels_new if impact_label in i]

    reused_comp = reuse_components.sum()[filter_imp].join(reuse_components.sum()["Mass"],
                                                                    how='outer')
    reused_comp = reused_comp[filter_imp].div(reused_comp["Mass"], axis=0).div(Building.results_factor)
    reused_comp["Component"] = reused_comp.index
    reused_comp["Status"] = "Reused"

    reused_comp_new = reuse_components.sum()[filter_imp_new].join(reuse_components.sum()["Mass"],
                                                                         how='outer')
    reused_comp_new = reused_comp_new[filter_imp_new].div(reused_comp_new["Mass"], axis=0).div(
        Building.results_factor)
    reused_comp_new = reused_comp_new.rename(
        columns={filter_imp_new[i]: filter_imp[i] for i in range(len(filter_imp))})
    reused_comp_new["Component"] = reused_comp_new.index
    reused_comp_new["Status"] = "New"

    results = pd.concat([pd.concat([reused_comp[["Component", col, "Status"]].rename( # ChatGPT proposition
        columns={"Component": "Component", col: impact_name[impact_label], "Status": "Status"}).assign(
        Step=col.replace(impact_label + "_", '')),
                                    reused_comp_new[["Component", col, "Status"]].rename(
                                        columns={"Component": "Component", col: impact_name[impact_label],
                                                 "Status": "Status"}).assign(Step=col.replace(impact_label + "_", ''))])
                         for col in filter_imp], ignore_index=True)

    fig = go.Figure()
    for r, c in zip([x for x in filter_imp], colors):
        step = r.replace(impact_label+"_", '')
        plot_df = results[results["Step"]==step]
        fig.add_trace(
            go.Bar(x=[plot_df["Status"], plot_df["Component"]], y=plot_df[impact_name[impact_label]].round(3), name=step, marker_color=c),
        )
    fig.update_layout(
        template="simple_white",
        xaxis=dict(title_text="Component"),
        yaxis=dict(title_text=impact_name[impact_label]),
        barmode="stack",
        title_text = title
    )

    fig.update_xaxes(tickangle= -45)
    fig.show()
    fig.write_html(html_path)

def generate_reuse_tables(Building):
    pd.options.display.float_format = '{0:.2f}'.format
    cfg = get_cfg()
    reused_data = Building.data[Building.data["Status"]=="Reused"]

    cols = ["Map_id", "Element", "Category", "Reuse_origin", "Age",
            "Reference_service_lifetime", "Service_life_extension",
            "Pieces","Element_area", "Volume", "Mass", "Mass with loss", "Loss", "Loss data rating",
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

    try:
        full_table = reused_data[cols]
    except KeyError as err:
        print('Error: ', err)
        print("Coming from Building Case: ", Building.case)
        raise

    # convert to int
    int_cols = ["Map_id", "Age", "Reference_service_lifetime", "Service_life_extension",
                "DIS - Machine power", "TR_A2 - Total distance"
                ]
    full_table[int_cols] = full_table[int_cols].fillna(0)
    full_table[int_cols] = full_table[int_cols].astype(int)

    def replace_pieces(row):
        if pd.isna(row["Pieces"]):
            return "-"
        else:
            return int(row["Pieces"])

    full_table["Pieces"] = full_table.apply(lambda row: replace_pieces(row), axis=1)

    float_cols = ["Element_area", "Volume", "Mass", "Mass with loss", "Loss",
                "DIS - Operating time", "GWP_DIS", "GWP_TR_A2", "ST - Storage space",
                "ST - Duration (years)", "GWP_ST", "MOD - Ratio impact",
                "MOD - Operating time", "GWP_MOD", "GWP_LOSSES","GWP_TR_A4",
                "GWP_A1-A5", "GWP_New_A1-A5", "GWP_Avoided_prod", "GWP_Avoided_Waste", "GWP_Avoided_Total"
                ]
    full_table[float_cols] = full_table[float_cols].fillna(0)
    full_table[float_cols] = full_table[float_cols].apply(pd.to_numeric, errors='coerce')

    # Fomattage des inventaires
    full_table["Losses"] = full_table.apply(lambda row: create_losses_col(row), axis=1)
    full_table["Dismantling"] = full_table.apply(lambda row: create_dis_col(row), axis=1)
    full_table["Storage"] = full_table.apply(lambda row: create_st_col(row, default_storage = Building.hypotheses["Default storage duration (year)"].values[0]), axis=1)
    full_table["Modification"] = full_table.apply(lambda row: create_mod_col(row), axis=1)
    full_table["Transport A2"] = full_table.apply(lambda row: create_tr_a2_col(row), axis=1)
    full_table["Transport A4"] = full_table.apply(lambda row: create_tr_a4_col(row), axis=1)
    full_table["Conventional product and end-of-life"] = full_table.apply(lambda row: create_neweq_col(row), axis=1)
    full_table["Service lifespan extension"] = full_table.apply(lambda row: create_lifespan_ext(row), axis=1)
    full_table["Difference of production's GWP (%)"] = full_table.apply(lambda row: create_reduction_col(row), axis=1)

    cols2 = ["Map_id", "Element", "Category",
             "Reuse_origin", "Age", "Service lifespan extension",
             "Pieces","Element_area", "Volume", "Mass", "Mass with loss",
             "Conventional product and end-of-life", "KBOB_dataset_id",
             "Losses","Dismantling","Storage","Modification",
             "Transport A2","Transport A4",
             "GWP_DIS","GWP_ST","GWP_MOD","GWP_LOSSES","GWP_TR_A2","GWP_TR_A4",
             "GWP_A1-A5", "GWP_New_A1-A5", "GWP_Avoided_prod", "GWP_Avoided_Waste", "GWP_Avoided_Total", "Difference of production's GWP (%)"]


    # Conversion des valeurs GWP selon les 3 options: total, par kg de matière et par m² de SRE
    gwp_cols = [col for col in cols if "GWP" in col]
    full_table[gwp_cols] = full_table[gwp_cols].div(Building.results_factor)

    filtered_table = full_table[cols2]

    full_table_total = filtered_table.copy(deep=True)
    full_table_sqm = filtered_table.copy(deep=True)
    full_table_sqm[gwp_cols] = full_table_sqm[gwp_cols].div(Building.sqm)

    full_table_kg = filtered_table.copy(deep=True)
    def div_kg(row, cols):
        try:
            for col in cols:
                row[col] = row[col]/row["Mass"]
            return row
        except ZeroDivisionError:
            print("Erreur dans la masse de l'élément: ",row["Element"])
            raise

    full_table_kg = full_table_kg.apply(lambda row: div_kg(row, cols=gwp_cols), axis=1)


    mapping_names = {"Map_id": "n°",
                     "Element":"Product",
                     "Category":"Building category",
                     "Reuse_origin":"Source",
                     "Age":"Age",
                     "Pieces":"no. pieces",
                     "Element_area":"Area (m²)",
                     "Volume":"Volume (m3)",
                     "Mass":"Mass used (kg)",
                     "Mass with loss":"Mass before losses (kg)",
                     "Losses":"Losses",
                     "Service_life_extension":"Service lifespan extension",
                     "Dismantling inventory":"Dismantling",
                     "GWP_DIS":"GWP: Dismantling (A1)",
                     "Transport A2 inventory":"Transport A2",
                     "TR_A2 - Data rating": "Transport A2 data rating",
                     "GWP_TR_A2":"GWP: Transport (A2)",
                     "Storage inventory":"Storage",
                     "GWP_ST":"GWP: Storage (A3)",
                     "Modification inventory":"Modification",
                     "GWP_MOD":"GWP: Modification (A3)",
                     "Transport A4 inventory":"Transport A4",
                     "TR_A4 - Data rating":"Transport A4 data rating",
                     "GWP_TR_A4":"GWP: Transport (A4)",
                     "KBOB_dataset_name":"KBOB dataset (for new prod. and EoL)",
                     "KBOB_dataset_id": "KBOB dataset id",
                     "GWP_LOSSES":"GWP: Losses (A3)",
                     "GWP_A1-A5":"GWP: Total reuse (A1-A4)",
                     "GWP_New_A1-A5":"GWP: Conventional equivalent (A1-A4)",
                     "GWP_Avoided_prod":"GWP: Avoided, production",
                    "GWP_Avoided_Waste":"GWP: Avoided, waste treatment",
                    "GWP_Avoided_Total":"GWP: Avoided, total",
                     "Difference of production's GWP (%)":"GWP: difference in production (%)"
                     }

    for suffix, df in {"gwp_total":full_table_total,
               "gwp_per_sqm":full_table_sqm,
               "gwp_per_kg":full_table_kg}.items():
        final_table = df.rename(columns=mapping_names)
        # # Apply formatting to DataFrame
        final_table = final_table.applymap(format_float)
        html = final_table.to_html(index=False, table_id = "myTable" )
        html = html.replace('border="1" ','')
        html = html.replace('class="dataframe"','class="display"')
        html = html.replace("&amp;","&")
        html = html.replace("&lt;","<")
        html = html.replace("&gt;",">")
        print(html)
        # Open the table template

        with open(os.path.join(ROOT_DIR, cfg['templates_folder'], cfg['templates']['reuse_table']), 'r') as f:
            html_template = f.read()

        html_content = html_template
        html_content = html_content.replace('{reuse_table_from_df}', html)

        # Write final HTML to file
        with open(os.path.join(ROOT_DIR, cfg['html_tables_folder'], Building.case + cfg['table_suffix'][suffix]),
                  'w', encoding='utf-8') as f:
            f.write(html_content)


if __name__ == "__main__":
    # Hobel = Building("Hobelwerk")
    # # building_impacts_table(Hobel)
    # # building_impacts_table(Hobel, variant="New")
    # # material_sunburst(Hobel)
    # # material_sunburst_ebkp(Hobel)
    # bar_reused_comp(Hobel, "GWP")
    # bar_reused_comp(Hobel, "UBP")
    # bar_reused_comp(Hobel, "PE-NR")
    cfg = get_cfg()
    print(os.path.realpath(os.path.join(cfg['figures_folder'], "html")))