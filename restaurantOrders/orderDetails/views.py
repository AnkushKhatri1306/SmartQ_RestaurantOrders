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

    # for save item and order details
    @action(methods=['POST', 'GET'], url_path='save-item-order', detail=False)
    def save_item_order_detail_xlsx(self, request):
        """
        METHOD : GET, POST
        URL: 127.0.0.1:9001/home/rest/save-item-order/
        :param request:
        :return:
        """
        try:
            data = self.save_item_order_details_from_xlsx(request)
            return Response(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            exception_detail(e)
            return Response(data={'status': 'error'}, status=status.HTTP_300_MULTIPLE_CHOICES)

    # for getting the restaurant total sale
    @action(methods=['GET'], url_path='tot-sale', detail=False)
    def get_restaurant_total_sale_detail(self, request):
        """
        METHOD: GET
        URL: 127.0.0.1:9001/home/rest/tot-sale/
        PARAMS: {
            'restaurantId': <NAME OF RESTAURANT>,
            'dateSample': <23-10-2019>
        }
        :param request:
        :return:
        """
        try:
            data = self.get_restaurant_total_sale(request)
            return Response(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            exception_detail(e)
            return Response(data={'status': 'error'}, status=status.HTTP_300_MULTIPLE_CHOICES)

    # particular item available currently, provided date how many items
    @action(methods=['GET'], url_path='tot-item-sold', detail=False)
    def get_item_avail_current_and_sale_details(self, request):
        """
        METHOD: GET
        URL: 127.0.0.1:9001/home/rest/tot-item-sold/
        PARAMS: {
            'itemname': <NAME OF ITEM>,
            'sample': <23-10-2019>
        }
        :param request:
        :return:
        """
        try:
            data = self.get_item_avail_current_and_sale(request)
            return Response(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            exception_detail(e)
            return Response(data={'status': 'error'}, status=status.HTTP_300_MULTIPLE_CHOICES)

    # list of the 5 most ordered and trending
    @action(methods=['GET'], url_path='trending-item', detail=False)
    def get_trending_item_details(self, request):
        """
        METHOD: GET
        URL: 127.0.0.1:9001/home/rest/tot-sale/
        PARAMS: {
            'restaurantId': <NAME OF RESTAURANT>,
            'dateSample': <23-10-2019>
        }
        :param request:
        :return:
        """
        try:
            data = self.get_trending_item(request)
            return Response(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            exception_detail(e)
            return Response(data={'status': 'error'}, status=status.HTTP_300_MULTIPLE_CHOICES)

    @action(methods=['GET'], url_path='csv-download', detail=False)
    def csv_download_data(self, request):
        """
        METHOD: GET
        URL: 127.0.0.1:9001/home/rest/tot-sale/
        PARAMS: {
            'restaurantId': <NAME OF RESTAURANT>,
            'dateSample': <23-10-2019>
        }
        :param request:
        :return:
        """
        try:
            return self.csv_download(request)
        except Exception as e:
            exception_detail(e)
            return Response(data={'status': 'error'}, status=status.HTTP_300_MULTIPLE_CHOICES)