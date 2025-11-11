from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    """Company/Business customer"""
    CUSTOMER_TYPE_CHOICES = [
        ('prospect', 'Prospect'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    company_name = models.CharField(max_length=200, unique=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='prospect')
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Business details
    tax_id = models.CharField(max_length=50, blank=True, help_text="Tax ID / VAT Number")
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['company_name']

    def __str__(self):
        return self.company_name

    @property
    def total_contacts(self):
        """Get total number of contacts"""
        return self.contacts.count()

    @property
    def total_purchase_orders(self):
        """Get total number of purchase orders"""
        return self.purchase_orders.count()


class Contact(models.Model):
    """Individual contact person at a customer company"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts')

    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, help_text="Job title")

    # Contact details
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)

    # Status
    is_primary = models.BooleanField(default=False, help_text="Primary contact for this customer")
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer.company_name})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Interaction(models.Model):
    """Track interactions and notes with customers"""
    INTERACTION_TYPE_CHOICES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('task', 'Task'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='interactions')

    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()

    interaction_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who created this interaction")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-interaction_date']

    def __str__(self):
        return f"{self.interaction_type}: {self.subject} - {self.customer.company_name}"
