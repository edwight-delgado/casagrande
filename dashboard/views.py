from django.shortcuts import render

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from shopping.models import Item, OrderItem, Order, BillingAddress, Payment, Coupon, Refund, Category
from django.http import HttpResponseRedirect
from django.shortcuts import render as render_to_response
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.db import connection
# Create your views here.
import random
import string

#todos los clientes
#Post.objects.all()

# Create your views here.


class DashboardView(View):
    def dictfetchall(self,cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    def get(self, *args, **kwargs):
        items = Item.objects.filter(is_active=True)
        cursor = connection.cursor()
        cursor.execute('SELECT shopping_payment.id, methods, SUM(amount) AS Total from shopping_order join shopping_payment ON shopping_order.payment_id=shopping_payment.id WHERE shopping_order.received=1 GROUP BY methods')
        payments = self.dictfetchall(cursor)
        cursor.close()
        cursor = connection.cursor()
        #payments = Payment.objects.raw('SELECT id, methods, SUM(amount) AS Total from shopping_payment GROUP BY methods')
        cursor.execute('SELECT SUM(amount) AS Total from shopping_order join shopping_payment ON shopping_order.payment_id=shopping_payment.id WHERE shopping_order.received==1  GROUP BY methods')
        payment_total = cursor.fetchall()
        order_total = Order.objects.filter(ordered=True).count()
        item_total = Item.objects.filter(is_active=True).count()
        user_total = User.objects.filter(is_active=True).count()
        payment_total = sum([x[0] for x in payment_total])
        orders = Order.objects.select_related('payment','user','billing_address').filter(ordered=1)
        #my_book.authors.all()
        context = {
            'items': items,
            'payments':payments,
            'orders': orders,
            'order_total':order_total,
            'item_total': item_total,
            'user_total': user_total,
            'payment_total':payment_total
        }
        return render(self.request, "dashboard/home/index2.html", context)

class DashboardProductView(View):
    def get(self, *args, **kwargs):
        items = Item.objects.all()
        context = {
            'items': items
        }
        return render(self.request, "dashboard/home/product.html", context)
    
def order_api(request, order_id):

        # get the nick name from the client side.

        #nick_name = request.GET.get("order_id", None)
        order_items = Order.objects.get(id=order_id).items.all()

        #data = serialize("json", order_items, fields=('title', ''))
        response = {
                'items': list([ {'title':x.item.title, 'price':x.item.price, 'quantity':x.quantity, 'img':str(x.item.image)} for x in order_items]),
                
        }
        return JsonResponse(response)
    
    
class DashboardCustomerView(View):
    def get(self, *args, **kwargs):
        users = User.objects.filter(is_active=True)
        #orders = Order.objects.select_related('payment','user','billing_address').all()
        context = {
            #'orders': orders
            'users':users
        }
        return render(self.request, "dashboard/home/customer.html", context)
    
class DashboardOrderDetailsView(View):
    def get(self, *args, **kwargs):
        user=self.kwargs['user_id']
        userQuery = User.objects.filter(is_active=True).get(id=user)
        orders = Order.objects.select_related('payment','user','billing_address').filter(user_id=user)
        #order_items = OrderItem.objects.select_related('item').filter(user_id=user)
        cursor = connection.cursor()
        #payments = Payment.objects.raw('SELECT id, methods, SUM(amount) AS Total from shopping_payment GROUP BY methods')
        cursor.execute(f'SELECT SUM(amount) AS Total from shopping_order join shopping_payment ON shopping_order.payment_id=shopping_payment.id WHERE shopping_order.user_id==1 AND shopping_order.received==1 GROUP BY methods')
        payment_total = cursor.fetchall()
        order_total = Order.objects.filter(ordered=True, user_id=user).count()
        received_total = Order.objects.filter(received=True, user_id=user).count()
        order_pendientes = abs(order_total-received_total)
        context = {
            'orders': orders,
            'user':userQuery,
            'payment_total':payment_total[0],
            'order_total':order_total,
            'order_pendientes':order_pendientes,
            'order_received_total':received_total
        }
        return render(self.request, "dashboard/home/orderdetails.html", context)
    
class DashboardOrderedItemView(View):
    def get(self, *args, **kwargs):
        
        orders = Order.objects.select_related('payment','user','billing_address').filter(ordered=True)
        context = {
            'orders': orders,
        }
        return render(self.request, "dashboard/home/ordered_items.html", context)
    

def received(request, order_id):

        # get the nick name from the client side.
        #nick_name = request.GET.get("order_id", None)
        order = Order.objects.get(id=order_id)
        order.received = 1
        order.note = request.GET.get('note')
        #order.seller_id = request.user.id
        order.save()
        #data = serialize("json", order_items, fields=('title', ''))
        
        messages.error(request, "order update to received")
        return redirect("/dashboard/ordered-items")


