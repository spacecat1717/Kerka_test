from log_settings import LoggingSettings
from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime
import main_settings
from user import User

user = User()
user.create_user(888, 'test8')
logging = LoggingSettings()
p2p = QiwiP2P(auth_key=main_settings.QIWI_PRIV_KEY)

def test_1(user_id):
    user = User()
    is_admin = user.get_user_admin_status(user_id)
    if not is_admin:
        print('Недостаточно прав!')
        logging.logger_warn.warning(f'Пользователь {user_id} пытался зайти в админ-панель!')
    else:
        users_list = user.get_all_users()
        print(users_list)
        for user1 in users_list:
            print(f"ID:{user1['user_id']}\nИмя:{user1['username']}\nБаланс:{user1['balance']}")
        logging.logger_info.info('Выгружен список пользователей')




