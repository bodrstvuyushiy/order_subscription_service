from django import forms
from django.contrib import admin

from .models import Order, ProductItem


class OrderAdminForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=ProductItem.objects.filter(is_active=True),
        label="Product",
        help_text="Выберите товар из каталога — его цена будет подставлена автоматически.",
    )

    class Meta:
        model = Order
        fields = ("user", "product", "price", "quantity", "status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].disabled = True
        self.fields["price"].required = False
        if self.instance.pk:
            try:
                product = ProductItem.objects.get(name=self.instance.product_name)
                self.fields["product"].initial = product
                self.fields["price"].initial = self.instance.price
            except ProductItem.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        if product:
            cleaned_data["price"] = product.price
            self.instance.price = product.price
        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        product = self.cleaned_data["product"]
        order.product_name = product.name
        order.price = product.price
        if commit:
            order.save()
        return order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = (
        "id",
        "user",
        "product_name",
        "price",
        "quantity",
        "status",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")


admin.site.register(ProductItem)
