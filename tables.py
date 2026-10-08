import mysql.connector
cnx = mysql.connector.connect(
    host="185.114.247.43", port=3306,
    database="sch688_vvedenie",
    user="sch688_vvedenie", password="Qwerty123"
)
cur = cnx.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    request_type ENUM('text', 'image') NOT NULL DEFAULT 'text',
    user_message TEXT,
    ai_reply TEXT,
    cost DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_created (user_id, created_at)
)""")
cur.execute("""
CREATE TABLE IF NOT EXISTS balance_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_created (user_id, created_at)
)""")
cnx.commit()
cur.close()
cnx.close()
print("Таблицы созданы")