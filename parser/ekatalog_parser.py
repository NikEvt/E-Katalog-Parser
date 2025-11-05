import lxml.html as l
from typing import Dict, List, Optional, Union
from pathlib import Path
import re

# удаляет спец символы и единицы измерения из колонок
def clean_text_to_number(text: str, extract_first_number: bool = False) -> Optional[Union[str, int, float]]:

    if not text:
        return None

    cleaned_text = text.replace('\u00a0', ' ').replace('\xa0', ' ').strip()

    if extract_first_number:
        numeric_text = re.sub(r'[^\d.,]', '', cleaned_text)

        if not numeric_text:
            return None

        numeric_text = numeric_text.replace(',', '.')

        try:
            number = float(numeric_text)
            return int(number) if number.is_integer() else number
        except ValueError:
            return None
    else:
        return cleaned_text

class EkatalogProductParser:
    def __init__(self, html_source: Union[str, Path] = None):
        self.html_source = html_source
        self.root = None
        self._parsed_data = {}
        if html_source:
            self.load_html(html_source)

    def load_html(self, html_source: Union[str, Path]):
        if isinstance(html_source, (str, Path)):
            if Path(html_source).exists():
                with open(html_source, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.root = l.fromstring(content)
            else:
                self.root = l.fromstring(html_source)
        else:
            raise ValueError("html_source must be a file path or HTML string")

    def extract_characteristics(self) -> Dict[str, str]:
        chars_divs = self.root.xpath("//div[@class='m-s-f3']")

        numeric_fields = ['Диагональ', 'Частота', 'Яркость']

        characteristics = {}
        for div in chars_divs:
            title = div.get('title', '').strip()
            value = div.text_content().strip()

            if ':' in title:
                key = title.split(':', 1)[0].strip()
                char_value = title.split(':', 1)[1].strip()

                if key in numeric_fields:
                    characteristics[key] = clean_text_to_number(char_value, extract_first_number=True)
                else:
                    characteristics[key] = clean_text_to_number(char_value, extract_first_number=False)
            elif title:

                characteristics[title] = clean_text_to_number(value, extract_first_number=False)

        return characteristics

    def extract_price_info(self) -> Dict[str, Optional[Union[int, float]]]:
        price_spans = self.root.xpath(
            "//div[starts-with(@id, 'price_') and contains(@class, 'desc-big-price')]/span"
        )

        price_info = {
            'min_price': None,
            'max_price': None
        }

        if len(price_spans) > 0:
            min_price_text = price_spans[0].text.strip() if price_spans[0].text else None
            if min_price_text:
                price_info['min_price'] = clean_text_to_number(min_price_text, extract_first_number=True)

        if len(price_spans) > 1:
            max_price_text = price_spans[1].text.strip() if price_spans[1].text else None
            if max_price_text:
                price_info['max_price'] = clean_text_to_number(max_price_text, extract_first_number=True)

        return price_info

    def extract_links_and_texts(self) -> List[str]:
        links = self.root.xpath("//div[@class='m-c-f1']//a")
        texts = [link.text_content().strip() for link in links if link.text_content().strip()]
        return texts

    def extract_headers(self) -> List[str]:

        headers = self.root.xpath('//div[@class="h2 h2-slice"]')
        header_texts = []

        for header in headers:
            if header.text:
                header_texts.append(header.text.strip())

        return header_texts

    def extract_name(self) -> str:
        name = self.root.xpath('//div[@class="cont-block-title"]')[0]
        name_text = name.xpath('//span[@class="blue"]//text()')[0]
        return name_text.strip()


    def extract_all_data(self) -> Dict:
        all_data = {
            'name': self.extract_name(),
            'characteristics': self.extract_characteristics(),
            'price_info': self.extract_price_info(),
            'links_and_texts': self.extract_links_and_texts(),
            'headers': self.extract_headers(),
            'metadata': {
                'total_characteristics': len(self.extract_characteristics()),
                'has_price_info': any(self.extract_price_info().values()),
                'total_links': len(self.extract_links_and_texts()),
                'total_headers': len(self.extract_headers())
            }
        }

        self._parsed_data = all_data
        return all_data

    def get_structured_product_data(self) -> Dict:
        data = self.extract_all_data()

        structured_data = {
            'name': data['name'],
            'characteristics': data['characteristics'],
            'min_price': data['price_info']['min_price'],
            'max_price': data['price_info']['max_price'],
            'related_links': data['links_and_texts'],
            'headers': data['headers'],
            'extraction_metadata': data['metadata']
        }

        return structured_data

    def to_dict(self) -> Dict:
        return self._parsed_data if self._parsed_data else self.extract_all_data()