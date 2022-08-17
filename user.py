import psycopg2
from log_settings import LoggingSettings
import main_settings


class User():
    #TODO в конце поставить заглушки вместо данных ДБ
    logging = LoggingSettings()
    conn = main_settings.conn
    cursor = conn.cursor()
    def __init__(self):
        try:
            commands = (

                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    balance BIGINT,
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

    def check_user_exists(self, user_id):
        self.logging.logger_info.info(f'Trying to find user {user_id} in DB')
        command = (
            """
            SELECT user_id FROM users WHERE user_id = %s
            """
        )
        value = (user_id, )
        self.cursor.execute(command, value)
        if self.cursor.fetchone() is not None:
            self.logging.logger_info.info(f'User {user_id} exists')
            return True
        self.logging.logger_info.info(f'User {user_id} does not exists')
        return False

    def create_user(self, user_id, username, balance=0, is_admin=False, is_blocked=False):
        try:
            command = (
                """
                INSERT INTO users (ID, USER_ID, USERNAME, BALANCE, IS_ADMIN, IS_BLOCKED) 
                                    VALUES (nextval('user_sequence'), %s, %s, %s, %s, %s)
                """)
            values = (user_id, username, balance, is_admin, is_blocked)
            self.cursor.execute(command, values)
            self.conn.commit()
            self.logging.logger_info.info(f'User{user_id}, {username} was created in DB')
            return True
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
            self.logging.logger_error.error(f'User {user_id} does not exists!')
            return False

    def set_admin_status(self, user_id):
        self.logging.logger_info.info(f'Giving an admin status to user {user_id}')
        try:
            if self.check_user_exists(user_id):
                if self.get_user_admin_status(user_id):
                    self.logging.logger_error.error(f'User{user_id} is already admin!')
                    return False
                else:
                    command = (
                        """
                        UPDATE users SET is_admin = %s WHERE user_id = %s 
                        """
                    )
                    values = (True, user_id)
                    self.cursor.execute(command, values)
                    self.conn.commit()
                    self.logging.logger_info.info(f'User {user_id} is admin now!')
                    return True
            else:
                self.logging.logger_warn.warning(f'User {user_id} does not exists!')
                return False
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
            self.logging.logger_warn.warning(f'User{user_id} does not exists!')
            return False

    def set_block(self, user_id):
        try:
            if self.check_user_exists(user_id):
                if self.get_user_block_status(user_id):
                    self.logging.logger_error.error(f'User{user_id} was alresdy blocked!')
                    return False
                command = (
                    """
                    UPDATE users SET is_blocked = %s WHERE user_id = %s
                    """
                )
                values = (True, user_id)
                self.cursor.execute(command, values)
                self.conn.commit()
                self.logging.logger_info.info(f'User {user_id} was blocked!')
                return True
            else:
                self.logging.logger_error.error(f'User{user_id} does not exists!')
                return False
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)

    def remove_block(self, user_id):
        try:
            if self.check_user_exists(user_id):
                if not self.get_user_block_status(user_id):
                    self.logging.logger_error.error(f'User{user_id} was not blocked!')
                    return False
                command = (
                    """
                    UPDATE users SET is_blocked = %s WHERE user_id = %s
                    """
                )
                values = (False, user_id)
                self.cursor.execute(command, values)
                self.conn.commit()
                self.logging.logger_info.info(f'User {user_id} was unblocked!')
                return True
            else:
                self.logging.logger_error.error(f'User{user_id} does not exists!')
                return False 
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)

    def get_all_users(self):
        self.logging.logger_info.info('Start getting all users info')
        try:
            command = (
                """
                SELECT user_id, username, balance, is_admin, is_blocked FROM users
                """
            )
            self.cursor.execute(command)
            res = self.cursor.fetchall()
            query = []
            for i in res:
                user = {'user_id': i[0],
                'username': i[1],
                'balance': i[2],
                'admin': i[3],
                'blocked': i[4]}
                query.append(user)
            self.logging.logger_info.info('Data got')   
            return query
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)

    def get_user_balance(self, user_id):
        self.logging.logger_info.info(f'Trying to get balance of user {user_id}')
        try:
            if self.check_user_exists(user_id):
                command = (
                    """
                    SELECT balance FROM users WHERE user_id = %s
                    """
                )
                self.cursor.execute(command, (user_id, ))
                res = self.cursor.fetchone()[0]
                self.logging.logger_info.info(f'Balance of user {user_id} got')
                return res
            else:
                self.logging.logger_error.error(f'User{user_id} does not exists!')
                return False 
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)

    def change_user_balance(self, user_id, summ):
        self.logging.logger_info.info(f'Changing balance of user {user_id}')
        try:
            if self.check_user_exists(user_id):
                command = (
                    """UPDATE users SET balance = %s WHERE user_id = %s
                    """
                )
                values = (summ, user_id)
                self.cursor.execute(command, values)
                self.logging.logger_info.info(f'Balance of user {user_id} was changed')
            else:
                self.logging.logger_error.error(f'User{user_id} does not exists!')
                return False
        except (Exception, psycopg2.DatabaseError) as error:
            self.logging.logger_error.error('DB error:', error)


