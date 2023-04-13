from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('efectivo', 'Efectivo'),
    ('transferencia', 'Transferencia'),
    ('debito', 'Debito')
)

ADDRESS_CHOICES = (
    ('recoger', 'Recoger'),
    ('entrega', 'Entrega'),
)

class CheckoutForm(forms.Form):
    def clean(self):
        cleaned_data = super(CheckoutForm, self).clean()
        #if self.instance.field:
            #raise Exception
        return cleaned_data

    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'pedro edificio santa isabel 754',
        'class': 'form-control mr-sm-2',
        'id': 'address-search',
        'list':'list-timezone',
        'onkeyup':'myFunction()',
        'type':'search'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite',
        'class': 'form-control'
    }))
    apartment_number = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': '1205',
        'class': 'form-control',
        'id': 'address_number'
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '+56 9 4534 567',
    }))
    #same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.Select, choices=PAYMENT_CHOICES)

    payment_shipping = forms.ChoiceField(
        widget=forms.Select, choices=ADDRESS_CHOICES)

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()
