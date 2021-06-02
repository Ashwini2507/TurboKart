from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from localflavor.in_.forms import INStateSelect
from django.contrib.auth.models import User

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)

ITEM_STATUS_CHOICES = (
    ('Enabled','Enabled'),
    ('Disabled','Disabled'),
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

INVOICE_STATUS_CHOICES = (
    ('Not Invoiced','Not Invoiced'),
    ('Partial Invoice','Partial Invoice'),
    ('Invoice Complete','Invoice Complete'),
)

SHIPMENT_STATUS_CHOICES = (
    ('No Shipments','No Shipments'),
    ('Partial Shipment','Partial Shipment'),
    ('Shipment Complete', 'Shipment Complete'),
)

REFUND_REQUEST_CHOICES = (
    ('No Refunds Requested','No Refunds Requested'),
    ('Partial Refunds Requested','Partial Refunds Requested'),
    ('Full Refund Requested', 'Full Refunds Requested'),
)

REFUND_STATUS_CHOICES = (
    ('No Refunds Initiated','No Refunds Initiated'),
    ('Partial Refunds Initiated','Partial Refunds Initiated'),
    ('Full Refund Initiated', 'Full Refunds Initiated'),
)

REPLACEMENT_REQUEST_CHOICES = (
    ('No Replacements Requested','No Replacements Requested'),
    ('Partial Replacements Requested','Partial Replacements Requested'),
    ('Full Replacements Requested', 'Full Replacements Requested'),
)

REPLACEMENT_STATUS_CHOICES = (
    ('No Replacements Initiated','No Replacement Initiated'),
    ('Partial Replacement Initiated','Partial Replacement Initiated'),
    ('Full Replacement Initiated', 'Full Replacement Initiated'),
)

ORDER_STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Processing', 'Processing'),
    ('Shipped', 'Shipped'),
    ('Delivered','Delivered'),
    ('Complete','Complete'),
    ('Cancelled','Cancelled'),
    ('On Hold','On Hold'),
    ('Dispute Raised','Dispute Raised'),
    ('Resolution in Process','Resolution in Process'),
    ('Dispute Resolved','Dispute Resolved'),
)

STATE_CHOICES = (
                 ('Karnataka', 'Karnataka'), ('Andhra Pradesh', 'Andhra Pradesh'), ('Kerala', 'Kerala'), ('Tamil Nadu', 'Tamil Nadu'), 
                 ('Maharashtra', 'Maharashtra'), ('Uttar Pradesh', 'Uttar Pradesh'), ('Goa', 'Goa'), ('Gujarat', 'Gujarat'), 
                 ('Rajasthan', 'Rajasthan'), ('Himachal Pradesh', 'Himachal Pradesh'), ('Jammu and Kashmir', 'Jammu and Kashmir'), 
                 ('Telangana', 'Telangana'), ('Arunachal Pradesh', 'Arunachal Pradesh'), ('Assam', 'Assam'), 
                 ('Bihar', 'Bihar'), ('CG', 'Chattisgarh'), ('Haryana', 'Haryana'), ('Jharkhand', 'Jharkhand'), 
                 ('Madhya Pradesh', 'Madhya Pradesh'), ('Manipur', 'Manipur'), ('Meghalaya', 'Meghalaya'), ('Mizoram', 'Mizoram'), 
                 ('Nagaland', 'Nagaland'), ('Orissa', 'Orissa'), ('Punjab', 'Punjab'), ('Sikkim', 'Sikkim'), 
                 ('Tripura', 'Tripura'), ('Uttarakhand', 'Uttarakhand'), ('West Bengal', 'West Bengal'), 
                 ('Andaman and Nicobar', 'Andaman and Nicobar'), ('Chandigarh', 'Chandigarh'), ('Dadra and Nagar Haveli', 'Dadra and Nagar Haveli'), 
                 ('Daman and Diu', 'Daman and Diu'), ('Delhi', 'Delhi'), ('Lakshadweep', 'Lakshadweep'), ('Pondicherry', 'Pondicherry')
                )

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    priority = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,blank=True, null=True ,related_name='children')

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        unique_together = ('slug', 'parent',)

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def get_absolute_url(self):
        return reverse('store:products_by_category',kwargs={
            'slug': self.slug
        })

