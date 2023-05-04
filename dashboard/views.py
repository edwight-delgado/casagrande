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
from django.http import HttpResponse
from datetime import datetime
import datetime
from datetime import timedelta
import xlwt
from django.urls import reverse

from django.core.cache import cache
cache.clear()

from django.db.models import Sum
from django.db.models import F, FloatField
#todos los clientes
#Post.objects.all()

# Create your views here.

def excel_item(wb):
    ws_itens = wb.add_sheet('Inventario de Productos')

    # Sheet header, first row
    row_num = 5

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    style = xlwt.XFStyle()
    style.num_format_str = 'DD/MM/AA'
    ws_itens.write(0, 0, 'Fecha', style)
    ws_itens.write(0, 1, datetime.datetime.now(), style)

    columns = ['Nombre', 'Precio', 'Cantidad', 'Valor total','Disponibilidad','Categoria']

    for col_num in range(len(columns)):
        ws_itens.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    #rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    rows = Item.objects.select_related('category','marca').all()
    col_num = 0

    for row in rows:
        
        valores = [row.title, row.price, float(row.quantity), (float(row.price) * float(row.quantity)), row.is_active, row.category.title]
        row_num += 1
        for valor in valores:
            ws_itens.write(row_num, col_num, valor, font_style)
            col_num += 1
        col_num =0

    valor_total = Item.objects.filter(is_active=True).aggregate(total=Sum(F('price') * F('quantity'), output_field=FloatField()))['total']
    item_total = Item.objects.filter(is_active=True).count()
    item_no_active = Item.objects.filter(is_active=False).count()
    mydic = {'Valor Total':valor_total,'Cantidad Total':item_total,'total faltante':item_no_active}
    row_num = 1
    col_num = 0
    for key,value in mydic.items():
        col_num += 1
        ws_itens.write(row_num, col_num, key, font_style)
        ws_itens.write(row_num+1, col_num, value, font_style)

def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Historial de Pedido') # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 5

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Nombre', 'Total Pedido', 'Metodo de Pago', 'estatus ordenado','estatus recivido','telefono','dirección','nota']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    #rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    rows = Order.objects.select_related('payment','user','billing_address').filter(ordered=1)
    style = xlwt.XFStyle()
    style.num_format_str = 'DD/MM/AA'
    col_num = 0
    for row in rows:
        fecha = row.ordered_date
        fecha = fecha.strftime('%d/%m/%Y')

        valores = [row.user.username, row.payment.amount, row.payment.methods, row.ordered, row.received,row.billing_address.zip, row.billing_address.street_address, row.note]
        row_num += 1

        for valor in valores:
            ws.write(row_num, col_num, valor, font_style)
            col_num += 1
        ws.write(row_num, col_num+1, fecha, style)
        col_num =0

    order_total = Order.objects.filter(ordered=True).count()
    item_total = Item.objects.filter(is_active=True).count()
    user_total = User.objects.filter(is_active=True).count()
    mydic = {'pedidos totales':order_total,'productos totales':item_total,'total de clientes':user_total}
    row_num = 1
    col_num = 0
    for key,value in mydic.items():
        col_num += 1
        ws.write(row_num, col_num, key, font_style)
        ws.write(row_num+1, col_num, value, font_style)

    excel_item(wb)
    wb.save(response)

    return response

