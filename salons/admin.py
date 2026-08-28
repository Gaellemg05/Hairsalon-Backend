from django.contrib import admin
from django import forms
from .models import Salon, Service, SalonPublication, HairstylePublication, Review, SubscriptionTransaction


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    fields = ('name', 'description', 'price', 'duration', 'category')


class SalonPublicationInline(admin.TabularInline):
    model = SalonPublication
    extra = 1
    fields = ('title', 'description', 'media_url', 'media_type')


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('client', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_number', 'email', 'latitude', 'longitude', 'manager')
    search_fields = ('name', 'address', 'email')
    list_filter = ('manager',)
    filter_horizontal = ('hairdressers',)
    inlines = [ServiceInline, SalonPublicationInline, ReviewInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'address', 'phone_number', 'email', 'image_url', 'video_url', 'latitude', 'longitude', 'manager', 'hairdressers')
        }),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'category', 'price', 'duration')
    list_filter = ('salon', 'category')
    search_fields = ('name',)


@admin.register(SalonPublication)
class SalonPublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'salon', 'media_type', 'created_at')
    list_filter = ('salon', 'media_type')
    search_fields = ('title',)


@admin.register(HairstylePublication)
class HairstylePublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'hairdresser', 'created_at')
    list_filter = ('hairdresser',)
    search_fields = ('title',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('salon', 'client', 'rating', 'created_at')
    list_filter = ('salon', 'rating')
    search_fields = ('salon__name', 'client__username')


@admin.register(SubscriptionTransaction)
class SubscriptionTransactionAdmin(admin.ModelAdmin):
    list_display = ('salon', 'amount', 'operator', 'transaction_type', 'created_at')
    list_filter = ('transaction_type', 'operator')
    search_fields = ('salon__name', 'phone_number')
