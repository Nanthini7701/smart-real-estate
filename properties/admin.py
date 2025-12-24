from django.contrib import admin
from .models import Property, BookingRequest, Payment, Notification, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1



@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines = (PropertyImageInline,)
    list_display = ('title', 'owner', 'location', 'price', 'image', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('title', 'location', 'owner__username')


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('property__title', 'tenant__username')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'booking',
        'amount',
        'status',
        'razorpay_order_id',
        'razorpay_payment_id',
        'paid_on'
    )
    list_filter = ('status', 'paid_on')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
