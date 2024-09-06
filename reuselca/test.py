import plotly.graph_objects as go
import plotly.express as px
import os
from reuselca.utils import Building, get_cfg, ROOT_DIR
from reuselca.utils_html import *
import pandas as pd
import numpy as np

# Créer un objet Building
case = Building("K118")

# Charger les données
aaa = case.impacts
aaa2 = case.impacts_new

# Calculer les différences
aaa[['Total difference Initial emissions', 'Total difference SIA 2023 scope']] = pd.DataFrame({
    'Total difference Initial emissions': aaa['A1-A3'] + aaa['A4'],
    'Total difference SIA 2023 scope': aaa['A1-A3'] + aaa['A4'] + aaa['C1-C4']
})
aaa2[['Total difference Initial emissions', 'Total difference SIA 2023 scope']] = pd.DataFrame({
    'Total difference Initial emissions': aaa2['A1-A3'] + aaa2['A4'],
    'Total difference SIA 2023 scope': aaa2['A1-A3'] + aaa2['A4'] + aaa2['C1-C4']
})

# Calculer la différence entre aaa2 et aaa
aaa3 = aaa2 - aaa
aaa3[['A1-A3', 'A4', 'B4', 'C1-C4']] = 0

# Renommer les colonnes
aaa = aaa.rename(columns={'Total': 'Total difference Building life cycle'})
aaa2 = aaa2.rename(columns={'Total': 'Total difference Building life cycle'})
aaa3 = aaa3.rename(columns={'Total': 'Total difference Building life cycle'})

# Réinitialiser les colonnes à 0
aaa[['Total difference Building life cycle', 'Total difference SIA 2023 scope', 'Total difference Initial emissions']] = 0
aaa2[['Total difference Building life cycle', 'Total difference SIA 2023 scope', 'Total difference Initial emissions']] = 0

# Transposer les DataFrames
aaa = aaa.transpose()
aaa2 = aaa2.transpose()
aaa3 = aaa3.transpose()

# Ajouter une colonne pour le type de variante
aaa["variant"] = case.case
aaa2["variant"] = "Reference scenario without reuse"
aaa3["variant"] = "Difference in impact thanks to reuse"

# Concaténer les DataFrames
bbb = pd.concat([aaa, aaa2, aaa3], axis=0)
print(bbb)
sqm = 700
years = 60  # Durée de vie en années
bbb["GWP (kg/m²)"] = bbb["GWP"] * 1000 / sqm
bbb["GWP (kg/m²/an)"] = bbb["GWP"] * 1000 / (sqm * years)
print(bbb)

# Réinitialiser l'index
bbb.reset_index(inplace=True)
bbb.columns = ['Life cycle steps', 'Total difference Building life cycle', 'Total difference SIA 2023 scope', 'Total difference Initial emissions', 'variant']

# Afficher le DataFrame final

