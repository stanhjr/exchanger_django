import binascii
import os
import smtplib
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from jinja2 import Template
from celery import Celery

from .config import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exchanger_django.settings")
app = Celery(
    "celery_tasks",
    broker="redis://localhost:6379",
)

app.config_from_object(config)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


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


def transaction_to_withdraw(transaction, white_bit_api):
    from exchanger.exchange_exceptions import ExchangeTradeError
    try:
        provider = None
        if transaction.crypto_to_fiat:
            provider = True
        withdraw_crypto = white_bit_api.create_withdraw(
            # unique_id=str(transaction.unique_id),
            unique_id=str(transaction.fiat_unique_id),
            network=transaction.currency_received.network,
            currency=transaction.currency_received.name_from_white_bit,
            address=transaction.address,
            amount_price=str(transaction.amount_received + transaction.currency_exchange.commission_withdraw),
            provider=provider,

        )
        if not withdraw_crypto:
            transaction.try_fixed_count_error += 1
            transaction.save(failed_error=transaction.failed_error)
            return 'Retry withdraw'
        # status to create_for_payment
        transaction.failed = False
        transaction.failed_error = None
        transaction.try_fixed_count_error = 0
        transaction.status_update()
        return 'Fixed failed withdraw'
    except ExchangeTradeError as e:
        print(e)
        transaction.try_fixed_count_error += 1
        transaction.failed_error = str(e)
        transaction.save(failed_error=True)
        return 'Retry trade'


@app.task
def fixer_failed_trade():
    from exchanger.models import Transactions
    from exchanger.whitebit_api import WhiteBitApi
    from exchanger.exchange_exceptions import ExchangeTradeError
    from django.utils import timezone
    from datetime import timedelta

    transactions = Transactions.objects.filter(failed=True,
                                               status='payment_received',
                                               try_fixed_count_error__lte=4,
                                               status_time_update__lte=timezone.now() - timedelta(seconds=60)).all()
    if not transactions:
        return
    white_bit_api = WhiteBitApi()
    for transaction in transactions:
        try:
            to_crypto = None
            if not transaction.crypto_to_fiat:
                to_crypto = True
            white_bit_api.start_trading(
                transaction_pk=transaction.pk,
                name_from_white_bit_exchange=transaction.currency_exchange.name_from_white_bit,
                name_from_white_bit_received=transaction.currency_received.name_from_white_bit,
                market=transaction.market,
                amount_exchange=str(transaction.amount_real_exchange),
                amount_received=str(transaction.amount_received),
                to_crypto=to_crypto,
            )
            # status to currency_changing
            transaction.failed = False
            transaction.failed_error = None
            transaction.try_fixed_count_error = 0
            transaction.status_update()
            return 'Fixed trade'
        except ExchangeTradeError as e:
            print(e)
            transaction.try_fixed_count_error += 1
            transaction.failed_error = str(e)
            transaction.save(failed_error=True)
            transaction_to_withdraw(transaction=transaction,
                                    white_bit_api=white_bit_api)
            return 'Retry trade'


@app.task
def fixer_failed_withdraw():
    from exchanger.models import Transactions
    from exchanger.whitebit_api import WhiteBitApi
    from exchanger.exchange_exceptions import ExchangeTradeError
    from django.utils import timezone
    from datetime import timedelta

    transactions = Transactions.objects.filter(failed=True,
                                               status='currency_changing',
                                               try_fixed_count_error__lte=4,
                                               status_time_update__lte=timezone.now() - timedelta(seconds=60)).all()
    if not transactions:
        return
    white_bit_api = WhiteBitApi()
    for transaction in transactions:
        try:
            provider = None
            if transaction.crypto_to_fiat:
                provider = True
            withdraw_crypto = white_bit_api.create_withdraw(
                # unique_id=str(transaction.unique_id),
                unique_id=str(transaction.fiat_unique_id),
                network=transaction.currency_received.network,
                currency=transaction.currency_received.name_from_white_bit,
                address=transaction.address,
                amount_price=str(transaction.amount_received + transaction.currency_exchange.commission_withdraw),
                provider=provider,

            )
            if not withdraw_crypto:
                transaction.try_fixed_count_error += 1
                transaction.save(failed_error=transaction.failed_error)
                return 'Retry withdraw'
            # status to create_for_payment
            transaction.failed = False
            transaction.failed_error = None
            transaction.try_fixed_count_error = 0
            transaction.status_update()
            return 'Fixed failed withdraw'
        except ExchangeTradeError as e:
            print(e)
            transaction.try_fixed_count_error += 1
            transaction.failed_error = str(e)
            transaction.save(failed_error=True)
            return 'Retry trade'