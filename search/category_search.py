import requests
from lxml import html
import time
import logging
from search.product_search import search_products


def search_category(city_links):
    logging.info("Начало поиска по категориям")
    for city in city_links:
        logging.info(f"Обработка города: {city['name']}")
        url = f"{city['href']}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                tree = html.fromstring(response.text)
                categories = tree.xpath('//a[contains(@class, "option")]')
                logging.info(f"Найдено категорий: {len(categories)}")
                
                for category in categories:
                    if category.text_content().strip() == "Спецтехника":
                        logging.info("Пропуск категории 'Спецтехника'")
                        continue
                    category_url = category.get('href')
                    category_name = category.text_content().strip()
                    logging.info(f"Обработка категории: {category_name}")
                    time.sleep(5)
                    search_products(city, category_url, category_name)
        except Exception as e:
            logging.error(f"Ошибка при обработке города {city['name']}: {e}")
            continue