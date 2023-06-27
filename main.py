from reuselca import *

def generate_case(case_name, nav_bar):
    Building = utils.Building(case_name)
    building_impacts_table(Building)
    building_impacts_table(Building, variant="New")
    material_sunburst(Building)
    material_sunburst_ebkp(Building)
    bar_reused_comp(Building, "GWP")
    bar_reused_comp(Building, "UBP")
    bar_reused_comp(Building, "PE-NR")
    generate_building_html(Building, nav_bar)

if __name__ == "__main__":
    cfg = get_cfg()
    cases = cfg["cases"]
    nav_bar = case_studies_nav(cases)
    for case in cases:
        generate_case(case, nav_bar)
