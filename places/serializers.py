from rest_framework import serializers
from django.db.models import Avg
from .models import Place, Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'rating', 'text', 'user_name', 'created_at']
        read_only_fields = ['id', 'user_name', 'created_at']


class CreateReviewSerializer(serializers.Serializer):
    place_name = serializers.CharField(max_length=255)
    place_address = serializers.CharField(max_length=500)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    text = serializers.CharField()

    def validate(self, data):
        user = self.context['request'].user
        place = Place.objects.filter(
            name__iexact=data['place_name'],
            address__iexact=data['place_address']
        ).first()
        if place and Review.objects.filter(user=user, place=place).exists():
            raise serializers.ValidationError('You have already reviewed this place')
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        place, _ = Place.objects.get_or_create(
            name__iexact=validated_data['place_name'],
            address__iexact=validated_data['place_address'],
            defaults={
                'name': validated_data['place_name'],
                'address': validated_data['place_address']
            }
        )
        review = Review.objects.create(
            user=user,
            place=place,
            rating=validated_data['rating'],
            text=validated_data['text']
        )
        return review


class PlaceSearchSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Place
        fields = ['id', 'name', 'average_rating']


class PlaceDetailSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ['id', 'name', 'address', 'average_rating', 'reviews', 'created_at']

    def get_average_rating(self, obj):
        if hasattr(obj, 'avg_rating'):
            return obj.avg_rating
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 2) if avg else None

    def get_reviews(self, obj):
        user = self.context.get('request').user
        user_review = None
        other_reviews = []
        
        reviews = obj.reviews.select_related('user').all()
        for review in reviews:
            if review.user_id == user.id:
                user_review = review
            else:
                other_reviews.append(review)
        
        ordered_reviews = []
        if user_review:
            ordered_reviews.append(user_review)
        ordered_reviews.extend(other_reviews)
        
        return ReviewSerializer(ordered_reviews, many=True).data
