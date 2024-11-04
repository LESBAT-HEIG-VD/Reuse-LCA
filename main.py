from reuselca import *
from reuselca.sankey import sankey


def generate_case(case_name, nav_bar):
#    try:
        # Création d'une instance de Building pour le cas donné
        Building = utils.Building(case_name)
        print(Building.location)
        # Génération et sauvegarde des tableaux d'impact et visualisations
        building_impacts_table(Building)
        building_impacts_table(Building, variant="New")
        impact_total_graph_lot(Building)
        impact_total_graph_comparing(Building)
        impact_total_graph_bundle(Building)
        sankey(Building)
        generate_reuse_tables(Building)

        # Génération du rapport HTML pour le cas de bâtiment
        generate_building_html(Building, nav_bar)
        print(f"Rapport généré pour le cas : {case_name}")

#    except Exception as e:
#        print(f"Erreur lors de la génération du rapport pour le cas {case_name} : {e}")


if __name__ == "__main__":
#    try:
        # Chargement de la configuration
        cfg = get_cfg()
        cases = cfg.get("cases", [])

        # Génération de la barre de navigation
        nav_bar = case_studies_nav(cases)

        # Traitement de chaque cas
        #for case in cases:
        for case in ["K118","Faraday","Hobelwerk","Elys",]:
        # for case in ["K118",]:
        #for case in ["Firmenich",]:
                generate_case(case, nav_bar)

#    except Exception as e:
#        print(f"Erreur durant la génération des rapports : {e}")

    # Building = utils.Building("Faraday")
    # print(Building.impacts)
