from django import forms
from .models import Order, Product
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['supplier', 'product', 'quantity']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.none()

        if 'supplier' in self.data:
            try:
                supplier_id = int(self.data.get('supplier'))
                self.fields['product'].queryset = Product.objects.filter(supplier_id=supplier_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['product'].queryset = self.instance.supplier.products.all()
        else:
            self.fields['product'].queryset = Product.objects.none()

