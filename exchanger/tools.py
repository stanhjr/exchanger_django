from decimal import Decimal

from django.core.exceptions import ValidationError


def value_to_dollars(amount_exchange: Decimal, currency_white_bit_name: str) -> Decimal:
    from exchanger.redis_api import redis_cache
    from exchanger.models import Currency, ExchangeRates

    redis_cache.cache_exchange_rates()

    currency_usdt = Currency.objects.filter(name_from_white_bit='USDT').first()
    currency_uah = Currency.objects.filter(name_from_white_bit='UAH').first()
    currency_to_exchange = Currency.objects.filter(name_from_white_bit=currency_white_bit_name).first()
    if currency_to_exchange == currency_usdt:
        return amount_exchange
    if not currency_usdt or not currency_uah or not currency_to_exchange:
        raise ValidationError

    if currency_to_exchange.fiat:
        exchange_pair = ExchangeRates.objects.filter(currency_left=currency_to_exchange,
                                                     currency_right=currency_usdt).first()

        return exchange_pair.get_trade(amount_exchange)
    else:
        exchange_pair = ExchangeRates.objects.filter(currency_left=currency_to_exchange,
                                                     currency_right=currency_uah).first()
        uah = exchange_pair.get_trade(amount_exchange)
        exchange_pair = ExchangeRates.objects.filter(currency_left=currency_uah,
                                                     currency_right=currency_usdt).first()
        return exchange_pair.get_trade(uah)


def get_zero_or_none(info):
    if info is None:
        return 0
    return info