class Brand(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    priority = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'brand'
        verbose_name_plural = 'brands'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:products_by_brand',kwargs={
            'slug': self.slug
        })

class TaxRate(models.Model):
    name = models.CharField(max_length=100)
    rate = models.FloatField()
    def __str__(self):
        return self.name


class Item(models.Model):
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=ITEM_STATUS_CHOICES, default='Enabled')
    SKU = models.CharField(max_length=20,blank=True, null=True)
    price = models.FloatField()
    HSN = models.CharField(max_length=20,blank=True, null=True)
    Tax_Rate = models.ForeignKey(TaxRate,
                             on_delete=models.CASCADE,blank=True, null=True)
    category = models.ManyToManyField(Category)
    brand = models.ForeignKey(Brand,
                             on_delete=models.CASCADE, blank=True, null=True)
    discount_price = models.FloatField(blank=True, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, blank=True, null=True)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("store:product", kwargs={
            'slug': self.slug
        })
    def get_add_to_cart_url(self):
        return reverse("store:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("store:remove-from-cart", kwargs={
            'slug': self.slug
        })

class ItemSource(models.Model):
    source_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.source_name}"


class SourceInventory(models.Model):
    source_name = models.ForeignKey(ItemSource,on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    available_quantity = models.IntegerField(default=0)
    min_stock_quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.source_name} - {self.item} - Available Quantity {self.available_quantity} Min Stock Quantity {self.min_stock_quantity}"

class Stock(models.Model):
    stock_name = models.CharField(max_length=100)
    source_inventory = models.ManyToManyField(SourceInventory)

    def __str__(self):
        return f"{self.stock_name}"

