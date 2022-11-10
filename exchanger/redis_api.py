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


redis_cache = RedisCache()
