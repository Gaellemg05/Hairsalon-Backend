from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Salon, Service, SalonPublication, HairstylePublication, Review, SubscriptionTransaction
from users.serializers import UserSerializer

User = get_user_model()

class ServiceSerializer(serializers.ModelSerializer):
    salon = serializers.PrimaryKeyRelatedField(queryset=Salon.objects.all())

    class Meta:
        model = Service
        fields = '__all__'

class SalonPublicationSerializer(serializers.ModelSerializer):
    salon = serializers.PrimaryKeyRelatedField(queryset=Salon.objects.all())
    media_url = serializers.SerializerMethodField()
    media = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = SalonPublication
        fields = ('id', 'salon', 'title', 'description', 'media', 'media_url', 'media_type', 'created_at')

    def get_media_url(self, obj):
        if obj.media:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.media.url) if request else obj.media.url
        return None

class HairstylePublicationSerializer(serializers.ModelSerializer):
    hairdresser_details = UserSerializer(source='hairdresser', read_only=True)
    salon_details = serializers.SerializerMethodField()
    salon = serializers.PrimaryKeyRelatedField(queryset=Salon.objects.all(), required=False, allow_null=True)
    hairdresser = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    media_url = serializers.SerializerMethodField()
    media = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = HairstylePublication
        fields = ('id', 'hairdresser', 'hairdresser_details', 'salon', 'salon_details', 'title', 'description', 'media', 'media_url', 'created_at', 'updated_at')

    def get_salon_details(self, obj):
        try:
            salon = obj.salon
            if salon:
                services = salon.services.all()
                return {
                    'id': salon.id,
                    'name': salon.name,
                    'address': salon.address,
                    'image_url': salon.image_url,
                    'services': [
                        {
                            'id': s.id,
                            'name': s.name,
                            'category': s.category,
                        }
                        for s in services
                    ],
                }
        except Exception:
            pass
        return None

    def get_media_url(self, obj):
        if obj.media:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.media.url) if request else obj.media.url
        return obj.media_url if obj.media_url else None

class ReviewSerializer(serializers.ModelSerializer):
    client_details = UserSerializer(source='client', read_only=True)
    client = serializers.PrimaryKeyRelatedField(read_only=True)
    salon = serializers.PrimaryKeyRelatedField(queryset=Salon.objects.all())

    class Meta:
        model = Review
        fields = ('id', 'salon', 'client', 'client_details', 'appointment', 'rating', 'comment', 'created_at')

class SubscriptionTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTransaction
        fields = '__all__'

class SalonSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    publications = SalonPublicationSerializer(many=True, read_only=True)
    hairstyle_publications = HairstylePublicationSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    manager_details = UserSerializer(source='manager', read_only=True)
    hairdressers = UserSerializer(many=True, read_only=True)
    manager = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Salon
        fields = (
            'id', 'name', 'description', 'address', 'phone_number',
            'email', 'image_url', 'video_url', 'latitude', 'longitude',
            'manager', 'manager_details', 'hairdressers', 'services',
            'publications', 'hairstyle_publications', 'reviews',
            'subscription_active_until'
        )
