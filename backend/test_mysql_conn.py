import pymysql

passwords = ['', 'root', 'admin', 'password', '123456']
connected_pwd = None

for pwd in passwords:
    try:
        conn = pymysql.connect(host='localhost', port=3306, user='root', password=pwd)
        print(f"[OK] Successfully connected to MySQL 8.4 Server with user='root', password='{pwd}'")
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS hotel_analytics_db;")
        cursor.execute("SHOW DATABASES;")
        databases = [row[0] for row in cursor.fetchall()]
        print("MySQL Databases:", databases)
        connected_pwd = pwd
        conn.close()
        break
    except Exception as e:
        print(f"Password '{pwd}' attempt error: {e}")

if connected_pwd is None:
    print("Could not connect to MySQL with default credentials.")
