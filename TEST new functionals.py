from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import os
import re

# Переменные для логина и пароля
login = 'abris@abrisplus.ru'
password = '123456'

# Базовый URL для изображений
base_image_url = "https://www.abrisplus.ru"

# Текстовые данные для поиска элементов на странице
search_query = 'Клинико-аналитические инструменты'  # Текст для поиска категории товара
country_option_text = "Россия"  # Текст опции выбора страны
your_brand = "АБРИС+" #Текст для бренда
group_input_placeholder = "Автоматические биохимические анализаторы"  # Placeholder для поля группировка
minimal_input_value = '10'  # Значение для ввода минимального количества товара
dropdown_option_text = "уница"  # Текст опции для выпадающего списка

def download_image(img_url, img_name):
    response = requests.get(img_url, stream=True)
    if response.status_code == 200:
        with open(img_name, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

def normalize_product_name(name):
    words = re.findall(r"[\w+—-]+|[.,!?;]", name)
    return ' '.join(word.capitalize() if word.isalnum() else word for word in words)

def fill_product_info(product_url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)

    try:
        # Get product information from the provided URL
        response = requests.get(product_url)
        soup = BeautifulSoup(response.text, "html.parser")
        main_class = soup.find('div', class_="span8") #MAIN BODY

        name_p_element = main_class.find('h1') #НАЗВАНИЕ PRODUCT
        name_p = name_p_element.get_text()

        description_element = main_class.find('p', itemprop='description') #DESCRIPTION PRODUCT
        description = description_element.get_text()

        # Find the image URL
        img_element = main_class.find('img', {'style': 'opacity:0'}) #PICTURE PRODUCT
        img_url = f"{base_image_url}{img_element['src']}" if img_element else None
        img_name = "product_image.jpg"

        if img_url:
            download_image(img_url, img_name)

        # Authentication and product filling
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

        # Filling product fields
        search_field = driver.find_element(By.ID, 'searchq2')
        search_field.send_keys(search_query)
        time.sleep(5)

        category = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'bread_piece')))
        category.click()

        product_name_xpath = '//input[@name="p_name"]'
        normalized_name = normalize_product_name(name_p)
        product_name_field = driver.find_element(By.XPATH, product_name_xpath)
        product_name_field.send_keys(normalized_name)
        time.sleep(1)

        description_css_selector = '.nicEdit-main'
        description_field = driver.find_element(By.CSS_SELECTOR, description_css_selector)
        description_field.send_keys(description)

        country_dropdown = driver.find_element(By.ID, 'select2-chosen-1')
        country_dropdown.click()
        country_option = driver.find_element(By.XPATH, f'//div[contains(text(), "{country_option_text}")]')
        country_option.click()

        additional_fields_button = driver.find_element(By.CLASS_NAME, 'show_hide_inputs')
        additional_fields_button.click()
        time.sleep(1)

        # Заполнение поля группировки
        group_input = driver.find_element(By.NAME, 'p_gruppa_new')
        group_input.send_keys(group_input_placeholder)  # Используйте group_input_placeholder для вставки слова

        minimal_input = driver.find_element(By.NAME, 'p_minimal')
        minimal_input.send_keys(minimal_input_value)

        # Находим поле ввода бренда
        brand_input = driver.find_element(By.NAME, 'p_brand')
        brand_input.clear()
        brand_input.send_keys(your_brand)

        # Кликнуть на элемент, чтобы открыть выпадающий список
        driver.find_element(By.ID, 'select2-chosen-4').click()
        options = driver.find_elements(By.CSS_SELECTOR, '.select2-results li')
        for option in options:
            if dropdown_option_text in option.text:
                option.click()
                break

        radio_button = driver.find_element(By.CSS_SELECTOR, 'input[name="p_radio_price"][value="3"]')
        radio_button.click()

        # Uploading the product image
        if img_url and os.path.exists(img_name):
            # Click the image upload element to trigger the file input
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
        print("Произошла ошибка:", e)

product_url = input("Введите URL продукта: ")
fill_product_info(product_url)
