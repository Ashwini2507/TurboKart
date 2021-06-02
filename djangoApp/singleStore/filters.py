import django_filters

from .models import *

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = ['ref_code','status','ordered_date']

