from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from exchanger.exchange_exceptions import ExchangeTradeError
from exchanger.models import Transactions
from exchanger.whitebit_api import WhiteBitApi
from webhook.serializers import WhiteBitSerializer
from celery_tasks.tasks import send_transaction_satus


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
            print(method)
            print(params)
            unique_id = params.get("uniqueId")
            wallet_address = params.get("address")
            if method == 'deposit.processed' and unique_id:
                transaction = Transactions.objects.filter(unique_id=unique_id).first()
                if not transaction:
                    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
                transaction.hash = params.get('transactionHash')
                # status to payment_received
                transaction.status_update()
                try:
                    self.white_bit_api.start_trading(
                        transaction_pk=transaction.pk,
                        name_from_white_bit_exchange=transaction.currency_exchange.name_from_white_bit,
                        name_from_white_bit_received=transaction.currency_received.name_from_white_bit,
                        market=transaction.market,
                        amount_exchange=transaction.amount_real_exchange,
                        amount_received=transaction.amount_received,
                    )
                except ExchangeTradeError as e:
                    print(e)
                    transaction.failed = True
                    transaction.failed_error = str(e)
                    return Response(serializer.data, status=status.HTTP_200_OK)

                # status to currency_changing
                transaction.status_update()
                withdraw_crypto = self.white_bit_api.create_withdraw(
                    unique_id=transaction.unique_id,
                    network=transaction.currency_received.network_for_min_max,
                    currency=transaction.currency_received.name_from_white_bit,
                    address=transaction.address,
                    amount_price=transaction.amount_received
                )
                if not withdraw_crypto:
                    transaction.failed = True
                    transaction.save(failed_error='not withdraw_crypto')
                    return Response(serializer.data, status=status.HTTP_200_OK)

                # status to create_for_payment
                transaction.status_update()
                return Response(serializer.data, status=status.HTTP_200_OK)

            if method == 'deposit.processed' and wallet_address:
                transaction = Transactions.objects.filter(deposit_address=wallet_address).first()
                if not transaction:
                    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

                # status to payment_received
                transaction.hash = params.get('transactionHash')
                transaction.status_update()
                try:
                    self.white_bit_api.start_trading(
                        transaction_pk=transaction.pk,
                        name_from_white_bit_exchange=transaction.currency_exchange.name_from_white_bit,
                        name_from_white_bit_received=transaction.currency_received.name_from_white_bit,
                        market=transaction.market,
                        amount_exchange=transaction.amount_real_exchange,
                        amount_received=transaction.amount_received
                    )
                except ExchangeTradeError as e:
                    print(e)
                    transaction.failed = True
                    transaction.failed_error = str(e)
                    return Response(serializer.data, status=status.HTTP_200_OK)

                # status to currency_changing
                transaction.status_update()

                withdraw_crypto = self.white_bit_api.create_withdraw(
                    unique_id=transaction.unique_id,
                    network=transaction.currency_received.network,
                    currency=transaction.currency_received.name_from_white_bit,
                    address=transaction.address,
                    amount_price=transaction.amount_received,
                    provider=True,
                )
                if not withdraw_crypto:
                    transaction.failed = True
                    transaction.save(failed_error='not withdraw_fiat')
                    return Response(serializer.data, status=status.HTTP_200_OK)

                # status to create_for_payment
                transaction.status_update()
                return Response(serializer.data, status=status.HTTP_200_OK)

            if method == 'withdraw.pending':
                transaction = Transactions.objects.filter(unique_id=unique_id).first()
                # status to create_for_payment
                transaction.status_update()
                return Response(serializer.data, status=status.HTTP_200_OK)

            if method == 'withdraw.successful':
                transaction = Transactions.objects.filter(unique_id=unique_id).first()
                transaction.status = 'completed'
                transaction.is_confirm = True
                transaction.failed = False
                transaction.failed_error = None
                transaction.try_fixed_count_error = 0
                transaction.save()
                send_transaction_satus.delay(email_to=transaction.email,
                                             transaction_id=transaction.unique_id,
                                             transaction_status=transaction.status)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WhiteBitVerify(APIView):

    def get(self, request):
        return Response([settings.WHITEBIT_WEB_HOOK_PUBLIC_KEY], status=status.HTTP_200_OK)
