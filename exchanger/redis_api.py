import time
from decimal import Decimal

import redis


class RedisCache:
    def __init__(self):
        self.session = redis.StrictRedis(host='localhost', port=6379, db=5)

    @property
    def commission_to_fiat(self) -> Decimal:
        commission = self.session.get("commission_to_fiat")
        if not commission:
            from exchanger.models import Commissions
            commission = Commissions.objects.first()
            commission.set_commission()
            return Decimal(commission.to_fiat_commission_percent)
        return Decimal(commission)

    @property
    def commission_to_crypto(self):
        commission = self.session.get("commission_to_crypto")
        if not commission:
            from exchanger.models import Commissions
            commission = Commissions.objects.first()
            commission.set_commission()
            return Decimal(commission.to_crypto_commission_percent)
        return Decimal(commission)

    @property
    def white_bit_commission(self):
        commission = self.session.get("white_bit_commission")
        if not commission:
            from exchanger.models import Commissions
            commission = Commissions.objects.first()
            commission.set_commission()
            return Decimal(commission.white_bit_commission_percent)
        return Decimal(commission)

    def set_commission(self, dict_percent_commission: dict):
        for key, value in dict_percent_commission.items():
            self.session.set(key, value)
        return True

    def set_datetime_exchange_rates_save(self):
        time_now = int(time.time())
        self.session.set("exchange_rates_time_update", time_now)

    def cache_exchange_rates(self) -> bool:
        time_update = self.session.get("exchange_rates_time_update")
        if not time_update or int(time_update) + 10 > int(time.time()):
            from exchanger.models import Currency
            from exchanger.models import ExchangeRates
            from exchanger.whitebit_api import WhiteBitInfo
            white_bit = WhiteBitInfo()
            Currency.update_min_max_value(assets_dict=white_bit.get_assets_dict())
            Currency.update_commission(white_bit.get_info())
            ExchangeRates.update_rates(tickers_list=white_bit.get_tickers_list())
            self.set_datetime_exchange_rates_save()
            return True
        return True


redis_cache = RedisCache()
