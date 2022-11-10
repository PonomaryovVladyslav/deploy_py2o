from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView
from django.views.generic.base import TemplateView

from store.forms import UserRegisterForm, CreatePurchaseForm
from store.models import Product, Purchase, MyUser


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
    # model = Product
    # fields = ['title', 'description', 'price', 'quantity']
    form_class = CreatePurchaseForm
    template_name = 'store/update_product.html'
    success_url = reverse_lazy('home')


class CreatePurchaseView(CreateView):
    model = Purchase
    fields = ['quantity']
    template_name = 'store/home.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['form'] = CreatePurchaseForm()
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.customer = self.request.user
        obj.product = Product.objects.get(id=self.kwargs.get('pk'))
        obj.save()
        return super().form_valid(form=obj)


# class CreatePurchaseView(ListView):
#     model = Product
#     paginate_by = 10
#     template_name = 'store/home.html'
