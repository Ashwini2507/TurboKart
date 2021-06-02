from django import template
from singleStore.models import OrderItem
from django.shortcuts import get_object_or_404

register = template.Library()


@register.filter
def cart_count(user):
    if user.is_authenticated:
        try:
            print(user)
            order_items = OrderItem.objects.filter(user=user, ordered=False)
            print("order-items:",order_items)
            total = 0
            for order_item in order_items:
                total = total + order_item.quantity
            return total
        except:
            return 0
    return 0
