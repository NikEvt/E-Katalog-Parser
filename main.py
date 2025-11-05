from config import config
from parser.dataset_builder import EkatalogDatasetBuilder

if __name__ == "__main__":
    builder = EkatalogDatasetBuilder()
    builder.process_directory(config.SOURCE_DIRECTORY)
    builder.export_to_csv(config.OUTPUT_FILE)