import pandas as pd
import plotly.graph_objects as go
import matplotlib as plt

# Paramètres fixes à renseinger ou charger depuis un fichier
project_SRE = 723.9
elys_path = "C:/Users/mija.frossard/Documents/OneDrive - HESSO/RaD/Projet_Reuse-LCA/Cas études/Elys/20221130_ELYS_Reuse_LCA_calculation_v2.xlsx"

# Code
elys_table = pd.read_excel(elys_path, sheet_name="LCI+LCIA", header=2)
elys_param = pd.read_excel(elys_path, sheet_name="Parameters", header=1, nrows=1)
elys_res_config = pd.read_excel(elys_path, sheet_name="Parameters", header=9, nrows=1)
results_factor = elys_res_config.iloc[0]["Results factor"]

new_inventory = elys_table[elys_table["Status"]=="New"]
reuse_inventory = elys_table[elys_table["Status"]=="Reused"]

project_SRE = elys_param["Building SRE (m2)"]

gwp_reuse_results = ["GWP_A1-A3", "GWP_A4", "GWP_A5", "GWP_B4", "GWP_C1-C4"]
gwp_new_results = ["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A5", "GWP_New_B4", "GWP_New_C1-C4"]

reuse_components = reuse_inventory.groupby("Composition_name")

reuse_comp_gwp = reuse_components.sum()[gwp_reuse_results].join(pd.DataFrame(reuse_components.sum()["Mass"]), how='outer')
reuse_comp_gwp = reuse_comp_gwp[gwp_reuse_results].div(reuse_comp_gwp["Mass"], axis=0).div(results_factor)
reuse_comp_gwp["Component"] = reuse_comp_gwp.index
reuse_comp_gwp["Status"] = "Reused"

reuse_comp_gwp_as_new = reuse_components.sum()[gwp_new_results].join(pd.DataFrame(reuse_components.sum()["Mass"]), how='outer')
reuse_comp_gwp_as_new = reuse_comp_gwp_as_new[gwp_new_results].div(reuse_comp_gwp_as_new["Mass"], axis=0).div(results_factor)
reuse_comp_gwp_as_new = reuse_comp_gwp_as_new.rename(columns={gwp_new_results[i]: gwp_reuse_results[i] for i in range(len(gwp_new_results))})
reuse_comp_gwp_as_new["Component"] = reuse_comp_gwp_as_new.index
reuse_comp_gwp_as_new["Status"] = "New"

l = []
for col in gwp_reuse_results:
    i = reuse_comp_gwp[["Component",col,"Status"]].rename(columns={"Component":"Component", col:"GHG emission (kg CO2eq./kg)", "Status":"Status"})
    i["Step"] = col.replace("GWP_",'')
    l.append(i)
    j = reuse_comp_gwp_as_new[["Component",col,"Status"]].rename(columns={"Component":"Component", col:"GHG emission (kg CO2eq./kg)", "Status":"Status"})
    j["Step"] = col.replace("GWP_",'')
    l.append(j)

results = pd.concat(l, ignore_index=True)

# pio.renderers.default = 'svg'
cmapping = plt.cm.get_cmap('Set2')
# cmapping = cmapping(np.linspace(0, 1, 5))
colors = [plt.colors.rgb2hex(cmapping(i)) for i in range(4)]

fig = go.Figure()

fig.update_layout(
    template="simple_white",
    xaxis=dict(title_text="Component"),
    yaxis=dict(title_text="GHG emission (kg CO2eq./kg)"),
    barmode="stack",
)

for r, c in zip([x for x in gwp_reuse_results if x != "GWP_B4"], colors):
    step = r.replace("GWP_","")
    plot_df = results[results["Step"]==step]
    fig.add_trace(
        go.Bar(x=[plot_df["Component"], plot_df["Status"]], y=plot_df["GHG emission (kg CO2eq./kg)"], name=step, marker_color=c),
    )

fig.show()