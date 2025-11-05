
class Config:
    GECKODRIVER_PATH = '/Users/ivanivanov/PycharmProjects/ekatalog_parser/crawler/geckodriver'

    BASE_URL = "https://e-katalog.pl"
    CATALOG_URL = "https://e-katalog.kz/ek-list.php?katalog_=157&page_={}&preset_mode_=0"
    CATALOG_PL_URL = "https://e-katalog.pl/ek-list.php?katalog_=264&page_={}&preset_mode_=0"


    SOURCE_DIRECTORY = "/Users/ivanivanov/PycharmProjects/ekatalog_parser/crawler/ekatalog_pl_bikes"
    OUTPUT_FILE = "bikes_ekatalog.csv"
    OUTPUT_DIR = "ekatalog_pl_bikes"

    MAX_PAGES = 10000
    SLEEP_INTERVAL = 1


config = Config()