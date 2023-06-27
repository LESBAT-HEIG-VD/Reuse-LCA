import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

current_palette = sns.color_palette()

new_palette = [current_palette[1], current_palette[2], current_palette[0]]+current_palette[3::]

sns.set_palette(new_palette)

path= "comparaison_cas.csv"

table = pd.read_csv(path, delimiter=';')
plt.figure()
ax = sns.scatterplot(data=table, x="Material intensity (kg/m²)", y="GWP A1-C4 (kgCO2eq./m²)", size="% of reuse", hue="Cas")
ax.set(ylim=(300, 800))
ax.set(xlim=(600, 1500))
plt.show()
