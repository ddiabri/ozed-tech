from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, Avg, F
from django.utils import timezone
from django.shortcuts import render
from datetime import timedelta
from decimal import Decimal

from inventory.models import Item, SalesOrder, PurchaseOrder
from crm.models import Customer, Interaction


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """
    Get overview statistics for the dashboard
    """
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    # Inventory Stats
    total_items = Item.objects.filter(is_active=True).count()
    low_stock_count = Item.objects.filter(
        is_active=True,
        quantity__lte=F('low_stock_threshold')
    ).count()
    out_of_stock_count = Item.objects.filter(is_active=True, quantity=0).count()
    total_inventory_value = Item.objects.filter(is_active=True).aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or Decimal('0.00')

    # Sales Stats
    total_sales_orders = SalesOrder.objects.count()
    confirmed_orders = SalesOrder.objects.filter(status__in=['confirmed', 'processing', 'shipped']).count()
    pending_orders = SalesOrder.objects.filter(status='draft').count()
    delivered_orders = SalesOrder.objects.filter(status='delivered').count()

    # Recent sales (last 30 days)
    recent_sales = SalesOrder.objects.filter(
        order_date__gte=last_30_days
    ).aggregate(
        total_revenue=Sum('total_amount'),
        order_count=Count('id')
    )

    # Payment Status
    unpaid_amount = SalesOrder.objects.filter(
        payment_status='unpaid',
        status__in=['confirmed', 'processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # Purchase Orders
    pending_po = PurchaseOrder.objects.filter(
        status__in=['draft', 'pending', 'approved']
    ).count()

    # CRM Stats
    total_customers = Customer.objects.count()
    active_customers = Customer.objects.filter(customer_type='active').count()
    prospect_customers = Customer.objects.filter(customer_type='prospect').count()

    # Recent interactions
    recent_interactions = Interaction.objects.filter(
        interaction_date__gte=timezone.now() - timedelta(days=7)
    ).count()

    return Response({
        'inventory': {
            'total_items': total_items,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_value': float(total_inventory_value),
        },
        'sales': {
            'total_orders': total_sales_orders,
            'confirmed_orders': confirmed_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'recent_revenue': float(recent_sales['total_revenue'] or 0),
            'recent_order_count': recent_sales['order_count'],
            'unpaid_amount': float(unpaid_amount),
        },
        'purchases': {
            'pending_orders': pending_po,
        },
        'crm': {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'prospect_customers': prospect_customers,
            'recent_interactions': recent_interactions,
        },
        'period': {
            'last_30_days': str(last_30_days),
            'today': str(today),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_analytics(request):
    """
    Get detailed inventory analytics
    """
    from django.db import models

    # Stock alerts
    low_stock_items = Item.objects.filter(
        is_active=True,
        quantity__lte=models.F('low_stock_threshold'),
        quantity__gt=0
    ).values('id', 'name', 'sku', 'quantity', 'low_stock_threshold')[:10]

    out_of_stock_items = Item.objects.filter(
        is_active=True,
        quantity=0
    ).values('id', 'name', 'sku')[:10]

    # Top items by value
    top_items_by_value = Item.objects.filter(
        is_active=True
    ).annotate(
        total_value=models.F('quantity') * models.F('unit_price')
    ).order_by('-total_value').values('id', 'name', 'sku', 'quantity', 'unit_price', 'total_value')[:10]

    # Category distribution
    category_stats = Item.objects.filter(
        is_active=True
    ).values('category__name').annotate(
        item_count=Count('id'),
        total_quantity=Sum('quantity')
    ).order_by('-item_count')

    return Response({
        'low_stock_items': list(low_stock_items),
        'out_of_stock_items': list(out_of_stock_items),
        'top_items_by_value': list(top_items_by_value),
        'category_distribution': list(category_stats),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_analytics(request):
    """
    Get detailed sales analytics
    """
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    # Sales by status
    status_breakdown = SalesOrder.objects.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('total_amount')
    ).order_by('status')

    # Payment status breakdown
    payment_breakdown = SalesOrder.objects.values('payment_status').annotate(
        count=Count('id'),
        total_amount=Sum('total_amount')
    ).order_by('payment_status')

    # Top customers by revenue
    top_customers = SalesOrder.objects.filter(
        status='delivered'
    ).values('customer__company_name').annotate(
        total_revenue=Sum('total_amount'),
        order_count=Count('id')
    ).order_by('-total_revenue')[:10]

    # Recent orders
    recent_orders = SalesOrder.objects.filter(
        order_date__gte=last_7_days
    ).values(
        'id', 'order_number', 'customer__company_name',
        'order_date', 'status', 'total_amount'
    ).order_by('-order_date')[:10]

    # Daily sales trend (last 30 days)
    from django.db.models.functions import TruncDate
    daily_sales = SalesOrder.objects.filter(
        order_date__gte=last_30_days
    ).annotate(
        date=TruncDate('order_date')
    ).values('date').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('date')

    return Response({
        'status_breakdown': list(status_breakdown),
        'payment_breakdown': list(payment_breakdown),
        'top_customers': list(top_customers),
        'recent_orders': list(recent_orders),
        'daily_sales_trend': list(daily_sales),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_analytics(request):
    """
    Get detailed customer analytics
    """
    # Customer type distribution
    customer_distribution = Customer.objects.values('customer_type').annotate(
        count=Count('id')
    ).order_by('customer_type')

    # Customers with most orders
    customers_by_orders = Customer.objects.annotate(
        order_count=Count('sales_orders')
    ).filter(order_count__gt=0).order_by('-order_count').values(
        'id', 'company_name', 'customer_type', 'order_count'
    )[:10]

    # Customers with most interactions
    customers_by_interactions = Customer.objects.annotate(
        interaction_count=Count('interactions')
    ).filter(interaction_count__gt=0).order_by('-interaction_count').values(
        'id', 'company_name', 'interaction_count'
    )[:10]

    # Interaction types breakdown
    interaction_types = Interaction.objects.values('interaction_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Customers without orders (prospects to follow up)
    customers_no_orders = Customer.objects.annotate(
        order_count=Count('sales_orders')
    ).filter(order_count=0, customer_type='prospect').values(
        'id', 'company_name', 'created_at'
    ).order_by('-created_at')[:10]

    return Response({
        'customer_distribution': list(customer_distribution),
        'top_customers_by_orders': list(customers_by_orders),
        'top_customers_by_interactions': list(customers_by_interactions),
        'interaction_types': list(interaction_types),
        'prospects_to_follow_up': list(customers_no_orders),
    })


def dashboard_view(request):
    """
    Render the dashboard HTML template
    """
    return render(request, 'dashboard.html')
