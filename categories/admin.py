from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_products',
                    'active_products', 'out_of_stock')
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)
