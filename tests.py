import unittest, random
from user import User

class UserExistsTestCase(unittest.TestCase):
    def setUp(self):
        self.db = User()
        commands = ( """
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
        self.db.create_user(666, 'test1')
        self.db.create_user(555, 'test2')
        self.db.set_admin_status(666)
        self.db.set_block(555)


    def test_check_user_exists_True(self):
        test_user_id = 666
        self.assertTrue(self.db.check_user_exists(test_user_id))
    
    def test_check_user_exists_False(self):
        test_user_id = 123
        self.assertFalse(self.db.check_user_exists(test_user_id))

class UserFlagsTest(unittest.TestCase):
    def setUp(self):
        self.db = User()
    
    def test_set_admin_status_user_does_not_exists(self):
        test_user_id = 111
        self.assertFalse(self.db.set_admin_status(test_user_id))

    def test_get_admin_status_user_exists_not_admin(self):
        test_user_id = 555
        self.assertFalse(self.db.get_user_admin_status(test_user_id))

    def test_get_admin_status_user_exists_admin(self):
        test_user_id = 666
        self.assertTrue(self.db.get_user_admin_status(test_user_id))

    def test_get_admin_status_user_does_not_exists(self):
        test_user_id = 123
        self.assertFalse(self.db.get_user_admin_status(test_user_id))

    def test_set_block_status_user_does_not_exists(self):
        test_user_id = 111
        self.assertFalse(self.db.set_block(test_user_id))

    def test_get_block_status_user_does_not_exists(self):
        test_user_id = 111
        self.assertFalse(self.db.get_user_block_status(test_user_id))

    def test_get_block_status_user_exists_blocked(self):
        test_user_id = 555
        self.assertTrue(self.db.get_user_block_status(test_user_id))

    def test_get_block_status_user_exists_not_blocked(self):
        test_user_id = 666
        self.assertFalse(self.db.get_user_block_status(test_user_id))

    def test_get_block_status_user_does_not_exists(self):
        test_user_id = 111
        self.assertFalse(self.db.get_user_block_status(test_user_id))

    def test_remove_block_user_does_not_exists(self):
        test_user_id = 111
        self.assertFalse(self.db.remove_block(test_user_id))

    def test_remove_block_user_exists_not_blocked(self):
        test_user_id = 666
        self.assertFalse(self.db.remove_block(test_user_id))

class UserBalanceTest(unittest.TestCase):
    def setUp(self):
        self.db = User()

    def test_get_balance_user_does_not_exists(self):
        test_user_id = 111
        self.assertFalse(self.db.get_user_balance(test_user_id))
    
    def test_get_user_balance_user_exists(self):
        test_user_id = 555
        self.assertTrue(self.db.get_user_balance(test_user_id)>=0)

    def test_change_balance_user_does_not_exists(self):
        test_user_id = 111
        self.assertFalse(self.db.change_user_balance(test_user_id, 100))

    def test_change_balance_user_exists(self):
        test_user_id = 555
        summ = 50
        self.db.change_user_balance(test_user_id, summ)
        new_balance = self.db.get_user_balance(test_user_id)
        self.assertEqual(new_balance, summ)

class UsersListTest(unittest.TestCase):
    def setUp(self):
        self.db = User()

    def test_user_list_correct(self):
        self.db.cursor.execute("""SELECT user_id FROM users""")
        quantity_of_users = self.db.cursor.fetchall()
        queryset = self.db.get_all_users()
        self.assertEqual(len(queryset), len(quantity_of_users))
        
