from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, ContactViewSet, InteractionViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'interactions', InteractionViewSet, basename='interaction')

urlpatterns = [
    path('', include(router.urls)),
]
