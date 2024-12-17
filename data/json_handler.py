import json
import logging

def save_seller_to_json(seller_info):
    logging.info(f"Сохранение информации о продавце: {seller_info.get('name', 'Неизвестный')}")
    sellers = []
    try:
        # Пытаемся прочитать существующий файл
        with open('Продавцы.json', 'r', encoding='utf-8') as f:
            content = f.read()
            if content:
                sellers = json.loads(content)
                if not isinstance(sellers, list):
                    sellers = [sellers]
                logging.info(f"Загружено существующих продавцов: {len(sellers)}")
    except (FileNotFoundError, json.JSONDecodeError):
        logging.info("Создание нового файла с продавцами")
        sellers = []

    # Проверяем, есть ли уже такой продавец
    seller_exists = False
    for existing_seller in sellers:
        if existing_seller['name'] == seller_info['name']:
            logging.info(f"Обновление существующего продавца: {seller_info['name']}")
            # Обновляем телефоны и emails
            existing_seller['phones'] = list(set(existing_seller['phones'] + seller_info['phones']))
            existing_seller['emails'] = list(set(existing_seller['emails'] + seller_info['emails']))
            
            if 'date' in existing_seller and 'date' in seller_info:

                all_dates = []
                for date_item in existing_seller['date'] + seller_info['date']:
                    if isinstance(date_item, list):
                        all_dates.extend(date_item)
                    else:
                        all_dates.append(date_item)
                existing_seller['date'] = list(set(all_dates))
            
            if 'category' in existing_seller and 'category' in seller_info:
                all_categories = []
                for cat_item in existing_seller['category'] + seller_info['category']:
                    if isinstance(cat_item, list):
                        all_categories.extend(cat_item)
                    else:
                        all_categories.append(cat_item)
                existing_seller['category'] = list(set(all_categories))
            elif 'category' in seller_info:
                existing_seller['category'] = seller_info['category']
                
            seller_exists = True
            break

    if not seller_exists:
        logging.info(f"Добавление нового продавца: {seller_info['name']}")
        # Обработка данных перед добавлением нового продавца
        if 'date' in seller_info and isinstance(seller_info['date'], list):
            all_dates = []
            for date_item in seller_info['date']:
                if isinstance(date_item, list):
                    all_dates.extend(date_item)
                else:
                    all_dates.append(date_item)
            seller_info['date'] = list(set(all_dates))
            
        if 'category' in seller_info and isinstance(seller_info['category'], list):
            all_categories = []
            for cat_item in seller_info['category']:
                if isinstance(cat_item, list):
                    all_categories.extend(cat_item)
                else:
                    all_categories.append(cat_item)
            seller_info['category'] = list(set(all_categories))
            
        sellers.append(seller_info)

    # Перезаписываем весь файл
    with open('Продавцы.json', 'w', encoding='utf-8') as f:
        json.dump(sellers, f, ensure_ascii=False, indent=4)
        logging.info("Файл с продавцами успешно обновлен")