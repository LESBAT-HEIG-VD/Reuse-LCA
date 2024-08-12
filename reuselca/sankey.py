import yaml
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os
import warnings

# Fonction pour charger le fichier de configuration
def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        return yaml.safe_load(file)

# Spécifier le chemin absolu vers le fichier config.yml
config_file_path = 'C:/Users/gauthier.demonchy/PycharmProjects/Reuse-LCA/config.yml'
config = load_config(config_file_path)

# Récupérer les chemins et les paramètres depuis le fichier de configuration
figures_folder = config['figures_folder']
cases = config['cases']
figures_suffix = config['figures_suffix']
colors_file_path = r'\\eistore2\igt-lesbat\RaD\107020_Reuse-LCA\4. Communication\diagrammes_sankey\couleurs_rapport_REUSE_LCA.xlsx'

# Construire le chemin absolu pour le répertoire de sauvegarde
output_directory = os.path.join('C:/Users/gauthier.demonchy/PycharmProjects/Reuse-LCA', figures_folder)

# Assurer que le répertoire pour sauvegarder les fichiers HTML existe
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Fonction pour charger les couleurs des labels
def load_label_colors(colors_file_path):
    try:
        df_colors = pd.read_excel(colors_file_path, header=None)
        # Assumer que la première colonne est les labels et la deuxième colonne est les couleurs
        label_colors = dict(zip(df_colors.iloc[1:, 0], df_colors.iloc[1:, 1]))
        return label_colors
    except Exception as e:
        print(f"Erreur lors de la lecture des couleurs : {e}")
        return {}

# Fonction pour créer le diagramme de Sankey
def create_sankey(file_path, label_colors):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        try:
            # Lire la surface SRE depuis la feuille Parameters
            df_params = pd.read_excel(file_path, sheet_name='Parameters', header=None)
            surface_SRE = df_params.iloc[2, 1]  # 3ème ligne, 2ème colonne

            if pd.isna(surface_SRE) or surface_SRE <= 0:
                print(f"Valeur invalide pour la surface SRE dans {file_path}: {surface_SRE}")
                return None

            # Lire les données nécessaires depuis la feuille LCI+LCIA
            df = pd.read_excel(file_path, sheet_name='LCI+LCIA', header=2)
            required_columns = ['Bundle', 'Status', 'Material type 2', 'Mass']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"Colonnes manquantes dans {file_path}: {', '.join(missing_columns)}")
                return None

            df_sankey = df[required_columns].copy()
            df_sankey['Mass per m² SRE'] = df_sankey['Mass'] / surface_SRE

            df_grouped = df_sankey.groupby(['Bundle', 'Status', 'Material type 2']).sum().reset_index()

            labels = list(pd.concat([df_grouped['Bundle'], df_grouped['Status'], df_grouped['Material type 2']]).unique())
            label_to_index = {label: idx for idx, label in enumerate(labels)}

            total_mass_per_sre = df_grouped['Mass per m² SRE'].sum()
            node_mass = {label_to_index[label]: df_grouped[df_grouped.isin([label]).any(axis=1)]['Mass per m² SRE'].sum() for label in labels}
            node_proportion = {label: mass / total_mass_per_sre for label, mass in node_mass.items()}

            source_bundle = df_grouped['Bundle'].map(label_to_index)
            target_status = df_grouped['Status'].map(label_to_index)
            target_material = df_grouped['Material type 2'].map(label_to_index)
            value = df_grouped['Mass per m² SRE']

            links = []
            for i in range(len(df_grouped)):
                links.append({'source': source_bundle.iloc[i], 'target': target_status.iloc[i], 'value': value.iloc[i]})
                links.append({'source': target_status.iloc[i], 'target': target_material.iloc[i], 'value': value.iloc[i]})

            combined_links = pd.DataFrame(links).groupby(['source', 'target'], as_index=False).sum()
            source_sums = combined_links.groupby('source')['value'].sum()
            combined_links['proportion'] = combined_links.apply(lambda row: row['value'] / source_sums[row['source']], axis=1)

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
                    customdata=[f"Proportion: {node_proportion[idx]:.1%}<br>Mass: {node_mass[idx]:.1f} kg/m² SRE" for idx in range(len(labels))],
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

            fig.update_layout(
                font_size=18,
                autosize=True,
                width=None,
                height=None,
                margin=dict(l=50, r=50, t=50, b=50)
            )

            return fig

        except Exception as e:
            print(f"Erreur lors de la création du Sankey pour {file_path}: {e}")
            return None

# Charger les couleurs des labels depuis le fichier Excel
label_colors = load_label_colors(colors_file_path)

# Créer et sauvegarder les diagrammes Sankey pour chaque cas d'étude
for case, file_path in cases.items():
    sankey_fig = create_sankey(file_path, label_colors)
    if sankey_fig:
        base_filename = os.path.basename(file_path).replace('.xlsx', '')
        html_filename = os.path.join(output_directory, f"{case}{figures_suffix['sankey']}")
        pio.write_html(sankey_fig, file=html_filename, include_plotlyjs='cdn')
        print(f"Diagramme Sankey sauvegardé en HTML : {html_filename}")

