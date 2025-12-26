from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, F, Q, Avg
from django.utils import timezone
from datetime import timedelta
from apps.sales.models import Sale, SaleItem
from apps.products.models import Product
from apps.inventory.models import StockMovement, StockAlert
from apps.payments.models import Payment


class SalesReportView(APIView):
    """Generate sales reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get date range from query params
        period = request.query_params.get('period', 'today')  # today, week, month, year, custom
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Determine date range
        now = timezone.now()
        if period == 'today':
            start = now.replace(hour=0, minute=0, second=0)
            end = now
        elif period == 'week':
            start = now - timedelta(days=7)
            end = now
        elif period == 'month':
            start = now - timedelta(days=30)
            end = now
        elif period == 'year':
            start = now - timedelta(days=365)
            end = now
        elif period == 'custom' and start_date and end_date:
            from dateutil import parser
            start = parser.parse(start_date)
            end = parser.parse(end_date)
        else:
            start = now.replace(hour=0, minute=0, second=0)
            end = now
        
        # Get sales data
        sales = Sale.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        )
        
        completed_sales = sales.filter(status='completed')
        
        # Calculate totals
        total_sales = completed_sales.count()
        total_revenue = completed_sales.aggregate(total=Sum('total'))['total'] or 0
        total_tax = completed_sales.aggregate(total=Sum('tax_amount'))['total'] or 0
        total_discount = completed_sales.aggregate(total=Sum('discount'))['total'] or 0
        
        # Sales by payment method
        payment_methods = Payment.objects.filter(
            sale__in=completed_sales,
            status='success'
        ).values('method').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # Sales by cashier
        sales_by_cashier = completed_sales.values(
            cashier_name=F('cashier__username')
        ).annotate(
            total_sales=Count('id'),
            total_revenue=Sum('total')
        ).order_by('-total_revenue')
        
        # Top selling products
        top_products = SaleItem.objects.filter(
            sale__in=completed_sales
        ).values(
            'product_name'
        ).annotate(
            quantity_sold=Sum('quantity'),
            total_revenue=Sum('total')
        ).order_by('-quantity_sold')[:10]
        
        # Sales by hour (for today)
        if period == 'today':
            hourly_sales = completed_sales.extra(
                select={'hour': "EXTRACT(hour FROM created_at)"}
            ).values('hour').annotate(
                sales_count=Count('id'),
                revenue=Sum('total')
            ).order_by('hour')
        else:
            hourly_sales = []
        
        return Response({
            'period': {
                'start': start,
                'end': end,
                'label': period
            },
            'summary': {
                'total_sales': total_sales,
                'total_revenue': float(total_revenue),
                'total_tax': float(total_tax),
                'total_discount': float(total_discount),
                'average_sale': float(total_revenue / total_sales) if total_sales > 0 else 0
            },
            'payment_methods': list(payment_methods),
            'sales_by_cashier': list(sales_by_cashier),
            'top_products': list(top_products),
            'hourly_sales': list(hourly_sales)
        })


class InventoryReportView(APIView):
    """Generate inventory reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get all products with stock info
        products = Product.objects.filter(is_active=True)
        
        # Stock summary
        total_products = products.count()
        total_stock_value = sum(
            p.stock * p.cost_price for p in products
        )
        
        # Low stock items
        low_stock = products.filter(
            stock__lte=F('low_stock_threshold')
        ).values(
            'id', 'name', 'barcode', 'stock', 'low_stock_threshold'
        )
        
        # Out of stock
        out_of_stock = products.filter(stock=0).count()
        
        # Products by category
        by_category = products.values(
            category_name=F('category__name')
        ).annotate(
            product_count=Count('id'),
            total_stock=Sum('stock'),
            stock_value=Sum(F('stock') * F('cost_price'))
        )
        
        # Recent stock movements
        recent_movements = StockMovement.objects.select_related(
            'product', 'created_by'
        ).order_by('-created_at')[:20].values(
            'id', 'product__name', 'movement_type',
            'quantity', 'stock_before', 'stock_after',
            'created_by__username', 'created_at'
        )
        
        # Active stock alerts
        active_alerts = StockAlert.objects.filter(
            status='active'
        ).select_related('product').values(
            'id', 'product__name', 'product__barcode',
            'current_stock', 'threshold', 'created_at'
        )
        
        return Response({
            'summary': {
                'total_products': total_products,
                'total_stock_value': float(total_stock_value),
                'low_stock_count': low_stock.count(),
                'out_of_stock_count': out_of_stock,
                'active_alerts': active_alerts.count()
            },
            'low_stock_items': list(low_stock),
            'by_category': list(by_category),
            'recent_movements': list(recent_movements),
            'active_alerts': list(active_alerts)
        })


