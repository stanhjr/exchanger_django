from django.shortcuts import render


def best_change_xml(request):
    from exchanger.models import ExchangeRates
    exchange_rates = ExchangeRates.objects.all()
    return render(request, 'bestchange.xml', {'exchange_rates': exchange_rates}, content_type='text/xml')

