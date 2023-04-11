from django.urls import path
from django.urls import re_path

from .views import *

app_name = 'dashboard'

urlpatterns = [

    path('', DashboardView.as_view(), name='dashboard'),
    path('customer', DashboardCustomerView.as_view(), name='dashboard_customer'),
    path('order/invoice/<int:order_id>', DashboardOrderInvoiceView.as_view(), name='dashboard_invoice'),
    path('order/details/<int:user_id>', DashboardOrderDetailsView.as_view(), name='dashboard_order_details'),
    path('product', DashboardProductView.as_view(), name='dashboard_products'),
    path('order_api/<int:order_id>', order_api, name='order_api'),
    path('received/<int:order_id>', received, name='received'),
    path('ordered-items', DashboardOrderedItem, name='ordered_items'),
    path('export/excel', export_users_xls, name='export_excel'),
]
