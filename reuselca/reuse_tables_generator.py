import os
import pandas as pd
from reuselca.utils import get_cfg

def ensure_output_directory_exists(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def generate_reuse_tables(building):
    output_folder = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_folder, exist_ok=True)

    # Exemple de code pour lire les données du bâtiment
    full_table = building.data.copy()  # Utilisez les données du bâtiment comme exemple

    # Liste des colonnes que vous souhaitez convertir en entiers
    int_cols = [col for col in full_table.columns if 'int' in col]  # Ajustez la condition selon les noms des colonnes

    # Nettoyer les colonnes avant la conversion
    for col in int_cols:
        # Afficher les valeurs non numériques pour diagnostic
        non_numeric_values = full_table[col][~full_table[col].apply(pd.to_numeric, errors='coerce').notna()]
        if not non_numeric_values.empty:
            print(f"Valeurs non numériques dans la colonne {col}:")
            print(non_numeric_values)

        # Remplacer les valeurs non numériques par NaN
        full_table[col] = pd.to_numeric(full_table[col], errors='coerce')

    # Remplacer les NaN par 0 et convertir en entier
    full_table[int_cols] = full_table[int_cols].fillna(0).astype(int)

    # Exemple d'enregistrement du fichier
    output_file = os.path.join(output_folder, f"{building.case}_reuse_table.xlsx")
    full_table.to_excel(output_file, index=False)
    print(f"Table de réutilisation pour {building.case} générée et sauvegardée dans {output_file}")