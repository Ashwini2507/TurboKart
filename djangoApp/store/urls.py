from django.urls import path
from . import views
from .views import (
    ItemDetailView,
    CheckoutView,
    DefaultHomeView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    CategoryView,
    BrandView,
    UserOrdersView,
    OrderDashboardView,
    InvoiceDashboardView,
    ShipmentDashboardView,
    RefundDashboardView,
    ViewItems,
    ViewCustomers
)

app_name = 'store'

urlpatterns = [
    path('', DefaultHomeView.as_view(), name='store-default-home'),
    path('<str:store_slug>/home', HomeView.as_view(), name='store-home'),
    path('<str:store_slug>/checkout/', CheckoutView.as_view(), name='checkout'),
    path('<str:store_slug>/order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('<str:store_slug>/product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('<str:store_slug>/add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('<str:store_slug>/add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('<str:store_slug>/remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('<str:store_slug>/remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('<str:store_slug>/payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('category/<str:slug>',CategoryView.as_view(), name='by_category'),
    path('orders/',UserOrdersView.as_view(), name='user-orders'),
    path('brand/<str:slug>',BrandView.as_view(), name='by_brand'),
    path('sales_orders/',OrderDashboardView.as_view(), name='sales-orders'),
    path('update_order/<str:pk>/', views.updateOrder, name="update_order"),
    path('generate_invoice/<str:pk>/', views.invoiceOrder, name="generate_invoice"),
    path('sales_invoices/',InvoiceDashboardView.as_view(), name='sales-invoices'),
    path('view_invoice/<str:pk>/', views.viewInvoice, name="view_invoice"),
    path('view_order_invoice/<str:ref_code>/', views.customerViewInvoice, name="customer_view_invoice"),
    path('generate_shipment/<str:pk>/', views.ShipOrder, name="generate_shipment"),
    path('sales_shipments/',ShipmentDashboardView.as_view(), name='sales-shipments'),
    path('view_shipment/<str:pk>/', views.viewShipment, name="view_shipment"),
    path('request_refund/<str:ref_code>/', views.RequestRefund, name="request_refund"),
    path('generate_refund/<str:pk>/', views.RefundOrder, name="generate_refund"),
    path('sales_refunds/',RefundDashboardView.as_view(), name='sales-refunds'),
    path('view_refund/<str:pk>/', views.viewRefund, name="view_refund"),
    path('view_items/', ViewItems.as_view(),name="view_items"),
    path('update_item/<str:pk>/', views.updateItem, name="update_item"),
    path('view_invoices/<str:ref_code>', views.viewInvoices, name="view_invoices"),
    path('view_shipments/<str:ref_code>', views.viewShipments, name="view_shipments"),
    path('view_refunds/<str:ref_code>', views.viewRefunds, name="view_refunds"),
    path('order_invoices/<str:ref_code>', views.viewInvoicesCustomers, name="order_invoices"),
    path('order_shipments/<str:ref_code>', views.viewShipmentsCustomers, name="order_shipments"),
    path('order_refunds/<str:ref_code>', views.viewRefundsCustomers, name="order_refunds"),
    path('customers/',ViewCustomers.as_view(), name='view-customers'),
    path('create_item/', views.createItem, name="create_item"),
]
