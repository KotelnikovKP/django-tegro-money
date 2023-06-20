import json

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django_tegro_money.models import TegroMoneyOrder


@csrf_exempt
def payment_status(request):

    if request.method == 'POST':

        try:
            data = json.load(request)
        except Exception as e:
            return JsonResponse({'type': 'error', 'desc': f'Invalid request json: {e}'}, status=400)

        shop_id = data.get('shop_id')
        order_id = data.get('order_id')
        status = data.get('status')
        amount = data.get('amount')
        payment_system = data.get('payment_system')
        currency = data.get('currency')
        test = data.get('test')
        sign = data.get('sign')

        if shop_id is not None and order_id is not None and status is not None:

            orders = TegroMoneyOrder.objects.filter(shop_id=shop_id, order_id=order_id)
            if len(orders) != 1:
                return JsonResponse({'type': 'error', 'desc': 'order not found'}, status=404)

            order = orders[0]

            with transaction.atomic():
                order.status = status
                order.save()

            return JsonResponse({'type': 'success', 'desc': ''}, status=200)

        else:
            return JsonResponse({'type': 'error', 'desc': 'Invalid request: shop_id, order_id, status are expected'},
                                status=400)

    else:
        return JsonResponse({'type': 'error', 'desc': 'Invalid request: method must be POST'}, status=400)
