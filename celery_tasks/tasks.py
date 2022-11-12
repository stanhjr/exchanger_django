import binascii
import os
import smtplib
import ssl
from decimal import Decimal

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from jinja2 import Template
from celery import Celery, Task

from .config import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exchanger_django.settings")
app = Celery(
    "celery_tasks",
    broker="redis://localhost:6379",
)

app.config_from_object(config)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    max_retries = 5
    default_retry_delay = 3
    retry_backoff = False
    retry_backoff_max = 700
    retry_jitter = False


def generate_key() -> str:
    """
    Generated and returned random code

    :return: str: key
    """
    return binascii.hexlify(os.urandom(20)).decode()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(120.0, fixer_failed_withdraw.s(), name='fixer_failed_withdraw')
    sender.add_periodic_task(120.0, fixer_failed_trade.s(), name='fixer_failed_trade')


@app.task
def send_registration_link_to_email(code: str, email_to: str, subject: str):
    text = f"""\
    Hi,
    How are you?
    This is your registration link:
    {settings.HOST}/account/account-activate/?code=4641cb74c97b79fa0f7ed9158a6f0e69b7f8d3b3"""

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_HOST_USER
    message["To"] = email_to
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, 465, context=context) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(
                settings.EMAIL_HOST_USER, email_to, message.as_string()
            )

        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)


@app.task
def send_verify_code_to_email(code: str, email_to: str, subject: str):
    text = f"""\
    Hi,
    How are you?
    This is your verify code:
    {code}
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_HOST_USER
    message["To"] = email_to
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, 465, context=context) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(
                settings.EMAIL_HOST_USER, email_to, message.as_string()
            )

        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)


@app.task
def send_reset_password_code_to_email(code: str, email_to: str, subject: str):
    text = f"""\
    Hi,
    How are you?
    This is your reset password code:
    {code}
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_HOST_USER
    message["To"] = email_to
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, 465, context=context) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(
                settings.EMAIL_HOST_USER, email_to, message.as_string()
            )

        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)


@app.task
def send_reset_password_link_to_email(code: str, email_to: str, subject: str):
    text = f"""\
    Hi,
    How are you?
    This is your restore password link:
    {settings.HOST}/account/reset-password/?code={code}"""

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_HOST_USER
    message["To"] = email_to

    part1 = MIMEText(text, "plain")

    message.attach(part1)

    try:

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, 465, context=context) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(
                settings.EMAIL_HOST_USER, email_to, message.as_string()
            )

        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)


