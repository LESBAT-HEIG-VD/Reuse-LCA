import plotly.graph_objects as go
import plotly.express as px
import os
from reuselca.utils import Building, get_cfg, ROOT_DIR
from reuselca.utils_html import *
import pandas as pd
import numpy as np

case = Building("K118")
aaa=case.impacts
sqr=case.sqm
aaa2=case.impacts-new

def get_values(unit):
    if unit == "tonnes CO2 eq.":
        ccc = bbb.copy()
        ccc[ccc.select_dtypes(include='number').columns] /= 1000
        values_lists= [[val if i == j else 0 for i in range(len(ccc['GWP']))] for j, val in enumerate(ccc['GWP'])]
        return values_lists
    elif unit == "kg CO2 eq./m²/an":
        ccc = bbb.copy()
        ccc[ccc.select_dtypes(include='number').columns] /= sqr * 60
        values_lists= [[val if i == j else 0 for i in range(len(ccc['GWP']))] for j, val in enumerate(ccc['GWP'])]
        return values_lists
    elif unit == "kg CO2 eq./m²":
        ddd = bbb.copy()
        ddd[ddd.select_dtypes(include='number').columns] /= sqr
        values_lists= [[val if i == j else 0 for i in range(len(ddd['GWP']))] for j, val in enumerate(ddd['GWP'])]
        return values_lists

import plotly.express as px
bbb= aaa.transpose()
bbb["variant"]="K118"
bbb["steps"] = bbb.index
fig = px.bar(bbb, x="variant", y="GWP", color="steps", title="K118")

updatemenus=[
        {
            "buttons": [
                {
                    "label": "tonnes CO2 eq.",
                    "method": "update",
                    "args": [{"x": [np.array(['K118', 'K118', 'K118', 'K118', 'K118'], dtype=object)],
                              "y": get_values("tonnes CO2 eq."),
                              "yaxis": {"title": "Emissions (tonnes CO2 eq.)"},
                              "title": "Construction's life cycle GHG emissions",
                              "visible": True
                              },
                             ]
                },
                {
                    "label": "kg CO2 eq./m²",
                    "method": "update",
                    "args": [
                        {"x": [np.array(['K118', 'K118','K118', 'K118', 'K118'], dtype=object)],
                         "y": get_values("kg CO2 eq./m²"),
                         "yaxis": {"title": "Emissions (kg CO2 eq./m²)"},
                         "title": "Construction's life cycle GHG emissions",
                         "visible": True
                         },
                    ]
                },
                {
                    "label": "kg CO2 eq./m²/an",
                    "method": "update",
                    "args": [
                        {"x": [np.array(['K118', 'K118','K118', 'K118', 'K118'], dtype=object)],
                         "y": get_values("kg CO2 eq./m²/an"),
                         "yaxis": {"title": "Emissions (kg CO2 eq./m²/an)"},
                         "title": "Construction's life cycle GHG emissions",
                         "visible":True
                        },
                    ]
                },
            ],
            "type":"dropdown",
            "direction": "down",
            "showactive": True,
            "x": -0.2,  # Position horizontale du menu des unités (dans la marge)
            "y": 0.9  # Position verticale pour le menu des unités
        },
    {
        'active': 1,
        "buttons": [
            {
                "label": "Initial emissions (modules A)",
                "method": "update",
                "args": [
                    {
                        "title": "Construction's initial GHG emissions",
                        "visible": [True, True, False, False, False]
                     },
                ]
            },
            {
                "label": "Building life cycle",
                "method": "update",
                "args": [
                    {
                        "title": "Construction's life cycle GHG emissions",
                        "visible": [True, True, True, True, False]
                     },
                ]
            },
            {
                "label": "SIA",
                "method": "update",
                "args": [
                    {
                        "title": "Construction's life cycle GHG emissions according to SIA 2032",
                        "visible": [True, False, True, True, False]
                     },
                ]
            }
        ],
        "type": "buttons",
        "direction": "down",
        "showactive": False,
         "x": -0.2,  # Position horizontale du menu des unités (dans la marge)
         "y": 0.5 # Position verticale pour le menu des unités
    }

]

fig.update_layout(
    title="Total Impact of Building",
    xaxis_title="Variant",
    yaxis_title="Emissions",
    template="plotly_white",
    # barmode='stack',  # Activer l'empilement des barres
    margin=dict(l=200, r=50, t=50, b=50))

fig.update_layout(updatemenus=updatemenus)

fig.show()

cfg = get_cfg()

scope = ["A1-A3", "A4", "B4", "C1-C4", "Total"]
impact_names = ["GWP", "UBP", "PE-NR"]
imp_labels = [impact+"_"+module for module in scope for impact in impact_names]
imp_labels_new = [impact+"_"+"New"+"_"+module for module in scope for impact in impact_names]

impact_name = {"GWP":"GHG emission (kg CO2eq./kg)",
               "UBP":"Ecological Scarcity 2021 (UBP/kg)",
               "PE-NR":"Primary energy, non renewable (kWh/kg)"}


data_GWP = Building.data2
print(data_GWP.columns)