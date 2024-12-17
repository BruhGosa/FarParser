import requests
from lxml import html
import time
import random
import logging
from utils.cookies import get_new_cookies
from utils.captcha import check_captcha
from data.json_handler import save_seller_to_json


def search_additional_information_seller(seller_url, seller_info):
    try:
        logging.info(f"Получение дополнительной информации продавца: {seller_url}")
        cookies = get_new_cookies()
        
        # Делаем запрос к странице продавца
        response = requests.get(seller_url, cookies=cookies)
        if response.status_code == 200:
            tree = html.fromstring(response.text)
            # Проверяем наличие капчи
            if check_captcha(response.text):
                logging.warning(f"Обнаружена капча при загрузке дополнительной информации")
                time.sleep(5)
                return False
                
            logging.info("Поиск дополнительных контактов")

            additional_phones = tree.xpath('//span[contains(@class, "phone")]//text()')
            additional_phones = [phone.strip() for phone in additional_phones if phone.strip()]
            logging.info(f"Найдено дополнительных телефонов: {len(additional_phones)}")
            
            additional_emails = tree.xpath('//a[contains(@class, "emailLink")]//text()')
            additional_emails = [email.strip() for email in additional_emails if email.strip()]
            logging.info(f"Найдено дополнительных email: {len(additional_emails)}")
            
            # Объединяем и удаляем дубликаты
            all_phones = list(set(seller_info['phones'] + additional_phones))
            all_emails = list(set(seller_info['emails'] + additional_emails))
            
            # Обновляем информацию о продавце
            seller_info['phones'] = all_phones
            seller_info['emails'] = all_emails
            
            logging.info("Сохранение обновленной информации о продавце")
            save_seller_to_json(seller_info)
            time.sleep(5)
            
    except Exception as e:
        logging.error(f"Ошибка при получении дополнительной информации о продавце: {e}")


def search_sellers(product_url, city, seller_info):
    try:

        logging.info(f"Начало обработки нового продавца со страницы: {product_url}")

        phones = []
        emails = []

        # Получаем новые куки для запроса
        cookies = get_new_cookies()
        
        # Делаем запрос к странице продукта
        response = requests.get(product_url, cookies=cookies)
        
        if response.status_code == 200:
            # Проверяем наличие капчи
            if check_captcha(response.text):
                logging.warning(f"Обнаружена капча при загрузке страницы продавца")
                time.sleep(60)
                return False
                
            tree = html.fromstring(response.text)
            
            # Поиск продавца
            saller = tree.xpath('//span[contains(@class, "userNick") and contains(@class, "auto-shy")]/a')
            
            if not saller:
                logging.error(f"Продавец не найден на странице: {product_url}")
                return False
            
            logging.info(f"Найден продавец: {saller[0].text_content()}")
            
            # Получаем хлебные крошки для категории
            breadcrumbs = tree.xpath('//span[@itemprop="name"]/text()')
            breadcrumbs = [crumb.strip() for crumb in breadcrumbs if crumb.strip()]
            category_path = " / ".join(breadcrumbs)
            logging.info(f"Категория: {category_path}")

            # Получаем дату
            data = tree.xpath('//div[contains(@class, "viewbull-actual-date")]//text()')
            logging.info(f"Дата: {data}")

            # Получаем ссылку на контакты
            contact_link = tree.xpath('//a[contains(@class, "viewAjaxContacts")]/@href')

            if contact_link:
                contact_url = f"https://www.farpost.ru{contact_link[0]}"
                logging.info(f"Ссылка на контакты: {contact_url}")

                # Добавляем случайную задержку перед запросом контактов
                time.sleep(random.uniform(2, 4))
                contact_response = requests.get(contact_url, cookies=cookies)
                
                if contact_response.status_code == 200:
                    if check_captcha(contact_response.text):
                        logging.warning(f"Обнаружена капча при загрузке страницы контактов")
                        time.sleep(60)
                        return False
                        
                    contact_tree = html.fromstring(contact_response.content)
                    
                    # Получаем телефоны
                    phones = contact_tree.xpath('//div[contains(@class, "new-contacts__td") and contains(@class, "new-contact__phone")]//text()')
                    phones = [phone.strip() for phone in phones if phone.strip()]
                    logging.info(f"Найдено телефонов: {len(phones)}")
                    # Получаем email
                    emails = contact_tree.xpath('//a[contains(@class, "emailLink")]//text()')
                    emails = [email.strip() for email in emails if email.strip()]
                    logging.info(f"Найдено email: {len(emails)}")
                else:
                    logging.error(f"Ошибка при получении контактов: {contact_response.status_code}")

            name_saller = saller[0].text_content()
            geo_seller = city['name']

            # Создаем информацию о продавце
            seller_info.update({
                'name': name_saller,
                'phones': phones,
                'geo': geo_seller,
                'date': [data],
                'category': [category_path],
                'emails': emails,
            })

            logging.info(f"Сохранение информации о продавце: {name_saller}")
            time.sleep(5)
            # Получаем дополнительную информацию
            search_additional_information_seller(f"https://www.farpost.ru{saller[0].get('href')}", seller_info)
            
        else:
            logging.error(f"Ошибка при получении страницы продавца: {response.status_code}")
            
    except Exception as e:
        logging.error(f"Ошибка при поиске информации о продавце: {e}")
        time.sleep(5)
    
    return False