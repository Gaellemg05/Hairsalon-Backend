from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SalonViewSet, ServiceViewSet, SalonPublicationViewSet,
    HairstylePublicationViewSet, ReviewViewSet
)

router = DefaultRouter()
router.register(r'salons', SalonViewSet, basename='salon')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'salon-publications', SalonPublicationViewSet, basename='salonpublication')
router.register(r'hairstyle-publications', HairstylePublicationViewSet, basename='hairstylepublication')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
