from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.contrib import messages
import logging

import razorpay

logger = logging.getLogger(__name__)

from .models import (
    Property,
    BookingRequest,
    Payment,
    Notification,
    PropertyImage
)

# ---------------- OWNER DASHBOARD ----------------

@login_required
def owner_dashboard(request):
    properties = Property.objects.filter(owner=request.user)
    return render(request, 'owner_dashboard.html', {'properties': properties})


@login_required
def add_property(request):
    if request.method == 'POST':
        data = {
            'owner': request.user,
            'title': request.POST['title'],
            'location': request.POST['location'],
            'price': request.POST['price'],
            'description': request.POST['description']
        }

        prop = Property.objects.create(**data)

        # Handle multiple images (gallery)
        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            pi = PropertyImage.objects.create(property=prop, image=img)
            # keep backward compatibility with single `Property.image`
            if idx == 0 and not prop.image:
                prop.image = pi.image
                prop.save(update_fields=['image'])

        return redirect('owner_dashboard')
    return render(request, 'property_form.html')


# ---------------- TENANT DASHBOARD ----------------

@login_required
def tenant_dashboard(request):
    properties = Property.objects.all()
    return render(request, 'tenant_dashboard.html', {'properties': properties})


def property_detail(request, pk):
    prop = get_object_or_404(Property, id=pk)
    images = prop.images.all()
    return render(request, 'property_detail.html', {'property': prop, 'images': images})


@login_required
def send_request(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)

    booking, created = BookingRequest.objects.get_or_create(
        property=property_obj,
        tenant=request.user,
        defaults={'status': 'pending'}
    )

    if created:
        messages.success(request, 'Booking created. Redirecting to payment...')
    else:
        messages.info(request, 'Existing booking found. Resuming payment (if any).')

    return redirect('initiate_payment', booking_id=booking.id)

# ---------------- OWNER REQUEST MANAGEMENT ----------------

@login_required
def owner_requests(request):
    requests = BookingRequest.objects.filter(property__owner=request.user)
    return render(request, 'owner_requests.html', {'requests': requests})


@login_required
def update_request(request, request_id, status):
    booking = get_object_or_404(
        BookingRequest,
        id=request_id,
        property__owner=request.user   # 🔐 security check
    )
    booking.status = status
    booking.save()
    messages.success(request, f"Request {status} successfully.")
    return redirect('owner_requests')


# ---------------- RAZORPAY PAYMENT ----------------

@login_required
def initiate_payment(request, booking_id):
    booking = get_object_or_404(
        BookingRequest,
        id=booking_id
    )

    # Optional safety check
    if booking.tenant != request.user:
        return redirect('tenant_dashboard')

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # If a Payment already exists for this booking, reuse it when possible
    payment = Payment.objects.filter(booking=booking).first()

    if payment:
        # If already paid, inform user and redirect
        if payment.status == 'paid':
            messages.info(request, "This booking has already been paid.")
            return redirect('tenant_dashboard')

        # If an order id already exists, reuse it
        if payment.razorpay_order_id:
            messages.info(request, 'Resuming your pending payment.')
            order_id = payment.razorpay_order_id
            amount = booking.property.price * 100
        else:
            try:
                order = client.order.create({
                    "amount": int(booking.property.price * 100),
                    "currency": "INR",
                    "payment_capture": 1
                })
            except Exception as exc:
                logger.exception('Error creating razorpay order for booking %s: %s', booking.id, exc)
                messages.error(request, 'Payment gateway error. Please try again later or contact support.')
                return redirect('tenant_dashboard')
            payment.razorpay_order_id = order['id']
            payment.save(update_fields=['razorpay_order_id'])
            order_id = order['id']
            amount = booking.property.price * 100
    else:
        # No payment exists yet: create an order and Payment record.
        try:
            order = client.order.create({
                "amount": int(booking.property.price * 100),
                "currency": "INR",
                "payment_capture": 1
            })
        except Exception as exc:
            logger.exception('Error creating razorpay order for booking %s: %s', booking.id, exc)
            messages.error(request, 'Payment gateway error. Please try again later or contact support.')
            return redirect('tenant_dashboard')

        try:
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.property.price,
                razorpay_order_id=order['id']
            )
        except IntegrityError:
            # Race condition: another process created it concurrently — fetch existing
            payment = Payment.objects.get(booking=booking)
        except Exception as exc:
            logger.exception('Error creating Payment record for booking %s: %s', booking.id, exc)
            messages.error(request, 'Server error while preparing payment. Please try again later.')
            return redirect('tenant_dashboard')

        order_id = order['id']
        amount = booking.property.price * 100

    return render(request, "razorpay_checkout.html", {
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "order_id": order_id
    })
# ---------------- PAYMENT SUCCESS CALLBACK ----------------

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")

        payment = get_object_or_404(Payment, razorpay_order_id=order_id)

        # (Optional) Razorpay signature verification
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
        except Exception as exc:
            # Verification failed — mark payment failed and inform user
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            messages.error(request, 'Payment verification failed. If money was charged, contact support.')
            return redirect('tenant_dashboard')

        # All good — record payment details
        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = "paid"
        payment.paid_on = timezone.now()
        payment.save()

        Notification.objects.create(
            user=payment.booking.property.owner,
            message=f"Rent payment received for {payment.booking.property.title}"
        )

        messages.success(request, 'Payment successful. Thank you!')
        return redirect('tenant_dashboard')
