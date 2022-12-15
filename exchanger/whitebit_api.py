import base64
import hashlib
import hmac
import json
import time
from decimal import Decimal
import logging

import requests
from django.conf import settings


from exchanger.exchange_exceptions import ExchangeAmountMinMaxError
from exchanger.exchange_exceptions import ExchangeTradeError


logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)


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
        print(response.json())
        return response.status_code

    def transfer_to_trade_balance(self, currency: str, amount_exchange: str):
        request_url = '/api/v4/main-account/transfer'
        data = {
            "ticker": currency,
            "amount": amount_exchange,
            "from": "main",
            "to": "spot",
            "request": request_url,
            "nonce": self._nonce
        }
        return self._get_response_status_code(data=data, complete_url=self.base_url + request_url)

    def transfer_to_main_balance(self, currency: str, amount_received: str) -> int:
        request_url = '/api/v4/main-account/transfer'
        data = {
            "ticker": currency,
            "amount": amount_received,
            "from": "spot",
            "to": "main",
            "request": request_url,
            "nonce": self._nonce
        }
        status_code = self._get_response_status_code(data=data, complete_url=self.base_url + request_url)
        if status_code > 210:
            raise ExchangeTradeError('ERROR transfer_to_main_balance failed')
        return status_code

    def _get_stock_precision(self, market: str) -> int:
        request_url = '/api/v2/public/markets'
        response = requests.get(url=self.base_url + request_url)
        result_dict = response.json()
        result_list = result_dict.get('result')
        for dict_ in result_list:
            if dict_.get('name') == market:
                return int(dict_.get('stockPrec'))
        raise ExchangeTradeError('get_stock_precision ERROR')

    def _get_money_precision(self, market: str) -> int:
        request_url = '/api/v2/public/markets'
        response = requests.get(url=self.base_url + request_url)
        result_dict = response.json()
        result_list = result_dict.get('result')
        for dict_ in result_list:
            if dict_.get('name') == market:
                return int(dict_.get('moneyPrec'))
        raise ExchangeTradeError('_get_money_precision ERROR')

    def get_history_from_currency(self, currency_ticker: str):
        request_url = '/api/v4/main-account/history'
        data = {
            "transactionMethod": "2",
            "ticker": "UAH",
            "offset": 0,
            "limit": 100,
            "status": [1, 2, 6, 10, 11, 12, 13, 14, 15, 16, 17, 3, 7, 4, 5, 18, 9],
            "request": request_url,
            "nonce": self._nonce
        }
        result = self._get_response_dict(data=data, complete_url=self.base_url + request_url)
        print(result)

    def create_withdraw(self, amount_price: str, currency: str, address: str,
                        unique_id: str, provider: str, network: str):

        request_url = '/api/v4/main-account/withdraw'
        data = {
            "ticker": currency,
            "amount": amount_price,
            "address": address,
            "uniqueId": str(unique_id),
            "request": request_url,
            "nonce": self._nonce,
            "nonceWindow": True
        }
        if network:
            data.update(network=network)
        if provider:
            data.update(provider=provider)

        data_json = self._get_data_json(data)
        headers = self._get_headers(data_json)
        response = requests.post(self.base_url + request_url, headers=headers, data=data_json)
        logging.info('-------try create_withdraw ---------')
        logging.info(data)
        logging.info(response.json())
        print(data)
        print(response.json())
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

    def _get_amount_precision(self, amount, market):
        precision = f'1.{"0" * self._get_stock_precision(market=market)}'
        if precision == '1.':
            precision = '1'
        return str(Decimal(amount).quantize(Decimal(precision)))

    def exchange_fiat_to_crypto(self, client_order_id: str, amount_received: str, market: str):
        request_url = '/api/v4/order/stock_market'
        amount_received = self._get_amount_precision(amount=amount_received,
                                                     market=market)
        data = {
            "market": market,
            "side": 'buy',
            "clientOrderId": client_order_id,
            "amount": amount_received,
            "request": request_url,
            "nonce": self._nonce,
        }
        print(data)
        status_code = self._get_response_status_code(data=data, complete_url=self.base_url + request_url)
        print('status code', status_code)
        return status_code

    def exchange_crypto_to_fiat(self, client_order_id: str, amount_exchange: str, market: str):
        request_url = '/api/v4/order/stock_market'
        amount_exchange = self._get_amount_precision(amount=amount_exchange,
                                                     market=market)
        data = {
            "market": market,
            "side": 'sell',
            "clientOrderId": client_order_id,
            "amount": amount_exchange,
            "request": request_url,
            "nonce": self._nonce,
        }
        print(data)
        return self._get_response_status_code(data=data, complete_url=self.base_url + request_url)

    def get_trade_balance(self):
        request_url = '/api/v4/trade-account/balance'
        data = {
            "request": request_url,
            "nonce": self._nonce
        }
        result = self._get_response_dict(data=data, complete_url=self.base_url + request_url)
        print("----trade balance----")
        print(self._nonce)
        for i, v in result.items():
            if i == 'UAH' or i == 'USDT' or i == 'ETH':
                print(i, v)

    def get_main_balance(self):
        request_url = '/api/v4/main-account/balance'
        data = {
            "request": request_url,
            "nonce": self._nonce
        }
        result = self._get_response_dict(data=data, complete_url=self.base_url + request_url)
        print("----main balance----")
        for i, v in result.items():
            if i == 'UAH' or i == 'USDT' or i == 'ETH':
                print(i, v)


if __name__ == '__main__':
    wb = WhiteBitApi()
    wb.get_trade_balance()
    wb.get_main_balance()


# UAH {'available': '54.27085926', 'freeze': '0'}
# USDT {'available': '0.1385', 'freeze': '0'}
# UAH {'main_balance': '27.1093'}
# USDT {'main_balance': '0.9998'}


# UAH {'available': '54.27085926', 'freeze': '0'}
# USDT {'available': '0.1385', 'freeze': '0'}
# UAH {'main_balance': '27.1093'}
# USDT {'main_balance': '10.9998'}


# UAH {'available': '55.88975326', 'freeze': '0'}
# USDT {'available': '0.1385', 'freeze': '0'}
# UAH {'main_balance': '27.1093'}
# USDT {'main_balance': '10.9998'


# ----trade balance----
# ETH {'available': '0.0000001', 'freeze': '0'}
# UAH {'available': '59.06521817', 'freeze': '0'}
# USDT {'available': '0.1353', 'freeze': '0'}
# ----main balance----
# ETH {'main_balance': '0.0102949'}
# UAH {'main_balance': '27.10915738'}
# USDT {'main_balance': '21.343'}