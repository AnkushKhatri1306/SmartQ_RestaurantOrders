from django.db import models

# Create your models here.


class Item(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'item'

class ItemsTiming(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'item_timing'

class RestaurantDetail(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'restaurant_detail'

class OrderDetail(models.Model):
    restaurant = models.ForeignKey(RestaurantDetail, on_delete=models.DO_NOTHING)
    order_id = models.CharField(max_length=50)
    bill_amount = models.IntegerField(default=0)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'order_detail'


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING)
    quantity = models.SmallIntegerField()
    price = models.IntegerField()
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'order_item'

