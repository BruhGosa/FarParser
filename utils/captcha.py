from lxml import html
import logging

def check_captcha(response_text):
    tree = html.fromstring(response_text)
    captcha = tree.xpath('//div[contains(@class, "rc-anchor-content")]')
    if captcha:
        logging.warning(f"Обнаружена капча на странице!")
        return True
    return False