# listings/management/commands/seed.py
import random
import datetime as dt

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from listings.models import Listing, Booking, Review

try:
    from faker import Faker

    faker = Faker()
except Exception:
    faker = None


class Command(BaseCommand):
    help = "Seed the database with sample Listings (and optionally Bookings & Reviews)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--listings",
            type=int,
            default=12,
            help="How many listings to create (default: 12).",
        )
        parser.add_argument(
            "--bookings",
            type=int,
            default=0,
            help="Total bookings to create across all listings (default: 0).",
        )
        parser.add_argument(
            "--reviews",
            type=int,
            default=0,
            help="Total reviews to create across all listings (default: 0).",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing Bookings, Reviews, then Listings before seeding.",
        )

    def handle(self, *args, **options):
        listings_count = options["listings"]
        bookings_count = options["bookings"]
        reviews_count = options["reviews"]
        do_flush = options["flush"]

        # NOTE on models:
        # - Listing.updated_at typically should be auto_now=True (not auto_now_add=True).
        # - Booking.created_at appears twice in your model; keep one field to avoid migration issues.
        # Seeder will still run provided migrations succeed.

        with transaction.atomic():
            if do_flush:
                self.stdout.write(self.style.WARNING("Flushing listings data..."))
                Booking.objects.all().delete()
                Review.objects.all().delete()
                Listing.objects.all().delete()

            self.stdout.write(self.style.NOTICE("Seeding data..."))

            listings = self._seed_listings(listings_count)
            self.stdout.write(
                self.style.SUCCESS(f"Created {len(listings)} listing(s).")
            )

            created_bookings = (
                self._seed_bookings(bookings_count, listings)
                if bookings_count > 0
                else 0
            )
            if created_bookings:
                self.stdout.write(
                    self.style.SUCCESS(f"Created {created_bookings} booking(s).")
                )

            created_reviews = (
                self._seed_reviews(reviews_count, listings) if reviews_count > 0 else 0
            )
            if created_reviews:
                self.stdout.write(
                    self.style.SUCCESS(f"Created {created_reviews} review(s).")
                )

            self.stdout.write(self.style.SUCCESS("Seeding complete!"))

    # -------------------------
    # Helpers
    # -------------------------
    def _seed_listings(self, count: int):
        """Create 'count' Listing rows with sensible lengths for your field constraints."""
        if count <= 0:
            return []

        # fallback pools when Faker isn't available
        names = [
            "Cozy Studio Westlands",
            "Garden View Apartment",
            "CBD Compact Room",
            "Lakeside Cottage",
            "Hilltop Bungalow",
            "Modern Loft Kilimani",
            "Beachside Getaway",
            "Safari Retreat",
            "Urban Chic Suite",
            "Riverside Nook",
            "Sunset Villa",
            "Parkview Condo",
        ]
        locations = [
            "Nairobi",
            "Mombasa",
            "Nakuru",
            "Kisumu",
            "Nanyuki",
            "Diani",
            "Naivasha",
        ]

        listings_to_create = []
        for i in range(count):
            name = (
                faker.sentence(nb_words=3) if faker else random.choice(names)
            ).strip(".")
            # ensure <= 50 chars
            name = name[:50]

            if faker:
                # keep description within 50 chars (your model max_length=50)
                desc = faker.sentence(nb_words=8)
            else:
                desc = "Great location, fast Wi-Fi, self check-in."
            desc = desc[:50]

            loc = faker.city() if faker else random.choice(locations)
            loc = loc[:30]

            price = random.randint(3000, 15000)  # KES-ish nightly price

            listings_to_create.append(
                Listing(
                    name=name,
                    description=desc,
                    location=loc,
                    pricepernight=price,
                )
            )

        # bulk_create to speed things up
        created = Listing.objects.bulk_create(listings_to_create, batch_size=200)
        return list(created)

    def _seed_bookings(self, total: int, listings):
        """Create 'total' bookings across provided listings."""
        if total <= 0 or not listings:
            return 0

        created = 0
        status_choices = [
            c[0] for c in Booking.Status.choices
        ]  # ["pending","confirmed","cancelled"]

        for _ in range(total):
            listing = random.choice(listings)
            nights = random.randint(1, 10)

            # start between -20 and +30 days from today
            start_offset = random.randint(-20, 30)
            start = timezone.now().date() + dt.timedelta(days=start_offset)
            end = start + dt.timedelta(days=nights)

            # compute total price
            total_price = nights * listing.pricepernight

            Booking.objects.create(
                Listing_id=listing,  # NOTE: your FK field name is capitalized
                start_date=start,
                end_date=end,
                total_price=total_price,
                status=random.choice(status_choices),
            )
            created += 1

        return created

    def _seed_reviews(self, total: int, listings):
        """Create 'total' reviews across provided listings."""
        if total <= 0 or not listings:
            return 0

        comments_pool = [
            "Clean and comfortable stay.",
            "Great host and excellent location.",
            "Would definitely book again.",
            "Wi-Fi was fast, perfect for work.",
            "Place matched the photos.",
            "Super convenient check-in.",
            "Quiet neighborhood, slept well.",
            "Spacious and well equipped.",
        ]

        to_create = []
        for _ in range(total):
            listing = random.choice(listings)
            rating = random.randint(1, 5)
            comment = random.choice(comments_pool)
            to_create.append(
                Review(
                    listing_id=listing,  # your Review FK is named 'listing_id'
                    rating=rating,
                    comment=comment,
                )
            )

        Review.objects.bulk_create(to_create, batch_size=200)
        return len(to_create)
