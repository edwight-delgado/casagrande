from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
#from pictures.models import PictureField
from django.db import models
from django.db.models import signals
from datetime import date

def update_order_items(sender, instance, **kwargs):
        #si entra al if es que su orden ha sido recivida
        if instance.received == True:
            for orderitem in instance.items.all():
                if orderitem.quantity <= orderitem.item.quantity and orderitem.item.quantity > 0 and orderitem.item.is_active==True:
                    orderitem.item.quantity = abs(orderitem.quantity - orderitem.item.quantity )
                    if orderitem.item.quantity < 1:
                        orderitem.item.is_active = False
                        orderitem.item.label = 'agotado'
                    orderitem.item.save()
                    print("Update is called")



# Create your models here.

LABEL_CHOICES = (
    ('venta', 'venta'),
    ('nuevo', 'nuevo'),
    ('agotado', 'agotado'),
)

UNIT_CHOICES = (
    ('kilo', 'kilo'),
    ('gramos', 'gramos'),
    ('onza', 'onza'),
    ('ml', 'ml'),
    ('litros', 'litros'),
    ('centimetros', 'centimetros'),
    ('metros', 'metros'),
    ('unidad', 'unidad'),
)

ADDRESS_CHOICES = (
    ('recoger', 'Recoger'),
    ('entrega', 'Entrega'),
)

METHODS_PAYMENT_CHOICES = (
    ('transferencia', 'Transferencia'),
    ('efectivo', 'Efectivo'),
    ('debito', 'Debito'),
)


class Slide(models.Model):
    caption1 = models.CharField(max_length=100)
    caption2 = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    image = models.ImageField(help_text="Size: 960x125")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.caption1, self.caption2)


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("shopping:category", kwargs={
            'slug': self.slug
        })

class SubCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategory')
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("shopping:subcategory", kwargs={
            'slug': self.slug
        })

class Brand(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("shopping:marca", kwargs={
            'slug': self.slug
        })



class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    quantity = models.IntegerField(default=1)
    discount_price = models.FloatField(blank=True, null=True)
    peso = models.FloatField(blank=True, null=True)
    unit = models.CharField(blank=True, null=True, choices=UNIT_CHOICES, max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=50, default='venta')
    slug = models.SlugField()
    stock_no = models.CharField(max_length=10, null=True)
    description_short = models.CharField(max_length=50)
    description_long = models.TextField()
    image = models.ImageField(upload_to="images", width_field='item_img_height', height_field='item_img_width')
    item_img_height = models.IntegerField(default=190)
    item_img_width = models.IntegerField(default=190)
    #image = ImageWithThumbsField(upload_to='images', sizes=((190,190),(525,390)))
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def expiration(self):
        if self.expiration_date:
            return date.today() > self.expiration_date

    def get_absolute_url(self):
        return reverse("shopping:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("shopping:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("shopping:remove-from-cart", kwargs={
            'slug': self.slug
        })


class Img(models.Model):
    title = models.CharField(max_length=100)
    #picture = PictureField(upload_to="images")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.title

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'BillingAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'BillingAddress', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    note = models.CharField(max_length=150, blank=True, null=True)
    seller_id = models.ImageField()
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a BillingAddress
    (Failed Checkout)
    3. Payment
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class BillingAddress(models.Model):
    tag = models.CharField(max_length=100, default='domicilio')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address_type = models.CharField(max_length=50, choices=ADDRESS_CHOICES)
    payment_method = models.CharField(max_length=50, choices=METHODS_PAYMENT_CHOICES)
    default = models.BooleanField(default=False)
    latitude =  models.FloatField(blank=True, null=True)
    longitude =  models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'BillingAddresses'


class Payment(models.Model):
    #stripe_charge_id = models.CharField(max_length=50)
    methods = models.CharField(choices=METHODS_PAYMENT_CHOICES, max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}, {self.amount}, {self.methods}' 


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


signals.post_save.connect(receiver=update_order_items, sender=Order)
