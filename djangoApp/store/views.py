from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, OrderForm, InvoiceForm, ShipmentForm, RefundForm, \
    RefundRequestForm, ItemForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Category, Brand, InvoiceItem, \
    Invoice, ShipmentItem, Shipment, RefundItem, Refund, ItemSource, Stock, StoreFront, SourceInventory
from django.contrib.auth.models import User, Group
from django.urls import reverse
from users.models import Profile
from .filter_mixin import ListFilteredMixin
from .filters import OrderFilter

import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "store/products.html", context)


class ViewCustomers(PermissionRequiredMixin, ListView):
    model = Profile
    permission_required = 'auth.view_user'
    template_name = 'store/all_customers.html'
    paginate_by = 10
    context_object_name = 'profiles'

    def get_queryset(self):
        users = User.objects.filter(groups__name="customer")
        return Profile.objects.filter(user__id__in=users)


class CategoryView(ListView):
    model = Item
    template_name = 'store/by_category.html'
    paginate_by = 2

    def get_queryset(self):
        category_name = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return Item.objects.filter(category=category_name)


class BrandView(ListView):
    model = Item
    template_name = 'store/by_brand.html'
    paginate_by = 2

    def get_queryset(self):
        brand_name = get_object_or_404(Brand, slug=self.kwargs.get('slug'))
        return Item.objects.filter(brand=brand_name)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            store = get_object_or_404(StoreFront, store_slug=self.kwargs.get('store_slug'))
            order = Order.objects.get(user=self.request.user, store_front=store, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "store/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("store:store-home")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            store = get_object_or_404(StoreFront, store_slug=self.kwargs.get('store_slug'))
            order = Order.objects.get(user=self.request.user, store_front=store, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('store:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address_name = form.cleaned_data.get(
                        'shipping_address_name')
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_state = form.cleaned_data.get(
                        'shipping_state')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            name=shipping_address_name,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            state=shipping_state,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('store:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address_name = form.cleaned_data.get(
                        'billing_address_name')
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_state = form.cleaned_data.get(
                        'billing_state')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            name=billing_address_name,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            state=billing_state,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect(
                        reverse("store:payment", kwargs={"store_slug": store.store_slug, "payment_option": "stripe"}))
                elif payment_option == 'P':
                    return redirect(
                        reverse("store:payment", kwargs={"store_slug": store.store_slug, "payment_option": "paypal"}))
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('store:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("store:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        store = get_object_or_404(StoreFront, store_slug=self.kwargs.get('store_slug'))
        order = Order.objects.get(user=self.request.user, store_front=store, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "store/payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("store:checkout")

    def post(self, *args, **kwargs):
        store = get_object_or_404(StoreFront, store_slug=self.kwargs.get('store_slug'))
        order = Order.objects.get(user=self.request.user, store_front=store, ordered=False)
        for order_item in order.items.all():
            stock_item = store.item_list.source_inventory.get(item=order_item.item)
            request_quantity = order_item.quantity
            available_quantity = stock_item.available_quantity
            min_stock_quantity = stock_item.min_stock_quantity
            if request_quantity > available_quantity - min_stock_quantity:
                messages.warning(self.request, "Requested quantity of items no longer available.")
                return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))

        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            # token = form.cleaned_data.get('stripeToken')
            token = 'tok_visa'
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="inr",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="inr",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.payment_method_name = "Stripe"
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.ordered_date = timezone.now()
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()
                for order_item in order.items.all():
                    print(order_item)
                    stock_item = store.item_list.source_inventory.get(item=order_item.item)
                    print(stock_item)
                    request_quantity = order_item.quantity
                    print(request_quantity)
                    print(stock_item.available_quantity)
                    stock_item.available_quantity = stock_item.available_quantity - request_quantity
                    print(stock_item.available_quantity)
                    stock_item.save()
                messages.success(self.request, "Your order was successful!")
                return redirect(reverse("store:store-home", kwargs={"store_slug": store.store_slug}))

            except stripe.error.CardError as e:
                order.failed_payment = True
                order.save()
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/payment/stripe")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                order.failed_payment = True
                order.save()
                messages.warning(self.request, "Rate limit error")
                return redirect("/payment/stripe")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                order.failed_payment = True
                order.save()
                messages.warning(self.request, "Invalid parameters")
                return redirect("/payment/stripe")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                order.failed_payment = True
                order.save()
                messages.warning(self.request, "Not authenticated")
                return redirect("/payment/stripe")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                order.failed_payment = True
                order.save()
                messages.warning(self.request, "Network error")
                return redirect("/payment/stripe")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                order.failed_payment = True
                order.save()
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/payment/stripe")

            except Exception as e:
                # send an email to ourselves
                order.failed_payment = True
                order.save()
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/payment/stripe")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class DefaultHomeView(View):
    def get(self, *args, **kwargs):
        store = StoreFront.objects.get(store_slug='default')
        print(store)
        context = {
            'store': store
        }
        return render(self.request, 'store/home.html', context)


class HomeView(View):
    def get(self, *args, **kwargs):
        try:
            store = get_object_or_404(StoreFront, store_slug=self.kwargs.get('store_slug'))
            print(store)
            context = {
                'store': store
            }
            return render(self.request, 'store/home.html', context)

        except ObjectDoesNotExist:
            messages.warning(self.request, "Please select a valid store")
            return redirect("/")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            store = get_object_or_404(StoreFront, store_slug=self.kwargs.get('store_slug'))
            order = Order.objects.get(user=self.request.user, store_front=store, ordered=False)
            # url_path = self.request.path
            # print (url_path)
            # rel_url = url_path.split("/")[2]
            # print (rel_url)
            context = {
                'order': order,
                'store': store
            }
            return render(self.request, 'store/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(View):

    def get(self, *args, **kwargs):
        try:
            store = get_object_or_404(StoreFront, store_slug=self.kwargs.get('store_slug'))
            item = get_object_or_404(Item, slug=self.kwargs.get('slug'))
            # url_path = self.request.path
            # print (url_path)
            # rel_url = url_path.split("/")[2]
            # print (rel_url)
            context = {
                'object': item,
                'store': store
            }
            return render(self.request, 'store/product-page.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "This item does not exist")
            return redirect("/")


#    model = Item
#    template_name = "store/product.html"

# def get_object(self, **kwargs):
#    store = StoreFront.objects.get(store_slug=self.kwargs['store_slug'])
#    return store

# def get_context_data(self, **kwargs):
#    context = super(ItemDetailView, self).get_context_data(**kwargs)
#    context['item'] = Item.objects.get(slug=self.kwargs['slug'])
#    return context

@login_required
def add_to_cart(request, store_slug, slug):
    item = get_object_or_404(Item, slug=slug)
    # store_url = request.path.split("/")[2]
    # print (store_url)
    # store = StoreFront.objects.filter(store_url)
    # print (store)
    store = get_object_or_404(StoreFront, store_slug=store_slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        store_front=store,
        ordered=False
    )
    stock_item = store.item_list.source_inventory.get(item=item)
    available_quantity = stock_item.available_quantity
    min_stock_quantity = stock_item.min_stock_quantity

    order_qs = Order.objects.filter(user=request.user, store_front=store, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            available_quantity = available_quantity - order_item.quantity
            if available_quantity > min_stock_quantity:
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))
            else:
                messages.info(request, "Requested quantity of item not available.")
                return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))
    else:
        start_date = timezone.now()
        order = Order.objects.create(
            user=request.user, store_front=store, start_date=start_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))


