from django.contrib import admin
from .models import *

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'updated_at')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category')
    search_fields = ('name',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ProductImage)