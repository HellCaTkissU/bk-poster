import mysql.connector
from bs4 import BeautifulSoup
import requests

# URL, откуда извлекаем данные
url = 'https://kitobxon.com/uz/kitob/ornitologiya'

# Получаем HTML-код страницы
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

main_class = soup.find('div', class_="long_about")

header = main_class.find('h2').get_text()
genre = main_class.find('a', attrs={'itemprop': 'genre'}).get_text()
author = main_class.find('a', attrs={'itemprop': 'author'}).get_text()

try:
    # Подключение к базе данных
    connection = mysql.connector.connect(user='root', password='EAdeadspace3@',
                                         host='localhost', database='myrog')
    print("Подключение к базе данных успешно.")

    # Создаем курсор для выполнения SQL-запросов
    cursor = connection.cursor()

    # SQL-запрос для добавления новой книги
    insert_query = "INSERT INTO books (header, genre, author) VALUES (%s, %s, %s)"

    # Данные новой книги
    book_data = (header, genre, author)

    # Выполняем SQL-запрос с данными книги
    cursor.execute(insert_query, book_data)

    # Применение изменений
    connection.commit()
    print("Книга успешно добавлена в базу данных.")

except mysql.connector.Error as error:
    print("Ошибка при добавлении книги в базу данных: {}".format(error))

finally:
    # Закрытие курсора и соединения
    cursor.close()
    connection.close()
    print("Соединение с базой данных закрыто.")
