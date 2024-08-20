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


def impact_total_graph(Building, unit="kgCO2eq/m²", scope="Total"):
    # Charger les données
    data = Building.data

    # Définir le chemin pour enregistrer le graphique
    html_path = os.path.join(ROOT_DIR, cfg['figures_folder'], Building.case + "_impact_total.html")

    # Choix de la colonne en fonction de l'unité sélectionnée
    if unit == "kgCO2eq/m²":
        emission_column = "Emissions_kgCO2eq_m2"
    elif unit == "kgCO2eq/m²/an":
        emission_column = "Emissions_kgCO2eq_m2_an"
    elif unit == "tCO2eq":
        emission_column = "Emissions_tCO2eq"

    # Filtrage des données selon le périmètre sélectionné
    if scope == "Emissions initiales":
        df_filtered = data[data["Module"].isin(["A1-A3"])]
    elif scope == "Cycle de vie complet":
        df_filtered = data[data["Module"].isin(["A1-A3", "A4", "B4", "C1-C4"])]
    elif scope == "Cycle de vie SIA 390":
        df_filtered = data[data["Module"].isin(["A1-A3", "B4", "C1-C4"])]

    # Création du graphique
    fig = go.Figure()

    # Ajout des émissions du bâtiment
    fig.add_trace(go.Bar(
        x=df_filtered["Module"],
        y=df_filtered[emission_column],
        name=f"Building Emissions ({unit})",
        marker_color='rgb(26, 118, 255)'
    ))

    # Si le scope est SIA 390, ajoutez les valeurs cibles
    if scope == "Cycle de vie SIA 390":
        fig.add_trace(go.Scatter(
            x=df_filtered["Module"],
            y=df_filtered["SIA_Target_kgCO2eq_m2"],
            mode="lines+markers",
            name="SIA 390 Target",
            line=dict(color='firebrick', width=4, dash='dot')
        ))

    # Mise en page du graphique
    fig.update_layout(
        title=f"Total Impact of Building ({unit})",
        xaxis_title="Module",
        yaxis_title=f"Emissions ({unit})",
        template="plotly_white"
    )

    # Affichage et enregistrement du graphique
    fig.show()
    fig.write_html(html_path)

    return df_filtered