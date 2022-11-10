from django.contrib.auth import views
from django.urls import path

from store.views import RegisterUserView, CreateProductView, UpdateProductView, CreatePurchaseView

urlpatterns = [
    path('', CreatePurchaseView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('add-product/', CreateProductView.as_view(), name='add_product'),
    path('update-product/<int:pk>', UpdateProductView.as_view(), name='update_product'),
    path('add-purchase/<int:pk>', CreatePurchaseView.as_view(), name='add-purchase'),
]
