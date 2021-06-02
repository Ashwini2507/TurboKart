from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from localflavor.in_.forms import *
from django.forms import ModelForm
from .models import Category
from .models import Order, OrderItem, InvoiceItem, Item

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

STATE_CHOICES = (
                 ('Karnataka', 'Karnataka'), ('Andhra Pradesh', 'Andhra Pradesh'), ('Kerala', 'Kerala'), ('Tamil Nadu', 'Tamil Nadu'),
                 ('Maharashtra', 'Maharashtra'), ('Uttar Pradesh', 'Uttar Pradesh'), ('Goa', 'Goa'), ('Gujarat', 'Gujarat'),
                 ('Rajasthan', 'Rajasthan'), ('Himachal Pradesh', 'Himachal Pradesh'), ('Jammu and Kashmir', 'Jammu and Kashmir'),
                 ('Telangana', 'Telangana'), ('Arunachal Pradesh', 'Arunachal Pradesh'), ('Assam', 'Assam'), ('Select State', 'Select State'),
                 ('Bihar', 'Bihar'), ('CG', 'Chattisgarh'), ('Haryana', 'Haryana'), ('Jharkhand', 'Jharkhand'),
                 ('Madhya Pradesh', 'Madhya Pradesh'), ('Manipur', 'Manipur'), ('Meghalaya', 'Meghalaya'), ('Mizoram', 'Mizoram'),
                 ('Nagaland', 'Nagaland'), ('Orissa', 'Orissa'), ('Punjab', 'Punjab'), ('Sikkim', 'Sikkim'),
                 ('Tripura', 'Tripura'), ('Uttarakhand', 'Uttarakhand'), ('West Bengal', 'West Bengal'),
                 ('Andaman and Nicobar', 'Andaman and Nicobar'), ('Chandigarh', 'Chandigarh'), ('Dadra and Nagar Haveli', 'Dadra and Nagar Haveli'),
                 ('Daman and Diu', 'Daman and Diu'), ('Delhi', 'Delhi'), ('Lakshadweep', 'Lakshadweep'), ('Pondicherry', 'Pondicherry')
                )


class CheckoutForm(forms.Form):
    shipping_address_name = forms.CharField(required=False)
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    shipping_state = forms.ChoiceField(
        required=False,
        choices = STATE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'custom-select d-block w-100',
        }))
    shipping_zip = forms.CharField(required=False)

    billing_address_name = forms.CharField(required=False)
    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    billing_state = forms.ChoiceField(
        required=False,
        choices = STATE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'custom-select d-block w-100',
        }))
    billing_zip = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    refund_quantity = forms.IntegerField(required=False)
    refund_method = forms.CharField(required=True)
    refund_id = forms.CharField(required=True)

class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']

class InvoiceForm(forms.Form):
    invoice_quantity = forms.IntegerField(required=False)

class ShipmentForm(forms.Form):
    shipment_quantity = forms.IntegerField(required=False)
    shipment_carrier = forms.CharField(required=True)
    shipment_id = forms.CharField(required=True)

class RefundRequestForm(forms.Form):
    refundQuantity = forms.IntegerField(required=False)
    refundReason = forms.CharField(required=True)

class ItemForm(ModelForm):
    category = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=Category.objects.all())
    class Meta:
        model = Item
        fields = '__all__'

class CreateOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

