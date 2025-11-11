from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    SupplierViewSet,
    ItemViewSet,
    PurchaseOrderViewSet,
    PurchaseOrderItemViewSet,
    SalesOrderViewSet,
    SalesOrderItemViewSet,
    RFQViewSet,
    RFQItemViewSet,
    QuoteViewSet,
    QuoteItemViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'purchase-order-items', PurchaseOrderItemViewSet, basename='purchaseorderitem')
router.register(r'sales-orders', SalesOrderViewSet, basename='salesorder')
router.register(r'sales-order-items', SalesOrderItemViewSet, basename='salesorderitem')
router.register(r'rfqs', RFQViewSet, basename='rfq')
router.register(r'rfq-items', RFQItemViewSet, basename='rfqitem')
router.register(r'quotes', QuoteViewSet, basename='quote')
router.register(r'quote-items', QuoteItemViewSet, basename='quoteitem')

urlpatterns = [
    path('', include(router.urls)),
]
