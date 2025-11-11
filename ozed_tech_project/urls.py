"""
URL configuration for ozed_tech_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .session_views import session_status, SessionManagementView, extend_session

# Customize admin site
admin.site.site_header = "Ozed-Tech Administration"
admin.site.site_title = "Ozed-Tech Admin"
admin.site.index_title = "Welcome to Ozed-Tech Management Portal"


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API Root - Ozed Tech Inventory & CRM System
    """
    # Prepare data for both JSON and HTML responses
    data = {
        'message': 'Welcome to Ozed Tech API',
        'version': '1.0',
        'endpoints': {
            'inventory': {
                'categories': reverse('category-list', request=request, format=format),
                'suppliers': reverse('supplier-list', request=request, format=format),
                'items': reverse('item-list', request=request, format=format),
                'purchase_orders': reverse('purchaseorder-list', request=request, format=format),
                'purchase_order_items': reverse('purchaseorderitem-list', request=request, format=format),
                'sales_orders': reverse('salesorder-list', request=request, format=format),
                'sales_order_items': reverse('salesorderitem-list', request=request, format=format),
                'rfqs': reverse('rfq-list', request=request, format=format),
                'rfq_items': reverse('rfqitem-list', request=request, format=format),
                'quotes': reverse('quote-list', request=request, format=format),
                'quote_items': reverse('quoteitem-list', request=request, format=format),
            },
            'crm': {
                'customers': reverse('customer-list', request=request, format=format),
                'contacts': reverse('contact-list', request=request, format=format),
                'interactions': reverse('interaction-list', request=request, format=format),
            },
            'dashboard': {
                'overview': reverse('dashboard-overview', request=request, format=format),
                'inventory': reverse('dashboard-inventory', request=request, format=format),
                'sales': reverse('dashboard-sales', request=request, format=format),
                'customers': reverse('dashboard-customers', request=request, format=format),
            },
            'ticketing': {
                'tickets': reverse('ticket-list', request=request, format=format),
                'comments': reverse('ticketcomment-list', request=request, format=format),
                'attachments': reverse('ticketattachment-list', request=request, format=format),
                'history': reverse('tickethistory-list', request=request, format=format),
            },
            'session': {
                'status': reverse('session-status', request=request, format=format),
                'management': reverse('session-management', request=request, format=format),
                'extend': reverse('session-extend', request=request, format=format),
            },
            'admin': request.build_absolute_uri('/admin/'),
            'authentication': reverse('rest_framework:login', request=request, format=format),
        },
        'documentation': {
            'inventory_items': {
                'list': 'GET /api/inventory/items/',
                'create': 'POST /api/inventory/items/',
                'detail': 'GET /api/inventory/items/{id}/',
                'update': 'PUT /api/inventory/items/{id}/',
                'delete': 'DELETE /api/inventory/items/{id}/',
                'low_stock': 'GET /api/inventory/items/low_stock/',
                'out_of_stock': 'GET /api/inventory/items/out_of_stock/',
                'adjust_stock': 'POST /api/inventory/items/{id}/adjust_stock/',
            },
            'purchase_orders': {
                'list': 'GET /api/inventory/purchase-orders/',
                'create': 'POST /api/inventory/purchase-orders/',
                'detail': 'GET /api/inventory/purchase-orders/{id}/',
                'update': 'PUT /api/inventory/purchase-orders/{id}/',
                'delete': 'DELETE /api/inventory/purchase-orders/{id}/',
                'add_item': 'POST /api/inventory/purchase-orders/{id}/add_item/',
                'change_status': 'POST /api/inventory/purchase-orders/{id}/change_status/',
                'receive_order': 'POST /api/inventory/purchase-orders/{id}/receive_order/',
            },
            'customers': {
                'list': 'GET /api/crm/customers/',
                'create': 'POST /api/crm/customers/',
                'detail': 'GET /api/crm/customers/{id}/',
                'update': 'PUT /api/crm/customers/{id}/',
                'delete': 'DELETE /api/crm/customers/{id}/',
                'contacts': 'GET /api/crm/customers/{id}/contacts/',
                'interactions': 'GET /api/crm/customers/{id}/interactions/',
                'purchase_orders': 'GET /api/crm/customers/{id}/purchase_orders/',
            },
            'tickets': {
                'list': 'GET /api/ticketing/tickets/',
                'create': 'POST /api/ticketing/tickets/',
                'detail': 'GET /api/ticketing/tickets/{id}/',
                'update': 'PUT /api/ticketing/tickets/{id}/',
                'delete': 'DELETE /api/ticketing/tickets/{id}/',
                'assign': 'POST /api/ticketing/tickets/{id}/assign/',
                'change_status': 'POST /api/ticketing/tickets/{id}/change_status/',
                'add_comment': 'POST /api/ticketing/tickets/{id}/add_comment/',
                'add_attachment': 'POST /api/ticketing/tickets/{id}/add_attachment/',
                'my_tickets': 'GET /api/ticketing/tickets/my_tickets/',
                'unassigned': 'GET /api/ticketing/tickets/unassigned/',
                'overdue': 'GET /api/ticketing/tickets/overdue/',
                'statistics': 'GET /api/ticketing/tickets/statistics/',
            }
        }
    }

    # If requesting JSON format, return JSON response
    if format == 'json' or request.accepted_renderer.format == 'json':
        return Response(data)

    # Otherwise, render HTML template
    context = {
        'version': data['version'],
        'inventory': data['endpoints']['inventory'],
        'crm': data['endpoints']['crm'],
        'dashboard': data['endpoints']['dashboard'],
        'ticketing': data['endpoints']['ticketing'],
        'session': data['endpoints']['session'],
        'admin_url': data['endpoints']['admin'],
        'auth_url': data['endpoints']['authentication'],
        'auth_text': 'Logout' if request.user.is_authenticated else 'Login',
        'user': request.user,
    }

    return render(request, 'api_root.html', context)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/inventory/', include('inventory.urls')),
    path('api/crm/', include('crm.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/ticketing/', include('ticketing.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Session management endpoints
    path('api/session-status/', session_status, name='session-status'),
    path('api/session/', SessionManagementView.as_view(), name='session-management'),
    path('api/session/extend/', extend_session, name='session-extend'),
]

# Serve media files in development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
