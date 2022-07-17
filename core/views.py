from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, View

from .models import *


def checkout(request):
    return render(request, 'checkout.html')


class HomeView(ListView):
    model = Product
    paginate_by = 3
    template_name = 'home.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            return render(self.request, 'order_summary.html', {'object': order})
        except ObjectDoesNotExist:
            messages.error(self.request, 'У вас нет активных заказов')
            return redirect('/')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product.html'


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_product, created = OrderProduct.objects.get_or_create(
        product=product,
        user=request.user,
        )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__slug=product.slug).exists():
            order_product.quantity += 1
            order_product.save()
            messages.info(request, 'Товар был увеличен на +1')
            return redirect('core:order-summary')

        else:
            messages.info(request, 'Товар был добавлен в вашу корзину')
            order_product.quantity = 1
            order_product.save()
            order.products.add(order_product)
            return redirect('core:order-summary')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.products.add(order_product)
        messages.info(request, 'Товар был добавлен в вашу корзину')
        return redirect('core:order-summary')


@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            order.products.remove(order_product)
            order_product.quantity = 0
            order_product.save()
            messages.info(request, 'Товар был удален с вашей корзины')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'Товара нету в вашей корзине')
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, 'Вы ничего не заказали!')
        return redirect('core:product', slug=slug)


@login_required
def remove_single_product_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            if order_product.quantity > 1:
                order_product.quantity -= 1
            else:
                order.products.remove(order_product)
            order_product.save()
            messages.info(request, 'Товар был уменьшен на -1')
            return redirect('core:order-summary')

        else:
            messages.info(request, 'Товара нету в вашей корзине')
            return redirect('core:order-summary')

    else:
        messages.info(request, 'Вы ничего не заказали!')
        return redirect('core:order-summary')


