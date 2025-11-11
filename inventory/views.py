from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
from ozed_tech_project.export_utils import CSVExporter, ExcelExporter, PDFExporter
from .models import (
    Category, Supplier, Item, PurchaseOrder, PurchaseOrderItem,
    SalesOrder, SalesOrderItem, RFQ, RFQItem, Quote, QuoteItem
)
from .serializers import (
    CategorySerializer,
    SupplierSerializer,
    ItemSerializer,
    ItemListSerializer,
    PurchaseOrderSerializer,
    PurchaseOrderListSerializer,
    PurchaseOrderItemSerializer,
    SalesOrderSerializer,
    SalesOrderListSerializer,
    SalesOrderItemSerializer,
    RFQSerializer,
    RFQListSerializer,
    RFQItemSerializer,
    QuoteSerializer,
    QuoteListSerializer,
    QuoteItemSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing suppliers
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'contact_person', 'email']
    ordering_fields = ['name', 'created_at']


class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing inventory items with advanced filtering
    """
    queryset = Item.objects.select_related('category', 'supplier').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'created_at', 'quantity', 'unit_price']
    filterset_fields = ['category', 'supplier', 'is_active']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ItemListSerializer
        return ItemSerializer

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items that are low on stock"""
        low_stock_items = [item for item in self.queryset if item.is_low_stock]
        serializer = ItemListSerializer(low_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get items that are out of stock"""
        out_of_stock_items = self.queryset.filter(quantity=0)
        serializer = ItemListSerializer(out_of_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust stock quantity (add or remove)"""
        item = self.get_object()
        adjustment = request.data.get('adjustment', 0)

        try:
            adjustment = int(adjustment)
        except ValueError:
            return Response(
                {'error': 'Adjustment must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_quantity = item.quantity + adjustment

        if new_quantity < 0:
            return Response(
                {'error': 'Cannot reduce stock below zero'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = new_quantity
        item.save()

        serializer = ItemSerializer(item)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export items to CSV"""
        items = self.filter_queryset(self.get_queryset())

        headers = ['SKU', 'Name', 'Category', 'Supplier', 'Quantity', 'Unit Price',
                  'Low Stock Threshold', 'Stock Status', 'Total Value', 'Active']

        rows = []
        for item in items:
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

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        """Export items to Excel"""
        items = self.filter_queryset(self.get_queryset())

        headers = ['SKU', 'Name', 'Category', 'Supplier', 'Quantity', 'Unit Price',
                  'Low Stock Threshold', 'Stock Status', 'Total Value', 'Active']

        rows = []
        for item in items:
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


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase orders
    """
    queryset = PurchaseOrder.objects.select_related('supplier').prefetch_related('items__item').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'supplier__name', 'notes']
    ordering_fields = ['order_date', 'created_at', 'status']
    filterset_fields = ['supplier', 'status']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add an item to the purchase order"""
        purchase_order = self.get_object()

        if purchase_order.status not in ['draft', 'pending']:
            return Response(
                {'error': 'Cannot add items to orders with status: ' + purchase_order.status},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PurchaseOrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(purchase_order=purchase_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change the status of the purchase order"""
        purchase_order = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(PurchaseOrder.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        purchase_order.status = new_status
        purchase_order.save()

        serializer = PurchaseOrderSerializer(purchase_order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def receive_order(self, request, pk=None):
        """Mark order as received and update inventory quantities"""
        purchase_order = self.get_object()

        if purchase_order.status == 'received':
            return Response(
                {'error': 'Order already received'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if purchase_order.status not in ['approved', 'pending']:
            return Response(
                {'error': 'Can only receive approved or pending orders'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update inventory quantities
        for po_item in purchase_order.items.all():
            po_item.item.quantity += po_item.quantity
            po_item.item.save()

        purchase_order.status = 'received'
        purchase_order.save()

        serializer = PurchaseOrderSerializer(purchase_order)
        return Response(serializer.data)


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase order items
    """
    queryset = PurchaseOrderItem.objects.select_related('purchase_order', 'item').all()
    serializer_class = PurchaseOrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['purchase_order', 'item']


class SalesOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sales orders
    """
    queryset = SalesOrder.objects.select_related('customer', 'contact').prefetch_related('items__item').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_number', 'customer__company_name', 'notes']
    ordering_fields = ['order_date', 'created_at', 'status', 'total_amount']
    filterset_fields = ['customer', 'status', 'payment_status']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return SalesOrderListSerializer
        return SalesOrderSerializer

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add an item to the sales order"""
        sales_order = self.get_object()

        if sales_order.status not in ['draft', 'confirmed']:
            return Response(
                {'error': 'Cannot add items to orders with status: ' + sales_order.status},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SalesOrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sales_order=sales_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change the status of the sales order"""
        sales_order = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(SalesOrder.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sales_order.status = new_status
        sales_order.save()

        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm_order(self, request, pk=None):
        """Confirm order and deduct inventory"""
        sales_order = self.get_object()

        if sales_order.status != 'draft':
            return Response(
                {'error': 'Can only confirm draft orders'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check stock availability for all items
        insufficient_items = []
        for order_item in sales_order.items.all():
            if order_item.item.quantity < order_item.quantity:
                insufficient_items.append({
                    'item': order_item.item.name,
                    'required': order_item.quantity,
                    'available': order_item.item.quantity
                })

        if insufficient_items:
            return Response(
                {'error': 'Insufficient stock', 'items': insufficient_items},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduct inventory
        for order_item in sales_order.items.all():
            order_item.item.quantity -= order_item.quantity
            order_item.item.save()

        sales_order.status = 'confirmed'
        sales_order.save()

        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_shipped(self, request, pk=None):
        """Mark order as shipped"""
        sales_order = self.get_object()

        if sales_order.status not in ['confirmed', 'processing']:
            return Response(
                {'error': 'Can only ship confirmed or processing orders'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sales_order.status = 'shipped'
        sales_order.save()

        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Mark order as delivered"""
        sales_order = self.get_object()

        if sales_order.status != 'shipped':
            return Response(
                {'error': 'Can only mark shipped orders as delivered'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from datetime import date
        sales_order.status = 'delivered'
        sales_order.actual_delivery_date = date.today()
        sales_order.save()

        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        """Cancel order and restore inventory if confirmed"""
        sales_order = self.get_object()

        if sales_order.status in ['delivered', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel delivered or already cancelled orders'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Restore inventory if order was confirmed
        if sales_order.status in ['confirmed', 'processing', 'shipped']:
            for order_item in sales_order.items.all():
                order_item.item.quantity += order_item.quantity
                order_item.item.save()

        sales_order.status = 'cancelled'
        sales_order.save()

        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export sales orders to CSV"""
        orders = self.filter_queryset(self.get_queryset())

        headers = ['Order Number', 'Customer', 'Order Date', 'Expected Delivery',
                  'Status', 'Payment Status', 'Subtotal', 'Discount', 'Tax',
                  'Shipping', 'Total Amount']

        rows = []
        for order in orders:
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

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        """Export sales orders to Excel"""
        orders = self.filter_queryset(self.get_queryset())

        headers = ['Order Number', 'Customer', 'Order Date', 'Expected Delivery',
                  'Status', 'Payment Status', 'Subtotal', 'Discount', 'Tax',
                  'Shipping', 'Total Amount']

        rows = []
        for order in orders:
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

    @action(detail=True, methods=['get'])
    def generate_invoice(self, request, pk=None):
        """Generate PDF invoice for a sales order"""
        sales_order = self.get_object()
        return PDFExporter.create_invoice(sales_order)


class SalesOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sales order items
    """
    queryset = SalesOrderItem.objects.select_related('sales_order', 'item').all()
    serializer_class = SalesOrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sales_order', 'item']


class RFQViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing RFQs (Requests for Quote)
    """
    queryset = RFQ.objects.select_related('customer', 'contact', 'requested_by').prefetch_related('items__item').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['rfq_number', 'customer__company_name', 'notes']
    ordering_fields = ['request_date', 'required_by_date', 'created_at']
    filterset_fields = ['status', 'customer', 'requested_by']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return RFQListSerializer
        return RFQSerializer

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit RFQ for review"""
        rfq = self.get_object()

        if rfq.status != 'draft':
            return Response(
                {'error': 'Only draft RFQs can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not rfq.items.exists():
            return Response(
                {'error': 'Cannot submit RFQ without items'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rfq.status = 'submitted'
        rfq.save()

        serializer = RFQSerializer(rfq)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start_review(self, request, pk=None):
        """Start reviewing an RFQ"""
        rfq = self.get_object()

        if rfq.status != 'submitted':
            return Response(
                {'error': 'Only submitted RFQs can be reviewed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rfq.status = 'under_review'
        if not rfq.requested_by:
            rfq.requested_by = request.user
        rfq.save()

        serializer = RFQSerializer(rfq)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an RFQ"""
        rfq = self.get_object()

        if rfq.status in ['rejected', 'quoted']:
            return Response(
                {'error': f'Cannot reject RFQ with status: {rfq.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rfq.status = 'rejected'
        rfq.save()

        serializer = RFQSerializer(rfq)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_quote(self, request, pk=None):
        """Create a quote from this RFQ"""
        rfq = self.get_object()

        if rfq.status not in ['under_review', 'submitted']:
            return Response(
                {'error': 'RFQ must be under review to create quote'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get quote number
        quote_number = request.data.get('quote_number')
        if not quote_number:
            return Response(
                {'error': 'quote_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create quote
        expiration_days = int(request.data.get('expiration_days', 30))
        quote = Quote.objects.create(
            quote_number=quote_number.upper(),
            rfq=rfq,
            customer=rfq.customer,
            contact=rfq.contact,
            sales_rep=request.user,
            quote_date=datetime.now().date(),
            expiration_date=datetime.now().date() + timedelta(days=expiration_days),
            delivery_terms=request.data.get('delivery_terms', ''),
            notes=request.data.get('notes', ''),
        )

        # Copy items from RFQ to Quote
        for rfq_item in rfq.items.all():
            QuoteItem.objects.create(
                quote=quote,
                item=rfq_item.item,
                quantity=rfq_item.requested_quantity,
                unit_price=rfq_item.item.unit_price,
                notes=rfq_item.notes
            )

        quote.calculate_totals()

        # Update RFQ status
        rfq.status = 'quoted'
        rfq.save()

        serializer = QuoteSerializer(quote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add an item to the RFQ"""
        rfq = self.get_object()

        if rfq.status not in ['draft', 'submitted']:
            return Response(
                {'error': 'Cannot add items to RFQ in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RFQItemSerializer(data={**request.data, 'rfq': rfq.id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RFQItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing RFQ items
    """
    queryset = RFQItem.objects.select_related('rfq', 'item').all()
    serializer_class = RFQItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['rfq', 'item']


class QuoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Quotes
    """
    queryset = Quote.objects.select_related('rfq', 'customer', 'contact', 'sales_rep', 'sales_order').prefetch_related('items__item').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['quote_number', 'customer__company_name', 'notes']
    ordering_fields = ['quote_date', 'expiration_date', 'created_at', 'total_amount']
    filterset_fields = ['status', 'customer', 'sales_rep', 'rfq']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return QuoteListSerializer
        return QuoteSerializer

    @action(detail=True, methods=['post'])
    def send_to_customer(self, request, pk=None):
        """Mark quote as sent to customer"""
        quote = self.get_object()

        if quote.status not in ['draft', 'negotiating']:
            return Response(
                {'error': 'Only draft or negotiating quotes can be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )

        quote.status = 'sent'
        quote.save()

        serializer = QuoteSerializer(quote)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Mark quote as accepted by customer"""
        quote = self.get_object()

        if quote.status != 'sent':
            return Response(
                {'error': 'Only sent quotes can be accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quote.is_expired:
            return Response(
                {'error': 'Cannot accept expired quote'},
                status=status.HTTP_400_BAD_REQUEST
            )

        quote.status = 'accepted'
        quote.save()

        serializer = QuoteSerializer(quote)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject quote"""
        quote = self.get_object()

        if quote.status not in ['sent', 'negotiating']:
            return Response(
                {'error': f'Cannot reject quote with status: {quote.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        quote.status = 'rejected'
        quote.rejection_reason = request.data.get('rejection_reason', '')
        quote.save()

        serializer = QuoteSerializer(quote)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def request_revision(self, request, pk=None):
        """Request revision on quote (customer feedback)"""
        quote = self.get_object()

        if quote.status != 'sent':
            return Response(
                {'error': 'Only sent quotes can be revised'},
                status=status.HTTP_400_BAD_REQUEST
            )

        quote.status = 'negotiating'
        quote.save()

        serializer = QuoteSerializer(quote)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_revision(self, request, pk=None):
        """Create a new version of the quote"""
        original_quote = self.get_object()

        # Create new quote with incremented version
        new_quote = Quote.objects.create(
            quote_number=original_quote.quote_number,
            rfq=original_quote.rfq,
            customer=original_quote.customer,
            contact=original_quote.contact,
            sales_rep=request.user,
            version=original_quote.version + 1,
            status='draft',
            quote_date=datetime.now().date(),
            expiration_date=datetime.now().date() + timedelta(days=30),
            discount=original_quote.discount,
            tax=original_quote.tax,
            shipping_cost=original_quote.shipping_cost,
            payment_terms=original_quote.payment_terms,
            delivery_terms=original_quote.delivery_terms,
            validity_period=original_quote.validity_period,
            notes=original_quote.notes,
        )

        # Copy items
        for item in original_quote.items.all():
            QuoteItem.objects.create(
                quote=new_quote,
                item=item.item,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount,
                notes=item.notes
            )

        new_quote.calculate_totals()

        serializer = QuoteSerializer(new_quote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def convert_to_order(self, request, pk=None):
        """Convert accepted quote to sales order"""
        quote = self.get_object()

        if quote.status != 'accepted':
            return Response(
                {'error': 'Only accepted quotes can be converted to orders'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quote.sales_order:
            return Response(
                {'error': 'Quote has already been converted to an order'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check stock availability
        insufficient_items = []
        for quote_item in quote.items.all():
            if quote_item.item.quantity < quote_item.quantity:
                insufficient_items.append({
                    'item': quote_item.item.name,
                    'required': quote_item.quantity,
                    'available': quote_item.item.quantity
                })

        if insufficient_items:
            return Response(
                {'error': 'Insufficient stock', 'items': insufficient_items},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get order number
        order_number = request.data.get('order_number')
        if not order_number:
            return Response(
                {'error': 'order_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create sales order
        sales_order = SalesOrder.objects.create(
            order_number=order_number.upper(),
            customer=quote.customer,
            contact=quote.contact,
            order_date=datetime.now().date(),
            status='draft',
            payment_status='unpaid',
            discount=quote.discount,
            tax=quote.tax,
            shipping_cost=quote.shipping_cost,
            notes=f"Converted from Quote {quote.quote_number}. {quote.notes}"
        )

        # Copy items from quote to sales order
        for quote_item in quote.items.all():
            SalesOrderItem.objects.create(
                sales_order=sales_order,
                item=quote_item.item,
                quantity=quote_item.quantity,
                unit_price=quote_item.unit_price,
                discount=quote_item.discount
            )

        sales_order.calculate_totals()

        # Link quote to sales order
        quote.sales_order = sales_order
        quote.status = 'converted'
        quote.save()

        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add an item to the quote"""
        quote = self.get_object()

        if quote.status not in ['draft', 'negotiating']:
            return Response(
                {'error': 'Cannot add items to quote in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = QuoteItemSerializer(data={**request.data, 'quote': quote.id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF quote document"""
        from ozed_tech_project.export_utils import PDFExporter

        quote = self.get_object()
        return PDFExporter.create_quote_pdf(quote)


class QuoteItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Quote items
    """
    queryset = QuoteItem.objects.select_related('quote', 'item').all()
    serializer_class = QuoteItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quote', 'item']