class DashboardView(View):
    def dictfetchall(self,cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    def get(self, *args, **kwargs):
        items = Item.objects.filter(is_active=True).order_by('-quantity')[:5]
        cursor = connection.cursor()
        cursor.execute('SELECT methods, SUM(amount) AS Total from shopping_order join shopping_payment ON shopping_order.payment_id=shopping_payment.id WHERE shopping_order.received=1 GROUP BY methods')
        payments = self.dictfetchall(cursor)
        cursor.close()
        cursor = connection.cursor()
        #payments = Payment.objects.raw('SELECT id, methods, SUM(amount) AS Total from shopping_payment GROUP BY methods')
        cursor.execute('SELECT SUM(amount) AS Total from shopping_order join shopping_payment ON shopping_order.payment_id=shopping_payment.id WHERE shopping_order.received=1  GROUP BY methods')
        payment_total = cursor.fetchall()
        cursor.close()
        order_total = Order.objects.filter(ordered=True).count()
        item_total = Item.objects.filter(is_active=True).count()
        user_total = User.objects.filter(is_active=True).count()
        payment_total = sum([x[0] for x in payment_total])
        orders = Order.objects.select_related('payment','user','billing_address').filter(ordered=1).order_by('-id')[:10]
        cursor = connection.cursor()
        cursor.execute('SELECT auth_user.id AS idx, username, email, SUM(amount) AS total FROM auth_user JOIN shopping_payment ON auth_user.id = shopping_payment.user_id GROUP BY user_id')
        users = self.dictfetchall(cursor)
        cursor.close()
   

        today_date = datetime.date.today()
        #end_date = today_date-timedelta(days=1)

        #my_book.authors.all()
        context = {
            'today_date':today_date.strftime("%m/%d/%Y"),
            #'end_date':end_date.strftime("%m/%d/%Y"),
            'items': items,
            'payments':payments,
            'orders': orders,
            'order_total':order_total,
            'item_total': item_total,
            'user_total': user_total,
            'payment_total':payment_total,
            'users':users
        }
        return render(self.request, "dashboard/home/index.html", context)


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


class DashboardOrderInvoiceView(View):
    def get(self, *args, **kwargs):
        order_id=self.kwargs['order_id']
        #print(user)
        #order = Order.objects.get(id=order_id)
        #userQuery = User.objects.filter(is_active=True).get(id=user)
        order = Order.objects.select_related('payment','user','billing_address').get(id=order_id)
        #order_items = OrderItem.objects.select_related('item').filter(user_id=user)
        
        context = {
            'order': order,
            
        }
        return render(self.request, "dashboard/home/invoice.html", context)
    
class DashboardOrderDetailsView(View):
    def get(self, *args, **kwargs):
        user=self.kwargs['user_id']

        
        userQuery = User.objects.filter(is_active=True).get(id=user)
        orders = Order.objects.select_related('payment','user','billing_address').filter(user_id=user)
        #order_items = OrderItem.objects.select_related('item').filter(user_id=user)
        cursor = connection.cursor()
        #payments = Payment.objects.raw('SELECT id, methods, SUM(amount) AS Total from shopping_payment GROUP BY methods')
        cursor.execute(f'SELECT SUM(amount) AS Total from shopping_order join shopping_payment ON shopping_order.payment_id=shopping_payment.id WHERE (shopping_order.user_id=1 AND shopping_order.received=1) GROUP BY methods')
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
    
def DashboardOrderedItem(request):
    
        today_date = datetime.date.today()
        if request.POST:
            today_date = datetime.date.today()
            response = request.POST['range_date']
            start = response[:10]
            end = response[13:]
            
            
            start = datetime.datetime.strptime(start, "%m/%d/%Y")
            end = datetime.datetime.strptime(end, "%m/%d/%Y")

            orders = Order.objects.select_related('payment','user','billing_address').filter(
                ordered=True,
                ordered_date__range=[start, end]
            )
            context = {
                'orders': orders,
                'today_date':today_date.strftime("%m/%d/%Y"),
            }
            return render(request, "dashboard/home/ordered_items.html", context)
        
        #return render('dashboard:ordered_items',context)
        #return redirect("dashboard:ordered_items")

        orders = Order.objects.select_related('payment','user','billing_address').filter(
            ordered=True
        )
        context = {
            'orders': orders,
            'today_date':today_date.strftime("%m/%d/%Y"),
        }
        return render(request, "dashboard/home/ordered_items.html", context)


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
        return redirect("dashboard:ordered_items")


