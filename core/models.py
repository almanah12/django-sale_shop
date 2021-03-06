from django.conf import settings
from django.db import models
from django.urls import reverse

from core.utils import from_cyrillic_to_eng

CATEGORY_CHOICES = (
    ('TAV', 'ТВ, Аудио, Видео'),
    ('TG', 'Телефоны, гаджеты'),
    ('C', 'Компьютеры')

)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')

)


class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    label = models.CharField(choices=LABEL_CHOICES, max_length=2)
    slug = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(default='Описание товара')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = from_cyrillic_to_eng(str(self.title))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:product', kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse('core:add-to-cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('core:remove-from-cart', kwargs={'slug': self.slug})


class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"

    def get_total_product_price(self):
        return self.quantity * self.product.price

    def get_total_product_discount_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total_product_price() - self.get_total_product_discount_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_product_discount_price()
        else:
            return self.get_total_product_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} ordered"

    def get_total(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price()
        return total
