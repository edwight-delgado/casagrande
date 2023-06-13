from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm
from .models import Item, OrderItem, Order, BillingAddress, Payment, Coupon, Refund, Category
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
#from django.shortcuts import render as render_to_response
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
# Create your views here.
import random
import string

ITEMS_PER_PAGE = 10

def create_ref_code(user_id, order_id):
    rand_tail = ''.join(random.choices(string.digits, k=9))
    return str(user_id)+ str(order_id) + rand_tail

class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "u have not added a billing address")
            return redirect("shopping:checkout")

    def post(self, *args, **kwargs):    
        pass
       

class HomeView(ListView):
    template_name = "index.html"
    queryset = Item.objects.filter(is_active=True)
    context_object_name = 'items'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "No tienes un pedido activo")
            return redirect("/")


def MainSearch(request):
    if request.method == 'GET':
        search = request.GET.get('search')
        print(search)
        search = str(search).lower().strip()
        try:
            items = Item.objects.filter(title__contains=search)
            #total_comments = items.annotate(total=Sum('length')).values('total')
            
            if len(items) == 0:
                messages.error(request, "Producto no encontrado")
                items = Item.objects.all()
            else:

                messages.success(request, 'producto encontrado')
        except Item.DoesNotExist:
            messages.error(request, "Producto no encontrado")
            items = Item.objects.all()
    return render(request, 'index.html', {'items': items})


def Pedidos(request):
    orders = Order.objects.select_related('payment','user','billing_address').filter(
            ordered=True      
    )
    context = {
        'orders': orders,
    }
    return render(request, 'pedidos.html',context)


class ShopView(View):
    def get(self, request):
        try:
            items = Item.objects.all()
            paginator = Paginator(items, ITEMS_PER_PAGE)
            page_object = paginator.get_page(2)
            context = {"items":items, "items_on_page": page_object}
        except Item.DoesNotExist:
            return HttpResponse("Item no encontrado")
        
        return render(self.request,'shop.html', context)

       


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-detail.html"


# class CategoryView(DetailView):
#     model = Category
#     template_name = "category.html"

class CategoryView(View):
    def get(self, *args, **kwargs):
        category = Category.objects.get(slug=self.kwargs['slug'])
        item = Item.objects.filter(category=category, is_active=True)
        context = {
            'object_list': item,
            'category_title': category,
            'category_description': category.description,
            'category_image': category.image
        }
        return render(self.request, "category.html", context)


