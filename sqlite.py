import sqlite3
from config import USERS_COUNT

database = 'db.db'

def sqlite_add_new_user(user):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    simular = cursor.execute(f"SELECT user_name FROM users WHERE user_id = {user['id']}").fetchone()
    if simular == None:
        cursor.execute(f"INSERT INTO users(user_id, user_name, added_users, can_send_message, is_admin, posts_per_day) VALUES ({user['id']}, '{user['username']}', 0, 0, 0, 0)")
    connect.commit()
    connect.close()

def sqlite_add_new_user_optional(user):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    simular = cursor.execute(f"SELECT user_name FROM users WHERE user_id = {user['id']}").fetchone()
    if simular == None:
        cursor.execute(f"INSERT INTO users(user_id, user_name, added_users, can_send_message, is_admin, posts_per_day) VALUES ({user['id']}, '{user['username']}', 0, {user['send_message']}, {user['admin']}, 0)")
    connect.commit()
    connect.close()

def sqlite_update_added_users(user):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    added_users = int(cursor.execute(f"SELECT added_users FROM users WHERE user_id = {user['id']}").fetchone()[0])
    # print(added_users)
    added_users += 1
    cursor.execute(
        f"UPDATE users SET added_users = {added_users} WHERE user_id = {user['id']}")
    if added_users >= USERS_COUNT:
        cursor.execute(
            f"UPDATE users SET can_send_message = 1 WHERE user_id = {user['id']}")
    connect.commit()
    connect.close()

def sqlite_update_posts(user):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    posts = int(cursor.execute(f"SELECT posts_per_day FROM users WHERE user_id = {user['id']}").fetchone()[0])
    posts += 1
    cursor.execute(
        f"UPDATE users SET posts_per_day = {posts} WHERE user_id = {user['id']}")
    connect.commit()
    connect.close()

# def sqlite_update_can_send_message(user):
#     connect = sqlite3.connect(database)
#     cursor = connect.cursor()
#     cursor.execute(
#         f"UPDATE users SET can_send_message = 1 WHERE user_id = {user['id']}")
#     connect.commit()
#     connect.close()

def sqlite_select_posts(user):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    posts = int(cursor.execute(f"SELECT posts_per_day FROM users WHERE user_id = {user['id']}").fetchone()[0])
    connect.commit()
    connect.close()
    return posts

def sqlite_update_admin(user):
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute(
        f"UPDATE users SET is_admin = 1 WHERE user_id = {user['id']}")
    connect.commit()
    connect.close()

def sqlite_clear_posts():
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    cursor.execute(
        f"UPDATE users SET posts_per_day = 0")
    connect.commit()
    connect.close()

def sqlite_select_all_users_can_send_message():
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    raw_usernames = cursor.execute(
        f"SELECT user_name FROM users WHERE can_send_message = 1 AND is_admin = 0").fetchall()
    usernames = []
    for i in raw_usernames:
        usernames.append(i[0])
    # print(usernames)
    connect.commit()
    connect.close()
    return usernames

def sqlite_select_admins():
    connect = sqlite3.connect(database)
    cursor = connect.cursor()
    raw_admins = cursor.execute(
        f"SELECT user_id FROM users WHERE is_admin = 1").fetchall()
    admins = []
    for admin in raw_admins:
        admins.append(int(admin[0]))
    connect.commit()
    connect.close()
    return admins

if __name__=='__main__':
    user = {
        'id': 2,
        'username': 'name2'}
    # sqlite_add_new_user(user)
    # for i in range(10):
    #     sqlite_update_added_users(user)
    # sqlite_update_posts(user)
    # print(sqlite_select_admins())