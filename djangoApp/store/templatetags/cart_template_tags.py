from django import template
from store.models import Order, OrderItem
from store.models import StoreFront
from django.shortcuts import get_object_or_404

register = template.Library()


@register.simple_tag(name="cart_item_count")
def cart_item_count(user, *args, **kwargs):
    if user.is_authenticated:
        try:
            current_url = kwargs["url"]
            print(current_url)
            store_url = current_url.split("/")[2]
            if store_url == '':
                store_url = 'default'
            store = StoreFront.objects.get(store_slug = store_url)
            #order = Order.objects.get(user=user, store_front=store, ordered=False)
            order_items = OrderItem.objects.filter(user=user, store_front=store, ordered=False)
            print(order_items)
            total = 0
            for order_item in order_items:
                total = total + order_item.quantity
            return total
        except:
            return 0
    return 0

@register.simple_tag(name="store_url")
def store_url(user, *args, **kwargs):
    if user.is_authenticated:
        print(kwargs)
        current_url = kwargs["url"]
        print(current_url)
        store_url = current_url.split("/")[2]
        print (store_url)
        if store_url == '':
            store_url = 'default'
        #store = StoreFront.objects.get(store_slug = store_url)
        #print (store)
        #if qs.exists():
        #    return 
        return store_url
