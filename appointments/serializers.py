from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Availability, Appointment, Chat, Message
from users.serializers import UserSerializer
from salons.serializers import SalonSerializer, ServiceSerializer
from salons.models import Salon, Service, Review

User = get_user_model()

class AvailabilitySerializer(serializers.ModelSerializer):
    hairdresser_details = UserSerializer(source='hairdresser', read_only=True)
    hairdresser = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Availability
        fields = ('id', 'hairdresser', 'hairdresser_details', 'day_of_week', 'start_time', 'end_time')

class AppointmentSerializer(serializers.ModelSerializer):
    client_details = UserSerializer(source='client', read_only=True)
    hairdresser_details = UserSerializer(source='hairdresser', read_only=True)
    salon_details = SalonSerializer(source='salon', read_only=True)
    service_details = ServiceSerializer(source='service', read_only=True)
    client = serializers.PrimaryKeyRelatedField(read_only=True)
    review = serializers.SerializerMethodField()
    hairdresser = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    salon = serializers.PrimaryKeyRelatedField(queryset=Salon.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = Appointment
        fields = (
            'id', 'client', 'client_details', 'hairdresser', 'hairdresser_details',
            'salon', 'salon_details', 'service', 'service_details',
            'date', 'time', 'status', 'created_at', 'updated_at', 'review'
        )

    def get_review(self, obj):
        try:
            r = obj.review
            return {'id': r.id, 'rating': r.rating, 'comment': r.comment, 'created_at': r.created_at}
        except Review.DoesNotExist:
            return None

class MessageSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'chat', 'sender', 'sender_details', 'content', 'image', 'image_url', 'created_at', 'read')

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    client_details = UserSerializer(source='client', read_only=True)
    hairdresser_details = UserSerializer(source='hairdresser', read_only=True)
    salon_details = SalonSerializer(source='salon', read_only=True)
    unread_count = serializers.SerializerMethodField()
    client = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    hairdresser = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    salon = serializers.PrimaryKeyRelatedField(queryset=Salon.objects.all())

    class Meta:
        model = Chat
        fields = ('id', 'client', 'client_details', 'hairdresser', 'hairdresser_details', 'salon', 'salon_details', 'created_at', 'last_message', 'unread_count')

    def get_last_message(self, obj):
        last = obj.messages.last()
        if last:
            content = last.content
            if not content and last.image:
                content = '📷 Photo'
            return {
                'content': content,
                'sender': last.sender.username,
                'created_at': last.created_at,
                'read': last.read
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(read=False).exclude(sender=request.user).count()
        return obj.messages.filter(read=False).count()
