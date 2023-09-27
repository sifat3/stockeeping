# forms.py

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'quantity', 'unit_buying_price', 'unit_selling_price']
        

class BuyProductForm(forms.Form):
    product = forms.ChoiceField(choices=[], label='Select a Product', widget=forms.Select(attrs={'style': 'height: 50px; width: 140px;'}))
    quantity = forms.IntegerField(min_value=1, label='Enter Quantity')
    # additional_details = forms.CharField(required=False, label='Additional Details')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate product choices
        products = Product.objects.all()
        self.fields['product'].choices = [(product.id, product.name) for product in products]

class SellProductForm(forms.Form):
    product = forms.ChoiceField(choices=[], label='Select a Product', widget=forms.Select(attrs={'style': 'height: 50px; width: 140px;'}))
    quantity = forms.IntegerField(min_value=1, label='Enter Quantity')
    # additional_details = forms.CharField(required=False, label='Additional Details')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate product choices
        products = Product.objects.all()
        self.fields['product'].choices = [(product.id, product.name) for product in products]