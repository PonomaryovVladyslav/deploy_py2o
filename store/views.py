from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from store.forms import UserCreateForm, PurchaseCreateForm, ReturnCreateForm
from store.models import Product, Purchase, ReturnPurchase


class SuperuserRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('home')


class UserCreateView(CreateView):
    form_class = UserCreateForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        valid = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return valid


class ProductListView(ListView):
    model = Product
    template_name = 'store/home.html'
    extra_context = {'form': PurchaseCreateForm}


class ProductCreateView(SuperuserRequiredMixin, CreateView):
    model = Product
    fields = ['title', 'image', 'description', 'price', 'quantity']
    template_name = 'store/add_product.html'
    success_url = reverse_lazy('add_product')


class ProductUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Product
    fields = ['title', 'image', 'description', 'price', 'quantity']
    template_name = 'store/update_product.html'
    success_url = reverse_lazy('home')


class PurchaseListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Purchase
    template_name = 'store/purchase.html'
    extra_context = {'form': ReturnCreateForm}

    def get_queryset(self):
        if not self.request.user.is_superuser:
            customer_id = self.request.user.id
            returns = ReturnPurchase.objects.filter(purchase__customer_id=customer_id)
            returns_list = returns.values_list('purchase_id', flat=True)
            queryset = Purchase.objects.filter(customer_id=customer_id).exclude(id__in=returns_list)
            return queryset
        queryset = Purchase.objects.all()
        return queryset


class PurchaseCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    form_class = PurchaseCreateForm
    template_name = 'store/home.html'
    success_url = reverse_lazy('purchases')

    def form_valid(self, form):
        obj = form.save(commit=False)
        product_id = self.kwargs.get('pk')
        product = Product.objects.get(id=product_id)
        ordered_quantity = int(self.request.POST['quantity'])
        stock_quantity = product.quantity
        if ordered_quantity > stock_quantity:
            messages.error(self.request, 'Not enough goods in stock')
            return HttpResponseRedirect('/')
        purchase_amount = product.price * ordered_quantity
        # ---------------------------------------------------------------------------------------
        obj.product = product
        obj.customer = self.request.user
        obj.save()
        return super().form_valid(form)


class ReturnListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = ReturnPurchase
    template_name = 'store/return_purchase.html'

    def get_queryset(self):
        if not self.request.user.is_superuser:
            pk = self.request.user.id
            queryset = ReturnPurchase.objects.filter(purchase__customer_id=pk)
            return queryset
        queryset = ReturnPurchase.objects.all()
        return queryset


class ReturnCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    form_class = ReturnCreateForm
    template_name = 'store/purchase.html'
    success_url = reverse_lazy('returns')

    def form_valid(self, form):
        obj = form.save(commit=False)
        purchase_id = self.kwargs.get('pk')
        obj.purchase = Purchase.objects.get(id=purchase_id)
        obj.save()
        return super().form_valid(form)


class ReturnDeleteView(SuperuserRequiredMixin, DeleteView):
    model = ReturnPurchase
    success_url = reverse_lazy('returns')


class PurchaseDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Purchase
    success_url = reverse_lazy('returns')
