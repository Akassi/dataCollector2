# database.py
import psycopg2
from psycopg2 import sql
import config
import logging

def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None

def user_exists(conn, user_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("SELECT 1 FROM users WHERE discordid = %s"),
                [str(user_id)]
            )
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Ошибка при проверке пользователя в базе данных: {e}")
        return False

def add_user_to_db(conn, user_id, user_name):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("INSERT INTO users (discordid, login) VALUES (%s, %s) ON CONFLICT (discordid) DO NOTHING RETURNING discordid"),
                [str(user_id), user_name]
            )
            if cursor.fetchone():
                update_user_discord_status(conn, user_id, True, False)
            conn.commit()
            print(f"Пользователь {user_name} добавлен в базу данных")
            logging.info(f"Пользователь {user_name} с id {user_id} добавлен в базу данных")
    except Exception as e:
        print(f"Ошибка при добавлении пользователя в базу данных: {e}")

def update_user_discord_status(conn, user_id, in_discord, is_kicked):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("UPDATE users SET in_discord = %s, is_kicked = %s WHERE discordid = %s"),
                [in_discord, is_kicked, str(user_id)]
            )
            conn.commit()
            print(f"Статус пользователя с id {user_id} обновлен: in_discord={in_discord}, is_kicked={is_kicked}")
            logging.info(f"Статус пользователя с id {user_id} обновлен: in_discord={in_discord}, is_kicked={is_kicked}")
    except Exception as e:
        print(f"Ошибка при обновлении статуса пользователя в Discord: {e}")

def get_user_id(conn, discord_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("SELECT id FROM users WHERE discordid = %s"),
                [str(discord_id)]
            )
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"Ошибка при получении user_id из базы данных: {e}")
        return None

def add_user_call_to_db(conn, discord_id):
    user_id = get_user_id(conn, discord_id)
    if not user_id:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("INSERT INTO user_calls (userid, connecttime, createdate) VALUES (%s, NOW(), NOW())"),
                [user_id]
            )
            conn.commit()
            print(f"Запись о звонке для пользователя с id {user_id} добавлена в базу данных")
            logging.info(f"Запись о звонке для пользователя с id {user_id} добавлена в базу данных")
    except Exception as e:
        print(f"Ошибка при добавлении записи о звонке в базу данных: {e}")

def update_user_call_in_db(conn, discord_id):
    user_id = get_user_id(conn, discord_id)
    if not user_id:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("""
                    UPDATE user_calls
                    SET disconnecttime = NOW(), updatedate = NOW(), time = NOW() - connecttime
                    WHERE userid = %s AND disconnecttime IS NULL
                    RETURNING connecttime
                """),
                [user_id]
            )
            conn.commit()
            print(f"Запись о звонке для пользователя с id {user_id} обновлена в базе данных")
            logging.info(f"Запись о звонке для пользователя с id {user_id} обновлена в базе данных")
    except Exception as e:
        print(f"Ошибка при обновлении записи о звонке в базу данных: {e}")

def get_user_msg_record_pvp(conn, user_id, month):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("SELECT id, msg_count FROM user_msg_month_count_pvp WHERE userid = %s AND month = %s"),
                [user_id, month]
            )
            return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении записи о сообщениях пользователя в канале PvP: {e}")
        return None

def create_user_msg_record_pvp(conn, user_id, month):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("INSERT INTO user_msg_month_count_pvp (userid, msg_count, month, createdate) VALUES (%s, 0, %s, NOW())"),
                [user_id, month]
            )
            conn.commit()
            print(f"Создана новая запись о сообщениях для пользователя с id {user_id} в канале PvP на месяц {month}")
    except Exception as e:
        print(f"Ошибка при создании записи о сообщениях пользователя в канале PvP: {e}")

def update_user_msg_count_pvp(conn, record_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("UPDATE user_msg_month_count_pvp SET msg_count = msg_count + 1, updatedate = NOW() WHERE id = %s"),
                [record_id]
            )
            conn.commit()
            print(f"Обновлён счётчик сообщений для записи с id {record_id} в канале PvP")
    except Exception as e:
        print(f"Ошибка при обновлении счётчика сообщений пользователя в канале PvP: {e}")