class StoreFront(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address_line1 = models.CharField(max_length=100, blank=True, null =True)
    address_line2 = models.CharField(max_length=100, blank=True, null =True)
    country = CountryField(multiple=False, blank=True, null =True)
    state = models.CharField(choices=STATE_CHOICES, max_length=50, blank=True, null =True)
    pin = models.CharField(max_length=100, blank=True, null =True)
    store_slug = models.SlugField(unique=True)
    item_list=models.ForeignKey(Stock,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    store_front = models.ForeignKey(StoreFront, on_delete = models.SET_NULL, null= True, default=1)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    invoiced_quantity = models.IntegerField(default=0)
    shipped_quantity = models.IntegerField(default=0)
    refund_quantity = models.IntegerField(default=0)
    refund_request_quantity = models.IntegerField(default=0)
    refund_reason = models.CharField(max_length=100,blank=True, null=True)
    replacement_quantity = models.IntegerField(default=0)
    replacement_request_quantity = models.IntegerField(default=0)
    replacement_reason = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} of {self.item.title} by {self.user} invoiced {self.invoiced_quantity} shipped {self.shipped_quantity} refund requested {self.refund_request_quantity}  refund initiated {self.refund_quantity}"

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
    def get_tax_amount(self):
        return self.get_final_price() * self.item.Tax_Rate.rate/100

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    store_front = models.ForeignKey(StoreFront, on_delete = models.SET_NULL, null= True, default=1)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    #items = models.ForeignKey(OrderItem, on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateTimeField(blank=True,null=True)
    ordered_date = models.DateTimeField(blank=True,null=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=50, default='Pending')
    invoice_status = models.CharField(choices=INVOICE_STATUS_CHOICES, max_length=50, default='Not Invoiced')
    shipping_status = models.CharField(choices=SHIPMENT_STATUS_CHOICES, max_length=50, default='No Shipments')
    refund_request_status = models.CharField(choices=REFUND_REQUEST_CHOICES, max_length=50, default='No Refunds Requested')
    replacement_request_status = models.CharField(choices=REPLACEMENT_REQUEST_CHOICES, max_length=50, default='No Replacements Requested')
    refund_status = models.CharField(choices=REFUND_STATUS_CHOICES, max_length=50, default='No Refunds Initiated')
    replacement_status = models.CharField(choices=REPLACEMENT_STATUS_CHOICES, max_length=50, default='No Replacements Initiated')
    dispute_raised = models.BooleanField(default=False)
    dispute_raised_date = models.DateTimeField(blank=True,null=True)
    refund_requested_date = models.DateTimeField(blank=True,null=True)
    replacement_requested_date = models.DateTimeField(blank=True,null=True)
    refund_processed_date = models.DateTimeField(blank=True,null=True)
    replacement_processed_date = models.DateTimeField(blank=True,null=True)
    failed_payment = models.BooleanField(default=False)

    shipping_id = models.CharField(max_length=20, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        if self.ref_code == '':
                return self.user.username
        else:
                return f"{self.ref_code} ID {self.id}"

    def get_cart_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_total_tax(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_tax_amount()
        return total

    def get_total(self):
        return self.get_cart_total()+self.get_total_tax() 

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100,blank=True)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    state = models.CharField(choices=STATE_CHOICES, max_length=50, blank=True)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    payment_mode_name = models.CharField(max_length = 50, default='Stripe')
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code

class Group(models.Model):
    group_name = models.CharField(max_length=100, unique = True)

    def __str__(self):
        return self.group_name

class Customer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    group = models.ManyToManyField(Group)
    addresses = models.ManyToManyField(Address)
    payments = models.ManyToManyField(Payment)
    orders = models.ManyToManyField(Order)

    def __str__(self):
        return self.user.username


class InvoiceItem(models.Model):
    ref_id = models.CharField(max_length=20, blank=True, null=True)
    order_id = models.CharField(max_length=20, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    invoiced = models.BooleanField(default=False)

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
    def get_tax_amount(self):
        return self.get_final_price() * self.item.Tax_Rate.rate/100


class Invoice(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,blank=True, null=True)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(InvoiceItem)
    invoice_date = models.DateTimeField(blank=True, null=True)
    invoiced = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'invoice'
        verbose_name_plural = 'invoices'

    def __str__(self):
        return self.ref_code

    def get_invoice_total(self):
        total = 0
        for invoice_item in self.items.all():
            total += invoice_item.get_final_price()
        return total

    def get_total_tax(self):
        total = 0
        for invoice_item in self.items.all():
            total += invoice_item.get_tax_amount()
        return total

    def get_total(self):
        return self.get_invoice_total()+self.get_total_tax()

class ShipmentItem(models.Model):
    ref_id = models.CharField(max_length=20, blank=True, null=True)
    order_id = models.CharField(max_length=20, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    shipped = models.BooleanField(default=False)

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
    def get_tax_amount(self):
        return self.get_final_price() * self.item.Tax_Rate.rate/100


class Shipment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,blank=True, null=True)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(ShipmentItem)
    shipment_date = models.DateTimeField(blank=True, null=True)
    shipped = models.BooleanField(default=False)
    carrier = models.CharField(max_length=20, blank=True, null=True)
    shipment_id =  models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'shipment'
        verbose_name_plural = 'shipments'

    def __str__(self):
        return self.ref_code

    def get_shipment_total(self):
        total = 0
        for shipment_item in self.items.all():
            total += shipment_item.get_final_price()
        return total

    def get_total_tax(self):
        total = 0
        for shipment_item in self.items.all():
            total += shipment_item.get_tax_amount()
        return total

    def get_total(self):
        return self.get_shipment_total()+self.get_total_tax()


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)

class RefundItem(models.Model):
    ref_id = models.CharField(max_length=20, blank=True, null=True)
    order_id = models.CharField(max_length=20, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    refunded = models.BooleanField(default=False)

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
    def get_tax_amount(self):
        return self.get_final_price() * self.item.Tax_Rate.rate/100

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,blank=True, null=True)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(RefundItem)
    refund_date = models.DateTimeField(blank=True, null=True)
    refunded = models.BooleanField(default=False)
    refund_method = models.CharField(max_length=20, blank=True, null=True)
    refund_id =  models.CharField(max_length=20, blank=True, null=True)


    class Meta:
        verbose_name = 'refund'
        verbose_name_plural = 'refunds'

    def __str__(self):
        return self.ref_code

    def get_refund_total(self):
        total = 0
        for refund_item in self.items.all():
            total += refund_item.get_final_price()
        return total

    def get_total_tax(self):
        total = 0
        for refund_item in self.items.all():
            total += refund_item.get_tax_amount()
        return total

    def get_total(self):
        return self.get_refund_total()+self.get_total_tax()

