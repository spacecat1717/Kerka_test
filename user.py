import psycopg2
from log_settings import LoggingSettings


class User():
    #TODO в конце поставить заглушки вместо данных ДБ
    logging = LoggingSettings()
    conn = psycopg2.connect(dbname='kerka_test_db',
                            user='postgres', password='Teatea_0', host='localhost')
    cursor = conn.cursor()
    def __init__(self):
        try:
            commands = (
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN,
                    is_blocked BOOLEAN
                )
                """,
                
                """
                CREATE SEQUENCE IF NOT EXISTS user_sequence
                start 1
                increment 1;
                """
            )
            for command in commands:
                self.cursor.execute(command)
            self.conn.commit()
            self.logging.logger_info.info('Users table is ready to work')
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_crit.critical(error)

    def create_user(self, user_id, username, is_admin=False, is_blocked=False):
        try:
            command = (
                """
                INSERT INTO users (ID, USER_ID, USERNAME, IS_ADMIN, IS_BLOCKED) 
                                    VALUES (nextval('user_sequence'), %s, %s, %s, %s)
                """)
            values = (user_id, username, is_admin, is_blocked, )
            self.cursor.execute(command, values)
            self.conn.commit()
            self.logging.logger_info.info(f'User{user_id}, {username} was created in DB')
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_crit.critical(error)

    def get_user_admin_status(self, user_id):
        self.logging.logger_info.info(f'Trying to execute admin status for user {user_id}')
        try:
            command = (
                """
                SELECT is_admin FROM users WHERE user_id = %s
                """
            )
            value = user_id
            self.cursor.execute(command, (value,))
            res = self.cursor.fetchone()[0]
            self.logging.logger_info.info(f'Admin status for user {user_id} executed!')
            return res
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)

    def set_admin_status(self, user_id):
        self.logging.logger_info.info(f'Giving an admin status to user {user_id}')
        try:
            command = (
                """
                UPDATE users SET is_admin = %s WHERE user_id = %s 
                """
            )
            values = (True, user_id)
            self.cursor.execute(command, values)
            self.conn.commit()
            self.logging.logger_info.info(f'User {user_id} id admin now!')
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)

    def get_user_block_status(self, user_id):
        try:
            self.logging.logger_info.info(f'Checking block status for user {user_id}')
            command = (
                """
                SELECT is_blocked FROM users WHERE user_id = %s
                """
            )
            value = user_id
            self.cursor.execute(command, (user_id, ))
            res = self.cursor.fetchone()[0]
            self.logging.logger_info.info(f'Block status of user {user_id} executed!')
            return res
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)

    def set_block(self, user_id):
        self.logging.logger_info.info(f'Checking block status for user {user_id}')
        try:
            command = (
                """
                UPDATE users SET is_blocked = %s WHERE user_id = %s
                """
            )
            values = (True, user_id)
            self.cursor.execute(command, values)
            self.conn.commit()
            self.logging.logger_info.info(f'User {user_id} was blocked!')
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)

    def get_all_users(self):
        self.logging.logger_info.info('Start getting all users info')
        try:
            command = (
                """
                SELECT user_id, username, is_admin, is_blocked FROM users
                """
            )
            self.cursor.execute(command)
            res = self.cursor.fetchall()
            query = []
            for i in res:
                user = {'user_id': i[0],
                'username': i[1],
                'admin': i[2],
                'blocked': i[3]}
                query.append(user)
            self.logging.logger_info.info('Data got')   
            return query
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)

u = User()
u.get_all_users()


