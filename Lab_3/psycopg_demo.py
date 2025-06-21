import psycopg2

# параметри підключення
conn = psycopg2.connect(
    dbname="dragoncollect",
    user="postgres",
    password="2684",
    host="127.0.0.1",
    port="5432"
)

# курсор для виконання SQL-запитів
cursor = conn.cursor()

# Створення таблиці
cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_table (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER
    )
""")
conn.commit()
print("Таблиця test_table створена")

# вставка даних
cursor.execute("INSERT INTO test_table (name, age) VALUES (%s, %s)", ("Астрід", 22))
cursor.execute("INSERT INTO test_table (name, age) VALUES (%s, %s)", ("Іккінг", 23))
conn.commit()
print("Дані вставлено")

# вибірка даних
cursor.execute("SELECT * FROM test_table")
rows = cursor.fetchall()
print("Вміст test_table:")
for row in rows:
    print(row)

# оновлення
cursor.execute("UPDATE test_table SET age = age + 1 WHERE name = %s", ("Іккінг",))
conn.commit()
print("Вік Іккінга оновлено")

# видалення
cursor.execute("DELETE FROM test_table WHERE name = %s", ("Астрід",))
conn.commit()
print("Астрід видалено з таблиці")

# повторна вибірка для перевірки
cursor.execute("SELECT * FROM test_table")
rows = cursor.fetchall()
print("Вміст після змін:")
for row in rows:
    print(row)
 
#Очистити таблицю (за потреби)
def clear_table():
    #cursor.execute("DELETE FROM test_table")
    cursor.execute("TRUNCATE TABLE test_table RESTART IDENTITY")
    conn.commit()
    print("Таблицю test_table очищено")

# Виклик функції для очищення таблиці
#clear_table()

# закриття підключення
cursor.close()
conn.close()

print("Підключення закрито")
