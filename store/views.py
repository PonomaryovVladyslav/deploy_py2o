from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from config.settings import RETURN_TIME_LIMIT
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
    paginate_by = 3

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            if request.session.get('page_visit', False):
                request.session['page_visit'] += 1
            else:
                request.session['page_visit'] = 1
            if request.session.get('page_visit') == 4:
                request.session['page_visit'] = 0
                messages.info(self.request, 'This is your 4th visit to the page')
        return super(ProductListView, self).get(request, *args, **kwargs)


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
    paginate_by = 4

    def get_queryset(self):
        if not self.request.user.is_superuser:
            queryset = Purchase.objects.filter(customer=self.request.user)
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
        customer = self.request.user
        ordered_quantity = int(self.request.POST['quantity'])
        if ordered_quantity > product.quantity:
            messages.error(self.request, 'Not enough goods in stock')
            return HttpResponseRedirect('/')
        purchase_amount = product.price * ordered_quantity
        if purchase_amount > customer.deposit:
            messages.error(self.request, 'Not enough funds to make a purchase')
            return HttpResponseRedirect('/')
        obj.product = product
        obj.customer = customer
        product.quantity -= ordered_quantity
        customer.deposit -= purchase_amount

        with transaction.atomic():
            obj.save()
            product.save()
            customer.save()

        return super().form_valid(form)


class ReturnListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = ReturnPurchase
    template_name = 'store/return_purchase.html'
    paginate_by = 4

    def get_queryset(self):
        if not self.request.user.is_superuser:
            queryset = ReturnPurchase.objects.filter(purchase__customer=self.request.user)
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
        purchase = Purchase.objects.get(id=purchase_id)
        check_time_period = timezone.now() - purchase.date
        if check_time_period.seconds > RETURN_TIME_LIMIT:
            messages.error(self.request, 'Return time has expired')
            return HttpResponseRedirect('/purchases')
        obj.purchase = purchase
        obj.save()
        return super().form_valid(form)


class ReturnDeleteView(SuperuserRequiredMixin, DeleteView):
    model = ReturnPurchase
    success_url = reverse_lazy('returns')


class PurchaseDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Purchase
    success_url = reverse_lazy('returns')

    def form_valid(self, form):
        purchase = self.get_object()
        customer = purchase.customer
        product = purchase.product
        customer.deposit += purchase.purchase_amount()
        product.quantity += purchase.quantity

        with transaction.atomic():
            customer.save()
            product.save()
            purchase.delete()
        return HttpResponseRedirect(self.success_url)
