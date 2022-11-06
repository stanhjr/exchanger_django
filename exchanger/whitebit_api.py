import base64
import hashlib
import hmac
import json
import time
from decimal import Decimal

import requests
from django.conf import settings

from exchanger.exchange_exceptions import ExchangeAmountMinMaxError
from exchanger.models import Transactions


class WhiteBitApi:
    def __init__(self):
        # self.api_key = settings.WHITEBIT_API_KEY
        self.api_key = '88ba423355f18bf67fb7dea3f746bf2a'
        # self.secret_key = settings.WHITEBIT_SECRET_KEY
        self.secret_key = '44d2c4c196e1fa0518cc58da27daea03'
        self.base_url = 'https://whitebit.com'

    @property
    def __nonce(self):
        return time.time_ns() // 1_000_000

    def __get_headers(self, data_json: json) -> dict:
        payload = base64.b64encode(data_json.encode('ascii'))
        signature = hmac.new(self.secret_key.encode('ascii'), payload, hashlib.sha512).hexdigest()
        return {
            'Content-type': 'application/json',
            'X-TXC-APIKEY': self.api_key,
            'X-TXC-PAYLOAD': payload,
            'X-TXC-SIGNATURE': signature,
        }

    @staticmethod
    def __get_data_json(data: dict) -> json:
        return json.dumps(data, separators=(',', ':'))

    def __get_response_dict(self, data: dict, complete_url: str) -> dict:
        data_json = self.__get_data_json(data)
        headers = self.__get_headers(data_json)
        response = requests.post(complete_url, headers=headers, data=data_json)
        return response.json()

    def __transfer_to_trade_balance(self, currency: str, amount_price: str):
        request_url = '/api/v4/main-account/fiat-deposit-url'
        data = {
            "ticker": currency,
            "amount": amount_price,
            "from": "main",
            "to": "spot",
            "request": request_url,
            "nonce": self.__nonce
        }
        result = self.__get_response_dict(data=data, complete_url=self.base_url + request_url)

    def __transfer_to_main_balance(self, currency: str, amount_price: str):
        request_url = '/api/v4/main-account/fiat-deposit-url'
        data = {
            "ticker": currency,
            "amount": amount_price,
            "from": "spot",
            "to": "main",
            "request": request_url,
            "nonce": self.__nonce
        }
        result = self.__get_response_dict(data=data, complete_url=self.base_url + request_url)

    def create_stock_market(self, amount_price: str, market: str, client_order_id: str):
        request_url = '/api/v4/order/stock_market'
        data = {
            "market": market,
            "side": "buy",
            "clientOrderId": client_order_id,
            "amount": amount_price,
            "request": request_url,
            "nonce": self.__nonce,
        }
        result = self.__get_response_dict(data=data, complete_url=self.base_url + request_url)

    def get_info(self):
        request_url = '/api/v4/public/fee'
        response = requests.get(url=self.base_url + request_url)
        return response.json()

    def create_withdraw_crypto(self, amount_price: Decimal, currency: str, address: str, unique_id: str, network: str):

        request_url = '/api/v4/main-account/withdraw'
        data = {
            "ticker": currency,
            "amount": str(amount_price),
            "address": address,
            "uniqueId": unique_id,
            "request": request_url,
            "nonce": self.__nonce
        }
        if network:
            data.update(network=network)

        data_json = self.__get_data_json(data)
        headers = self.__get_headers(data_json)
        response = requests.post(self.base_url + request_url, headers=headers, data=data_json)
        if response.status_code == 201:
            return True

    def get_deposit_address(self, currency_ticker: str, amount_price: Decimal, network: str = None) -> str:
        """
        Takes currency_ticker (USDT, BTC, ETH), amount_price and returned deposit address
        if amount_price is valid
        :param network:
        :param currency_ticker:
        :param amount_price:
        :return: deposit address
        """
        if not self.__check_to_deposit(white_bit_currency_name=currency_ticker, amount_price=amount_price):
            raise ExchangeAmountMinMaxError
        request_url = '/api/v4/main-account/create-new-address'

        data = {
            "ticker": currency_ticker,
            "request": request_url,
            "network": network,
            "nonce": self.__nonce
        }
        result = self.__get_response_dict(data=data, complete_url=self.base_url + request_url)
        return result.get("account")["address"]

    def get_fiat_form(self, transaction_unique_id: str, amount_price: str):
        request_url = '/api/v4/main-account/fiat-deposit-url'
        data = {
            "ticker": "UAH",
            "provider": "VISAMASTER",
            "amount": amount_price,
            "uniqueId": transaction_unique_id,
            "request": request_url,
            "nonce": self.__nonce
        }
        result = self.__get_response_dict(data=data, complete_url=self.base_url + request_url)
        return result.get("url")

    def get_commission_to_deposit(self, white_bit_currency_name: str, amount_price: Decimal):
        info_for_crypto = self.get_info_for_crypto(white_bit_currency_name)
        min_amount = float(info_for_crypto['deposit']['min_amount'])
        max_amount = float(info_for_crypto['deposit']['max_amount'])
        if float(amount_price) < min_amount:
            return
        if float(amount_price) > max_amount and max_amount:
            return
        if not info_for_crypto['deposit']['fixed']:
            return 0
        return Decimal(info_for_crypto['deposit']['fixed'])

    def __check_to_deposit(self, white_bit_currency_name: str, amount_price: Decimal):
        info_for_crypto = self.get_info_for_crypto(white_bit_currency_name)
        min_amount = float(info_for_crypto['deposit']['min_amount'])
        max_amount = float(info_for_crypto['deposit']['max_amount'])
        if float(amount_price) < min_amount:
            return
        if float(amount_price) > max_amount and max_amount:
            return
        return True

    def get_commission_to_withdraw(self, white_bit_currency_name: str, amount_price: Decimal):
        info_for_crypto = self.get_info_for_crypto(white_bit_currency_name)
        min_amount = float(info_for_crypto['withdraw']['min_amount'])
        max_amount = float(info_for_crypto['withdraw']['max_amount'])
        if float(amount_price) < min_amount:
            return
        if float(amount_price) > max_amount and max_amount:
            return
        if not info_for_crypto['withdraw']['fixed']:
            return 0
        return Decimal(info_for_crypto['withdraw']['fixed'])

    def get_info_for_crypto(self, white_bit_currency_name: str) -> dict:
        """
        Takes white_bit_currency_name    BTC, USDT (TRC20), ETH (ERC20)
        returned info for currency
        :param white_bit_currency_name:
        :return:
        """
        request_url = '/api/v4/public/fee'
        response = requests.get(url=self.base_url + request_url)
        result_dict = response.json()
        return result_dict.get(white_bit_currency_name)

    def start_exchange_fiat_to_crypto(self, transaction_obj: Transactions):
        # TODO WEBHOOK, VALIDATION and etc
        # payment expected
        transaction_obj.status_update()
        client_order_id = f'order_{transaction_obj.unique_id}'
        currency_name = transaction_obj.currency_received.name_from_white_bit
        amount_received = transaction_obj.amount_received
        amount_exchange = str(transaction_obj.amount_exchange)

        # start exchange
        transaction_obj.status_update()
        self.__transfer_to_trade_balance(currency='UAH',
                                         amount_price=amount_exchange)
        self.create_stock_market(amount_price=amount_received,
                                 market=transaction_obj.market,
                                 client_order_id=client_order_id)
        self.__transfer_to_main_balance(currency=transaction_obj.currency_received.name_from_white_bit,
                                        amount_price=transaction_obj.amount_received)

        transaction_obj.status_update()
        withdraw_crypto = self.create_withdraw_crypto(amount_price=amount_received,
                                                      currency=currency_name,
                                                      unique_id=transaction_obj.pk,
                                                      address=transaction_obj.address,
                                                      network=transaction_obj.currency_received.network)
        if withdraw_crypto:
            transaction_obj.status_update()


white_bit = WhiteBitApi()
result = white_bit.get_info_for_crypto('BTC')
print(white_bit.get_commission_to_withdraw('ETH (ERC20)', 0.1))
