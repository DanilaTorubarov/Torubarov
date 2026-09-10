from flask import Flask, render_template, request, jsonify
import mysql.connector
import bcrypt

def hash_password(password):
    # Пароль должен быть в байтовом формате
    password_bytes = password.encode('utf-8')
    # Генерируем соль
    salt = bcrypt.gensalt()
    # Создаём хеш
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode()  # Возвращаем строку для хранения

app = Flask(__name__)  

@app.route('/user_register', methods=['POST'])
def user_register():
    req = request.get_json()
    cnx = mysql.connector.connect(
        host="185.114.247.43",
        port=3306,
        database="sch688_vvedenie",
        user="sch688_vvedenie",
        password="Qwerty123")
    
    name = req['name']
    login = req['email']
    password = hash_password(req['password'])
    print(password)
    date = (name, login, password)
    cur = cnx.cursor()
    rows = cur.execute('INSERT INTO `users`(`username`, `email`, `password_hash`) VALUES (%s, %s, %s)', date)
    cnx.commit()
    cnx.close()

    return 'vse ok'

# # Fetch one result
# row = cur.fetchone()
# print("Current date is: {0}".format(row[0]))

# # Close connection
# cnx.close()

@app.route("/")
def registration():
    return render_template('registration.html')

@app.route("/login")
def login():
    return render_template('login.html')
app.run()