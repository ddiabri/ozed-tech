"""
Admin export actions for CSV and Excel
"""
from datetime import datetime
from ozed_tech_project.export_utils import CSVExporter, ExcelExporter, PDFExporter


def export_to_csv_action(modeladmin, request, queryset):
    """Generic admin action to export selected items to CSV"""
    model_name = queryset.model.__name__

    # Get field names from the model
    fields = [field.name for field in queryset.model._meta.fields if field.name not in ['id']]
    headers = [field.replace('_', ' ').title() for field in fields]

    rows = []
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field)
            # Handle related objects
            if hasattr(value, '__str__'):
                value = str(value)
            row.append(value if value is not None else 'N/A')
        rows.append(row)

    filename = f'{model_name.lower()}_export_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return CSVExporter.export_to_csv(filename, headers, rows)

export_to_csv_action.short_description = "Export selected to CSV"


def export_to_excel_action(modeladmin, request, queryset):
    """Generic admin action to export selected items to Excel"""
    model_name = queryset.model.__name__

    # Get field names from the model
    fields = [field.name for field in queryset.model._meta.fields if field.name not in ['id']]
    headers = [field.replace('_', ' ').title() for field in fields]

    rows = []
    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field)
            # Handle related objects
            if hasattr(value, '__str__') and not isinstance(value, (int, float, bool)):
                value = str(value)
            row.append(value if value is not None else 'N/A')
        rows.append(row)

    filename = f'{model_name.lower()}_export_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return ExcelExporter.export_to_excel(filename, model_name, headers, rows)

export_to_excel_action.short_description = "Export selected to Excel"


def export_items_csv_action(modeladmin, request, queryset):
    """Export inventory items to CSV"""
    headers = ['SKU', 'Name', 'Category', 'Supplier', 'Quantity', 'Unit Price',
              'Low Stock Threshold', 'Stock Status', 'Total Value', 'Active']

    rows = []
    for item in queryset:
        rows.append([
            item.sku or 'N/A',
            item.name,
            item.category.name if item.category else 'N/A',
            item.supplier.name if item.supplier else 'N/A',
            item.quantity,
            f'{item.unit_price:.2f}',
            item.low_stock_threshold,
            item.stock_status,
            f'{item.total_value:.2f}',
            'Yes' if item.is_active else 'No'
        ])

    filename = f'inventory_items_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return CSVExporter.export_to_csv(filename, headers, rows)

export_items_csv_action.short_description = "📥 Export selected items to CSV"


def export_items_excel_action(modeladmin, request, queryset):
    """Export inventory items to Excel"""
    headers = ['SKU', 'Name', 'Category', 'Supplier', 'Quantity', 'Unit Price',
              'Low Stock Threshold', 'Stock Status', 'Total Value', 'Active']

    rows = []
    for item in queryset:
        rows.append([
            item.sku or 'N/A',
            item.name,
            item.category.name if item.category else 'N/A',
            item.supplier.name if item.supplier else 'N/A',
            item.quantity,
            float(item.unit_price),
            item.low_stock_threshold,
            item.stock_status,
            float(item.total_value),
            'Yes' if item.is_active else 'No'
        ])

    filename = f'inventory_items_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return ExcelExporter.export_to_excel(filename, 'Inventory Items', headers, rows)

export_items_excel_action.short_description = "📊 Export selected items to Excel"


def export_sales_orders_csv_action(modeladmin, request, queryset):
    """Export sales orders to CSV"""
    headers = ['Order Number', 'Customer', 'Order Date', 'Expected Delivery',
              'Status', 'Payment Status', 'Subtotal', 'Discount', 'Tax',
              'Shipping', 'Total Amount']

    rows = []
    for order in queryset:
        rows.append([
            order.order_number,
            order.customer.company_name,
            order.order_date.strftime('%Y-%m-%d'),
            order.expected_delivery_date.strftime('%Y-%m-%d') if order.expected_delivery_date else 'N/A',
            order.get_status_display(),
            order.get_payment_status_display(),
            f'{order.subtotal:.2f}',
            f'{order.discount:.2f}',
            f'{order.tax:.2f}',
            f'{order.shipping_cost:.2f}',
            f'{order.total_amount:.2f}'
        ])

    filename = f'sales_orders_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return CSVExporter.export_to_csv(filename, headers, rows)

