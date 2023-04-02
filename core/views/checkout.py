import stripe
from django.conf import settings  # new
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from core.models.customer import Customer
from django.views import View
from django.http.response import JsonResponse  # new
from django.views.decorators.csrf import csrf_exempt  # new

from core.models.product import Products
from core.models.orders import Order

global_price = 0
global_qty = 0

class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Products.get_products_by_id(list(cart.keys()))
        print(address, phone, customer, cart, products)

        for product in products:
            print(cart.get(str(product.id)))
            order = Order(customer=Customer(id=customer),
                          product=product,
                          price=product.price,
                          address=address,
                          phone=phone,
                          quantity=cart.get(str(product.id)))
            order.save()
            global global_qty
            global global_price
            global_qty = order.quantity
            global_price += order.price * global_qty
        global_qty = 0
        request.session['cart'] = {}
        return redirect('create-checkout-session')

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


stripe.api_key = settings.STRIPE_SECRET_KEY


class create_checkout_session(View):
    def get(self, request):
        global global_price
        domain = "https://yourdomain.com"
        if settings.DEBUG:
            domain = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'cad',
                    'product_data': {
                        'name': "Cosmos Clothing Order",
                    },
                    'unit_amount': global_price * 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=domain + '/success/',
            cancel_url=domain + '/cancel/',
        )
        global_price = 0
        global_qty = 0
        return redirect(checkout_session.url)
