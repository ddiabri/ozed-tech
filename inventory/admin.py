from django.contrib import admin
from ozed_tech_project.admin_export import (
    export_items_csv_action,
    export_items_excel_action,
    export_sales_orders_csv_action,
    export_sales_orders_excel_action,
    generate_invoice_action
)
from .models import (
    Category, Supplier, Item, PurchaseOrder, PurchaseOrderItem,
    SalesOrder, SalesOrderItem, RFQ, RFQItem, Quote, QuoteItem
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'email', 'phone', 'created_at']
    search_fields = ['name', 'contact_person', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'supplier', 'quantity', 'unit_price', 'stock_status', 'is_active']
    list_filter = ['category', 'supplier', 'is_active', 'created_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at', 'stock_status', 'is_low_stock', 'total_value']
    actions = [export_items_csv_action, export_items_excel_action]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'description', 'is_active')
        }),
        ('Categorization', {
            'fields': ('category', 'supplier')
        }),
        ('Stock Information', {
            'fields': ('quantity', 'low_stock_threshold', 'unit_price')
        }),
        ('Computed Values', {
            'fields': ('stock_status', 'is_low_stock', 'total_value'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    fields = ['item', 'quantity', 'unit_price']
    can_delete = True

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ['item']
        return []


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'supplier', 'order_date', 'expected_delivery_date', 'status', 'total_amount', 'total_items', 'created_at']
    list_filter = ['status', 'supplier', 'order_date', 'created_at']
    search_fields = ['order_number', 'supplier__name', 'customer__company_name', 'notes']
    readonly_fields = ['total_amount', 'total_items', 'created_at', 'updated_at']
    inlines = [PurchaseOrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'supplier', 'status')
        }),
        ('Dates', {
            'fields': ('order_date', 'expected_delivery_date')
        }),
        ('Details', {
            'fields': ('notes',)
        }),
        ('Summary', {
            'fields': ('total_amount', 'total_items'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Convert order_number to uppercase before saving"""
        obj.order_number = obj.order_number.upper()
        super().save_model(request, obj, form, change)


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'item', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['purchase_order__status', 'item__category']
    search_fields = ['purchase_order__order_number', 'item__name', 'item__sku']

    def get_fields(self, request, obj=None):
        fields = ['purchase_order', 'item', 'quantity', 'unit_price']
        if obj:  # editing an existing object
            fields.extend(['created_at', 'updated_at'])
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ['created_at', 'updated_at']
        return []


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 0
    fields = ['item', 'quantity', 'unit_price', 'discount']
    can_delete = True

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ['item']
        return []


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'contact', 'order_date', 'status', 'payment_status', 'total_amount', 'total_items', 'created_at']
    list_filter = ['status', 'payment_status', 'customer', 'order_date', 'created_at']
    search_fields = ['order_number', 'customer__company_name', 'contact__first_name', 'contact__last_name', 'notes']
    readonly_fields = ['subtotal', 'total_amount', 'total_items', 'total_quantity', 'created_at', 'updated_at']
    actions = [export_sales_orders_csv_action, export_sales_orders_excel_action, generate_invoice_action]
    inlines = [SalesOrderItemInline]
    date_hierarchy = 'order_date'
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'contact', 'status', 'payment_status')
        }),
        ('Dates', {
            'fields': ('order_date', 'expected_delivery_date', 'actual_delivery_date')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'discount', 'tax', 'shipping_cost', 'total_amount')
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Summary', {
            'fields': ('total_items', 'total_quantity'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Convert order_number to uppercase and calculate totals"""
        obj.order_number = obj.order_number.upper()
        super().save_model(request, obj, form, change)
        obj.calculate_totals()


@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    list_display = ['sales_order', 'item', 'quantity', 'unit_price', 'discount', 'subtotal']
    list_filter = ['sales_order__status', 'item__category']
    search_fields = ['sales_order__order_number', 'item__name', 'item__sku']

    def get_fields(self, request, obj=None):
        fields = ['sales_order', 'item', 'quantity', 'unit_price', 'discount']
        if obj:
            fields.extend(['created_at', 'updated_at'])
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_at', 'updated_at']
        return []


# RFQ Admin

class RFQItemInline(admin.TabularInline):
    model = RFQItem
    extra = 0
    fields = ['item', 'requested_quantity', 'notes']
    can_delete = True

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['item']
        return []


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = ['rfq_number', 'customer', 'contact', 'requested_by', 'status', 'request_date', 'required_by_date', 'total_items', 'created_at']
    list_filter = ['status', 'customer', 'request_date', 'created_at']
    search_fields = ['rfq_number', 'customer__company_name', 'contact__first_name', 'contact__last_name', 'notes']
    readonly_fields = ['total_items', 'total_quantity', 'created_at', 'updated_at']
    inlines = [RFQItemInline]
    date_hierarchy = 'request_date'
    fieldsets = (
        ('RFQ Information', {
            'fields': ('rfq_number', 'customer', 'contact', 'requested_by', 'status')
        }),
        ('Dates', {
            'fields': ('request_date', 'required_by_date')
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes')
        }),
        ('Summary', {
            'fields': ('total_items', 'total_quantity'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Convert rfq_number to uppercase before saving"""
        obj.rfq_number = obj.rfq_number.upper()
        super().save_model(request, obj, form, change)


@admin.register(RFQItem)
class RFQItemAdmin(admin.ModelAdmin):
    list_display = ['rfq', 'item', 'requested_quantity', 'created_at']
    list_filter = ['rfq__status', 'item__category']
    search_fields = ['rfq__rfq_number', 'item__name', 'item__sku']

    def get_fields(self, request, obj=None):
        fields = ['rfq', 'item', 'requested_quantity', 'notes']
        if obj:
            fields.extend(['created_at', 'updated_at'])
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_at', 'updated_at']
        return []


# Quote Admin

class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0
    fields = ['item', 'quantity', 'unit_price', 'discount', 'notes']
    can_delete = True

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['item']
        return []


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'version', 'customer', 'contact', 'sales_rep', 'status', 'quote_date', 'expiration_date', 'is_expired', 'total_amount', 'total_items', 'created_at']
    list_filter = ['status', 'customer', 'sales_rep', 'quote_date', 'created_at']
    search_fields = ['quote_number', 'customer__company_name', 'contact__first_name', 'contact__last_name', 'notes']
    readonly_fields = ['subtotal', 'total_amount', 'total_items', 'total_quantity', 'is_expired', 'created_at', 'updated_at']
    inlines = [QuoteItemInline]
    date_hierarchy = 'quote_date'
    fieldsets = (
        ('Quote Information', {
            'fields': ('quote_number', 'version', 'rfq', 'customer', 'contact', 'sales_rep', 'status')
        }),
        ('Dates', {
            'fields': ('quote_date', 'expiration_date', 'is_expired')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'discount', 'tax', 'shipping_cost', 'total_amount')
        }),
        ('Terms', {
            'fields': ('payment_terms', 'delivery_terms', 'validity_period')
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Conversion', {
            'fields': ('sales_order',),
            'classes': ('collapse',)
        }),
        ('Summary', {
            'fields': ('total_items', 'total_quantity'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Convert quote_number to uppercase and calculate totals"""
        obj.quote_number = obj.quote_number.upper()
        super().save_model(request, obj, form, change)
        obj.calculate_totals()


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = ['quote', 'item', 'quantity', 'unit_price', 'discount', 'subtotal']
    list_filter = ['quote__status', 'item__category']
    search_fields = ['quote__quote_number', 'item__name', 'item__sku']

    def get_fields(self, request, obj=None):
        fields = ['quote', 'item', 'quantity', 'unit_price', 'discount', 'notes']
        if obj:
            fields.extend(['created_at', 'updated_at'])
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_at', 'updated_at']
        return []
