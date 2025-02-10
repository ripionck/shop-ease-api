from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline): # Display order items inline in order admin
    model = OrderItem
    extra = 0 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline] # Include order items inline
    list_display = ['id', 'user', 'total_amount', 'status', 'created_at']
    readonly_fields = ['id', 'total_amount', 'created_at', 'updated_at']
    search_fields = ['id', 'user__username'] 
    list_filter = ['status', 'payment_method']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price']
    search_fields = ['order__id', 'product__name']