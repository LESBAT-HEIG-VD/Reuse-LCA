import pandas as pd
chemin = r"\\eistore2\igt-lesbat\RaD\123315_REMCO\3. Données+calculs\Coopérative ArgeCo - Solives Bois et grange Denens\LCA_Calculation_DENENS_V3_GDY.xlsx"
try:
    df = pd.read_excel(chemin, sheet_name="Parameters", header=1, nrows=1)
    print(df.head())
except Exception as e:
    print(f"Erreur : {e}")