from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from store.forms import UserCreateForm, PurchaseCreateForm, ReturnCreateForm
from store.models import Product, Purchase, ReturnPurchase


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


class ProductCreateView(CreateView):
    model = Product
    fields = ['title', 'description', 'price', 'quantity']
    template_name = 'store/add_product.html'
    success_url = reverse_lazy('add_product')


class ProductUpdateView(UpdateView):
    model = Product
    fields = ['title', 'description', 'price', 'quantity']
    template_name = 'store/update_product.html'
    success_url = reverse_lazy('home')


class PurchaseListView(ListView):
    model = Purchase
    template_name = 'store/purchase.html'
    extra_context = {'form': ReturnCreateForm}

    def get_queryset(self):
        if not self.request.user.is_superuser:
            pk = self.request.user.id
            queryset = Purchase.objects.filter(customer_id=pk)
            return queryset
        queryset = Purchase.objects.all()
        return queryset


class PurchaseCreateView(CreateView):
    form_class = PurchaseCreateForm
    template_name = 'store/home.html'
    success_url = reverse_lazy('purchases')

    def form_valid(self, form):
        obj = form.save(commit=False)
        product_id = self.request.POST.get('_product')
        obj.product = Product.objects.get(id=product_id)
        obj.customer = self.request.user
        obj.save()
        return super().form_valid(form)


class ReturnListView(ListView):
    model = ReturnPurchase
    template_name = 'store/return_purchase.html'

    def get_queryset(self):
        if not self.request.user.is_superuser:
            pk = self.request.user.id
            queryset = ReturnPurchase.objects.filter(purchase__customer_id=pk)
            return queryset
        queryset = ReturnPurchase.objects.all()
        return queryset


class ReturnCreateView(CreateView):
    form_class = ReturnCreateForm
    template_name = 'store/purchase.html'
    success_url = reverse_lazy('returns')

    def form_valid(self, form):
        obj = form.save(commit=False)
        purchase_id = self.request.POST.get('_purchase')
        obj.purchase = Purchase.objects.get(id=purchase_id)
        obj.save()
        return super().form_valid(form)


class ReturnDeleteView(DeleteView):
    model = ReturnPurchase
    success_url = reverse_lazy('returns')


class PurchaseDeleteView(DeleteView):
    model = Purchase
    success_url = reverse_lazy('returns')

