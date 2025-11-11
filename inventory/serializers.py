from rest_framework import serializers
from .models import (
    Category, Supplier, Item, PurchaseOrder, PurchaseOrderItem,
    SalesOrder, SalesOrderItem, RFQ, RFQItem, Quote, QuoteItem
)


class CategorySerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_items_count(self, obj):
        return obj.items.count()


class SupplierSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_items_count(self, obj):
        return obj.items.count()


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Item
        fields = [
            'id', 'name', 'sku', 'description',
            'category', 'category_name',
            'supplier', 'supplier_name',
            'quantity', 'low_stock_threshold', 'unit_price',
            'stock_status', 'is_low_stock', 'total_value',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_sku(self, value):
        """Ensure SKU is uppercase"""
        return value.upper()

    def validate_quantity(self, value):
        """Ensure quantity is not negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value

    def validate_unit_price(self, value):
        """Ensure unit price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero")
        return value


class ItemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'sku', 'category_name', 'quantity', 'unit_price', 'stock_status', 'is_active']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_sku = serializers.CharField(source='item.sku', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'item', 'item_name', 'item_sku', 'quantity', 'unit_price', 'subtotal']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'supplier_name',
            'order_date', 'expected_delivery_date', 'status',
            'notes', 'items', 'total_amount', 'total_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_order_number(self, value):
        """Ensure order number is uppercase"""
        return value.upper()


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'order_number', 'supplier_name', 'order_date', 'status', 'total_amount', 'total_items']


class SalesOrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_sku = serializers.CharField(source='item.sku', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SalesOrderItem
        fields = ['id', 'item', 'item_name', 'item_sku', 'quantity', 'unit_price', 'discount', 'subtotal']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate(self, data):
        """Check if there's enough stock"""
        item = data.get('item')
        quantity = data.get('quantity')

        if item and quantity:
            if item.quantity < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Insufficient stock. Only {item.quantity} available.'
                })

        return data


class SalesOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    items = SalesOrderItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = SalesOrder
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'contact', 'contact_name',
            'order_date', 'expected_delivery_date', 'actual_delivery_date',
            'status', 'payment_status',
            'subtotal', 'discount', 'tax', 'shipping_cost', 'total_amount',
            'notes', 'shipping_address',
            'items', 'total_items', 'total_quantity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['subtotal', 'total_amount', 'created_at', 'updated_at']

    def validate_order_number(self, value):
        """Ensure order number is uppercase"""
        return value.upper()


class SalesOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = SalesOrder
        fields = [
            'id', 'order_number', 'customer_name', 'order_date',
            'status', 'payment_status', 'total_amount', 'total_items'
        ]


# RFQ Serializers

class RFQItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_sku = serializers.CharField(source='item.sku', read_only=True)
    unit_price = serializers.DecimalField(source='item.unit_price', read_only=True, max_digits=10, decimal_places=2)
    available_quantity = serializers.IntegerField(source='item.quantity', read_only=True)

    class Meta:
        model = RFQItem
        fields = [
            'id', 'rfq', 'item', 'item_name', 'item_sku',
            'requested_quantity', 'unit_price', 'available_quantity',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RFQSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    items = RFQItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = RFQ
        fields = [
            'id', 'rfq_number', 'customer', 'customer_name', 'contact', 'contact_name',
            'requested_by', 'requested_by_name', 'status',
            'request_date', 'required_by_date',
            'notes', 'internal_notes',
            'items', 'total_items', 'total_quantity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_rfq_number(self, value):
        """Ensure RFQ number is uppercase"""
        return value.upper()


class RFQListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = RFQ
        fields = [
            'id', 'rfq_number', 'customer_name', 'request_date',
            'required_by_date', 'status', 'total_items'
        ]


# Quote Serializers

class QuoteItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_sku = serializers.CharField(source='item.sku', read_only=True)
    subtotal = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = QuoteItem
        fields = [
            'id', 'quote', 'item', 'item_name', 'item_sku',
            'quantity', 'unit_price', 'discount', 'subtotal',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['subtotal', 'created_at', 'updated_at']


class QuoteSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    sales_rep_name = serializers.CharField(source='sales_rep.username', read_only=True)
    rfq_number = serializers.CharField(source='rfq.rfq_number', read_only=True)
    items = QuoteItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Quote
        fields = [
            'id', 'quote_number', 'rfq', 'rfq_number',
            'customer', 'customer_name', 'contact', 'contact_name',
            'sales_rep', 'sales_rep_name', 'version', 'status',
            'quote_date', 'expiration_date', 'is_expired',
            'subtotal', 'discount', 'tax', 'shipping_cost', 'total_amount',
            'payment_terms', 'delivery_terms', 'validity_period',
            'notes', 'internal_notes', 'rejection_reason',
            'sales_order', 'items', 'total_items', 'total_quantity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['subtotal', 'total_amount', 'is_expired', 'created_at', 'updated_at']

    def validate_quote_number(self, value):
        """Ensure quote number is uppercase"""
        return value.upper()


class QuoteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Quote
        fields = [
            'id', 'quote_number', 'customer_name', 'quote_date',
            'expiration_date', 'is_expired', 'status', 'version',
            'total_amount', 'total_items'
        ]
