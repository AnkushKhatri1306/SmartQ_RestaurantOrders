from .models import *
from rest_framework import serializers

class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ('id', 'name')


class RestaurantDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = RestaurantDetail
        fields = ('id', 'name')


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name")
    order_time = serializers.DateTimeField(source="order_detail.timestamp", format="%H:%M:%S")

    class Meta:
        model = OrderItem
        fields = ('id', 'item_name', 'quantity', 'order_time', 'price')