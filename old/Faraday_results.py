import pandas as pd

# Paramètres fixes à renseinger ou charger depuis un fichier
project_SRE = 723.9
faraday_path = "C:/Users/mija.frossard/Documents/OneDrive - HESSO/RaD/Projet_Reuse-LCA/Cas études/Faraday/20221216_Faraday_Reuse_LCA_calculation_v3.xlsx"

# Code
faraday_table = pd.read_excel(faraday_path, sheet_name="LCI+LCIA", header=2)
faraday_param = pd.read_excel(faraday_path, sheet_name="Parameters", header=1, nrows=1)
faraday_res_config = pd.read_excel(faraday_path, sheet_name="Parameters", header=9, nrows=1)
results_factor = faraday_res_config.iloc[0]["Results factor"]

new_inventory = faraday_table[faraday_table["Status"]=="New"]
reuse_inventory = faraday_table[faraday_table["Status"]=="Reused"]

project_SRE = faraday_param["Building SRE (m2)"]

gwp_reuse_results = ["GWP_A1-A3", "GWP_A4", "GWP_A5", "GWP_B4", "GWP_C1-C4"]
gwp_new_results = ["GWP_New_A1-A3", "GWP_New_A4", "GWP_New_A5", "GWP_New_B4", "GWP_New_C1-C4"]

reuse_components = reuse_inventory.groupby("Element")

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

import plotly.graph_objects as go
import matplotlib as plt

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



reused_elts = results[(results["Step"]=='A1-A3') & (results["Status"]=='Reused')][["Component","GHG emission (kg CO2eq./kg)"]]
reused_elts = reused_elts.set_index("Component")
reused_elts = reused_elts.rename(columns={"GHG emission (kg CO2eq./kg)":"GHG reused"})
new_elts = results[(results["Step"]=='A1-A3') & (results["Status"]=='New')]
new_elts = new_elts.set_index("Component")
new_elts = new_elts.rename(columns={"GHG emission (kg CO2eq./kg)":"GHG new"})
all_elts = reused_elts.join(new_elts, how='outer')
all_elts["variability"] = (all_elts["GHG reused"]-all_elts["GHG new"])/all_elts["GHG new"]
