from django.contrib.auth import views
from django.urls import path

from store.views import UserCreateView, ProductCreateView, ProductUpdateView,\
    PurchaseCreateView, ProductListView, PurchaseListView, ReturnCreateView, ReturnListView

urlpatterns = [
    path('', ProductListView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('add-product/', ProductCreateView.as_view(), name='add_product'),
    path('update-product/<int:pk>', ProductUpdateView.as_view(), name='update_product'),
    path('add-purchase/', PurchaseCreateView.as_view(), name='add_purchase'),
    path('purchases/', PurchaseListView.as_view(), name='purchases'),
    path('add-return/', ReturnCreateView.as_view(), name='add_return'),
    path('returns/', ReturnListView.as_view(), name='returns'),
]