def get_user_msg_record(conn, user_id, month):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("SELECT id, msg_count FROM user_msg_month_count WHERE userid = %s AND month = %s"),
                [user_id, month]
            )
            return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении записи о сообщениях пользователя: {e}")
        return None

def create_user_msg_record(conn, user_id, month):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("INSERT INTO user_msg_month_count (userid, msg_count, month, createdate) VALUES (%s, 0, %s, NOW())"),
                [user_id, month]
            )
            conn.commit()
            print(f"Создана новая запись о сообщениях для пользователя с id {user_id} на месяц {month}")
    except Exception as e:
        print(f"Ошибка при создании записи о сообщениях пользователя: {e}")

def update_user_msg_count(conn, record_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("UPDATE user_msg_month_count SET msg_count = msg_count + 1, updatedate = NOW() WHERE id = %s"),
                [record_id]
            )
            conn.commit()
            print(f"Обновлён счётчик сообщений для записи с id {record_id}")
    except Exception as e:
        print(f"Ошибка при обновлении счётчика сообщений пользователя: {e}")

def get_user_msg_record_pve(conn, user_id, month):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("SELECT id, msg_count FROM user_msg_month_count_pve WHERE userid = %s AND month = %s"),
                [user_id, month]
            )
            return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении записи о сообщениях пользователя в канале PvE: {e}")
        return None

def create_user_msg_record_pve(conn, user_id, month):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("INSERT INTO user_msg_month_count_pve (userid, msg_count, month, createdate) VALUES (%s, 0, %s, NOW())"),
                [user_id, month]
            )
            conn.commit()
            print(f"Создана новая запись о сообщениях для пользователя с id {user_id} в канале PvE на месяц {month}")
    except Exception as e:
        print(f"Ошибка при создании записи о сообщениях пользователя в канале PvE: {e}")

def update_user_msg_count_pve(conn, record_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("UPDATE user_msg_month_count_pve SET msg_count = msg_count + 1, updatedate = NOW() WHERE id = %s"),
                [record_id]
            )
            conn.commit()
            print(f"Обновлён счётчик сообщений для записи с id {record_id} в канале PvE")
    except Exception as e:
        print(f"Ошибка при обновлении счётчика сообщений пользователя в канале PvE: {e}")

def get_all_users(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("SELECT discordid FROM users"))
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении всех пользователей из базы данных: {e}")
        return []

def update_user_ban_status(conn, user_id, is_banned):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("UPDATE users SET is_banned = %s WHERE discordid = %s"),
                [is_banned, str(user_id)]
            )
            conn.commit()
            status = "забанен" if is_banned else "не забанен"
            print(f"Статус пользователя с id {user_id} обновлен: {status}")
            logging.info(f"Статус пользователя с id {user_id} обновлен: {status}")
    except Exception as e:
        print(f"Ошибка при обновлении статуса бана пользователя: {e}")

def add_discord_to_db(conn, discord_id, discord_name):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("INSERT INTO discord (discordId, discordName) VALUES (%s, %s) ON CONFLICT (discordId) DO NOTHING"),
                [str(discord_id), discord_name]
            )
            conn.commit()
            print(f"Сервер {discord_name} добавлен в базу данных")
            logging.info(f"Сервер {discord_name} с id {discord_id} добавлен в базу данных")
    except Exception as e:
        print(f"Ошибка при добавлении сервера в базу данных: {e}")

def get_discord_id(conn, discord_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("SELECT id FROM discord WHERE discordId = %s"),
                [str(discord_id)]
            )
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"Ошибка при получении discord_id из базы данных: {e}")
        return None

def add_message_to_db(conn, user_id, discord_id, message, message_date):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("INSERT INTO message_log (userId, discordId, message, message_date) VALUES (%s, %s, %s, %s)"),
                [user_id, discord_id, message, message_date]
            )
            conn.commit()
            print(f"Сообщение от пользователя с id {user_id} добавлено в базу данных")
            logging.info(f"Сообщение от пользователя с id {user_id} добавлено в базу данных")
    except Exception as e:
        print(f"Ошибка при добавлении сообщения в базу данных: {e}")
