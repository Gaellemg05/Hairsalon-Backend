from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvailabilityViewSet, AppointmentViewSet, ChatViewSet, MessageViewSet, chatbot_view

router = DefaultRouter()
router.register(r'availability', AvailabilityViewSet, basename='availability')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('chatbot/', chatbot_view, name='chatbot'),
    path('', include(router.urls)),
]
