from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'payment_method', 'status', 'created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'transaction_id'] 
    search_fields = ['order__id', 'transaction_id'] 
    list_filter = ['status', 'payment_method'] 