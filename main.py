from search.city_search import search_city
from search.category_search import search_category
import logging

# В начале файла добавляем настройку логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Начало парсинга сайта Farpost.ru")
    cities = search_city()
    search_category(cities)
    logging.info("Парсинг сайта Farpost.ru завершен")

if __name__ == "__main__":
    main()