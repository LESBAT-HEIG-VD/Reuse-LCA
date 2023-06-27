import plotly.graph_objects as go
import plotly.express as px
import os
from reuselca.utils import Building, get_cfg, ROOT_DIR
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
        html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.name+cfg['figures_suffix']['impacts_table'])
    elif variant == "New":
        impacts = Building.impacts_new
        title = 'Table 1: Building LCA impacts - "Only new" variant'
        html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.name+cfg['figures_suffix']['impacts_table_new'])

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
    html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.name+cfg['figures_suffix']['material_sunburst'])
    # Aggregate the data by reuse, material type, and component
    agg_data = data.groupby(["Status", "Material type", "Element"]).agg({"Mass": "sum"}).reset_index()

    total_mass_df = data.groupby("Status").agg({"Mass": "sum"}).reset_index()
    agg_data["Mass"] = agg_data["Mass"] / 1000
    # Calculate the share of each row as a percentage of the total mass
    agg_data["Share"] = agg_data["Mass"] / Building.total_mass * 100 * 1000

    agg_data["Share text"] = agg_data["Share"].apply(lambda x: "{:.1f}%".format(x) if x < 0.1 else "{:.2f}%".format(x))

    # Create a sunburst chart
    fig = px.sunburst(
        agg_data,
        path=["Status", "Material type", "Element"],
        values="Share",
        # hover_data=["Mass"],
        # custom_data=["Mass"]
    )

    fig.update_traces(
        hovertemplate = "<b>%{label}</b><br>" +
                      "Share: %{value:.2f}%<br>"
                      # "Mass: %{customdata:.2f} tons<br>" +
                    # "%{parent}"
    )

    fig.update_layout(title_text=title)
    fig.show()
    fig.write_html(html_path)
    return agg_data

def material_sunburst_ebkp(Building):
    data = Building.data
    title = "Share of Reused and New Components by e-BKP category"
    html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.name+cfg['figures_suffix']['material_sunburst_ebkp'])
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

def bar_reused_comp(Building, impact_label):
    import plotly.graph_objects as go
    import matplotlib as plt
    data = Building.data
    title = 'Comparison of the reused components with their "new" equivalent'
    html_path = os.path.join(ROOT_DIR,cfg['figures_folder'],Building.name+"_"+impact_label+"_"+cfg['figures_suffix']['reused_comp_bar'])
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

    # l = []
    # for col in filter_imp:
    #     i = reused_comp[["Component", col, "Status"]].rename(
    #         columns={"Component": "Component", col: impact_name[impact_label], "Status": "Status"})
    #     i["Step"] = col.replace(impact_label+"_", '')
    #     l.append(i)
    #     j = reused_comp_new[["Component", col, "Status"]].rename(
    #         columns={"Component": "Component", col: impact_name[impact_label], "Status": "Status"})
    #     j["Step"] = col.replace(impact_label+"_", '')
    #     l.append(j)
    #
    # results = pd.concat(l, ignore_index=True)

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