@login_required
def remove_from_cart(request, slug, store_slug):
    item = get_object_or_404(Item, slug=slug)
    store = get_object_or_404(StoreFront, store_slug=store_slug)
    order_qs = Order.objects.filter(
        user=request.user,
        store_front=store,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))
        else:
            messages.info(request, "This item was not in your cart")
            return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))
    else:
        messages.info(request, "You do not have an active order")
        return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))


@login_required
def remove_single_item_from_cart(request, store_slug, slug):
    item = get_object_or_404(Item, slug=slug)
    store = get_object_or_404(StoreFront, store_slug=store_slug)
    order_qs = Order.objects.filter(
        user=request.user,
        store_front=store,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))
        else:
            messages.info(request, "This item was not in your cart")
            return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))
    else:
        messages.info(request, "You do not have an active order")
        return redirect(reverse("store:order-summary", kwargs={"store_slug": store.store_slug}))


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        code = 'Invalid Code'
        coupon = Coupon.objects.get(code=code)
        return coupon


class AddCouponView(View):
    def post(self, *args, **kwargs):
        store = get_object_or_404(StoreFront, store_slug=self.kwargs.get('store_slug'))
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, store_front=store, ordered=False)
                order.coupon = get_coupon(self.request, code)
                if order.coupon.code != 'Invalid Code':
                    order.save()
                    messages.success(self.request, "Successfully added coupon")
                    return redirect(reverse("store:checkout", kwargs={"store_slug": store.store_slug}))
                else:
                    order.coupon = get_coupon(self.request, code)
                    messages.info(self.request, "This coupon does not exist")
                    return redirect(reverse("store:checkout", kwargs={"store_slug": store.store_slug}))

            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect(reverse("store:checkout", kwargs={"store_slug": store.store_slug}))


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "store/request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("store:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("store:request-refund")