class MetodoPagoView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if self.request.user.is_superuser:
                billing_address = BillingAddress.objects.all().order_by('-id')
            else:
                billing_address = BillingAddress.objects.filter(user_id=self.request.user).order_by('-id')
            users = User.objects.filter(is_active=True)
            print(billing_address)
            form = CheckoutForm()
            context = {
                'form': form,
                'billing_address':billing_address,
                'couponform': CouponForm(),
                'order': order,
                'users':users,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "metodo_pago.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("shopping:home")

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if self.request.user.is_superuser:
                billing_address = BillingAddress.objects.all().order_by('-id')
            else:
                billing_address = BillingAddress.objects.filter(user_id=self.request.user).order_by('-id')
            users = User.objects.filter(is_active=True)
            print(billing_address)
            form = CheckoutForm()
            context = {
                'form': form,
                'billing_address':billing_address,
                'couponform': CouponForm(),
                'order': order,
                'users':users,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("shopping:home")


    def post(self, *args, **kwargs):            
        try:
            if self.request.method == 'POST' and self.request.POST:
                if self.request.POST.get('address_id'):
                    print('............................')
                    billing_address = BillingAddress.objects.get(id=self.request.POST['address_id'])
                    print(self.request.POST)
                    user = self.request.user
                    if self.request.user.is_superuser:
                        user = billing_address.user_id
                    print('.........')
                    print(user)
                    order = Order.objects.get(user=self.request.user, ordered=False)
                    order.user_id = user
                    #order.OrderItem.
                    order.save()
                    order_item = OrderItem.objects.filter(
                        user=self.request.user,
                        ordered=False
                    ).order_by('-id')[0]
                    order_item.user_id = user
                    order_item.save()
                    print(billing_address)
                    order.billing_address = billing_address
                        
                    # create the payment (pago)
                    payment = Payment()
                    #ids = charge['id']
                    payment.stripe_charge_id = 1
                    payment.user_id = user

                    payment.amount = order.get_total()
                    payment.methods = self.request.POST.get('payment_option')
                    payment.save()

                    # assign the payment to the order
                    order.ordered = True
                    order.payment_id = payment.id
                    #TODO : assign ref code
                    order.ref_code = create_ref_code(user, order.id)
                    order.save()
                    #aqui modulo que envia msg a whatssapp
                    # enviar -> billing_address
                    # enviar -> user
                    # enviar orderitem
                    # enviar amount
                    # enviar methods
                    # enviar link
                
                    messages.success(self.request, "Su orden fue exitosa Order Confirmation")
                    return redirect("/")
                else:
                    return redirect('shopping:checkout')
                # end ----------------- nuevo --------------------
                # add redirect to the selected payment option
        except ObjectDoesNotExist:
            messages.error(self.request, "No tienes una orden activa")
            return redirect("shopping:home")


class BillingAddressView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if self.request.user.is_superuser:
                billing_address = BillingAddress.objects.all().order_by('-id')
            else:
                billing_address = BillingAddress.objects.filter(user_id=self.request.user).order_by('-id')
            print(billing_address)
            users = User.objects.filter(is_active=True)
            form = CheckoutForm()
            context = {
                'form': form,
                'billing_address':billing_address,
                'couponform': CouponForm(),
                'order': order,
                'users':users,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("shopping:home")

    def post(self, *args, **kwargs):
        print('111111111111111111111111111')
        form = CheckoutForm(self.request.POST or None)
        try:
            print('111111111111111111111111111........')
            order = Order.objects.get(user=self.request.user, ordered=False)
            latitude = 0
            longitude = 0
            if form.is_valid():
                print('111111111111111111111111111........2222222222222')
                print(self.request.POST)
                user = self.request.user
                if self.request.user.is_superuser:
                    #user recivido de Post
                    user = self.request.POST.get('user')
                tag = form.cleaned_data.get('tag')
                print('------------------------')
                print(self.request.POST)
                print('............................')
                print(user)
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                apartment_number = form.cleaned_data.get('apartment_number')
                latitude = form.cleaned_data.get('latitude')
                longitude = form.cleaned_data.get('longitude')
                phone = form.cleaned_data.get('phone')
                # add functionality for these fields
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                #payment_option = form.cleaned_data.get('payment_option')
                payment_shipping = form.cleaned_data.get('payment_shipping')
                print('guardado',street_address)
                billing_address = BillingAddress(
                    user_id=user,
                    tag=tag,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    number=apartment_number,
                    phone=phone ,
                    address_type=payment_shipping,
                    #payment_method=payment_option ,
                    #longitude=longitude,
                    #latitude=latitude
                )
                billing_address.save()
                print('eeeeeeeeeeeeeeeeeeeeeeeee')
                print(billing_address)
                order.billing_address = billing_address
                
                order.save()

                
                messages.success(self.request, "Su orden fue exitosa")
                return redirect("shopping:checkout")
                # end ----------------- nuevo --------------------
                # add redirect to the selected payment option
        except ObjectDoesNotExist:
            messages.error(self.request, "No tienes una orden activa")
            return redirect("shopping:checkout")


# def home(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "index.html", context)
#
#
# def products(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "product-detail.html", context)
#
#
# def shop(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "shop.html", context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            if item.quantity <= order_item.quantity:
                order_item.quantity = item.quantity
            else:
                order_item.quantity += 1
            order_item.save()
            messages.info(request, "La cantidad fue actualizada.")
            return redirect("shopping:home")
        else:
            order.items.add(order_item)
            messages.info(request, "El producto fue agregado al carrito de Compras")
            return redirect("shopping:home")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "El Producto fue agregado al carrito.")
    

    
    #return JsonResponse(response)
    return redirect("shopping:home")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "El Producto fue eliminado de su carrito de compra.")
            return redirect("shopping:home")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("shopping:home", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "No tiene una Orden activa")
        return redirect("shopping:home", slug=slug)
    return redirect("shopping:home", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "La Cantidad fue actualizada.")
            return redirect("shopping:home")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("shopping:home", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("shopping:home", slug=slug)
    return redirect("shopping:nome", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("shopping:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("shopping:checkout")

            except ObjectDoesNotExist:
                messages.info(request, "You do not have an active order")
                return redirect("shopping:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received")
                return redirect("shopping:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect("shopping:request-refund")


@login_required
def shopping_card_api(request):
    ordered = 0
    ordered = Order.objects.filter(user=request.user, ordered=True).latest('id').ordered
    received = Order.objects.filter(user=request.user, ordered=True).latest('id').received
    #return ordered
    try:
        #ordered = Order.objects.get(user=request.user, ordered=True).ordered
        order = Order.objects.filter(user=request.user, ordered=False).latest('id')
        #ordered = Order.objects.get(user=request.user, ordered=True).values('orderded')
        response = {
                'items': list([ {'title':x.item.title, 'slug':x.item.slug, 'price':x.item.price, 'quantity':x.quantity,'monto':(x.quantity*x.item.price), 'img':str(x.item.image)} for x in order.items.all()]),
                'status_ordered': ordered,
                'status_received':received,
                'total': order.get_total(),
        }
        return JsonResponse(response)
    except:
        response = {
                'items': 0,
                'status_ordered': ordered,
                'status_received':False,
                'total': 0
                
        }
        return JsonResponse(response)


def show_detail(request, item_id:int):
    
    try:
        item = Item.objects.get(id=item_id)
        orders = Order.objects.filter(user=request.user, ordered=False, items__item_id=item_id)
        print(item)
        print(orders)
        if orders.exists():
            print('-----------existe-------')
            order = Order.objects.get(user=request.user, ordered=False)
            order_item = order.items.get(item_id=item)
            order_item = order_item.quantity
        else:
            order_item = 0
        print(item)
        response = {
            "data":{
                'title': item.title,
                'image': str(item.image),
                'label':item.label,
                'peso':item.peso,
                'unit':item.unit,
                'code_bar':item.stock_no,
                'price': item.price,
                'quantity':item.quantity,
                'quantity_cart':order_item,
                'short_description':item.description_short,
                'long_description':item.description_long,
                'category':item.category.title,
                'sub_category':item.subcategory.title,
                'category_url':item.category.slug,
                'slug':item.slug,
                #'brand':item.brand.title,
                #'brand_url':item.brand.slug
            }
        }
        
    except:
        try:
            item = Item.objects.get(id=item_id)
            response = {
                "data":{
                    'title': item.title,
                    'image': str(item.image),
                    'label':item.label,
                    'peso':item.peso,
                    'unit':item.unit,
                    'code_bar':item.stock_no,
                    'price': item.price,
                    'quantity':item.quantity,
                    'quantity_cart':0,
                    'short_description':item.description_short,
                    'long_description':item.description_long,
                    'category':item.category.title,
                    'sub_category':item.subcategory.title,
                    'category_url':item.category.slug,
                    'slug':item.slug,
                    #'brand':item.brand.title,
                    #'brand_url':item.brand.slug
                }
            }
        except:
            response = {
                "data":{}
                    
            }
   
    return JsonResponse(response)

def categories_api(request):
   
    categories = Category.objects.filter(is_active=True)
        #print(categories[1].subcategory_set.all())

    response = {
                'category': list([ {'title':cat.title, 'url':cat.slug, 'sub_categories':list([{'title':sub.title, 'url':sub.slug} for sub in cat.subcategory.all()])} for cat in categories]),
                
                    
    }

    try:
        categories = Category.objects.filter(is_active=True)
        #print(categories[1].subcategory_set.all())

        
    except:
        response = {}
    
    return JsonResponse(response)