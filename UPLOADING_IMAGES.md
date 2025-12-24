## Media / Image upload setup

What I changed
- Added `image = models.ImageField(upload_to='property_images/', null=True, blank=True)` to `properties.Property` model and created migration `properties/migrations/0005_property_image.py`.
- Added `MEDIA_URL = '/media/'` and `MEDIA_ROOT = BASE_DIR / 'media'` in `core/settings.py`.
- Configured `core/urls.py` to serve media files during development when `DEBUG=True`.
- Updated `templates/property_form.html` to include `enctype="multipart/form-data"` and a file input for `image`.
- Updated `properties/views.add_property` to accept `request.FILES['image']` when provided.
- Updated `tenant_dashboard.html` and `owner_dashboard.html` to display the property image when present.
- Updated admin to show the `image` field in `PropertyAdmin`.

How to enable uploads locally
1. Install Pillow (required for ImageField):

   ```bash
   pip install pillow
   ```

2. Make sure migrations are applied (already run here):

   ```bash
   python manage.py migrate
   ```

3. Run development server:

   ```bash
   python manage.py runserver
   ```

4. Add a property from Owner Dashboard and upload an image. Tenant Dashboard will display it.

Notes
- In production, configure a proper media file storage (S3, etc.) and do not use Django static file serving for media.
- Implemented `PropertyImage` model for multiple images per property and automatic thumbnail generation using Pillow. Thumbnails are created on save at ~600x400 and stored at `property_images/thumbnails/`.
- On creation, the first uploaded image is assigned to `Property.image` for backward compatibility.
- Added a property detail page (`/property/<id>/`) with a simple gallery viewer (click a thumbnail to view the full-size image) and a "Book & Pay" button so tenants can see details before booking.