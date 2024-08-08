import os
from reuselca.utils import get_cfg, Building
from reuselca.reuse_tables_generator import generate_reuse_tables  # Ajustez le chemin si nécessaire

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

def process_all_buildings():
    cfg = get_cfg()
    cases = cfg.get("names", {}).keys()  # Obtient tous les noms des bâtiments à partir du fichier de configuration
    for case in cases:
        building = Building(case)
        generate_reuse_tables(building)

if __name__ == "__main__":
    process_all_buildings()
