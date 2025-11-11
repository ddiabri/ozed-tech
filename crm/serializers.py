from rest_framework import serializers
from .models import Customer, Contact, Interaction


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'customer', 'first_name', 'last_name', 'full_name',
            'title', 'email', 'phone', 'mobile',
            'is_primary', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InteractionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.company_name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Interaction
        fields = [
            'id', 'customer', 'customer_name', 'contact', 'contact_name',
            'interaction_type', 'subject', 'description',
            'interaction_date', 'user', 'user_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['interaction_date', 'created_at', 'updated_at']


class CustomerSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    total_contacts = serializers.IntegerField(read_only=True)
    total_purchase_orders = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'company_name', 'customer_type', 'industry', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'tax_id', 'credit_limit',
            'contacts', 'total_contacts', 'total_purchase_orders',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CustomerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    total_contacts = serializers.IntegerField(read_only=True)
    total_purchase_orders = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'company_name', 'customer_type', 'industry',
            'city', 'country', 'total_contacts', 'total_purchase_orders'
        ]
