from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Item, OrderItem, Order, BillingAddress, Payment, Coupon, Refund, Category

@receiver(pre_save, sender=OrderItem)
def check_product_quantity(sender, instance, **kwargs):
    if instance.item.quantity < instance.quantity:
        raise ValidationError("No hay suficiente stock para este producto.")
    