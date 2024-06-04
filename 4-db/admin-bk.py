import mysql.connector

try:
    # Подключение к базе данных
    connection = mysql.connector.connect(user='a0426806_bzkm_test_user', password='z%jxCTg1#f',
                                         host='localhost', database='a0426806_bizkim_test_db')
    print("Подключение к базе данных успешно.")

    # Если вам нужно выполнить какие-то действия с базой данных, добавьте их здесь

    # Не забудьте закрыть соединение после завершения работы
    connection.close()
    print("Соединение с базой данных закрыто.")

except mysql.connector.Error as error:
    print("Ошибка при подключении к базе данных: {}".format(error))
