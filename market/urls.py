from django.urls import path
from . import views


app_name = "market"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("order-summary/", views.OrderSummaryView.as_view(), name="order-summary"),
    path("product/<slug>/", views.ProductView.as_view(), name="product"),
    path("add-to-cart/<slug>/", views.add_to_cart, name="add-to-cart"),
    path("remove-from-cart/<slug>/", views.remove_from_cart, name="remove-from-cart"),
    path(
        "remove-single-item-from-cart/<slug>/",
        views.remove_single_item_from_cart,
        name="remove-single-item-from-cart",
    ),
    path(
        "add-to-cart-in-order/<slug>/",
        views.add_to_cart_in_order,
        name="add-to-cart-in-order",
    ),
    path(
        "remove-from-cart-in-order/<slug>/",
        views.remove_from_cart_in_order,
        name="remove-from-cart-in-order",
    ),
    path("load_subregions/", views.load_subregions, name="load-subregions"),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_canceled, name='payment_cancelled'),
]
