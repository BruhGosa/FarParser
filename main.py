from lxml import html
import undetected_chromedriver as uc
import requests
import time
import json

# Кол-во продавцов в категории
# Если 0, то будет искать всех продавцов в категории
count_sellers_in_category = 5

def setup_driver():
    # Настройка опций
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    
    # Создание драйвера с опциями
    driver = uc.Chrome(options=options)
    return driver


def search_additional_information_seller(seller_url, seller_info, driver):
    driver.get(seller_url)
    while True: 
        try:
            time.sleep(2)
            page_source = driver.page_source
            tree = html.fromstring(page_source)

            saller = tree.xpath('//span[contains(@class, "userNick") and contains(@class, "auto-shy")]')

            if saller:
                # Собираем дополнительные телефоны
                additional_phones = tree.xpath('//span[contains(@class, "phone")]//text()')
                additional_phones = [phone.strip() for phone in additional_phones if phone.strip()]
                
                # Собираем дополнительные email
                additional_emails = tree.xpath('//a[contains(@class, "emailLink")]//text()')
                additional_emails = [email.strip() for email in additional_emails if email.strip()]
                
                # Объединяем и удаляем дубликаты
                all_phones = list(set(seller_info['phones'] + additional_phones))
                all_emails = list(set(seller_info['emails'] + additional_emails))
                
                # Обновляем информацию о продавце
                seller_info['phones'] = all_phones
                seller_info['emails'] = all_emails

                break

            else:
                print("Ожидание решения капчи или загрузки элемента...")
                time.sleep(5)

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            time.sleep(5)
            continue

    save_seller_to_json(seller_info)
    pass


def search_sellers(product_url, city, driver):
    seller_info = {}
    driver.get(product_url)
    
    while True:
        try:
            time.sleep(2)
            page_source = driver.page_source
            tree = html.fromstring(page_source)
            
            # Поиск продавца
            saller = tree.xpath('//span[contains(@class, "userNick") and contains(@class, "auto-shy")]/a')
            
            if saller:

                breadcrumbs = tree.xpath('//span[@itemprop="name"]/text()')
                breadcrumbs = [crumb.strip() for crumb in breadcrumbs if crumb.strip()]
                category_path = " / ".join(breadcrumbs)  # Соединяем все элементы через "/"

                # Пробуем найти кнопку первого типа
                try:
                    contact_button = driver.find_element("css selector", ".viewAjaxContacts.ajaxLink.gtm__btn-contact-view")
                except:
                    try:
                        # Если не нашли первую, ищем кнопку второго типа
                        contact_button = driver.find_element("css selector", ".viewAjaxContacts.bzr-btn.bzr-btn_wide.bzr-btn_size_xl.bzr-btn_style_info.gtm__btn-contact-view")
                    except:
                        print("Не удалось найти кнопку показа контактов")
                        continue
                
                # Кликаем по найденной кнопке
                driver.execute_script("arguments[0].click();", contact_button)
                time.sleep(2)
                
                
                while True:
                    # Получаем обновленный HTML после открытия модального окна
                    page_source = driver.page_source
                    tree = html.fromstring(page_source)
                    
                    # Собираем телефоны
                    phones = tree.xpath('//div[contains(@class, "new-contacts__td") and contains(@class, "new-contact__phone")]//text()')
                    if phones:
                        phones = [phone.strip() for phone in phones if phone.strip()]
                        # Собираем email
                        emails = tree.xpath('//a[contains(@class, "emailLink")]//text()')
                        if emails:
                            emails = [email.strip() for email in emails if email.strip()]
                        else:
                            emails = []
                        break
                    else:
                        print("Ожидание решения капчи или загрузки элемента...")
                        time.sleep(2)  # Ждём 2 секунды перед следующей проверкой
                
                # Формируем информацию о продавце
                name_saller = saller[0].text_content()
                geo_seller = city['name']
                seller_info = {
                    'name': name_saller,
                    'phones': phones,
                    'geo': geo_seller,
                    'category': [category_path],
                    'emails': emails
                }

                search_additional_information_seller(f"https://www.farpost.ru{saller[0].get('href')}", seller_info, driver)
                
                break
            else:
                print("Ожидание решения капчи или загрузки элемента...")
                time.sleep(5)  # Ждём 5 секунд перед следующей проверкой
                
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            time.sleep(5)
            continue



