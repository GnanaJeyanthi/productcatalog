# D:\2312040-wfp\productcatalog_project\store\forms.py
from django import forms
from .models import Order, Product, Category, Brand

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'state', 'pincode', 'payment_method']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 XXXXX XXXXX'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'House No., Building Name, Street, Area'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '600001'
            }),
            'payment_method': forms.RadioSelect(),
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'address': 'Delivery Address',
            'city': 'City',
            'state': 'State',
            'pincode': 'PIN Code',
            'payment_method': 'Payment Method',
        }

class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        empty_label="Select Brand (Optional)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    specs = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter specifications as JSON, e.g. {"RAM": "8GB", "Storage": "256GB"}'
        }),
        help_text='Enter specifications in JSON format'
    )


    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'brand', 'price', 'stock', 'specs']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Product Description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10'
            }),
        }

    def clean_specs(self):
        specs = self.cleaned_data.get('specs')
        if specs:
            try:
                import json
                json.loads(specs)
            except json.JSONDecodeError:
                raise forms.ValidationError("Please enter valid JSON format for specifications.")
        return specs
