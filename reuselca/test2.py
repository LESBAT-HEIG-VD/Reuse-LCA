import plotly.graph_objects as go
import plotly.express as px
import os
from reuselca.utils import Building, get_cfg, ROOT_DIR
from reuselca.utils_html import *
import pandas as pd
import numpy as np

case = Building("Elys")

aaa = case.data
aaa = aaa.groupby("Category")[["GWP_A1-A3", "GWP_A4", "GWP_B4", "GWP_C1-C4"]].sum().reset_index()

# Reshape the DataFrame using the melt function
aaa = aaa.melt(id_vars=["Category"], var_name="Steps", value_name="GWP")

# Extract step names from the Steps column
aaa["Steps"] = aaa["Steps"].str.replace("GWP_", "")

# Rename Category to Variante to match your desired output
aaa.rename(columns={"Category": "variant"}, inplace=True)



import plotly.express as px
print(aaa)
fig = px.bar(bbb, x="variant", y="GWP", color="steps", title="K118")

updatemenus=[
        {
            "buttons": [
                {
                    "label": "tonnes CO2 eq.",
                    "method": "update",
                    "args": [{"x": [np.array([("K118"), ("K118_new")], dtype=object)],
                              "y": [(values_list_k1181),(values_list_k1181_new)],
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
                        {"x": [np.array([("K118"), ("K118_new")], dtype=object)],
                         "y": [(values_list_k1182),(values_list_k1182_new)],
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
                        {"x": [np.array([("K118"), ("K118_new")], dtype=object)],
                         "y": [(values_list_k1183),(values_list_k1183_new)],
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
            "y": 0.65  # Position verticale pour le menu des unités
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

                     },
                ]
            },
            {
                "label": "Building life cycle",
                "method": "update",
                "args": [
                    {
                        "title": "Construction's life cycle GHG emissions",

                     },
                ]
            },
            {
                "label": "SIA",
                "method": "update",
                "args": [
                    {
                        "title": "Construction's life cycle GHG emissions according to SIA 2032",

                     },
                ]
            }
        ],
        "type": "buttons",
        "direction": "down",
        "showactive": False,
         "x": -0.2,  # Position horizontale du menu des unités (dans la marge)
         "y": 0.9 # Position verticale pour le menu des unités
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

