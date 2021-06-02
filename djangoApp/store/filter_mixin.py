from django.core.exceptions import ImproperlyConfigured
from django.views.generic import ListView

class ListFilteredMixin(object):
    """
    Mixin that adds support for django-filter
    """

    filter_set = None
    
    def get_filter_set(self):
        if self.filter_set:
            print("filter_set:",self.filter_set)
            return self.filter_set
        else:
            raise ImproperlyConfigured(
                "ListFilterMixin requires either a definition of "
                "'filter_set' or an implementation of 'get_filter()'")

    def get_filter_set_kwargs(self):
        """
        Returns the keyword arguments for instanciating the filterset.
        """
        print("data:", self.request.GET)
        print("qs:", len(self.get_base_queryset()))
        return {
            'data': self.request.GET,
            'queryset': self.get_base_queryset(),
        }

    def get_base_queryset(self):
        """
        We can decided to either alter the queryset before or after applying the
        FilterSet
        """
        return super(ListFilteredMixin, self).get_queryset()

    def get_constructed_filter(self):
        # We need to store the instantiated FilterSet cause we use it in
        # get_queryset and in get_context_data
        if getattr(self, 'constructed_filter', None):
            print("constructed filter:", self.constructed_filter)
            return self.constructed_filter
        else:
            f = self.get_filter_set()(**self.get_filter_set_kwargs())
            self.constructed_filter = f
            print("f:", f)
            return f

    def get_queryset(self):
        print("queryset:", self.get_constructed_filter().qs)
        return self.get_constructed_filter().qs

    def get_context_data(self, **kwargs):
        kwargs.update({'filter': self.get_constructed_filter()})
        print("context data:", super(ListFilteredMixin, self).get_context_data(**kwargs))
        return super(ListFilteredMixin, self).get_context_data(**kwargs)

class ListFilteredView(ListFilteredMixin, ListView):
    """
    A list view that can be filtered by django-filter
    """
