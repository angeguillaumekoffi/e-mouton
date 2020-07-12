from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('mon-panier/', views.cart, name="cart"),
	path('details-<int:id>/', views.details, name="details"),
	path('connexion/', views.loginView, name="login"),
	path('logout/', views.signoutView, name="logout"),
	path('inscription/', views.inscrire, name="inscription"),
	path('finir-commande/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),

]