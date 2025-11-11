"""
URL configuration for the Ticketing app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TicketViewSet,
    TicketCommentViewSet,
    TicketAttachmentViewSet,
    TicketHistoryViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'comments', TicketCommentViewSet, basename='ticketcomment')
router.register(r'attachments', TicketAttachmentViewSet, basename='ticketattachment')
router.register(r'history', TicketHistoryViewSet, basename='tickethistory')

urlpatterns = [
    path('', include(router.urls)),
]
