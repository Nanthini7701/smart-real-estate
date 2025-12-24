from django.db import models
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
# Pillow is optional for development; if not installed, thumbnail creation is skipped
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    Image = None
    PIL_AVAILABLE = False

User = settings.AUTH_USER_MODEL

class Property(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')
    thumbnail = models.ImageField(upload_to='property_images/thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"

    def _create_thumbnail(self):
        if not self.image or not PIL_AVAILABLE:
            return
        try:
            img = Image.open(self.image)
            img = img.convert('RGB')
            img.thumbnail((600, 400))
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)
            thumb_name = self.image.name.rsplit('/', 1)[-1]
            self.thumbnail.save(f"thumb_{thumb_name}", ContentFile(thumb_io.getvalue()), save=False)
        except Exception:
            # If thumbnail creation fails, ignore silently (you can log this in prod)
            pass

    def save(self, *args, **kwargs):
        is_new = not self.pk
        # Save first so `self.image` is available in storage
        if is_new:
            super().save(*args, **kwargs)
            self._create_thumbnail()
            super().save(update_fields=['thumbnail'])
        else:
            super().save(*args, **kwargs)

class BookingRequest(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('pending','Pending'), ('approved','Approved')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    
class Payment(models.Model):
    booking = models.OneToOneField(BookingRequest, on_delete=models.CASCADE)
    amount = models.IntegerField()
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=10,
        choices=(('created', 'Created'), ('paid', 'Paid')),
        default='created'
    )
    paid_on = models.DateTimeField(null=True, blank=True)    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user}"    