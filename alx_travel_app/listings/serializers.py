from .models import Listing, Booking
from rest_framework import serializers

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        
        read_only_fields = ["listing_id", "created_at", "updated_at"]

class BookingSerializer(serializers.ModelSerializer):
    listing = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source="Listing_id",
        write_only=True,
        help_text="listing primary key for this booking"
    )

    listing_detail = ListingSerializer(source="Listing_id", read_only=True)

    status = serializers.ChoiceField(
        choices=Booking.Status.choices,
        default=Booking.Status.PENDING,
        help_text="Booking status: defaults to pending"
    )

    class Meta:
        model = Booking
        fields = '__all__'

        read_only_fields = ["booking_id", "total_price", "created_at"]

    def validate(self, attrs):
        start = attrs.get("start_date") if "start_date" in attrs else getattr(self.instance, "start_date", None)
        end = attrs.get("end_date") if "end_date" in attrs else getattr(self.instance, "end_date", None)

        if start and end and end <= start:
            raise serializers.ValidationError({"end_date": "end_date must be after start_date."})
        return attrs
    
    def create(self, validated_data):
        listing = validated_data.pop("Listing_id")
        start = validated_data["start_date"]
        end = validated_data["end_date"]
        nights = (end - start).days
        if nights < 0:
            raise serializers.ValidationError({"end_date": "end_date must be after start_date."})
        
        validated_data = ["total_price"] = nights * listing.pricepernight

        return Booking.objects.create(Listing_id=listing, **validated_data)
    

    def update(self, instance, validated_data):
        validated_data.pop("Listing_id", None)

        start = validated_data.get("start_date", instance.start_date)
        end = validated_data.get("end_date", instance.end_date)

        if end <= start:
            raise serializers.ValidationError({"end_date": "end_date must be after start_date."})
        
        nights = (end - start).days
        instance.total_price = nights * instance.Listing_id.pricepernight

        return super().update(instance, validated_data)
    