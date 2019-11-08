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