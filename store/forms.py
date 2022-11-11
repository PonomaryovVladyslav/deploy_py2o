from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.urls import reverse

from store.models import MyUser, Purchase, ReturnPurchase


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput)
    email = forms.EmailField(widget=forms.EmailInput)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    deposit = forms.DecimalField(initial=2000, widget=forms.HiddenInput)

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'password1', 'password2', 'deposit')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if MyUser.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered')
        return email


class CreatePurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['quantity']


class CreateReturnPurchaseForm(forms.ModelForm):
    class Meta:
        model = ReturnPurchase
        fields = ['purchase']
