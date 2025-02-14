from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'category', 'subcategory',
                    'brand', 'price', 'stock')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'brand', 'category__name')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'is_main')
    list_filter = ('is_main',)
    search_fields = ('product__name',)
