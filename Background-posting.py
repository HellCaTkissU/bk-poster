from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import os
import re

# Log In
login = 'abris@abrisplus.ru'
password = '123456'

# Main site to tale IMG
base_image_url = "https://www.abrisplus.ru"

# Auto-fill input to boxes, dropdown and radio                    # INPUTS
search_query = 'Клинико-аналитические инструменты'                # Category
country_option_text = "Россия"                                    # County
your_brand = "АБРИС+"                                             # Brand
group_input_placeholder = "ПОЛУАВТОМАТИЧЕСКИЕ ИММУНОФЕРМЕНТНЫЕ АНАЛИЗАТОРЫ".capitalize()                      # Group
minimal_input_value = '1'                                         # Minimum quantity
dropdown_option_text = "шт."                                      # Unit

group_input_placeholder = group_input_placeholder.capitalize()
group_input_placeholder = ' '.join([group_input_placeholder.split()[0]] + [word.lower() for word in group_input_placeholder.split()[1:]])

# divs. Take information                                                # LINKS
main_body_tag, main_body_class = 'div', 'span8'                         # Main body
name_product_tag = ("h1")                                               # Name
description_p_tag, description_attr = 'p', {'itemprop': 'description'}  # Description
img_tag, img_style = 'img', {'style': 'opacity:0'}                      # img


def download_image(img_url, img_name):
    response = requests.get(img_url, stream=True)
    if response.status_code == 200:
        with open(img_name, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)


def normalize_product_name(name):
    words = re.findall(r"[\w+—-]+|[.,!?;]", name)

    normalized_words = [word.capitalize() for word in words]

    for i in range(1, len(normalized_words)):
        if '-' in normalized_words[i]:
            parts = normalized_words[i].split('-')
            capitalized_parts = [part.capitalize() for part in parts]
            normalized_words[i] = '-'.join(capitalized_parts)
    return ' '.join(normalized_words)


def login_to_website(driver):
    try:
        driver.get('https://bizkim.uz/ru/add-product')
        login_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Войдите')))
        login_link.click()
        login_window = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'login')))
        username_field = driver.find_element(By.ID, 'auth_email_tel')
        password_field = driver.find_element(By.ID, 'auth_psw')
        username_field.send_keys(login)
        password_field.send_keys(password)
        login_button_inside = login_window.find_element(By.XPATH, '//button[contains(text(), "Войти")]')
        login_button_inside.click()
        time.sleep(3)
        return True
    except Exception as e:
        print("Произошла ошибка во время авторизации:", e)
        return False


def fill_product_info(driver, product_url):
    try:
        # Get product information from the provided URL
        response = requests.get(product_url)
        soup = BeautifulSoup(response.text, "html.parser")
        main_class = soup.find(main_body_tag, class_=main_body_class)                       # MAIN BODY

        name_p_element = main_class.find(name_product_tag)                                  # NAME PRODUCT
        name_p = name_p_element.get_text() if name_p_element else None
        normalized_name = normalize_product_name(name_p)

        description_element = main_class.find(description_p_tag, attrs=description_attr)    # DESCRIPTION PRODUCT
        description = description_element.get_text() if description_element else None

        # Find the image URL
        img_element = main_class.find(img_tag, img_style)
        if img_element:
            img_url = f"{base_image_url}{img_element['src']}"
            img_name = "product_image.jpg"
            download_image(img_url, img_name)

        # Filling product fields
        search_field = driver.find_element(By.ID, 'searchq2')
        search_field.send_keys(search_query)
        time.sleep(5)

        category = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'bread_piece')))
        time.sleep(1)
        category.click()

        product_name_xpath = '//input[@name="p_name"]'
        normalized_name = normalize_product_name(name_p)
        product_name_field = driver.find_element(By.XPATH, product_name_xpath)
        product_name_field.send_keys(normalized_name)
        time.sleep(1)

        description_css_selector = '.nicEdit-main'
        description_field = driver.find_element(By.CSS_SELECTOR, description_css_selector)
        description_field.send_keys(description)
        time.sleep(1)

        country_dropdown = driver.find_element(By.ID, 'select2-chosen-1')
        country_dropdown.click()
        time.sleep(1)
        country_options = driver.find_elements(By.XPATH, '//ul[@id="select2-results-1"]/li[@role="presentation"]')
        for option in country_options:
            country_name = option.find_element(By.XPATH, './div[@role="option"]').text
            if country_name == country_option_text:
                option.click()
                break

        additional_fields_button = driver.find_element(By.CLASS_NAME, 'show_hide_inputs')
        additional_fields_button.click()
        time.sleep(1)

        group_input = driver.find_element(By.NAME, 'p_gruppa_new')
        group_input.send_keys(group_input_placeholder)

        minimal_input = driver.find_element(By.NAME, 'p_minimal')
        minimal_input.send_keys(minimal_input_value)

        brand_input = driver.find_element(By.NAME, 'p_brand')
        brand_input.clear()
        brand_input.send_keys(your_brand)

        driver.find_element(By.ID, 'select2-chosen-4').click()
        options = driver.find_elements(By.CSS_SELECTOR, '.select2-results li')
        for option in options:
            if dropdown_option_text in option.text:
                option.click()
                break

        # Deafult mark on
        # radio_button = driver.find_element(By.CSS_SELECTOR, 'input[name="p_radio_price"][value="3"]')
        # radio_button.click()

        # Uploading the product image
        if img_url and os.path.exists(img_name):
            image_upload_element = driver.find_element(By.ID, 'edit_foto1')
            image_upload_element.click()

            # Provide the path to the file input field
            file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
            file_input.send_keys(os.path.abspath(img_name))

            time.sleep(3)

            submit_button = driver.find_element(By.XPATH, '//button[contains(text(), "Отправить на модерацию")]')
            submit_button.click()

            time.sleep(2)

    except Exception as e:
        print("Произошла ошибка при обработке товара по URL {}: {}".format(product_url, e))


def upload_multiple_products():
    links_input = input("Введите URL'ы продуктов, разделенные пробелами: ")
    product_urls = links_input.split()

    print('\n\nRunning...')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.binary_location = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)

    # Log in once
    if login_to_website(driver):
        for product_url in product_urls:
            fill_product_info(driver, product_url.strip())

            driver.get('https://bizkim.uz/ru/add-product')

    driver.quit()

    print('\n\nDone!')


upload_multiple_products()