from django.urls import path
from .views import (
    ItemDetailView,
    HomeView,
    add_to_cart,
    remove_from_cart,
    ShopView,
    OrderSummaryView,
    remove_single_item_from_cart,
    CheckoutView,
    PaymentView,
    show_detail,
    AddCouponView,
    RequestRefundView,
    CategoryView,
    MainSearch,
    categories_api,
    shopping_card_api,
    BillingAddressView,
    Pedidos
)

app_name = 'shopping'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('address', BillingAddressView.as_view(), name='address'),
    #path('pedidos', BillingAddressView.as_view(), name='pedidos'),
    path('category/<slug>/', CategoryView.as_view(), name='category'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('show_detail/<item_id>/', show_detail, name='show-detail'),
    path('category_api/', categories_api, name='category-api'),
    path('add_coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('pedidos/', Pedidos, name='pedidos'),
    path('search/', MainSearch, name='search'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('shopping-card-api', shopping_card_api, name='shopping-card-api'),
    
]
