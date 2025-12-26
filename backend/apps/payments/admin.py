from django.contrib import admin
from .models import Payment, PaymentCallback, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_reference', 'sale', 'method', 'amount', 'status', 'initiated_at']
    list_filter = ['method', 'status', 'initiated_at']
    search_fields = ['transaction_reference', 'external_reference', 'phone_number']
    readonly_fields = ['transaction_reference', 'initiated_at', 'completed_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('sale', 'method', 'amount', 'status')
        }),
        ('References', {
            'fields': ('transaction_reference', 'external_reference')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'account_number')
        }),
        ('Audit Info', {
            'fields': ('initiated_by', 'initiated_at', 'completed_at', 'error_message')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentCallback)
class PaymentCallbackAdmin(admin.ModelAdmin):
    list_display = ['callback_type', 'transaction_id', 'amount', 'success', 'processed', 'received_at']
    list_filter = ['callback_type', 'processed', 'success', 'received_at']
    search_fields = ['transaction_id', 'phone_number']
    readonly_fields = ['received_at', 'processed_at']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_reference', 'payment', 'amount', 'status', 'requested_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['refund_reference', 'external_reference']
    readonly_fields = ['refund_reference', 'requested_at', 'completed_at']
