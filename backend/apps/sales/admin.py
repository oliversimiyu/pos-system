from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['subtotal', 'tax_amount', 'total']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['sale_number', 'cashier', 'total', 'payment_status', 'status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['sale_number', 'customer_name', 'customer_phone']
    readonly_fields = ['sale_number', 'subtotal', 'tax_amount', 'total', 'created_at', 'updated_at']
    inlines = [SaleItemInline]
    
    fieldsets = (
        ('Sale Information', {
            'fields': ('sale_number', 'cashier', 'status', 'payment_status')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'discount', 'total', 'amount_paid', 'change')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product_name', 'quantity', 'unit_price', 'total']
    list_filter = ['created_at']
    search_fields = ['product_name', 'product_barcode']
    readonly_fields = ['subtotal', 'tax_amount', 'total', 'created_at']
