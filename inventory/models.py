from django.db import models
from django.core.validators import MinValueValidator
from datetime import date, timedelta
from decimal import Decimal


def get_default_expiration_date():
    """Return default expiration date (30 days from today)"""
    return date.today() + timedelta(days=30)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')

    # Stock tracking fields
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.01'))])

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (SKU: {self.sku})"

    @property
    def is_low_stock(self):
        """Check if item is below low stock threshold"""
        return self.quantity <= self.low_stock_threshold

    @property
    def stock_status(self):
        """Return stock status as a string"""
        if self.quantity == 0:
            return "Out of Stock"
        elif self.is_low_stock:
            return "Low Stock"
        return "In Stock"

    @property
    def total_value(self):
        """Calculate total value of stock"""
        return self.quantity * self.unit_price


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders', blank=True, null=True)
    customer = models.ForeignKey('crm.Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders', help_text="Customer this order is for")
    order_date = models.DateField(default=date.today)
    expected_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date', '-created_at']

    def __str__(self):
        supplier_name = self.supplier.name if self.supplier else "No Supplier"
        return f"PO-{self.order_number} - {supplier_name}"

    @property
    def total_amount(self):
        """Calculate total amount of purchase order"""
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        """Get total number of items in the order"""
        return self.items.count()


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='purchase_order_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['purchase_order', 'item']

    def __str__(self):
        return f"{self.item.name} - Qty: {self.quantity}"

    @property
    def subtotal(self):
        """Calculate subtotal for this line item"""
        return self.quantity * self.unit_price


class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('crm.Customer', on_delete=models.PROTECT, related_name='sales_orders')
    contact = models.ForeignKey('crm.Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_orders')

    order_date = models.DateField(default=date.today)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')

    # Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Additional info
    notes = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date', '-created_at']

    def __str__(self):
        return f"SO-{self.order_number} - {self.customer.company_name}"

    def calculate_totals(self):
        """Calculate and update order totals"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total_amount = self.subtotal - self.discount + self.tax + self.shipping_cost
        self.save()

    @property
    def total_items(self):
        """Get total number of items in the order"""
        return self.items.count()

    @property
    def total_quantity(self):
        """Get total quantity of all items"""
        return sum(item.quantity for item in self.items.all())


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='sales_order_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['sales_order', 'item']

    def __str__(self):
        return f"{self.item.name} - Qty: {self.quantity}"

    @property
    def subtotal(self):
        """Calculate subtotal for this line item"""
        return (self.quantity * self.unit_price) - self.discount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update order totals when item is saved
        self.sales_order.calculate_totals()


class RFQ(models.Model):
    """Request for Quote - Customer requests pricing for items"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('quoted', 'Quoted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    rfq_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('crm.Customer', on_delete=models.PROTECT, related_name='rfqs')
    contact = models.ForeignKey('crm.Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='rfqs')
    requested_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='rfqs_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Dates
    request_date = models.DateField(default=date.today)
    required_by_date = models.DateField(null=True, blank=True, help_text="When customer needs items by")

    # Details
    notes = models.TextField(blank=True, help_text="Special requirements or instructions")
    internal_notes = models.TextField(blank=True, help_text="Internal notes not visible to customer")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-request_date', '-created_at']
        verbose_name = 'RFQ'
        verbose_name_plural = 'RFQs'

    def __str__(self):
        return f"{self.rfq_number} - {self.customer.company_name}"

    @property
    def total_items(self):
        """Get total number of different items requested"""
        return self.items.count()

    @property
    def total_quantity(self):
        """Get total quantity requested"""
        return sum(item.requested_quantity for item in self.items.all())


class RFQItem(models.Model):
    """Individual item in an RFQ"""
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='rfq_items')
    requested_quantity = models.IntegerField(validators=[MinValueValidator(1)])
    notes = models.TextField(blank=True, help_text="Specific requirements for this item")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['rfq', 'item']

    def __str__(self):
        return f"{self.item.name} - Qty: {self.requested_quantity}"


class Quote(models.Model):
    """Sales Quote - Formal price quote to customer"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent to Customer'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('negotiating', 'Under Negotiation'),
        ('converted', 'Converted to Order'),
    ]

    PAYMENT_TERMS_CHOICES = [
        ('net_15', 'Net 15 Days'),
        ('net_30', 'Net 30 Days'),
        ('net_60', 'Net 60 Days'),
        ('cod', 'Cash on Delivery'),
        ('prepaid', 'Prepaid'),
    ]

    quote_number = models.CharField(max_length=50, unique=True)
    rfq = models.ForeignKey(RFQ, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes')
    customer = models.ForeignKey('crm.Customer', on_delete=models.PROTECT, related_name='quotes')
    contact = models.ForeignKey('crm.Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes')
    sales_rep = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes_created')

    version = models.IntegerField(default=1, help_text="Quote version number for revisions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Dates
    quote_date = models.DateField(default=date.today)
    expiration_date = models.DateField(default=get_default_expiration_date, help_text="Quote expires after this date")

    # Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Terms
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='net_30')
    delivery_terms = models.TextField(blank=True, help_text="Delivery timeframe and conditions")
    validity_period = models.CharField(max_length=100, default='30 days', help_text="How long quote is valid")

    # Additional info
    notes = models.TextField(blank=True, help_text="Terms, conditions, and notes for customer")
    internal_notes = models.TextField(blank=True, help_text="Internal notes not visible to customer")
    rejection_reason = models.TextField(blank=True, help_text="Why quote was rejected")

    # Conversion
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotes')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-quote_date', '-created_at']

    def __str__(self):
        return f"{self.quote_number} - {self.customer.company_name} (v{self.version})"

    @property
    def is_expired(self):
        """Check if quote has expired"""
        from django.utils import timezone
        if not self.expiration_date:
            return False
        return date.today() > self.expiration_date and self.status not in ['accepted', 'converted', 'rejected']

    @property
    def total_items(self):
        """Get total number of items in quote"""
        return self.items.count()

    @property
    def total_quantity(self):
        """Get total quantity of all items"""
        return sum(item.quantity for item in self.items.all())

    def calculate_totals(self):
        """Calculate and update quote totals"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total_amount = self.subtotal - self.discount + self.tax + self.shipping_cost
        self.save()


class QuoteItem(models.Model):
    """Individual item in a quote"""
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='quote_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, help_text="Item-specific notes or specifications")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['quote', 'item']

    def __str__(self):
        return f"{self.item.name} - Qty: {self.quantity}"

    @property
    def subtotal(self):
        """Calculate subtotal for this line item"""
        return (self.quantity * self.unit_price) - self.discount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update quote totals when item is saved
        self.quote.calculate_totals()
