from django import forms
from .models import MenuItem, OrderItem


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_item'].queryset = MenuItem.objects.filter(
            is_available=True
        )
        self.fields['quantity'].min_value = 1
        self.fields['quantity'].widget = forms.NumberInput(
            attrs={'min': 1}
        )