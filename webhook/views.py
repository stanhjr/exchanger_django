from decimal import Decimal

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from exchanger.exchange_exceptions import ExchangeTradeError
from exchanger.models import Transactions, ExchangeRates
from exchanger.whitebit_api import WhiteBitApi
from webhook.serializers import WhiteBitSerializer
from celery_tasks.tasks import send_transaction_satus, start_trading


class WhiteBitWebHook(APIView):
    white_bit_api = WhiteBitApi()
    http_method_names = ['post', ]

    def post(self, request):
        if request.headers.get('X-TXC-APIKEY') != settings.WHITEBIT_WEB_HOOK_PUBLIC_KEY:
            print('WHITEBIT_WEB_HOOK_PUBLIC_KEY not valid!')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = WhiteBitSerializer(data=request.data)
        if serializer.is_valid():
            method = serializer.validated_data.get("method")
            params = serializer.validated_data.get("params")
            unique_id = params.get("uniqueId")
            wallet_address = params.get("address")
            if method == 'deposit.processed' and unique_id:
                # FIAT to CRYPTO EXCHANGE
                print(method)
                print(params)
                transaction = Transactions.objects.filter(fiat_unique_id=unique_id).first()
                if not transaction:
                    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
                transaction.address_from = params.get('address')
                transaction.hash = params.get('transactionHash')
                transaction.get_deposit = True
                try:
                    if Decimal(str(transaction.amount_exchange)) != Decimal(params.get('amount')):
                        transaction.amount_exchange = Decimal(params.get('amount'))
                        exchange_pair = ExchangeRates.objects.filter(currency_left=transaction.currency_exchange,
                                                                     currency_right=transaction.currency_received).first()
                        transaction.amount_received = exchange_pair.get_calculate(transaction.amount_exchange)
                except Exception as e:
                    print(e)

                # status to payment_received
                transaction.status_update()
                start_trading.apply_async(kwargs=dict(transaction_pk=str(transaction.pk), to_crypto=True))

                return Response(serializer.data, status=status.HTTP_200_OK)

            if method == 'deposit.processed' and wallet_address:
                # CRYPTO to FIAT EXCHANGE
                print(method)
                print(params)
                print('amount', params.get('amount'))

                transaction = Transactions.objects.filter(deposit_address=wallet_address).first()
                if not transaction:
                    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

                # status to payment_received
                try:
                    if Decimal(str(transaction.amount_exchange)) != Decimal(params.get('amount')):
                        transaction.amount_exchange = Decimal(params.get('amount'))
                        exchange_pair = ExchangeRates.objects.filter(currency_left=transaction.currency_exchange,
                                                                     currency_right=transaction.currency_received).first()
                        transaction.amount_received = exchange_pair.get_calculate(transaction.amount_exchange)
                except Exception as e:
                    print(e)
                transaction.get_deposit = True
                transaction.address_from = params.get('address')
                transaction.hash = params.get('transactionHash')

                transaction.status_update()

                start_trading.apply_async(kwargs=dict(transaction_pk=str(transaction.pk), to_crypto=None))

                return Response(serializer.data, status=status.HTTP_200_OK)

            if method == 'withdraw.pending':
                print(method)
                print(params)
                transaction = Transactions.objects.filter(unique_id=unique_id).first()
                # status to create_for_payment
                transaction.status_update()
                return Response(serializer.data, status=status.HTTP_200_OK)

            if method == 'withdraw.successful':
                print(method)
                print(params)
                transaction = Transactions.objects.filter(unique_id=unique_id).first()
                transaction.status = 'completed'
                transaction.is_confirm = True
                transaction.failed = False
                transaction.failed_error = None
                transaction.try_fixed_count_error = 0
                transaction.save()
                send_transaction_satus.delay(email_to=transaction.email,
                                             transaction_id=str(transaction.unique_id),
                                             transaction_status=transaction.status)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WhiteBitVerify(APIView):

    def get(self, request):
        return Response([settings.WHITEBIT_WEB_HOOK_PUBLIC_KEY], status=status.HTTP_200_OK)
