from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from django.views.generic.base import TemplateView

from store.forms import UserRegisterForm, CreatePurchaseForm, CreateReturnPurchaseForm
from store.models import Product, Purchase


class HomePageView(ListView):
    model = Product
    template_name = 'store/home.html'
    extra_context = {'form': CreatePurchaseForm}


class RegisterUserView(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        valid = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return valid


class CreateProductView(CreateView):
    model = Product
    fields = ['title', 'description', 'price', 'quantity']
    template_name = 'store/add_product.html'
    success_url = reverse_lazy('add_product')


class UpdateProductView(UpdateView):
    model = Product
    fields = ['title', 'description', 'price', 'quantity']
    template_name = 'store/update_product.html'
    success_url = reverse_lazy('home')


class CreatePurchaseView(CreateView):
    form_class = CreatePurchaseForm
    template_name = 'store/home.html'
    success_url = reverse_lazy('purchases')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        pk = self.kwargs.get('pk')
        self.object.customer = self.request.user
        self.object.product = Product.objects.get(id=pk)
        self.object.save()
        return super().form_valid(form)


class UserPurchaseView(ListView):
    model = Purchase
    template_name = 'store/purchase.html'
    extra_context = {'form': CreateReturnPurchaseForm}

    def get_queryset(self):
        pk = self.request.user.id
        queryset = Purchase.objects.filter(customer_id=pk)
        return queryset


class CreateReturnPurchaseView(CreateView):
    form_class = CreateReturnPurchaseForm
    template_name = 'store/purchase.html'
    success_url = reverse_lazy('purchases')

    # def get(self, request, *args, **kwargs):
    #     pk = self.kwargs.get('pk')
    #     self.object = Purchase.objects.get(id=pk)
    #     self.object.save()
    #     return super().get(request, *args, **kwargs)
