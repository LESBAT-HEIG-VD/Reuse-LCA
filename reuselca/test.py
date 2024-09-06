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
# Remplacer les parenthèses par des crochets pour ajouter plusieurs colonnes
aaa[['Total difference Initial emissions', 'Total difference SIA 2023 scope']] = pd.DataFrame({
    'Total difference Initial emissions': aaa['A1-A3'] + aaa['A4'],
    'Total difference SIA 2023 scope': aaa['A1-A3'] + aaa['A4'] + aaa['C1-C4']
})
aaa2[['Total difference Initial emissions', 'Total difference SIA 2023 scope']] = pd.DataFrame({
    'Total difference Initial emissions': aaa2['A1-A3'] + aaa2['A4'],
    'Total difference SIA 2023 scope': aaa2['A1-A3'] + aaa2['A4'] + aaa2['C1-C4']
})
aaa3 = aaa2 - aaa
aaa = aaa.rename(columns={'Total': 'Total difference Building life cycle'})
aaa2 = aaa2.rename(columns={'Total': 'Total difference Building life cycle'})
aaa3 = aaa3.rename(columns={'Total': 'Total difference Building life cycle'})
aaa3[['A1-A3', 'A4', 'B4', 'C1-C4']] = 0
aaa[['Total difference Building life cycle', 'Total difference SIA 2023 scope',
     'Total difference Initial emissions']] = 0
aaa2[['Total difference Building life cycle', 'Total difference SIA 2023 scope',
      'Total difference Initial emissions']] = 0
aaa = aaa.transpose()
aaa2 = aaa2.transpose()
aaa3 = aaa3.transpose()
aaa["variant"] = case
aaa2["variant"] = "Reference scenario without reuse"
aaa3["variant"] = "Difference in impact thanks to reuse"


bbb = pd.concat([aaa, aaa2,aaa3], axis=0)
print(bbb)

