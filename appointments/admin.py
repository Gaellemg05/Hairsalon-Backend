from django.contrib import admin
from .models import Availability, Appointment, Chat, Message

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('hairdresser', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('hairdresser', 'day_of_week')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'hairdresser', 'salon', 'service', 'date', 'time', 'status')
    list_filter = ('salon', 'status', 'date')
    search_fields = ('client__username', 'hairdresser__username')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('client', 'hairdresser', 'salon', 'created_at')
    list_filter = ('salon', 'created_at')
    search_fields = ('client__username', 'hairdresser__username', 'salon__name')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'content_preview', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('content', 'sender__username')

    def content_preview(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_preview.short_description = 'Content'
