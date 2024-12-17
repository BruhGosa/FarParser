import requests
from lxml import html
import time
import os
import logging
from dotenv import load_dotenv
from utils.cookies import get_new_cookies
from utils.captcha import check_captcha
from search.seller_search import search_sellers

load_dotenv()

# Кол-во продавцов в категории
# Если 0, то будет искать всех продавцов в категории
count_sellers_in_category = int(os.getenv('COUNT_SELLERS_IN_CATEGORY'))

def search_products(city, category_url, category_name):
    page = 1
    logging.info(f"Начало поиска товаров в категории: {category_name}")
    logging.info(f"Город: {city['name']}")
    
    while True:
        try:
            logging.info(f"Обработка страницы {page}")
            cookies = get_new_cookies()
            
            # Делаем запрос к странице категории
            response = requests.get(f"https://www.farpost.ru{category_url}/?page={page}", cookies=cookies)
            
            if response.status_code == 200:
                if check_captcha(response.text):
                    logging.warning(f"Обнаружена капча на странице {page}")
                    time.sleep(5)
                    continue
                    
                tree = html.fromstring(response.text)
                
                # Находим все карточки товаров
                products = tree.xpath('//div[contains(@class, "descriptionCell")]')
                
                if products:
                    logging.info(f"Найдено продуктов на странице {page}: {len(products)}")
                    print(f"Город: {city['name']} | Категория: {category_name} | Страница: {page} | Найдено продуктов: {len(products)}")

                    if count_sellers_in_category > 0:
                        count_sellers = count_sellers_in_category
                        for product in products:
                            if count_sellers <= 0:
                                return
                            
                            # Проверяем наличие блока компании
                            company_block = product.xpath('.//div[contains(@class, "ellipsis-text__left-side")]')
                            seller_type = "Компания" if company_block else "Частник"
                            
                            # Получаем ссылку на товар
                            product_link = product.xpath('.//a[contains(@class, "bulletinLink") and contains(@class, "bull-item__self-link")]/@href')
                            if product_link:
                                product_url = product_link[0]
                                print(f"Город: {city['name']} | Категория: {category_name} | Ссылка: https://www.farpost.ru{product_url}")
                                seller_info = {'type': seller_type}  # Создаем словарь с информацией о продавце
                                time.sleep(5)
                                search_sellers(f"https://www.farpost.ru{product_url}", city, seller_info)  # Передаем seller_info
                                count_sellers -= 1
                    else:
                        for product in products:
                            company_block = product.xpath('.//div[contains(@class, "ellipsis-text__left-side")]')
                            seller_type = "Компания" if company_block else "Частник"
                            
                            product_link = product.xpath('.//a[contains(@class, "bulletinLink") and contains(@class, "bull-item__self-link")]/@href')
                            if product_link:
                                product_url = product_link[0]
                                print(f"Город: {city['name']} | Категория: {category_name} | Ссылка: https://www.farpost.ru{product_url}")
                                seller_info = {'type': seller_type}  # Создаем словарь с информацией о продавце
                                time.sleep(5)
                                search_sellers(f"https://www.farpost.ru{product_url}", city, seller_info)  # Передаем seller_info

                    page += 1
                else:
                    logging.info(f"Продукты не найдены на странице {page}. Завершение поиска в категории.")
                    break
                    
            else:
                logging.error(f"Ошибка при получении страницы {page}: {response.status_code}")
                time.sleep(5)
                
        except Exception as e:
            logging.error(f"Ошибка при обработке страницы {page}: {e}")
            time.sleep(5)
            continue