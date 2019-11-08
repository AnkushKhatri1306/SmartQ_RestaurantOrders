from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from .models import Item
from .controllers import OrderDetailController
from .serializers import ItemSerializer
from restaurantOrders.utility import *

class OrderDetailViewset(viewsets.ModelViewSet, OrderDetailController):
    queryset = Item.objects.filter()
    serializer_class = ItemSerializer

    @action(methods=['POST'], url_path='save-item-order', detail=False)
    def save_item_order_detail_xlsx(self, request):
        try:
            data = self.save_item_order_details_from_xlsx(request)
            return Response(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            exception_detail(e)
            return Response(data={'status': 'error'}, status=status.HTTP_300_MULTIPLE_CHOICES)