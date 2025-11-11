from django.contrib import admin
from ozed_tech_project.admin_export import (
    export_customers_csv_action,
    export_customers_excel_action
)
from .models import Customer, Contact, Interaction


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0
    fields = ['first_name', 'last_name', 'title', 'email', 'phone', 'is_primary', 'is_active']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'customer_type', 'industry', 'city', 'country', 'total_contacts', 'total_purchase_orders', 'created_at']
    list_filter = ['customer_type', 'country', 'created_at']
    search_fields = ['company_name', 'industry', 'city', 'tax_id']
    readonly_fields = ['total_contacts', 'total_purchase_orders', 'created_at', 'updated_at']
    actions = [export_customers_csv_action, export_customers_excel_action]
    inlines = [ContactInline]
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'customer_type', 'industry', 'website')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Business Details', {
            'fields': ('tax_id', 'credit_limit')
        }),
        ('Statistics', {
            'fields': ('total_contacts', 'total_purchase_orders'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'customer', 'title', 'email', 'phone', 'is_primary', 'is_active', 'created_at']
    list_filter = ['is_primary', 'is_active', 'customer', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'customer__company_name']
    readonly_fields = ['full_name', 'created_at', 'updated_at']

    def get_fields(self, request, obj=None):
        fields = ['customer', 'first_name', 'last_name', 'title', 'email', 'phone', 'mobile', 'is_primary', 'is_active']
        if obj:
            fields.extend(['full_name', 'created_at', 'updated_at'])
        return fields


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'customer', 'contact', 'interaction_type', 'interaction_date', 'user']
    list_filter = ['interaction_type', 'interaction_date', 'customer']
    search_fields = ['subject', 'description', 'customer__company_name', 'contact__first_name', 'contact__last_name']
    readonly_fields = ['interaction_date', 'created_at', 'updated_at']
    date_hierarchy = 'interaction_date'

    fieldsets = (
        ('Interaction Details', {
            'fields': ('customer', 'contact', 'interaction_type', 'subject')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('user', 'interaction_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set the user who created the interaction"""
        if not obj.pk:  # Only set user on creation
            obj.user = request.user
        super().save_model(request, obj, form, change)
