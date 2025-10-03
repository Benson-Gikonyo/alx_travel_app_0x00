from django.db import models
import uuid

# Create your models here.


class Listing(models.Model):
    listing_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    # host_id = models.ForeignKey("User", verbose_name=_(""), on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=50, null=False)
    location = models.CharField(max_length=30, null=False)
    pricepernight = models.IntegerField(null=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    booking_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    Listing_id = models.ForeignKey("Listing", on_delete=models.CASCADE)
    # user_id = models.ForeignKey("User", on_delete=models.CASCADE)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    total_price = models.IntegerField(null=False)
    created_at = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, null=False, blank=False
    )
    created_at = models.DateField(auto_now_add=True)


class Review(models.Model):
    RATING_CHOICES = [
        (1, "Poor"),
        (2, "Fair"),
        (3, "Good"),
        (4, "Very Good"),
        (5, "Excellent"),
    ]

    review_id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4)
    listing_id = models.ForeignKey("Listing", on_delete=models.CASCADE)
    # user_id = models.ForeignKey("User", on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, null=False)
    comment = models.TextField(null=False)
    created_at = models.DateField(auto_now_add=True)
