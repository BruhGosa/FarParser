import requests
from lxml import html
import logging
from utils.cookies import get_new_cookies

def search_city():

    logging.info(f"Поиск городов")

    # Используем куки в запросе
    session_cookies = get_new_cookies()
    url = "https://www.farpost.ru/geo/nav/city?ajax=1"
    response = requests.get(url, cookies=session_cookies)
    
    if response.status_code == 200:
        tree = html.fromstring(response.text)
        # Используем xpath для поиска всех ссылок внутри нужных блоков
        cities = tree.xpath('//ul[contains(@class, "city-select-control__list_city")]//li[contains(@class, "city-select-control__item")]//a[contains(@class, "city-select-control__city")]')
        logging.info(f"Найдено городов: {len(cities)}")
        
        # Создаем список для хранения информации о городах
        city_links = []
        
        # Собираем информацию о каждом городе
        for city in cities:
            city_info = {
                'id': city.get('data-id'),
                'name': city.text_content(),
                'href': city.get('href')
            }
            logging.debug(f"Добавлен город: {city_info['name']}")
            city_links.append(city_info)
        return city_links
    else:
        logging.error(f"Ошибка при получении списка городов: {response.status_code}")
        return []
