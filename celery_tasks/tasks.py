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
    sender.add_periodic_task(10.0, update_exchange_rates.s(), name='update_exchange_rates')


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


@app.task
def update_exchange_rates():
    from exchanger.models import ExchangeRates, Currency
    from exchanger.whitebit_api import WhiteBitInfo
    white_bit = WhiteBitInfo()
    Currency.update_min_max_value(assets_dict=white_bit.get_assets_dict())
    ExchangeRates.update_rates(tickers_list=white_bit.get_tickers_list())
    return "currency and exchange rates updates"