# class DashboardView(LoginRequiredMixin, View):
#    def get(self, *args, **kwargs):
#        try:
#            orders = Order.objects.get(user=self.request.user, ordered=True)
#            context = {
#                'object': orders
#            }
#            return render(self.request, 'store/dashboard.html', context)
#        except ObjectDoesNotExist:
#            messages.warning(self.request, "You do not have an active order")
#            return redirect("/")

class UserOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'store/user_orders.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        # user_name = get_object_or_404(User, username=self.kwargs.get('username'))
        return Order.objects.filter(user=self.request.user, ordered=True).order_by('-ordered_date')


class OrderDashboardView(PermissionRequiredMixin, ListView):
    model = Order
    # filter_set = OrderFilter
    permission_required = 'store.view_order'
    template_name = 'store/sales_orders.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        return Order.objects.filter(ordered=True).order_by('-ordered_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = OrderFilter(self.request.GET, queryset=self.get_queryset())
        return context


@permission_required('store.view_order')
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':

        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'order': order, 'form': form}
    return render(request, 'store/order_form.html', context)


@permission_required('store.view_invoice')
def viewInvoices(request, ref_code):
    order = Order.objects.get(ref_code=ref_code)
    invoices = Invoice.objects.filter(order=order)
    context = {'invoices': invoices}
    return render(request, 'store/sales_invoices.html', context)


@permission_required('store.view_shipment')
def viewShipments(request, ref_code):
    order = Order.objects.get(ref_code=ref_code)
    shipments = Shipment.objects.filter(order=order)
    context = {'shipments': shipments}
    return render(request, 'store/sales_shipments.html', context)


@permission_required('store.view_refund')
def viewRefunds(request, ref_code):
    order = Order.objects.get(ref_code=ref_code)
    refunds = Refund.objects.filter(order=order)
    context = {'refunds': refunds}
    return render(request, 'store/sales_refunds.html', context)


def viewInvoicesCustomers(request, ref_code):
    order = Order.objects.get(ref_code=ref_code)
    invoices = Invoice.objects.filter(order=order)
    context = {'invoices': invoices}
    return render(request, 'store/customer_invoices.html', context)


def viewShipmentsCustomers(request, ref_code):
    order = Order.objects.get(ref_code=ref_code)
    shipments = Shipment.objects.filter(order=order)
    context = {'shipments': shipments}
    return render(request, 'store/customer_shipments.html', context)


