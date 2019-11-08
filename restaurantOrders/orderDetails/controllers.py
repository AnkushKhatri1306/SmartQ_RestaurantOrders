from .models import *
from restaurantOrders.utility import *
import xlrd
import itertools
from .serializers import *
import datetime, pytz, json
from django.db.models import Sum
from collections import OrderedDict

class OrderDetailController():

    def save_item_order_details_from_xlsx(self, request):
        """
        function to save item and order details present in the Excel file in different sheets
        1. checking that data is already there or not in the itemtiming table
        2. opening the excel file and start reading the sheet one by one
        3. saving the item then saving the timings of each item
        4. success calling the funtion to save the order details
        :param request: request data
        :return: success or error message
        """
        success = False
        msg = "Error in saving order details data from Excel"
        try:
            item_timing_count = ItemsTiming.objects.filter().count()
            if item_timing_count == 0:
                wb = xlrd.open_workbook("orderDetails/excel file/Smartq Data.xlsx")
                item_sheet = wb.sheet_by_name('food menu')
                order_sheet = wb.sheet_by_name('order details')
                time_create_list = []
                item_id_name_dict = {}
                for i in range(1, item_sheet.nrows):
                    item_row = item_sheet.row_values(i)
                    obj = Item()
                    obj.name = item_row[0]
                    obj.save()
                    item_id = obj.id
                    item_id_name_dict[item_row[0]] = item_id
                    time_create_list.extend(self.save_item_available_time_slot(item_id, item_row[1]))
                if time_create_list:
                    ItemsTiming.objects.bulk_create(time_create_list)
                    success = True
                if success:
                    success = self.save_order_details_data_from_xlxs(order_sheet, item_id_name_dict)
                    if success:
                        msg = "Success in saving order details data from Excel"
            return get_response_object(success, msg)
        except Exception as e:
            exception_detail(e)
            return get_response_object(False, msg)


    def save_item_available_time_slot(self, item_id, time_data):
        """
        function to return the item timing object for saving
        1. spliting the data and making a object for saving
        :param item_id: id of item that was saved in the DB
        :param time_data: time data is the data of the item need to save
        :return:
        """
        ret_data = []
        try:
            if item_id and time_data:
                slot = time_data.split(', ')
                for data in slot:
                    start_time, end_time = data.split(' - ')
                    obj = ItemsTiming()
                    obj.item_id = item_id
                    obj.start_time = start_time
                    obj.end_time = end_time
                    ret_data.append(obj)
            return ret_data
        except Exception as e:
            exception_detail(e)
            return []


    def save_order_details_data_from_xlxs(self, order_sheet, item_id_name_dict):
        """
        function to save the order details from the sheet
        1. first saving restaurant name to DB
        2. making a dict of name and id of the restaurant
        3. iterating over row and making a object of order detail and saving it
        4. saving order item details
        :param order_sheet: order detail sheet
        :param item_id_name_dict:  item with id dict mapping
        :return:
        """
        try:
            success = False
            restaurant_name_list = list(set(order_sheet.col_values(1)))
            restaurant_name_list.remove('restaurantid')
            success = self.save_restaurant_name_details(restaurant_name_list)
            if success:
                restaurant_obj = RestaurantDetail.objects.filter()
                restaurant_serializer = RestaurantDetailSerializer(restaurant_obj, many=True)
                restaurant_data = restaurant_serializer.data
                rest_id_name_dict = {data['name']: data['id'] for data in restaurant_data}
                order_item_create_list = []
                for i in range(1, order_sheet.nrows):
                    row_data = order_sheet.row_values(i)
                    obj = OrderDetail()
                    obj.restaurant_id = rest_id_name_dict.get(row_data[1])
                    obj.order_id = row_data[0]
                    obj.bill_amount = row_data[3]
                    obj.timestamp = datetime.datetime(1900, 1, 1, tzinfo=pytz.UTC) + datetime.timedelta(days=row_data[4])
                    obj.save()
                    order_id = obj.id
                    order_item_create_list.extend(self.save_order_item_details(order_id, row_data[2], item_id_name_dict))
                if order_item_create_list:
                    OrderItem.objects.bulk_create(order_item_create_list)
                    success = True
                else:
                    success = False
            return success
        except Exception as e:
            exception_detail(e)
            return False


    def save_restaurant_name_details(self, restaurant_name_list):
        """
        function to save restaurant name details in DB
        1. making object of each restaurant name
        2, saving using bulk_create
        :param restaurant_name_list:
        :return:
        """
        success = False
        try:
            create_list = []
            for name in restaurant_name_list:
                obj = RestaurantDetail()
                obj.name = name
                create_list.append(obj)
            if create_list:
                RestaurantDetail.objects.bulk_create(create_list)
                success = True
        except Exception as e:
            exception_detail(e)
        return success


    def save_order_item_details(self, order_id, order_list, item_id_name_dict):
        """
        funtion to save order item details i.e in single order how many items are present
        1. checking that order_id and order item list is there
        2. making object of each order item and sending it to the caller part
        :param order_id: order id
        :param order_list: order list containg all items
        :param item_id_name_dict: item dict with key as name and value as id
        :return:
        """
        try:
            create_list = []
            if order_id and order_list:
                order_list = order_list.replace('‘', '"')
                order_list = order_list.replace('’', '"')
                for item in json.loads(order_list):
                    obj = OrderItem()
                    item_name = item.get('itemname').lower()
                    obj.item_id = item_id_name_dict.get(item_name)
                    obj.quantity = item.get('quantity')
                    obj.price = item.get('price')
                    obj.order_detail_id = order_id
                    create_list.append(obj)
            return create_list
        except Exception as e:
            exception_detail(e)
            return []


    def get_restaurant_total_sale(self, request):
        """
        function to get the total sale of particular retaurant on date given
        1. getting the name and date
        2. changing it to particular format
        3. querying and getting the result
        :param request:
        :return:
        """
        success = False
        msg = 'Error in getting total sale sample'
        try:
            restuarant_id = request.GET.get('restaurantId', None)
            date_sample = request.GET.get('dateSample')
            if restuarant_id and date_sample:
                date_sample = datetime.datetime.strptime(date_sample, "%d-%M-%Y").strftime("%Y-%M-%d")
                tot_sale = OrderDetail.objects.filter(timestamp__date=date_sample, restaurant__name=restuarant_id) \
                        .aggregate(Sum('bill_amount'))
                success = True
                tot_sum = tot_sale.get('bill_amount__sum')
                if not tot_sum:
                    tot_sum = 0
                msg = 'Total sale sample - ' + str(tot_sum)
        except Exception as e:
            exception_detail(e)
        return get_response_object(success, msg)


    def get_item_avail_current_and_sale(self, request):
        """
        function to get the item is currently available or not and the sale of the item
        1. getting the data from request
        2. if present getting available count and quantity
        :param request:
        :return:
        """
        success = False
        msg = 'Error in getting Item available status'
        try:
            msg = 'Item not Available , '
            itemname = request.GET.get('itemname', None)
            date_sample = request.GET.get('sample')
            if itemname and date_sample:
                date_sample = datetime.datetime.strptime(date_sample, "%d-%M-%Y").strftime("%Y-%M-%d")
                curr_time = datetime.datetime.now().strftime("%H:%M:%S")
                available_count = ItemsTiming.objects.filter(item__name=itemname, start_time__lte=curr_time,
                                                             end_time__gte=curr_time).count()
                quantity = OrderItem.objects.filter(item__name=itemname, order_detail__timestamp__date=date_sample).\
                            aggregate(Sum('quantity'))
                if available_count:
                    msg = 'Item Available , '
                tot_sum = quantity.get('quantity__sum')
                if not tot_sum:
                    tot_sum = 0
                msg += str(tot_sum) + ' quantity sold .'
                success = True
        except Exception as e:
            exception_detail(e)
        return get_response_object(success, msg)


    def get_trending_item(self, request):
        """
        function to get the top 5 trending item in the particular restaurant according to the quantity sale
        1. making a dict with empty data
        2. getting the data from request and checking they are present or not
        3. getting all the data for that restaurant on the given date
        4. making datetime object for comparision of timing
        5. comparing and making the dict accordigly for all the time slots
        5. sending the value after sorted them on basis of maximun quantity
        :param request:
        :return:
        """
        success = False
        msg = 'Error in getting trending items .'
        try:
            ret_dict = {
                'Top 5 most sold item for the day': [],
                'Top 5 most sold item per slots': {}
            }
            restaurant_id = request.GET.get('restaurantId', None)
            date_sample = request.GET.get('dateSample')
            if restaurant_id and date_sample:
                date_sample = datetime.datetime.strptime(date_sample, "%d-%M-%Y").strftime("%Y-%M-%d")
                order_item_obj = OrderItem.objects.filter(order_detail__restaurant__name=restaurant_id,
                                                          order_detail__timestamp__date=date_sample)
                order_item_serializer = OrderItemSerializer(order_item_obj, many=True)
                order_item_data = order_item_serializer.data
                break_fast_start = datetime.datetime.strptime("07:00:00", "%H:%M:%S")
                break_fast_end = datetime.datetime.strptime("11:00:00", "%H:%M:%S")
                lunch_start = datetime.datetime.strptime("12:30:00", "%H:%M:%S")
                lunch_end = datetime.datetime.strptime("15:30:00", "%H:%M:%S")
                snacks_start = datetime.datetime.strptime("16:30:00", "%H:%M:%S")
                snacks_end = datetime.datetime.strptime("19:00:00", "%H:%M:%S")
                dinner_start = datetime.datetime.strptime("19:30:00", "%H:%M:%S")
                dinner_end = datetime.datetime.strptime("23:00:00", "%H:%M:%S")
                timeslot = {
                    'BREAKFAST': {},
                    'LUNCH': {},
                    'SNACKS': {},
                    'DINNER': {},
                }
                trending = {}
                for data in order_item_data:
                    if data.get('order_time'):
                        order_time = datetime.datetime.strptime(data.get('order_time'), "%H:%M:%S")
                        item_name = data.get('item_name')
                        if not trending.get(item_name, None):
                            trending[item_name] = 0
                        trending[item_name] += data.get('quantity')
                        if order_time >= break_fast_start and order_time <= break_fast_end:
                            if not timeslot.get('BREAKFAST', {}).get(item_name, None):
                                timeslot['BREAKFAST'][item_name] = 0
                            timeslot['BREAKFAST'][item_name] += 1
                        elif order_time >= lunch_start and order_time <= lunch_end:
                            if not timeslot.get('LUNCH', {}).get(item_name, None):
                                timeslot['LUNCH'][item_name] = 0
                            timeslot['LUNCH'][item_name] += 1
                        elif order_time >= snacks_start and order_time <= snacks_end:
                            if not timeslot.get('SNACKS', {}).get(item_name, None):
                                timeslot['SNACKS'][item_name] = 0
                            timeslot['SNACKS'][item_name] += 1
                        elif order_time >= dinner_start and order_time <= dinner_end:
                            if not timeslot.get('DINNER', {}).get(item_name, None):
                                timeslot['DINNER'][item_name] = 0
                            timeslot['DINNER'][item_name] += 1
                trending = sort_on_basis_of_value(trending, reverse=True)
                trending = OrderedDict(itertools.islice(trending.items(), 5))
                for k,v in timeslot.items():
                    temp = sort_on_basis_of_value(v, reverse=True)
                    timeslot[k] = list(temp.keys())[:5]
                ret_dict['Top 5 most sold item for the day'] = trending
                ret_dict['Top 5 most sold item per slots'] = timeslot
                success = True
                msg = 'Success in getting trending data .'
            return ret_dict
        except Exception as e:
            exception_detail(e)
            return get_response_object(success, msg)