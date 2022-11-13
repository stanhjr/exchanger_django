from django.shortcuts import render

from exchanger.redis_api import redis_cache


def best_change_xml(request):
    from exchanger.models import ExchangeRates
    redis_cache.cache_exchange_rates()
    exchange_rates = ExchangeRates.objects.all()
    return render(request, 'bestchange.xml', {'exchange_rates': exchange_rates}, content_type='text/xml')

