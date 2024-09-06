import yaml
import plotly.io as pio
import os
import warnings
import plotly.graph_objects as go
import plotly.express as px
from reuselca.utils import Building, get_cfg, ROOT_DIR
from reuselca.utils_html import *
import pandas as pd
import numpy as np

cfg = get_cfg()



# Fonction pour créer le diagramme de Sankey
def sankey(Building):

    # Récupérer les chemins et les paramètres depuis le fichier de configuration
    colors_file_path = r'\\eistore2\igt-lesbat\RaD\107020_Reuse-LCA\4. Communication\diagrammes_sankey\couleurs_rapport_REUSE_LCA.xlsx'
    df_colors = pd.read_excel(colors_file_path, header=None)
    # Assumer que la première colonne est les labels et la deuxième colonne est les couleurs
    label_colors = dict(zip(df_colors.iloc[1:, 0], df_colors.iloc[1:, 1]))

    # Définir le chemin pour enregistrer le graphique
    html_path = os.path.join(ROOT_DIR, cfg['figures_folder'], Building.case + "_sankey.html")

    # Création du graphique
    fig = go.Figure()

    warnings.simplefilter("ignore", category=UserWarning)
    try:
        # Lire la surface SRE depuis la feuille Parameters
        surface_SRE = Building.sqm

        if pd.isna(surface_SRE) or surface_SRE <= 0:
            print(f"Valeur invalide pour la surface SRE dans {Building.case}: {surface_SRE}")
            return None

        # Lire les données nécessaires depuis la feuille LCI+LCIA
        df = Building.data  # Remplacement correct de 'building.data' par 'Building.data'
        required_columns = ['Bundle', 'Status', 'Material type 2', 'Mass']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"Colonnes manquantes dans {Building.case}: {', '.join(missing_columns)}")
            return None

        df_sankey = df[required_columns].copy()
        df_sankey['Mass per m² SRE'] = df_sankey['Mass'] / surface_SRE

        # Grouper les données par 'Bundle', 'Status' et 'Material type 2'
        df_grouped = df_sankey.groupby(['Bundle', 'Status', 'Material type 2']).sum().reset_index()

        # Création des labels uniques
        labels = list(pd.concat([df_grouped['Bundle'], df_grouped['Status'], df_grouped['Material type 2']]).unique())
        label_to_index = {label: idx for idx, label in enumerate(labels)}

        # Calcul des masses totales et des proportions
        total_mass_per_sre = df_grouped['Mass per m² SRE'].sum()
        node_mass = {label_to_index[label]: df_grouped[df_grouped.isin([label]).any(axis=1)]['Mass per m² SRE'].sum()
                     for label in labels}
        node_proportion = {label: mass / total_mass_per_sre for label, mass in node_mass.items()}

        # Mapping des sources et des cibles pour le Sankey
        source_bundle = df_grouped['Bundle'].map(label_to_index)
        target_status = df_grouped['Status'].map(label_to_index)
        target_material = df_grouped['Material type 2'].map(label_to_index)
        value = df_grouped['Mass per m² SRE']

        # Création des liens entre les nœuds
        links = []
        for i in range(len(df_grouped)):
            links.append({'source': source_bundle.iloc[i], 'target': target_status.iloc[i], 'value': value.iloc[i]})
            links.append({'source': target_status.iloc[i], 'target': target_material.iloc[i], 'value': value.iloc[i]})

        combined_links = pd.DataFrame(links).groupby(['source', 'target'], as_index=False).sum()
        source_sums = combined_links.groupby('source')['value'].sum()
        combined_links['proportion'] = combined_links.apply(lambda row: row['value'] / source_sums[row['source']],
                                                            axis=1)

        source = combined_links['source'].tolist()
        target = combined_links['target'].tolist()
        value = combined_links['value'].tolist()
        proportion = combined_links['proportion'].tolist()

        # Création du diagramme de Sankey avec Plotly
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=40,
                line=dict(color="black", width=1),
                label=labels,
                color=[label_colors.get(label, '#CCCCCC') for label in labels],
                customdata=[f"Proportion: {node_proportion[idx]:.1%}<br>Mass: {node_mass[idx]:.1f} kg/m² SRE" for idx in
                            range(len(labels))],
                hovertemplate='%{label}<br>%{customdata}<extra></extra>'
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                customdata=proportion,
                hovertemplate=(
                    '%{source.label} → %{target.label} : %{customdata:.1%}<extra></extra><br>'
                    'Mass: %{value:.1f} kg/m² SRE<br>'
                )
            )
        )])

        # Mise à jour de la mise en page du graphique
        fig.update_layout(
            font_size=18,
            autosize=True,
            margin=dict(l=50, r=30, t=50, b=30)
        )

        # Enregistrer le graphique au format HTML
        fig.write_html(html_path)
        return fig

    except Exception as e:
        print(f"Erreur lors de la création du Sankey pour {Building.case}: {e}")
        return None