def viewRefundsCustomers(request, ref_code):
    order = Order.objects.get(ref_code=ref_code)
    refunds = Refund.objects.filter(order=order)
    context = {'refunds': refunds}
    return render(request, 'store/customer_refunds.html', context)


@permission_required('store.add_invoice', raise_exception=True)
def invoiceOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = InvoiceForm(request.POST)
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            data = request.POST.dict()
            data.pop('csrfmiddlewaretoken', None)

            for i in data.items():
                print(i)
                for order_item in order.items.all():
                    if str((i[0].split("_")[1])) == str(order_item.item.id):
                        if str(i[1]) == '':
                            entry = 0
                        else:
                            entry = i[1]
                        if order_item.invoiced_quantity + int(entry) > order_item.quantity:
                            messages.info(request, "Invoice quantity can't be greater than order quantity")
                            return redirect("store:generate_invoice", pk=order.id)

            for order_item in order.items.all():
                ref = str(order.id) + "_" + str(order_item.item.id)
                # if not InvoiceItem.objects.filter(ref_id = ref).exists():
                invoice_item, created = InvoiceItem.objects.get_or_create(
                    item=order_item.item,
                    order_id=order.id,
                    ref_id=str(order.id) + "_" + str(order_item.item.id),
                    invoiced=False,
                    quantity=0
                )
                invoice_item.save()

            for i in data.items():
                ref = str(order.id) + "_" + str(i[0].split("_")[1])
                # if InvoiceItem.objects.get(ref_id = ref).exists():
                if str(i[1]) == '':
                    entry = 0
                else:
                    entry = i[1]
                invoice_item_qs = InvoiceItem.objects.filter(ref_id=ref, invoiced=False)
                if invoice_item_qs.exists() and int(entry) > 0:
                    invoice_item = invoice_item_qs[0]
                    invoice_item.quantity = int(entry)
                    invoice_item.save()
                    for order_item in order.items.all():
                        if str((i[0].split("_")[1])) == str(order_item.item.id):
                            order_item.invoiced_quantity = order_item.invoiced_quantity + int(entry)
                            order_item.save()

            invoice_item_list = InvoiceItem.objects.filter(order_id=order.id, invoiced=False)
            for invoice_item in invoice_item_list:
                if invoice_item.quantity == 0:
                    invoice_item.delete()

            invoice_item_list = InvoiceItem.objects.filter(order_id=order.id, invoiced=False)
            invoice, created = Invoice.objects.get_or_create(
                order=order,
                ref_code=create_ref_code(),
                invoice_date=timezone.now()
            )
            invoice.save()
            print(invoice.ref_code)
            invoice_qs = Invoice.objects.filter(order=order, invoiced=False)
            invoice = invoice_qs[0]
            for invoice_item in invoice_item_list:
                invoice.items.add(invoice_item)
                invoice.save()
                invoice_item.invoiced = True
                invoice_item.save()
            if invoice.items.all().exists():
                invoice.invoiced = True
                invoice.save()

                order.status = 'Processing'
                order.save()

                order_invoices = Invoice.objects.filter(order=order)
                total_invoice_amount = 0
                for invoice in order_invoices:
                    total_invoice_amount = total_invoice_amount + invoice.get_total()
                    print(total_invoice_amount)
                if total_invoice_amount == order.get_total():
                    order.invoice_status = 'Invoice Complete'
                    order.save()
                else:
                    order.invoice_status = 'Partial Invoice'
                    order.save()

            else:
                invoice.delete()
            print(invoice.ref_code)
            return redirect('store/sales_orders')

        else:
            print(forms.errors)
    context = {'order': order, 'form': form}
    return render(request, 'store/generate_invoice.html', context)


class InvoiceDashboardView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'store/sales_invoices.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        # user_name = get_object_or_404(User, username=self.kwargs.get('username'))
        return Invoice.objects.filter(invoiced=True).order_by('-invoice_date')


def viewInvoice(request, pk):
    invoice = Invoice.objects.get(id=pk)
    context = {'invoice': invoice}
    return render(request, 'store/view_invoice.html', context)


