import yaml
from yaml.loader import SafeLoader
import pandas as pd
import os

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

scope = ["A1-A3", "A4", "B4", "C1-C4", "Total"]
impact_names = ["GWP", "UBP", "PE-NR"]
imp_labels = [impact + "_" + module for module in scope for impact in impact_names]
imp_labels_new = [impact + "_New_" + module for module in scope for impact in impact_names]


def to_raw(string):
    return fr"{string}"


def calc_stored_bio_co2(inventory, project_SRE, total=True):
    biogenic_carbon = inventory["RR_Biogenic_carbon_content"] * inventory["Extension_rate"]
    stored_co2_reuse = biogenic_carbon.fillna(0) * 3.67  # kgCO2eq/m2
    if total:
        stored_co2_reuse_total = stored_co2_reuse.sum() * project_SRE / 1000  # tCO2eq. total
        return stored_co2_reuse_total
    else:
        return stored_co2_reuse


def get_cfg():
    with open(os.path.join(ROOT_DIR, "config.yml"), "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=SafeLoader)
    return cfg


class Building:
    def __init__(self, case):
        self.case = case
        self.name = get_cfg()["names"][case]
        self.desc = pd.read_excel(get_cfg()["cases"][case], sheet_name="Parameters", header=1, nrows=1)
        self.data = pd.read_excel(get_cfg()["cases"][case], sheet_name="LCI+LCIA", header=2)
        self.data2 = pd.read_excel(get_cfg()["cases"][case], sheet_name="LCA results", header=0, nrows=1)
        self.config = pd.read_excel(get_cfg()["cases"][case], sheet_name="Parameters", header=9, nrows=1)
        self.hypotheses = pd.read_excel(get_cfg()["cases"][case], sheet_name="Parameters", header=13, nrows=1)
        self.sqm = self.desc["Building SRE (m2)"].values[0]
        self.lifespan = self.desc["Building lifetime (years)"].values[0]
        self.results_factor = self.config.iloc[0]["Results factor"]
        self.project_type = str(self.desc["Project type"].values[0])
        self.building_type = str(self.desc["Building type webpage"].values[0])
        self.construction_materials = str(self.desc["Construction materials"].values[0])
        self.nb_floors = '3' #str(self.desc["Floors"].values[0])
        self.location = str(self.desc["Location"].values[0])
        self.project_phase = str(self.desc["Project phase"].values[0])
        self.impacts, self.impacts_new, self.mat_intensity, self.share_reused = get_stats(self.data, self.sqm,
                                                                                          self.results_factor)
        self.impacts = format_impacts(self.impacts) # Total impacts
        self.impacts_new = format_impacts(self.impacts_new)
        self.total_mass = self.data["Mass"].sum()
        # Key metrics
        self.mat_intensity = round(self.total_mass / self.sqm)
        self.share_reused, self.avg_supply_dist, self.adaptiv_reused = calc_reused_info(self.data)
        self.ghg_total_sqm_yr = round(self.impacts["Total"]["GWP"] / self.sqm / self.lifespan, 1)
        self.avoided_ghg_sqm_yr = round(
            self.data["GWP_Avoided_Total"].sum() / self.sqm / self.lifespan / self.results_factor, 1)
        self.stored_bio_co2_sqm_yr = round(
            calc_stored_bio_co2(self.data) / self.sqm / self.lifespan / self.results_factor, 2)


def calc_reused_info(data):
    agg = data.groupby("Status").agg({"Mass": "sum"}).reset_index()
    total_mass = agg['Mass'].sum()
    reused_mass = agg[agg["Status"] == 'Reused']['Mass'].sum()
    adaptiv_mass = agg[agg["Status"] == 'Adaptive reuse']['Mass'].sum()
    share_reused = round(reused_mass / total_mass * 100, 2)
    adaptiv_reused = round(adaptiv_mass / total_mass * 100, 2)
    avg_supply_dist = data[data["Status"] == 'Reused']['Reuse_supply'].sum() / reused_mass
    return share_reused, round(avg_supply_dist, 1), adaptiv_reused


def calc_stored_bio_co2(data):
    carbon_content = data[data['Status'] == 'Reused']['Biogenic_carbon_content'].sum()
    co2_content = carbon_content * 3.67
    return co2_content


def get_stats(data, sqm, results_factor=None):
    if results_factor is None:
        results_factor = 1
    new = data[data["Status"] == "New"]
    reused = data[data["Status"] == "Reused"]
    total_mass = new["Mass"].sum() + reused["Mass"].sum()
    share_reused = reused["Mass"].sum() / total_mass
    mat_intensity = total_mass / sqm
    impacts = data[imp_labels].sum(numeric_only=True) / results_factor
    impacts_new = data[imp_labels_new]
    impacts_new = impacts_new.rename(columns=dict(zip(imp_labels_new, imp_labels)))
    impacts_new = impacts_new.sum(numeric_only=True) / results_factor
    return impacts, impacts_new, mat_intensity, share_reused


def format_impacts(impacts, scope=scope, impact_names=impact_names):
    impacts_dict = {impact: {mod: impacts[impact + "_" + mod] for mod in scope} for impact in impact_names}
    return pd.DataFrame(impacts_dict).transpose()


def case_studies_nav(cases):
    cfg = get_cfg()
    code_part = '                        <li><a href="{path}">{case}</a></li>'
    cases_list = []
    for case in cases:
        line = code_part.format(
            path=os.path.join(case + cfg['html_suffix']['case_study']).encode('unicode-escape').decode(),
            case=cfg['names'][case]
        )
        cases_list.append(line)
    return "\n".join(cases_list)


def generate_building_html(building, nav_bar):
    cfg = get_cfg()
    # Load template HTML file
    with open(os.path.join(ROOT_DIR, cfg['templates_folder'], cfg['templates']['building_template']), 'r') as f:
        html_template = f.read()
    with open(os.path.join(ROOT_DIR, cfg['templates_folder'], cfg['templates']['navigation_bar']), 'r') as f:
        navigation_bar = f.read()

    html_content = html_template
    # General description
    navigation_bar = navigation_bar.replace('{case_studies}', nav_bar)
    html_content = html_content.replace('{navigation_bar}', navigation_bar)
    html_content = html_content.replace('{title}', str(building.name))
    html_content = html_content.replace('{project_type}', str(building.project_type))
    html_content = html_content.replace('{building_type}', str(building.building_type))
    html_content = html_content.replace('{construction_materials}', str(building.construction_materials))
    html_content = html_content.replace('{sqm}', f"{building.sqm} m²")
    html_content = html_content.replace('{nb_floors}', str(building.nb_floors))
    html_content = html_content.replace('{location}', str(building.location))
    html_content = html_content.replace('{project_phase}', str(building.project_phase))
    # Key metrics
    html_content = html_content.replace('{mat_intensity}', str(building.mat_intensity))
    html_content = html_content.replace('{share_reused}', str(building.share_reused))
    html_content = html_content.replace('{adaptiv_reused}', str(building.adaptiv_reused))
    html_content = html_content.replace('{avg_supply_distance}', str(building.avg_supply_dist))
    html_content = html_content.replace('{ghg_total}', str(building.ghg_total_sqm_yr))
    html_content = html_content.replace('{avoided_ghg}', str(building.avoided_ghg_sqm_yr))
    html_content = html_content.replace('{stored_bio_carb}', str(building.stored_bio_co2_sqm_yr))
    # Pictures
    html_content = html_content.replace('{building_photo_src}', os.path.join('..', cfg["pictures_folder"],
                                                                             building.case + cfg['photos_suffix']))
    html_content = html_content.replace('{reuse_map_src}',
                                        os.path.join('..', cfg["pictures_folder"], building.case + cfg['maps_suffix']))
    # Figures

    html_content = html_content.replace('{reuse_table_tot_src}', os.path.join('..', cfg['html_tables_folder'],
                                                                                 building.case + cfg['table_suffix'][
                                                                                     'gwp_total']).encode(
        'unicode-escape').decode())
    html_content = html_content.replace('{reuse_table_kg_src}', os.path.join('..', cfg['html_tables_folder'],
                                                                                 building.case + cfg['table_suffix'][
                                                                                     'gwp_per_kg']).encode(
        'unicode-escape').decode())
    html_content = html_content.replace('{reuse_table_sqm_src}', os.path.join('..', cfg['html_tables_folder'],
                                                                                 building.case + cfg['table_suffix'][
                                                                                     'gwp_per_sqm']).encode(
        'unicode-escape').decode())
    html_content = html_content.replace('{material_sankey}', os.path.join('..', cfg['figures_folder'],
                                                                                 building.case + cfg['figures_suffix'][
                                                                                     'sankey']).encode(
        'unicode-escape').decode())
    html_content = html_content.replace('{impact_total}', os.path.join('..', cfg['figures_folder'],
                                                                                 building.case + cfg['figures_suffix'][
                                                                                     'imp_tot']).encode(
        'unicode-escape').decode())




    html_content = html_content.replace('{impacts_table}', os.path.join('..', cfg['figures_folder'],
                                                                        building.case + cfg['figures_suffix'][
                                                                            'impacts_table']).encode(
        'unicode-escape').decode())
    html_content = html_content.replace('{impacts_table_new}', os.path.join('..', cfg['figures_folder'],
                                                                        building.case + cfg['figures_suffix'][
                                                                            'impacts_table_new']).encode(
        'unicode-escape').decode())

    html_content = html_content.replace('{impacts_table_ebkp}', os.path.join('..', cfg['figures_folder'],
                                                                             building.case + cfg['figures_suffix'][
                                                                                 'impacts_table_ebkp']).encode(
        'unicode-escape').decode())
    html_content = html_content.replace('{ghg_ratio}', os.path.join('..', cfg['figures_folder'],
                                                                    building.case + cfg['figures_suffix'][
                                                                        'ghg_ratio']).encode('unicode-escape').decode())
    html_content = html_content.replace('{ghg_ratio_ebkp}', os.path.join('..', cfg['figures_folder'],
                                                                         building.case + cfg['figures_suffix'][
                                                                             'ghg_ratio_ebkp']).encode(
        'unicode-escape').decode())

    # Write HTML file
    case_html_filename = os.path.join(ROOT_DIR, cfg["html_folder"], building.case + cfg['html_suffix']['building'])
    os.makedirs(os.path.dirname(case_html_filename), exist_ok=True)
    with open(case_html_filename, 'w', encoding="utf-8") as f:
        f.write(html_content)


def main():
    cases = ["Faraday", "Hobelwerk", "K118", "Elys", "Firmenich"]
    for case in cases:
        building = Building(case)
        nav_bar = case_studies_nav(cases)
        generate_building_html(building, nav_bar)


if __name__ == "__main__":
    main()
