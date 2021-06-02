from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile, RefundItem, Refund, Group ,Customer
from .models import Category, Brand, TaxRate, Shipment, Invoice, InvoiceItem, ShipmentItem, Shipment,ItemSource, SourceInventory, Stock, StoreFront


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'name',
        'street_address',
        'apartment_address',
        'country',
        'state',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(TaxRate)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(ShipmentItem)
admin.site.register(Shipment)
admin.site.register(Refund)
admin.site.register(RefundItem)
admin.site.register(ItemSource)
admin.site.register(SourceInventory)
admin.site.register(Stock)
admin.site.register(StoreFront)
admin.site.register(Group)
admin.site.register(Customer)
