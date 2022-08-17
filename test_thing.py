from log_settings import LoggingSettings
from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime
import main_settings
from user import User

user = User()
user.create_user(888, 'test8')
logging = LoggingSettings()
p2p = QiwiP2P(auth_key=main_settings.QIWI_PRIV_KEY)



def create_test(user_id):
    p2p.bill(bill_id=user_id+1, amount=2, lifetime=5)
    print('bill created')
    


def test(user_id):
    if user.get_user_block_status(user_id):
        logging.logger_warn.warning(f'Заблокированный пользователь {user_id} пытался подключиться к боту!')
        return print('Вы были заблокированы')
        
    else:
        if p2p.check(bill_id=user_id+1).status != 'PAID':
            logging.logger_warn.warning(f'Пользователь {user_id} пытался пополнить баланс с неоплаченным счетом!')
            return print('Оплата не прошла!')
            
        else:
            current_balance = user.get_user_balance(user_id)
            new_balance = current_balance + float(p2p.check(bill_id=user_id+1).amount)
            logging.logger_info.info(f'Производится зачисление средств на баланс пользователя {user_id}')
            user.change_user_balance(user_id, new_balance)
            print('Деньги зачислены')
            logging.logger_info.info(f'Деньги зачислены. Баланс пользователя {new_balance}')