class ProfitReportView(APIView):
    """Generate profit/loss reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get date range
        period = request.query_params.get('period', 'today')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        now = timezone.now()
        if period == 'today':
            start = now.replace(hour=0, minute=0, second=0)
        elif period == 'week':
            start = now - timedelta(days=7)
        elif period == 'month':
            start = now - timedelta(days=30)
        elif period == 'custom' and start_date:
            from dateutil import parser
            start = parser.parse(start_date)
        else:
            start = now.replace(hour=0, minute=0, second=0)
        
        end = timezone.now()
        if end_date:
            from dateutil import parser
            end = parser.parse(end_date)
        
        # Get completed sales
        sales = Sale.objects.filter(
            status='completed',
            created_at__gte=start,
            created_at__lte=end
        )
        
        # Get sale items
        items = SaleItem.objects.filter(sale__in=sales)
        
        # Calculate profit
        total_revenue = items.aggregate(total=Sum('total'))['total'] or 0
        total_cost = items.aggregate(
            total=Sum(F('cost_price') * F('quantity'))
        )['total'] or 0
        total_tax = sales.aggregate(total=Sum('tax_amount'))['total'] or 0
        
        gross_profit = total_revenue - total_tax - total_cost
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Profit by product
        product_profit = items.values(
            'product_name'
        ).annotate(
            revenue=Sum('total'),
            cost=Sum(F('cost_price') * F('quantity')),
            quantity_sold=Sum('quantity')
        ).annotate(
            profit=F('revenue') - F('cost')
        ).order_by('-profit')[:20]
        
        # Profit by category
        category_profit = items.values(
            category_name=F('product__category__name')
        ).annotate(
            revenue=Sum('total'),
            cost=Sum(F('cost_price') * F('quantity'))
        ).annotate(
            profit=F('revenue') - F('cost')
        ).order_by('-profit')
        
        return Response({
            'period': {
                'start': start,
                'end': end,
                'label': period
            },
            'summary': {
                'total_revenue': float(total_revenue),
                'total_cost': float(total_cost),
                'total_tax': float(total_tax),
                'gross_profit': float(gross_profit),
                'profit_margin': float(profit_margin)
            },
            'product_profit': list(product_profit),
            'category_profit': list(category_profit)
        })


class DashboardStatsView(APIView):
    """Get dashboard statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0)
        
        # Today's sales
        today_sales = Sale.objects.filter(
            created_at__gte=today_start,
            status='completed'
        )
        
        today_revenue = today_sales.aggregate(total=Sum('total'))['total'] or 0
        today_sales_count = today_sales.count()
        
        # This month
        month_start = now.replace(day=1, hour=0, minute=0, second=0)
        month_sales = Sale.objects.filter(
            created_at__gte=month_start,
            status='completed'
        )
        month_revenue = month_sales.aggregate(total=Sum('total'))['total'] or 0
        
        # Low stock alerts
        low_stock_count = StockAlert.objects.filter(status='active').count()
        
        # Pending payments
        pending_payments = Payment.objects.filter(
            status__in=['pending', 'processing']
        ).count()
        
        # Recent sales
        recent_sales = Sale.objects.select_related('cashier').order_by(
            '-created_at'
        )[:5].values(
            'id', 'sale_number', 'total', 'status',
            'payment_status', 'cashier__username', 'created_at'
        )
        
        return Response({
            'today': {
                'sales_count': today_sales_count,
                'revenue': float(today_revenue)
            },
            'month': {
                'revenue': float(month_revenue)
            },
            'alerts': {
                'low_stock': low_stock_count,
                'pending_payments': pending_payments
            },
            'recent_sales': list(recent_sales)
        })
