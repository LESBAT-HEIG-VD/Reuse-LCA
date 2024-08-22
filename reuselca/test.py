import plotly.graph_objects as go
import plotly.express as px
import os
from reuselca.utils import Building, get_cfg, ROOT_DIR
from reuselca.utils_html import *
import pandas as pd
import numpy as np

case = Building("K118")
aaa = case.impacts
sqr = case.sqm
aaa2 = case.impacts_new
aaa3 = aaa2 - aaa
aaa = aaa.drop(columns=['Total'])
aaa2 = aaa2.drop(columns=['Total'])
aaa3 = aaa3.drop(columns=['A1-A3','A4','B4', ])
aaa = aaa.transpose()
aaa2 = aaa2.transpose()
aaa3 = aaa3.transpose()


print(aaa3)
aaa["variant"] = "K118"
aaa2["variant"] = "K118_new"

bbb = pd.concat([aaa, aaa2,aaa3], axis=0)

print(bbb)


def get_values_for_variant(df, variant, unit):
    filtered_df = df[df['variant'] == variant]
    if unit == "tonnes CO2 eq.":
        filtered_df[filtered_df.select_dtypes(include='number').columns] /= 1000
    elif unit == "kg CO2 eq./m²/an":
        filtered_df[filtered_df.select_dtypes(include='number').columns] /= sqr * 60
    elif unit == "kg CO2 eq./m²":
        filtered_df[filtered_df.select_dtypes(include='number').columns] /= sqr

    values_lists = [
        [val if i == j else 0 for i in range(len(filtered_df['GWP']))]
        for j, val in enumerate(filtered_df['GWP'])
    ]
    return values_lists


# Générer les lists pour chaque variant
# values_list_k118 = get_values_for_variant(bbb, "K118", "tonnes CO2 eq.")
# values_list_k118_new = get_values_for_variant(bbb, "K118_new", "tonnes CO2 eq.")
# print(values_list_k118)
# print(values_list_k118_new)
# values_list_k118 = get_values_for_variant(bbb, "K118", "kg CO2 eq./m²/an")
# values_list_k118_new = get_values_for_variant(bbb, "K118_new", "kg CO2 eq./m²/an")
# print(values_list_k118)
# print(values_list_k118_new)
# values_list_k118 = get_values_for_variant(bbb, "K118", "kg CO2 eq./m²")
# values_list_k118_new = get_values_for_variant(bbb, "K118_new", "kg CO2 eq./m²")
# print(values_list_k118)
# print(values_list_k118_new)

import plotly.express as px

bbb["steps"] = bbb.index
print(bbb)
fig = px.bar(bbb, x="variant", y="GWP", color="steps", title="K118")

updatemenus = [
    {
        "buttons": [
            {
                "label": "tonnes CO2 eq.",
                "method": "update",
                "args": [{"x": [
                    np.array(['cases', 'cases', 'cases', 'cases', 'cases'], dtype=object),
                    np.array(['cases_new', 'cases_new', 'cases_new', 'cases_new', 'cases_new'], dtype=object)
                ],
                    "y": [
                        [np.array(get_values_for_variant(bbb, "K118", "tonnes CO2 eq."),(get_values_for_variant(bbb, "K118_new", "tonnes CO2 eq.")],
                    ],
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
                    {"x": [
                        np.array(['cases', 'cases', 'cases', 'cases', 'cases'], dtype=object),
                        np.array(['cases_new', 'cases_new', 'cases_new', 'cases_new', 'cases_new'], dtype=object)
                    ],
                        "y": [(get_values_for_variant(bbb, "K118", "kg CO2 eq./m²")),
                              (get_values_for_variant(bbb, "K118_new", "kg CO2 eq./m²"))],
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
                    {"x": [
                        np.array(['cases', 'cases', 'cases', 'cases', 'cases'], dtype=object),
                        np.array(['cases_new', 'cases_new', 'cases_new', 'cases_new', 'cases_new'], dtype=object)
                    ],
                        "y": [(get_values_for_variant(bbb, "K118", "kg CO2 eq./m²/an")),
                              (get_values_for_variant(bbb, "K118_new", "kg CO2 eq./m²/an"))],
                        "yaxis": {"title": "Emissions (kg CO2 eq./m²/an)"},
                        "title": "Construction's life cycle GHG emissions",
                        "visible": True
                    },
                ]
            },
        ],
        "type": "dropdown",
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
        "y": 0.9  # Position verticale pour le menu des unités
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
