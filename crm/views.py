from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from ozed_tech_project.export_utils import CSVExporter, ExcelExporter
from .models import Customer, Contact, Interaction
from .serializers import (
    CustomerSerializer,
    CustomerListSerializer,
    ContactSerializer,
    InteractionSerializer
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customers
    """
    queryset = Customer.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name', 'industry', 'city', 'country']
    ordering_fields = ['company_name', 'created_at', 'customer_type']
    filterset_fields = ['customer_type', 'country']

    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        """Get all contacts for a customer"""
        customer = self.get_object()
        contacts = customer.contacts.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def interactions(self, request, pk=None):
        """Get all interactions for a customer"""
        customer = self.get_object()
        interactions = customer.interactions.all()
        serializer = InteractionSerializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def purchase_orders(self, request, pk=None):
        """Get all purchase orders for a customer"""
        from inventory.serializers import PurchaseOrderListSerializer
        customer = self.get_object()
        orders = customer.purchase_orders.all()
        serializer = PurchaseOrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export customers to CSV"""
        customers = self.filter_queryset(self.get_queryset())

        headers = ['Company Name', 'Customer Type', 'Industry', 'Email', 'Phone',
                  'Address', 'City', 'State', 'Country', 'Postal Code',
                  'Credit Limit', 'Website', 'Created Date']

        rows = []
        for customer in customers:
            rows.append([
                customer.company_name,
                customer.get_customer_type_display(),
                customer.industry or 'N/A',
                customer.email or 'N/A',
                customer.phone or 'N/A',
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

    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        """Export customers to Excel"""
        customers = self.filter_queryset(self.get_queryset())

        headers = ['Company Name', 'Customer Type', 'Industry', 'Email', 'Phone',
                  'Address', 'City', 'State', 'Country', 'Postal Code',
                  'Credit Limit', 'Website', 'Created Date']

        rows = []
        for customer in customers:
            rows.append([
                customer.company_name,
                customer.get_customer_type_display(),
                customer.industry or 'N/A',
                customer.email or 'N/A',
                customer.phone or 'N/A',
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


class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing contacts
    """
    queryset = Contact.objects.select_related('customer').all()
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'customer__company_name']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    filterset_fields = ['customer', 'is_primary', 'is_active']


class InteractionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing interactions
    """
    queryset = Interaction.objects.select_related('customer', 'contact', 'user').all()
    serializer_class = InteractionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['subject', 'description', 'customer__company_name']
    ordering_fields = ['interaction_date', 'created_at']
    filterset_fields = ['customer', 'contact', 'interaction_type', 'user']

    def perform_create(self, serializer):
        """Automatically set the user who created the interaction"""
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)
