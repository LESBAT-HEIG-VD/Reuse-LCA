import yaml
from yaml.loader import SafeLoader
import pandas as pd
import os
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

scope = ["A1-A3", "A4", "B4", "C1-C4", "Total"]
impact_names = ["GWP", "UBP", "PE-NR"]
imp_labels = [impact+"_"+module for module in scope for impact in impact_names]
imp_labels_new = [impact+"_"+"New"+"_"+module for module in scope for impact in impact_names]

def to_raw(string):
    return fr"{string}"

def calc_stored_bio_co2(inventory, project_SRE, total=True):
    biogenic_carbon = inventory["RR_Biogenic_carbon_content"]*inventory["Extension_rate"]
    stored_co2_reuse = biogenic_carbon.fillna(0)*3.67 # kgCO2eq/m2
    if total is True:
        stored_co2_reuse_total = stored_co2_reuse.sum()*project_SRE/1000 # tCO2eq. total
        return stored_co2_reuse_total
    else:
        return stored_co2_reuse

def get_cfg():
    with open(os.path.join(ROOT_DIR,"config.yml"), "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=SafeLoader)
    return cfg

class Building(object):
    def __init__(self, case):
        self.case = case
        self.name = get_cfg()["names"][case]
        self.desc = pd.read_excel(get_cfg()["cases"][case], sheet_name="Parameters", header=1, nrows=1)
        self.data = pd.read_excel(get_cfg()["cases"][case], sheet_name="LCI+LCIA", header=2)
        self.config = pd.read_excel(get_cfg()["cases"][case], sheet_name="Parameters", header=9, nrows=1)
        self.hypotheses = pd.read_excel(get_cfg()["cases"][case], sheet_name="Parameters", header=13, nrows=1)
        self.sqm = self.desc["Building SRE (m2)"].values[0]
        self.lifespan = self.desc["Building lifetime (years)"].values[0]
        self.results_factor = self.config.iloc[0]["Results factor"]
        self.project_type = self.desc["Project type"].values[0]
        self.building_type = self.desc["Building type webpage"].values[0]
        self.construction_materials = self.desc["Construction materials"].values[0]
        self.nb_floors = self.desc["Floors"].values[0]
        self.location = self.desc["Location"].values[0]
        self.project_phase = self.desc["Project phase"].values[0]
        self.impacts, self.impacts_new, self.mat_intensity, self.share_reused = get_stats(self.data, self.sqm, self.results_factor)
        self.impacts = format_impacts(self.impacts)
        self.impacts_new = format_impacts(self.impacts_new)
        self.total_mass = self.data["Mass"].sum()
        #key metrics
        self.mat_intensity = round(self.data["Mass"].sum()/self.sqm)
        self.share_reused, self.avg_supply_dist  = calc_reused_info(self.data)
        self.ghg_total_sqm_yr = round(self.impacts["Total"]["GWP"]/self.sqm/self.lifespan,1)
        self.avoided_ghg_sqm_yr = round(self.data["GWP_Avoided_Total"].sum()/self.sqm/self.lifespan/self.results_factor,1)
        self.stored_bio_co2_sqm_yr = round(calc_stored_bio_co2(self.data)/self.sqm/self.lifespan/self.results_factor,2)

def calc_reused_info(data):
    agg = data.groupby("Status").agg({"Mass": "sum"}).reset_index()
    value = agg[agg["Status"]=='Reused']['Mass']/agg['Mass'].sum()
    share_reused = round(value.values[0],2)*100
    value2 = data[data["Status"]=='Reused']['Reuse_supply'].sum()/agg[agg["Status"]=='Reused']['Mass']
    avg_supply_dist = round(value2.values[0],1)
    return share_reused, avg_supply_dist

def calc_stored_bio_co2(data):
    carbon_content = data[data['Status']=='Reused']['Biogenic_carbon_content'].sum()
    co2_content = carbon_content*3.67
    return co2_content

def get_stats(data, sqm, results_factor=None):
    if results_factor is None:
        results_factor = 1
    new = data[data["Status"] == "New"]
    reused = data[data["Status"] == "Reused"]
    total_mass = new.sum()["Mass"]+reused.sum()["Mass"]
    share_reused = reused.sum()["Mass"]/total_mass
    mat_intensity = total_mass/sqm
    impacts = data[imp_labels].sum()/results_factor
    impacts_new = data[imp_labels_new]
    impacts_new = impacts_new.rename(columns=dict(zip(imp_labels_new,imp_labels)))
    impacts_new = impacts_new.sum()/results_factor
    return impacts, impacts_new, mat_intensity, share_reused

def format_impacts(impacts, scope=scope, impact_names=impact_names):
    if scope is None:
        scope = ["A1-A3", "A4", "B4", "C1-C4", "Total"]
    if impact_names is None:
        impact_names = ["GWP", "UBP", "PE-NR"]
    impacts_dict = dict()
    for i in impact_names:
        impacts_dict[i] = dict()
        for j in scope:
            impacts_dict[i][j] = impacts[i+"_"+j]
    return pd.DataFrame(impacts_dict).transpose()

def case_studies_nav(cases):
    cfg = get_cfg()
    code_part = '                        <li><a href="{path}">{case}</a></li>'
    cases_list = []
    for case in cases:
        line = code_part.format(path=os.path.join(case + cfg['html_suffix']['case_study']).encode('unicode-escape').decode(),
                         case=cfg['names'][case])
        cases_list.append(line)
    return "\n".join(cases_list)

def generate_building_html(Building, nav_bar):
    cfg = get_cfg()
    # Load template HTML file
    with open(os.path.join(ROOT_DIR,cfg['templates_folder'],cfg['templates']['building_template']), 'r') as f:
        html_template = f.read()
    with open(os.path.join(ROOT_DIR,cfg['templates_folder'],cfg['templates']['navigation_bar']), 'r') as f:
        navigation_bar = f.read()

    html_content = html_template
    # General description
    navigation_bar = navigation_bar.replace('{case_studies}', nav_bar)
    html_content = html_content.replace('{navigation_bar}', navigation_bar)
    html_content = html_content.replace('{title}', Building.name.encode('utf-8').decode('utf-8'))
    html_content = html_content.replace('{project_type}', Building.project_type)
    html_content = html_content.replace('{building_type}', Building.building_type)
    html_content = html_content.replace('{construction_materials}', Building.construction_materials)
    html_content = html_content.replace('{sqm}', str(Building.sqm)+' m²')
    html_content = html_content.replace('{nb_floors}', str(Building.nb_floors))
    html_content = html_content.replace('{location}', Building.location.encode('utf-8').decode('utf-8'))
    html_content = html_content.replace('{project_phase}', Building.project_phase)
    # Key metrics
    html_content = html_content.replace('{mat_intensity}', str(Building.mat_intensity))
    html_content = html_content.replace('{share_reused}', str(Building.share_reused))
    html_content = html_content.replace('{avg_supply_distance}', str(Building.avg_supply_dist))
    html_content = html_content.replace('{ghg_total}', str(Building.ghg_total_sqm_yr))
    html_content = html_content.replace('{avoided_ghg}', str(Building.avoided_ghg_sqm_yr))
    html_content = html_content.replace('{stored_bio_carb}', str(Building.stored_bio_co2_sqm_yr))
    # Pictures
    html_content = html_content.replace('{building_photo_src}', os.path.join('..', cfg["pictures_folder"], Building.case+cfg['photos_suffix'])) # écrire des relatives paths en dur
    html_content = html_content.replace('{reuse_map_src}', os.path.join('..', cfg["pictures_folder"], Building.case+cfg['maps_suffix']))
    # Figures
    html_content = html_content.replace('{material_sunburst}', os.path.join('..',cfg['figures_folder'],Building.case+cfg['figures_suffix']['material_sunburst']).encode('unicode-escape').decode())
    html_content = html_content.replace('{material_sunburst_ebkp}', os.path.join('..',cfg['figures_folder'],Building.case+cfg['figures_suffix']['material_sunburst_ebkp']).encode('unicode-escape').decode())
    html_content = html_content.replace('{impacts_table}', os.path.join('..',cfg['figures_folder'],Building.case+cfg['figures_suffix']['impacts_table']).encode('unicode-escape').decode())
    html_content = html_content.replace('{impacts_table_new}', os.path.join('..',cfg['figures_folder'],Building.case+cfg['figures_suffix']['impacts_table_new']).encode('unicode-escape').decode())
    html_content = html_content.replace('{ghg_sunburst}', os.path.join('..',cfg['figures_folder'],Building.case+cfg['figures_suffix']['co2_sunburst']).encode('unicode-escape').decode())
    html_content = html_content.replace('{reused_comp_GWP_bar}', os.path.join('..',cfg['figures_folder'],Building.case+"_GWP_"+cfg['figures_suffix']['reused_comp_bar']).encode('unicode-escape').decode())
    html_content = html_content.replace('{reused_comp_UBP_bar}', os.path.join('..',cfg['figures_folder'],Building.case+"_UBP_"+cfg['figures_suffix']['reused_comp_bar']).encode('unicode-escape').decode())
    html_content = html_content.replace('{reused_comp_PE_NR_bar}', os.path.join('..',cfg['figures_folder'],Building.case+"_PE-NR_"+cfg['figures_suffix']['reused_comp_bar']).encode('unicode-escape').decode())

    # Reuse tables
    html_content = html_content.replace('{reuse_table_tot_src}', os.path.join('..', cfg['html_tables_folder'], Building.case + cfg['table_suffix']['gwp_total']).encode('unicode-escape').decode())
    html_content = html_content.replace('{reuse_table_kg_src}', os.path.join('..', cfg['html_tables_folder'], Building.case + cfg['table_suffix']['gwp_per_sqm']).encode('unicode-escape').decode())
    html_content = html_content.replace('{reuse_table_sqm_src}', os.path.join('..', cfg['html_tables_folder'], Building.case + cfg['table_suffix']['gwp_per_kg']).encode('unicode-escape').decode())

    # Write final HTML to file
    with open(os.path.join(ROOT_DIR, cfg['html_pages_folder'], Building.case + cfg['html_suffix']['case_study']), 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    cfg = get_cfg()
    print(cfg["cases"])
    # hobel_table = pd.read_excel("C:\\Users\\mija.frossard\\Documents\\OneDrive - HESSO\\RaD\\Projet_Reuse-LCA\\Cas études\\Faraday\\20221216_Faraday_Reuse_LCA_calculation_v3.xlsx", sheet_name="LCI+LCIA", header=2)

    Hobel = Building("Bistoquette")
    print(Hobel.impacts.div(Hobel.sqm).round(1))

