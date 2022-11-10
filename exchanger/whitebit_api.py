import base64
import hashlib
import hmac
import json
import time
from decimal import Decimal

import requests
from django.conf import settings

from exchanger.exchange_exceptions import ExchangeAmountMinMaxError
from exchanger.exchange_exceptions import ExchangeTradeError


class WhiteBitAbstract:
    def __init__(self):
        self.api_key = settings.WHITEBIT_API_KEY
        self.secret_key = settings.WHITEBIT_SECRET_KEY
        self.base_url = 'https://whitebit.com'

    def get_info_for_crypto(self, white_bit_currency_name: str, network: str) -> dict:
        """
        Takes white_bit_currency_name and network    BTC, USDT (TRC20), ETH (ERC20)
        returned info for currency
        :param network:
        :param white_bit_currency_name:
        :return:
        """
        request_url = '/api/v4/public/fee'
        response = requests.get(url=self.base_url + request_url)
        result_dict = response.json()
        currency_name = f"{white_bit_currency_name} ({network})" if network else white_bit_currency_name
        return result_dict.get(currency_name)


class WhiteBitInfo(WhiteBitAbstract):

    def get_info(self):
        request_url = '/api/v4/public/fee'
        response = requests.get(url=self.base_url + request_url)
        return response.json()

    def get_tickers_list(self) -> list:
        request_url = '/api/v2/public/ticker'
        response = requests.get(url=self.base_url + request_url)
        result = response.json()
        return result.get('result')

    def get_assets_dict(self) -> dict:
        request_url = '/api/v4/public/assets'
        response = requests.get(url=self.base_url + request_url)
        return response.json()


class WhiteBitApi(WhiteBitAbstract):

    @property
    def _nonce(self):
        return time.time_ns() // 1_000_000

    def _get_headers(self, data_json: json) -> dict:
        payload = base64.b64encode(data_json.encode('ascii'))
        signature = hmac.new(self.secret_key.encode('ascii'), payload, hashlib.sha512).hexdigest()
        return {
            'Content-type': 'application/json',
            'X-TXC-APIKEY': self.api_key,
            'X-TXC-PAYLOAD': payload,
            'X-TXC-SIGNATURE': signature,
        }

    @staticmethod
    def _get_data_json(data: dict) -> json:
        return json.dumps(data, separators=(',', ':'))

    def _get_response_dict(self, data: dict, complete_url: str) -> dict:
        data_json = self._get_data_json(data)
        headers = self._get_headers(data_json)
        response = requests.post(complete_url, headers=headers, data=data_json)
        return response.json()

    def _get_response_status_code(self, data: dict, complete_url: str) -> int:
        data_json = self._get_data_json(data)
        headers = self._get_headers(data_json)
        response = requests.post(complete_url, headers=headers, data=data_json)
        return response.status_code

    def _transfer_to_trade_balance(self, currency: str, amount_price: str):
        request_url = '/api/v4/main-account/fiat-deposit-url'
        data = {
            "ticker": currency,
            "amount": amount_price,
            "from": "main",
            "to": "spot",
            "request": request_url,
            "nonce": self._nonce
        }
        return self._get_response_status_code(data=data, complete_url=self.base_url + request_url)

    def _transfer_to_main_balance(self, currency: str, amount_price: str) -> int:
        request_url = '/api/v4/main-account/fiat-deposit-url'
        data = {
            "ticker": currency,
            "amount": amount_price,
            "from": "spot",
            "to": "main",
            "request": request_url,
            "nonce": self._nonce
        }
        return self._get_response_status_code(data=data, complete_url=self.base_url + request_url)

    def create_stock_market(self, amount_price: str, market: str, client_order_id: str) -> int:
        request_url = '/api/v4/order/stock_market'
        data = {
            "market": market,
            "side": "buy",
            "clientOrderId": client_order_id,
            "amount": amount_price,
            "request": request_url,
            "nonce": self._nonce,
        }
        return self._get_response_status_code(data=data, complete_url=self.base_url + request_url)

    def create_withdraw(self, amount_price: str, currency: str, address: str, unique_id: str,
                        network: str = None, provider: bool = False):

        request_url = '/api/v4/main-account/withdraw'
        data = {
            "ticker": currency,
            "amount": amount_price,
            "address": address,
            "uniqueId": unique_id,
            "request": request_url,
            "nonce": self._nonce
        }
        if network:
            data.update(network=network)
        if provider:
            data.pop("network")
            data.update(provider=network)

        data_json = self._get_data_json(data)
        headers = self._get_headers(data_json)
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
        if not self._check_to_deposit(white_bit_currency_name=currency_ticker,
                                      amount_price=amount_price,
                                      network=network):
            raise ExchangeAmountMinMaxError
        request_url = '/api/v4/main-account/create-new-address'

        data = {
            "ticker": currency_ticker,
            "request": request_url,
            "nonce": self._nonce
        }
        if network:
            data.update(network=network)
        result = self._get_response_dict(data=data, complete_url=self.base_url + request_url)
        return result.get("account")["address"]

    def get_fiat_form(self, transaction_unique_id: str, amount_price: str):
        """
        Takes transaction unique and amount_price, returner link for payment

        :param transaction_unique_id:
        :param amount_price:
        :return:
        """
        request_url = '/api/v4/main-account/fiat-deposit-url'
        data = {
            "ticker": "UAH",
            "provider": "VISAMASTER",
            "amount": amount_price,
            "uniqueId": str(transaction_unique_id),
            "request": request_url,
            "nonce": self._nonce
        }
        result = self._get_response_dict(data=data, complete_url=self.base_url + request_url)
        return result.get("url")

    def _check_to_deposit(self, white_bit_currency_name: str, amount_price: Decimal, network: str):
        info_for_crypto = self.get_info_for_crypto(white_bit_currency_name, network=network)
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

    def start_trading(self, unique_id: str, name_from_white_bit_exchange: str, name_from_white_bit_received: str,
                      market: str, amount_received: str, amount_exchange: str):
        """
        Takes params and exchange from WhiteBit, returned True If the exchange was successful
        raise ExchangeTradeError If the exchange was not successful

        :param unique_id:
        :param name_from_white_bit_exchange:
        :param name_from_white_bit_received:
        :param market:
        :param amount_received:
        :param amount_exchange:
        :return: True
        """

        client_order_id = f'order_{unique_id}'
        amount_exchange = str(Decimal(amount_exchange).quantize(Decimal("1.00000000")))
        amount_received = str(Decimal(amount_received).quantize(Decimal("1.00000000")))
        # start exchange
        status_code = self._transfer_to_trade_balance(currency=name_from_white_bit_exchange,
                                                      amount_price=amount_exchange)
        if status_code > 210:
            raise ExchangeTradeError('transfer_to_trade_balance failed')

        time.sleep(1)
        status_code = self.create_stock_market(amount_price=amount_received,
                                               market=market,
                                               client_order_id=client_order_id)
        if status_code > 210:
            raise ExchangeTradeError('create_stock_market')

        time.sleep(1)
        status_code = self._transfer_to_main_balance(currency=name_from_white_bit_received,
                                                     amount_price=amount_received)

        time.sleep(1)
        if status_code > 210:
            raise ExchangeTradeError('transfer_to_main_balance failed')

        return True
