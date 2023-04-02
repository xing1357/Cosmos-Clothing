from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from core.models.customer import Customer
from django.views import View
from core.models.product import Products
from core.models.orders import Order
from core.middlewares.auth import auth_middleware


class OrderView(View):
    def get(self, request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(orders)
        return render(request, 'orders.html', {'orders': orders})