def search_products(city, category_url, category_name, driver):
    page = 1
    
    while True:
        driver.get(f"https://www.farpost.ru{category_url}/?page={page}")
        
        while True:
            try:
                time.sleep(2)
                page_source = driver.page_source
                tree = html.fromstring(page_source)
                
                products = tree.xpath('//a[contains(@class, "bulletinLink") and contains(@class, "bull-item__self-link")]')
                
                if products:
                    print(f"Город: {city['name']} | Категория: {category_name} | Страница: {page} | Найдено продуктов: {len(products)}")

                    if count_sellers_in_category > 0:
                        count_sellers = count_sellers_in_category
                        for product in products:
                            if count_sellers <= 0:  # Добавляем проверку
                                return
                            product_url = product.get('href')
                            print(f"Город: {city['name']} | Категория: {category_name} | Ссылка: https://www.farpost.ru{product_url}")
                            search_sellers(f"https://www.farpost.ru{product_url}", city, driver)
                            count_sellers -= 1
                    else:
                        for product in products:
                            product_url = product.get('href')
                            print(f"Город: {city['name']} | Категория: {category_name} | Ссылка: https://www.farpost.ru{product_url}")
                            search_sellers(f"https://www.farpost.ru{product_url}", city, driver)
                    

                    page += 1
                    break
                    
                else:
                        
                    print("Ожидание решения капчи или загрузки элементов...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                time.sleep(5)
                continue



def search_category(city_links):
    driver = setup_driver()
    try:
        for city in city_links:
            url = f"{city['href']}"
            response = requests.get(url)
            if response.status_code == 200:
                tree = html.fromstring(response.text)
                categories = tree.xpath('//a[contains(@class, "option")]')
                
                for category in categories:
                    category_url = category.get('href')
                    category_name = category.text_content().strip()
                    time.sleep(2)
                    search_products(city, category_url, category_name, driver)
    finally:
        driver.quit()



def search_city():
    url = "https://www.farpost.ru/geo/nav/city?ajax=1"
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.text)
        # Используем xpath для поиска всех ссылок внутри нужных блоков
        cities = tree.xpath('//ul[contains(@class, "city-select-control__list_city")]//li[contains(@class, "city-select-control__item")]//a[contains(@class, "city-select-control__city")]')
        
        # Создаем список для хранения информации о городах
        city_links = []
        
        # Собираем информацию о каждом городе
        for city in cities:
            city_info = {
                'id': city.get('data-id'),
                'name': city.text_content(),
                'href': city.get('href')
            }
            city_links.append(city_info)
        return city_links


def save_seller_to_json(seller_info):
    sellers = []
    try:
        # Пытаемся прочитать существующий файл
        with open('Продавцы.json', 'r', encoding='utf-8') as f:
            content = f.read()
            if content:
                sellers = json.loads(content)
                if not isinstance(sellers, list):
                    sellers = [sellers]
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не существует или пустой, создаем пустой список
        sellers = []

    # Проверяем, есть ли уже такой продавец
    seller_exists = False
    for existing_seller in sellers:
        if existing_seller['name'] == seller_info['name']:
            # Обновляем информацию существующего продавца
            existing_seller['phones'] = list(set(existing_seller['phones'] + seller_info['phones']))
            existing_seller['emails'] = list(set(existing_seller['emails'] + seller_info['emails']))
            # Объединяем категории без дубликатов
            if 'category' in existing_seller and 'category' in seller_info:
                existing_seller['category'] = list(set(existing_seller['category'] + seller_info['category']))
            elif 'category' in seller_info:
                existing_seller['category'] = seller_info['category']
            seller_exists = True
            break

    if not seller_exists:
        # Если продавец новый, добавляем его
        sellers.append(seller_info)

    # Перезаписываем весь файл
    with open('Продавцы.json', 'w', encoding='utf-8') as f:
        json.dump(sellers, f, ensure_ascii=False, indent=4)

    print(f"{'Обновлен' if seller_exists else 'Добавлен'} продавец: {seller_info['name']}")


if __name__ == "__main__":
    cities = search_city()
    search_category(cities)