@app.task
def send_transaction_satus(transaction_id: str, email_to: str, transaction_status: str):
    text = f"""\
    Hi,
    How are you?
    transaction {transaction_id} status  changed to {transaction_status}
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = 'Transaction status changed'
    message["From"] = settings.EMAIL_HOST_USER
    message["To"] = email_to
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, 465, context=context) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(
                settings.EMAIL_HOST_USER, email_to, message.as_string()
            )

        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)


# def transaction_to_withdraw(transaction, white_bit_api):
#     from exchanger.exchange_exceptions import ExchangeTradeError
#     try:
#         withdraw_crypto = white_bit_api.create_withdraw(
#             unique_id=str(transaction.unique_id),
#             network=transaction.currency_received.network,
#             provider=transaction.currency_received.provider,
#             currency=transaction.currency_received.name_from_white_bit,
#             address=transaction.address,
#             amount_price=str(transaction.amount_real_received),
#         )
#         if not withdraw_crypto:
#             transaction.try_fixed_count_error += 1
#             transaction.save(failed_error=transaction.failed_error)
#             return 'Retry withdraw'
#         # status to create_for_payment
#         transaction.failed = False
#         transaction.failed_error = None
#         transaction.try_fixed_count_error = 0
#         transaction.status_update()
#         return 'Fixed failed withdraw'
#     except ExchangeTradeError as e:
#         print(e)
#         transaction.try_fixed_count_error += 1
#         transaction.failed_error = str(e)
#         transaction.save(failed_error=True)
#         return 'Retry trade'
#
#
# @app.task
# def fixer_failed_trade():
#     from exchanger.models import Transactions
#     from exchanger.whitebit_api import WhiteBitApi
#     from exchanger.exchange_exceptions import ExchangeTradeError
#     from django.utils import timezone
#     from datetime import timedelta
#
#     transactions = Transactions.objects.filter(failed=True,
#                                                status='payment_received',
#                                                try_fixed_count_error__lte=4,
#                                                status_time_update__lte=timezone.now() - timedelta(seconds=60)).all()
#     if not transactions:
#         return
#     white_bit_api = WhiteBitApi()
#     for transaction in transactions:
#         try:
#             to_crypto = None
#             if not transaction.crypto_to_fiat:
#                 to_crypto = True
#             white_bit_api.start_trading(
#                 transaction_pk=transaction.pk,
#                 name_from_white_bit_exchange=transaction.currency_exchange.name_from_white_bit,
#                 name_from_white_bit_received=transaction.currency_received.name_from_white_bit,
#                 market=transaction.market,
#                 amount_exchange=str(transaction.amount_real_exchange),
#                 amount_received=str(transaction.amount_received),
#                 to_crypto=to_crypto,
#             )
#             # status to currency_changing
#             transaction.failed = False
#             transaction.failed_error = None
#             transaction.try_fixed_count_error = 0
#             transaction.status_update()
#             transaction_to_withdraw(transaction=transaction,
#                                     white_bit_api=white_bit_api)
#             return 'Fixed trade'
#         except ExchangeTradeError as e:
#             print(e)
#             transaction.try_fixed_count_error += 1
#             transaction.failed_error = str(e)
#             transaction.save(failed_error=True)
#             return 'Retry trade'


# @app.task
# def fixer_failed_withdraw():
#     from exchanger.models import Transactions
#     from exchanger.whitebit_api import WhiteBitApi
#     from exchanger.exchange_exceptions import ExchangeTradeError
#     from django.utils import timezone
#     from datetime import timedelta
#
#     transactions = Transactions.objects.filter(failed=True,
#                                                status='currency_changing',
#                                                try_fixed_count_error__lte=4,
#                                                status_time_update__lte=timezone.now() - timedelta(seconds=60)).all()
#     if not transactions:
#         return
#     white_bit_api = WhiteBitApi()
#     for transaction in transactions:
#         try:
#             withdraw_crypto = white_bit_api.create_withdraw(
#                 unique_id=str(transaction.unique_id),
#                 network=transaction.currency_received.network,
#                 provider=transaction.currency_received.provider,
#                 currency=transaction.currency_received.name_from_white_bit,
#                 address=transaction.address,
#                 amount_price=str(transaction.amount_received + transaction.currency_exchange.commission_withdraw),
#
#             )
#             if not withdraw_crypto:
#                 transaction.try_fixed_count_error += 1
#                 transaction.save(failed_error=transaction.failed_error)
#                 return 'Retry withdraw'
#             # status to create_for_payment
#             transaction.failed = False
#             transaction.failed_error = None
#             transaction.try_fixed_count_error = 0
#             transaction.status_update()
#             return 'Fixed failed withdraw'
#         except ExchangeTradeError as e:
#             print(e)
#             transaction.try_fixed_count_error += 1
#             transaction.failed_error = str(e)
#             transaction.save(failed_error=True)
#             return 'Retry trade'


# =============================================== TASK EXCHANGE =================================

@app.task(bind=BaseTaskWithRetry)
def create_withdraw(transaction_pk):
    print('create_withdraw START')
    from exchanger.whitebit_api import WhiteBitApi
    from exchanger.exchange_exceptions import ExchangeTradeError
    from exchanger.models import Transactions

    transaction = Transactions.objects.filter(pk=transaction_pk, get_deposit=True, is_confirm=False).first()
    white_bit_api = WhiteBitApi()
    withdraw_crypto = white_bit_api.create_withdraw(
        unique_id=str(transaction.unique_id),
        network=transaction.currency_received.network,
        provider=transaction.currency_received.provider,
        currency=transaction.currency_received.name_from_white_bit,
        address=transaction.address,
        amount_price=str(transaction.amount_real_received),
    )
    if not withdraw_crypto:
        transaction.failed = True
        transaction.save(failed_error='not create_withdraw')
        raise ExchangeTradeError
    transaction.status_exchange = 'create_withdraw'
    transaction.status_update()
    return f'create withdraw {transaction.unique_id}'


@app.task(bind=BaseTaskWithRetry)
def transfer_to_main_balance(transaction_pk: str):
    print('transfer_to_main_balance START')
    from datetime import timedelta
    from django.utils.timezone import now

    from exchanger.whitebit_api import WhiteBitApi
    from exchanger.exchange_exceptions import ExchangeTradeError
    from exchanger.models import Transactions

    transaction = Transactions.objects.filter(pk=transaction_pk, get_deposit=True, is_confirm=False).first()
    if not transaction:
        return 'not transaction'

    white_bit_api = WhiteBitApi()

    status_code = white_bit_api.transfer_to_main_balance(currency=transaction.name_from_white_bit_received,
                                                         amount_received=transaction.amount_real_received)
    if status_code > 210:
        print('transfer_to_main_balance', status_code)
        transaction.failed = True
        transaction.failed_error = 'ERROR transfer_to_main_balance failed'
        raise ExchangeTradeError('ERROR transfer_to_main_balance failed')
    transaction.status_exchange = 'transfer_to_main'
    transaction.save()
    create_withdraw.apply_async(eta=now() + timedelta(seconds=5), kwargs={"transaction_pk": transaction_pk})
    return f'transfer_to_main_balance {transaction.amount_real_receive} {transaction.name_from_white_bit_received} complete'


@app.task(bind=BaseTaskWithRetry)
def start_exchange(transaction_pk: str, to_crypto=None):
    print('start_exchange START')
    from datetime import timedelta
    from django.utils.timezone import now

    from exchanger.whitebit_api import WhiteBitApi
    from exchanger.exchange_exceptions import ExchangeTradeError
    from exchanger.models import Transactions

    transaction = Transactions.objects.filter(pk=transaction_pk, get_deposit=True, is_confirm=False).first()
    if not transaction:
        return 'not transaction'

    white_bit_api = WhiteBitApi()
    client_order_id = f'order-client-{transaction_pk}'
    if to_crypto:
        status_code = white_bit_api.exchange_fiat_to_crypto(
            market=transaction.market,
            client_order_id=client_order_id,
            amount_received=transaction.amount_real_received,
        )
    else:
        status_code = white_bit_api.exchange_crypto_to_fiat(
            market=transaction.market,
            client_order_id=client_order_id,
            amount_exchange=transaction.amount_real_exchange
        )
    if status_code > 210:
        print('exchange_fiat_to_crypto ERROR', status_code)
        raise ExchangeTradeError('ERROR exchange API')

    transaction.status_exchange = 'exchange'
    transaction.status_update()
    transfer_to_main_balance.apply_async(eta=now() + timedelta(seconds=5), kwargs={"transaction_pk": transaction_pk})
    return f'exchange complete {transaction.unique_id} market {transaction.market} '


@app.task(bind=BaseTaskWithRetry)
def start_trading(transaction_pk: str, to_crypto=None):
    print('start_trading START')
    from datetime import timedelta
    from django.utils.timezone import now

    from exchanger.whitebit_api import WhiteBitApi
    from exchanger.exchange_exceptions import ExchangeTradeError
    from exchanger.models import Transactions

    transaction = Transactions.objects.filter(pk=transaction_pk, get_deposit=True, is_confirm=False).first()
    if not transaction:
        return 'not transaction'

    amount_exchange = str(Decimal(transaction.amount_real_exchange).quantize(Decimal("1.00000000")))
    white_bit_api = WhiteBitApi()

    status_code = white_bit_api.transfer_to_trade_balance(currency=transaction.name_from_white_bit_exchange,
                                                          amount_exchange=amount_exchange)
    if status_code > 210:
        print('transfer_to_trade_balance ERROR', status_code)
        transaction.failed = True
        transaction.failed_error = 'ERROR transfer_to_trade_balance failed'
        transaction.save()
        raise ExchangeTradeError('ERROR transfer_to_trade_balance failed')

    start_exchange.apply_async(eta=now() + timedelta(seconds=5), kwargs={"transaction_pk": transaction_pk,
                                                                         "to_crypto": to_crypto})
    transaction.status_exchange = 'transfer_to_trade'
    transaction.save()
    return f'transfer to trade balance {amount_exchange} {transaction.name_from_white_bit_exchange} complete'
