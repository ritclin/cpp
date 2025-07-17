from django.contrib import admin
from .models import Supplier, Product, Order

class ProductInline(admin.TabularInline):
    model = Product
    extra = 1

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'contact_email')
    inlines = [ProductInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'price_per_unit')

admin.site.register(Order, list_display=('user', 'supplier', 'product', 'quantity', 'status', 'created_at'))