def customerViewInvoice(request, ref_code):
    invoice = Invoice.objects.get(ref_code=ref_code)
    context = {'invoice': invoice}
    return render(request, 'store/customer_view_invoice.html', context)


def ShipOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = ShipmentForm(request.POST)
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            data = request.POST.dict()
            data.pop('csrfmiddlewaretoken', None)

            for i in data.items():
                print(i)
                for order_item in order.items.all():
                    if str((i[0].split("_")[1])) == str(order_item.item.id):
                        if str(i[1]) == '':
                            entry = 0
                        else:
                            entry = i[1]
                        if order_item.shipped_quantity + int(entry) > order_item.invoiced_quantity:
                            messages.warning(request, "Shipment quantity can't be greater than invoice quantity")
                            return redirect("store:generate_shipment", pk=order.id)

            for order_item in order.items.all():
                ref = str(order.id) + "_" + str(order_item.item.id)
                # if not InvoiceItem.objects.filter(ref_id = ref).exists():
                shipment_item, created = ShipmentItem.objects.get_or_create(
                    item=order_item.item,
                    order_id=order.id,
                    ref_id=str(order.id) + "_" + str(order_item.item.id),
                    shipped=False,
                    quantity=0
                )
                shipment_item.save()

            for i in data.items():
                if str(i[0].split("_")[0]) == 'shipment-quantity':
                    ref = str(order.id) + "_" + str(i[0].split("_")[1])
                    print(ref)
                    # if ShipmentItem.objects.get(ref_id = ref).exists():
                    if str(i[1]) == '':
                        entry = 0
                    else:
                        entry = i[1]

                    print(entry)
                shipment_item_qs = ShipmentItem.objects.filter(ref_id=ref, shipped=False)
                if shipment_item_qs.exists() and int(entry) > 0:
                    shipment_item = shipment_item_qs[0]
                    shipment_item.quantity = int(entry)
                    shipment_item.save()
                    for order_item in order.items.all():
                        if str((i[0].split("_")[1])) == str(order_item.item.id):
                            order_item.shipped_quantity = order_item.shipped_quantity + int(entry)
                            order_item.save()

            shipment_item_list = ShipmentItem.objects.filter(order_id=order.id, shipped=False)
            for shipment_item in shipment_item_list:
                if shipment_item.quantity == 0:
                    shipment_item.delete()

            shipment_carrier = form.cleaned_data.get('shipment_carrier')
            shipment_id = form.cleaned_data.get('shipment_id')

            shipment_item_list = ShipmentItem.objects.filter(order_id=order.id, shipped=False)
            shipment, created = Shipment.objects.get_or_create(
                order=order,
                ref_code=create_ref_code(),
                carrier=shipment_carrier,
                shipment_id=shipment_id,
                shipment_date=timezone.now()
            )
            shipment.save()
            print(shipment.ref_code)
            shipment_qs = Shipment.objects.filter(order=order, shipped=False)
            shipment = shipment_qs[0]
            for shipment_item in shipment_item_list:
                shipment.items.add(shipment_item)
                shipment.save()
                shipment_item.shipped = True
                shipment_item.save()
            if shipment.items.all().exists():
                shipment.shipped = True
                shipment.save()

                order.status = 'Shipped'
                order.save()

                order_shipments = Shipment.objects.filter(order=order)
                total_shipment_amount = 0
                for shipment in order_shipments:
                    total_shipment_amount = total_shipment_amount + shipment.get_total()
                    print(total_shipment_amount)
                if total_shipment_amount == order.get_total():
                    order.shipping_status = 'Shipment Complete'
                    order.save()
                else:
                    order.shipping_status = 'Partial Shipment'
                    order.save()

            else:
                shipment.delete()
            print(shipment.ref_code)
            print(order.shipping_status)
            return redirect('store/sales_orders')

        else:
            print(form.errors.as_data())
            messages.warning(request, "Please fill the required data")
            return redirect("store:generate_shipment", pk=order.id)

    context = {'order': order, 'form': form}
    return render(request, 'store/generate_shipment.html', context)


