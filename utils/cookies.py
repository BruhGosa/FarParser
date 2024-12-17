import requests
import logging

def get_new_cookies():
    logging.info("Запрос новых куки")
    response = requests.get("https://www.farpost.ru/")
    cookies = {}
    
    # Получаем все куки из заголовков
    if 'Set-Cookie' in response.headers:
        logging.info("Обработка полученных куки")
        all_cookies = response.headers.get('Set-Cookie').split(', ')
        for cookie in all_cookies:
            if 'ring=' in cookie or 'ring_session=' in cookie:
                name = cookie.split('=')[0]
                value = cookie.split('=')[1].split(';')[0]
                cookies[name] = value
    logging.info(f"Получены новые куки: {len(cookies)} шт.")
    return cookies
