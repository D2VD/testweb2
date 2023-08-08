from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.generic import View, ListView, DetailView
from .models import Item, OrderItem, Order, Subregion, BillingAddress, CATEGORY_CHOICES
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = "market/home_page.html"
    
    def get_queryset(self):
        # Override the get_queryset method to filter the items by category
        queryset = super().get_queryset() # Get the default queryset from the parent class
        selected_category = self.request.GET.get("category")
        search_query = self.request.GET.get("search")
        if selected_category:
            queryset = queryset.filter(category=selected_category)
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query))
        return queryset
    
    def get_context_data(self, **kwargs):
        # Override the get_context_data method to add extra variables to the context
        context = super().get_context_data(**kwargs) # Get the default context from the parent class
        context["CATEGORY_CHOICES"] = CATEGORY_CHOICES
        return context


class ProductView(DetailView):
    model = Item
    template_name = "market/product_page.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {"object": order}
            return render(self.request, "market/order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(
                self.request,
                "You do not have an active order! Please order at least 1 item.",
            )
            return redirect("/")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        checkout_form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            "checkout_form": checkout_form,
            "object": order,
        }
        return render(self.request, "market/checkout_page.html", context)

    def post(self, *args, **kwargs):
        checkout_form = CheckoutForm(self.request.POST or None)
        print(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            # check if form is valid
            if checkout_form.is_valid():
                print(checkout_form.cleaned_data)
                address = checkout_form.cleaned_data.get("address")
                address2 = checkout_form.cleaned_data.get("address2")
                region = checkout_form.cleaned_data.get("region")
                subregion = checkout_form.cleaned_data.get("subregion")
                # TODO: add func for these fields
                # same_shipping_address = form.cleaned_data.get("same_shipping_address")
                # save_info = form.cleaned_data.get("save_info")
                payment_option = checkout_form.cleaned_data.get("payment_option")
                billing_address = BillingAddress(
                    user=self.request.user,
                    address=address,
                    address2=address2,
                    region=region,
                    subregion=subregion,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # messages.success(self.request, "Checkout successful!")
                return redirect("market:process_payment")

            print(checkout_form.errors)
            messages.warning(self.request, "Failed checkout")
            return redirect("market:checkout")
        except ObjectDoesNotExist:
            messages.error(
                self.request,
                "You do not have an active order! Please order at least 1 item.",
            )
            return redirect("market:order-summary")


def process_payment(request):
    order = Order.objects.get(user=request.user, ordered=False)
    host = request.get_host()

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": order.get_total_price(),
        "item_name": "Order {}".format(order.user),
        "invoice": str(order.id),
        "currency_code": "USD",
        "notify_url": "http://{}{}".format(host, reverse("paypal-ipn")),
        "return_url": "http://{}{}".format(host, reverse("market:payment_done")),
        "cancel_return": "http://{}{}".format(
            host, reverse("market:payment_cancelled")
        ),
    }

    paypal_form = PayPalPaymentsForm(initial=paypal_dict)
    return render(
        request,
        "market/process_payment.html",
        {"order": order, "paypal_form": paypal_form},
    )


@csrf_exempt
def payment_done(request):
    order = Order.objects.get(user=request.user, ordered=False)
    order.ordered = True
    for item in order.items.all():
        item.ordered = True
        item.save()
    order.save()
    return redirect("market:home")


@csrf_exempt
def payment_canceled():
    return redirect("market:home")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False
    )
    # check if the Order has existed already
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        # check if the OrderItem has been in the Order already
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(
                request,
                f"This item quantity was updated.\nQuantity: {order_item.quantity}",
            )
            return redirect("market:product", slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("market:product", slug=slug)
    else:
        order = Order.objects.create(user=request.user, ordered_date=timezone.now())
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("market:product", slug=slug)


@login_required
def add_to_cart_in_order(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False
    )
    order_item.quantity += 1
    order_item.save()
    return redirect("market:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # check if the Order has existed already
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        # check if the OrderItem has been in the Order already
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False
            )[0]
            # order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed to your cart.")
            return redirect("market:product", slug=slug)
        else:
            messages.info(request, "This item is not in your cart.")
            return redirect("market:product", slug=slug)
    else:
        messages.info(request, "You have NOT had an order.")
        return redirect("market:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[
        0
    ]
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()
    return redirect("market:order-summary")


@login_required
def remove_from_cart_in_order(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[
        0
    ]
    order_item.delete()
    return redirect("market:order-summary")


@login_required
def load_subregions(request):
    region_id = request.GET.get("region_id")
    if region_id:
        subregions = Subregion.objects.filter(region_id=region_id)
        data = [
            {"id": subregion.id, "name": subregion.name} for subregion in subregions
        ]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)