class ShipmentDashboardView(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = 'store/sales_shipments.html'
    context_object_name = 'shipments'
    paginate_by = 20

    def get_queryset(self):
        # user_name = get_object_or_404(User, username=self.kwargs.get('username'))
        return Shipment.objects.filter(shipped=True).order_by('-shipment_date')


def viewShipment(request, pk):
    shipment = Shipment.objects.get(id=pk)
    context = {'shipment': shipment}
    return render(request, 'store/view_shipment.html', context)


def RequestRefund(request, ref_code):
    order = Order.objects.get(ref_code=ref_code)
    form = RefundRequestForm(request.POST)
    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            data = request.POST.dict()
            data.pop('csrfmiddlewaretoken', None)

            for i in data.items():
                print(i)
                if str(i[0].split("_")[0]) == 'refundQuantity':
                    for order_item in order.items.all():
                        if str((i[0].split("_")[1])) == str(order_item.item.id):
                            if str(i[1]) == '':
                                entry = 0
                            else:
                                entry = i[1]
                            if order_item.refund_request_quantity + int(entry) > order_item.quantity:
                                messages.info(request, "Refund quantity can't be greater than ordered quantity")
                                return redirect("store:request_refund", pk=order.id)

            for i in data.items():
                if str(i[0].split("_")[0]) == 'refundQuantity':
                    if str(i[1]) == '':
                        entry = 0
                    else:
                        entry = i[1]

                    item_id = int(i[0].split("_")[1])

                    for order_item in order.items.all():

                        if item_id == order_item.item.id:
                            order_item.refund_request_quantity = order_item.refund_request_quantity + int(entry)
                            order_item.save()

                if str(i[0].split("_")[0]) == 'refundReason':
                    reason = str(i[1])

                    for order_item in order.items.all():

                        if item_id == order_item.item.id:
                            order_item.refund_reason = reason
                            order_item.save()
            full_refund = 0
            for item in order.items.all():
                if item.refund_request_quantity == item.quantity:
                    full_refund = full_refund + 1
            if full_refund == order.items.count():
                order.refund_request_status = 'Full Refund Requested'
                order.save()
            else:
                order.refund_request_status = 'Partial Refund Requested'
                order.save()

            order.refund_request_status = 'Refund Requested'
            order.save()
            return redirect('store:sales-orders')

        else:
            print(form.errors)
            messages.warning(request, "Please fill the required fields")
            return redirect("store:request_refund", pk=order.id)

    context = {'order': order, 'form': form}
    return render(request, 'store/request_refund.html', context)


def RefundOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = RefundForm(request.POST)
    if request.method == 'POST':
        form = RefundForm(request.POST)
        if form.is_valid():
            data = request.POST.dict()
            data.pop('csrfmiddlewaretoken', None)

            for i in data.items():
                print(i)
                for order_item in order.items.all():
                    if str((i[0].split("_")[1])) == str(order_item.item.id):
                        if str(i[1]) == '':
                            entry = 0
                        else:
                            entry = i[1]
                        if order_item.refund_quantity + int(entry) > order_item.refund_request_quantity:
                            messages.warning(request, "Refund quantity can't be greater than requested refund quantity")
                            return redirect("store:generate_refund", pk=order.id)

            for order_item in order.items.all():
                ref = str(order.id) + "_" + str(order_item.item.id)
                refund_item, created = RefundItem.objects.get_or_create(
                    item=order_item.item,
                    order_id=order.id,
                    ref_id=str(order.id) + "_" + str(order_item.item.id),
                    refunded=False,
                    quantity=0
                )
                refund_item.save()

            for i in data.items():
                if str(i[0].split("_")[0]) == 'refund-quantity':
                    ref = str(order.id) + "_" + str(i[0].split("_")[1])
                    # if ShipmentItem.objects.get(ref_id = ref).exists():
                    if str(i[1]) == '':
                        entry = 0
                    else:
                        entry = i[1]

                refund_item_qs = RefundItem.objects.filter(ref_id=ref, refunded=False)
                if refund_item_qs.exists() and int(entry) > 0:
                    refund_item = refund_item_qs[0]
                    refund_item.quantity = int(entry)
                    refund_item.save()
                    for order_item in order.items.all():
                        if str((i[0].split("_")[1])) == str(order_item.item.id):
                            order_item.refund_quantity = order_item.refund_quantity + int(entry)
                            order_item.save()

            refund_item_list = RefundItem.objects.filter(order_id=order.id, refunded=False)
            for refund_item in refund_item_list:
                if refund_item.quantity == 0:
                    refund_item.delete()

            refund_method = form.cleaned_data.get('refund_method')
            refund_id = form.cleaned_data.get('refund_id')

            refund_item_list = RefundItem.objects.filter(order_id=order.id, refunded=False)
            refund, created = Refund.objects.get_or_create(
                order=order,
                ref_code=create_ref_code(),
                refund_method=refund_method,
                refund_id=refund_id,
                refund_date=timezone.now()
            )
            refund.save()
            print(refund.ref_code)
            refund_qs = Refund.objects.filter(order=order, refunded=False)
            refund = refund_qs[0]
            for refund_item in refund_item_list:
                refund.items.add(refund_item)
                refund.save()
                refund_item.refunded = True
                refund_item.save()
            if refund.items.all().exists():
                refund.refunded = True
                refund.save()

                order_refundss = Refund.objects.filter(order=order)
                total_refund_amount = 0
                for refund in order_refundss:
                    total_refund_amount = total_refund_amount + refund.get_total()
                    print(total_refund_amount)
                if total_refund_amount == order.get_total():
                    order.refund_status = 'Full Refund Initiated'
                    order.save()
                else:
                    order.shipment_status = 'Partial Refund Initiated'
                    order.save()
            else:
                refund.delete()
            print(refund.ref_code)
            return redirect('store:sales-orders')

        else:
            print(form.errors)
            messages.warning(request, "Please fill all required fields")
            return redirect("store:generate_refund", pk=order.id)

    context = {'order': order, 'form': form}
    return render(request, 'store/generate_refund.html', context)


class RefundDashboardView(LoginRequiredMixin, ListView):
    model = Refund
    template_name = 'store/sales_refunds.html'
    context_object_name = 'refunds'
    paginate_by = 20

    def get_queryset(self):
        # user_name = get_object_or_404(User, username=self.kwargs.get('username'))
        return Refund.objects.filter(refunded=True).order_by('-refund_date')


def viewRefund(request, pk):
    refund = Refund.objects.get(id=pk)
    context = {'refund': refund}
    return render(request, 'store/view_refund.html', context)


class RefundRequestDashboardView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'store/customer_refundRequests.html'
    context_object_name = 'refunds'
    paginate_by = 20

    def get_queryset(self):
        # user_name = get_object_or_404(User, username=self.kwargs.get('username'))
        return Order.objects.filter(status="Refund Requested")


class ViewItems(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'store/view_products.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        # user_name = get_object_or_404(User, username=self.kwargs.get('username'))
        return Item.objects.all()


def updateItem(request, pk):
    item = Item.objects.get(id=pk)
    form = ItemForm(instance=item)
    if request.method == 'POST':

        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "The item has been successfully saved!")
            return redirect("store:update_item", pk=item.id)

    context = {'item': item, 'form': form}
    return render(request, 'store/update_item.html', context)


def createItem(request):
    form = ItemForm()
    if request.method == 'POST':

        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "The item has been successfully saved!")
            return redirect("store:view_items")
        else:
            for error in form.errors:
                messages.error(request, "There was an error! Please check your entries and try again.")
                return redirect("store:create_item")

    context = {'form': form}
    return render(request, 'store/create_item.html', context)
