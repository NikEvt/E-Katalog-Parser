from typing import Dict, List, Union
from pathlib import Path
import pandas as pd

from parser.ekatalog_parser import EkatalogProductParser

class EkatalogDatasetBuilder:
    def __init__(self):
        self.dataset = []
        self.failed_pages = []

    def process_page(self, html_source: Union[str, Path]) -> bool:
        try:
            parser = EkatalogProductParser(html_source)
            data = parser.get_structured_product_data()

            self.dataset.append(data)
            return True

        except Exception as e:
            print(f"page failed: {e}")
            self.failed_pages.append({
                'source': str(html_source),
                'error': str(e)
            })
            return False

    def process_directory(self, directory_path: Path, file_pattern: str = "*.html"):
        directory = Path(directory_path)
        html_files = list(directory.glob(file_pattern))

        for html_file in html_files:
            self.process_page(html_file)

    def get_dataset(self) -> List[Dict]:
        return self.dataset

    def get_failed_pages(self) -> List[Dict]:
        return self.failed_pages

    def export_to_csv(self, output_path: str):


        if not self.dataset:
            raise ValueError("No data to export. Process some pages first.")

        flattened_data = []
        for item in self.dataset:
            flat_item = {
                'name': item.get('name'),
                'min_price': item.get('min_price'),
                'max_price': item.get('max_price'),
                'headers': '; '.join(item.get('headers', [])),
                'related_links': '; '.join(item.get('related_links',[])),
                'total_characteristics': item.get('extraction_metadata', {}).get('total_characteristics', 0)
            }

            characteristics = item.get('characteristics', {})
            for key, value in characteristics.items():
                flat_item[f"char_{key}"] = value

            flattened_data.append(flat_item)

        df = pd.DataFrame(flattened_data)
        df.to_csv(output_path, index=False, encoding='utf-8')