export_sales_orders_csv_action.short_description = "📥 Export selected orders to CSV"


def export_sales_orders_excel_action(modeladmin, request, queryset):
    """Export sales orders to Excel"""
    headers = ['Order Number', 'Customer', 'Order Date', 'Expected Delivery',
              'Status', 'Payment Status', 'Subtotal', 'Discount', 'Tax',
              'Shipping', 'Total Amount']

    rows = []
    for order in queryset:
        rows.append([
            order.order_number,
            order.customer.company_name,
            order.order_date.strftime('%Y-%m-%d'),
            order.expected_delivery_date.strftime('%Y-%m-%d') if order.expected_delivery_date else 'N/A',
            order.get_status_display(),
            order.get_payment_status_display(),
            float(order.subtotal),
            float(order.discount),
            float(order.tax),
            float(order.shipping_cost),
            float(order.total_amount)
        ])

    filename = f'sales_orders_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return ExcelExporter.export_to_excel(filename, 'Sales Orders', headers, rows)

export_sales_orders_excel_action.short_description = "📊 Export selected orders to Excel"


def generate_invoice_action(modeladmin, request, queryset):
    """Generate PDF invoice for the first selected sales order"""
    if queryset.count() != 1:
        from django.contrib import messages
        messages.warning(request, 'Please select exactly one sales order to generate an invoice.')
        return None

    sales_order = queryset.first()
    return PDFExporter.create_invoice(sales_order)

generate_invoice_action.short_description = "📄 Generate PDF Invoice"


def export_customers_csv_action(modeladmin, request, queryset):
    """Export customers to CSV"""
    headers = ['Company Name', 'Customer Type', 'Industry', 'Address', 'City',
              'State', 'Country', 'Postal Code', 'Credit Limit', 'Website', 'Created Date']

    rows = []
    for customer in queryset:
        rows.append([
            customer.company_name,
            customer.get_customer_type_display(),
            customer.industry or 'N/A',
            customer.address or 'N/A',
            customer.city or 'N/A',
            customer.state or 'N/A',
            customer.country or 'N/A',
            customer.postal_code or 'N/A',
            f'{customer.credit_limit:.2f}' if customer.credit_limit else 'N/A',
            customer.website or 'N/A',
            customer.created_at.strftime('%Y-%m-%d')
        ])

    filename = f'customers_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return CSVExporter.export_to_csv(filename, headers, rows)

export_customers_csv_action.short_description = "📥 Export selected customers to CSV"


def export_customers_excel_action(modeladmin, request, queryset):
    """Export customers to Excel"""
    headers = ['Company Name', 'Customer Type', 'Industry', 'Address', 'City',
              'State', 'Country', 'Postal Code', 'Credit Limit', 'Website', 'Created Date']

    rows = []
    for customer in queryset:
        rows.append([
            customer.company_name,
            customer.get_customer_type_display(),
            customer.industry or 'N/A',
            customer.address or 'N/A',
            customer.city or 'N/A',
            customer.state or 'N/A',
            customer.country or 'N/A',
            customer.postal_code or 'N/A',
            float(customer.credit_limit) if customer.credit_limit else 0,
            customer.website or 'N/A',
            customer.created_at.strftime('%Y-%m-%d')
        ])

    filename = f'customers_{request.user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return ExcelExporter.export_to_excel(filename, 'Customers', headers, rows)

export_customers_excel_action.short_description = "📊 Export selected customers to Excel"
