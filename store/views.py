from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, hashers, logout, login
from django.contrib import messages
from django.conf import settings
from .forms import *
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder

def loginView(request):
	
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			pwd = form.cleaned_data.get('password')
			try:
				user = authenticate(username=username, password=pwd)
				if user is not None:
					login(request,user)
					remember_me = form.cleaned_data.get("remember_me")
					if remember_me is True:
						ONE_MONTH = 30 * 24 * 60 * 60
						expiry = getattr(settings, "KEEP_LOGGED_DURATION", ONE_MONTH)
						request.session.set_expiry(expiry)
					messages.success(request, "Connexion réussie ... !")
					return redirect('store')
				else:
					messages.warning(request, "La connexion a échoué ! Saisissez un nom et un mot de passe corrects.")
					return redirect('login')

			except Exception as e:
				messages.warning(request, "Impossible de vous authentifier ! Saisissez un nom et un mot de passe corrects.")
				return redirect('store')
		else:
			messages.warning(request, "Erreur de validation des informations !")
			return redirect('login')
	
	else:
		form = LoginForm()
		data = cartData(request)
		cartItems = data['cartItems']
		
		context = {'cartItems':cartItems, 'form':form}
	return render(request, 'store/login.html', context)


def signoutView(request):
	logout(request)
	messages.success(request,"Vous êtes déconnecté ... !")
	return redirect('store')


def inscrire(request):
	if request.method == 'POST':
		form = InscrireForm(request.POST)
		if form.is_valid():
			pwda = form.cleaned_data.get('password1')
			pwdb = form.cleaned_data.get('password2')
			if pwda == pwdb:
				hashpwd = hashers.make_password(pwda, salt=None, hasher='default')
				username = form.cleaned_data.get('username')
				email = form.cleaned_data.get('email')
				user = User.objects.create_user(username, email, hashpwd)
				user.save()
				cust = Customer(user=user, name=user.username, email=user.email)
				cust.save()
				messages.success(request, "Félicitations! Votre compte est crée, vous pouvez acheter paisiblement")
				return redirect('store')
			else:
				messages.warning(request, "Erreur ! Les mots de passe ne correspondent pas.")
				return redirect('inscription')
		else:
			messages.warning(request, "Erreur de validation des informations !")
			return redirect('inscription')

	else:
		form = InscrireForm()
		data = cartData(request)
		cartItems = data['cartItems']
		
		context = {'cartItems':cartItems, 'form':form}
	return render(request, 'store/inscrire.html', context)


def store(request):
	data = cartData(request)
	cartItems = data['cartItems']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	user = request.user
	context = {'items':items, 'order':order, 'cartItems':cartItems, 'user':user}
	return render(request, 'store/checkout.html', context)

def details(request, **kwargs):
	Id = kwargs['id']
	product = Product.objects.get(id=Id)
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems, 'produit':product}
	return render(request, 'store/details.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = int(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		street=data['shipping']['street'],
		phone=data['shipping']['phone'],
		)

	return JsonResponse('Payment submitted..', safe=False)