from datetime import timedelta
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


CATEGORY_CHOICES = (
    ("S", "Shirt"),
    ("SW", "Sport Wear"),
    ("OW", "Outwear"),
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField(blank=False, null=False)
    date = models.DateField(default=timezone.now)
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(
        choices=CATEGORY_CHOICES,
        max_length=2,
        default="S",
    )
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="items/",
        null=True,
        blank=True,
        default="items/default.jpg",
    )
    recently = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    # Override the save method to populate the slug field
    def save(self, *args, **kwargs):
        # create slug automatically
        source = self.title + "-" + self.date.strftime("%d-%m-%Y")
        self.slug = slugify(source)

        # check if item was added recently
        time_delta = timezone.now() - timedelta(days=14)
        if self.date > time_delta.date():
            self.recently = True
        else:
            self.recently = False
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("market:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("market:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("market:remove-from-cart", kwargs={"slug": self.slug})


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_order_item_price(self):
        return self.quantity * self.item.price

    def get_total_order_item_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_saved_amount(self):
        return (
            self.get_total_order_item_price()
            - self.get_total_order_item_discount_price()
        )


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        "BillingAddress", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return self.user.username

    def get_basis_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_order_item_price()
        return total

    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            if order_item.item.discount_price:
                total += order_item.get_total_order_item_discount_price()
            else:
                total += order_item.get_total_order_item_price()
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    subregion = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Region(models.Model):
    name = models.CharField(max_length=200, blank=False)

    class Meta:
        managed = False
        db_table = "cities_light_region"

    def __str__(self):
        return self.name


class Subregion(models.Model):
    name = models.CharField(max_length=200, blank=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "cities_light_subregion"

    def __str__(self):
        return self.name
