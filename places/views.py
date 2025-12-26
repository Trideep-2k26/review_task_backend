from django.db.models import Avg, Case, When, Value, IntegerField
from django.core.cache import cache
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Place, Review
from .serializers import (
    CreateReviewSerializer,
    PlaceSearchSerializer,
    PlaceDetailSerializer,
    ReviewSerializer,
)


class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        cache.clear()
        return Response({
            'message': 'Review created successfully',
            'review': ReviewSerializer(review).data,
            'place_id': review.place.id
        }, status=status.HTTP_201_CREATED)


class PlaceSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        name = request.query_params.get('name', '').strip()
        min_rating = request.query_params.get('min_rating')

        cache_key = f"place_search_{name}_{min_rating}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return Response(cached_result)

        queryset = Place.objects.annotate(
            average_rating=Avg('reviews__rating')
        )

        if name:
            queryset = queryset.filter(name__icontains=name)
            queryset = queryset.annotate(
                match_rank=Case(
                    When(name__iexact=name, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                )
            ).order_by('match_rank', 'name')
        else:
            queryset = queryset.order_by('name')

        if min_rating:
            try:
                min_rating_value = float(min_rating)
                queryset = queryset.filter(average_rating__gte=min_rating_value)
            except ValueError:
                pass

        serializer = PlaceSearchSerializer(queryset, many=True)
        result = serializer.data
        cache.set(cache_key, result, getattr(settings, 'CACHE_TTL', 300))
        return Response(result)


class PlaceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        cache_key = f"place_detail_{pk}_{request.user.id}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return Response(cached_result)

        try:
            place = Place.objects.annotate(
                avg_rating=Avg('reviews__rating')
            ).prefetch_related('reviews__user').get(pk=pk)
        except Place.DoesNotExist:
            return Response(
                {'error': 'Place not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlaceDetailSerializer(place, context={'request': request})
        result = serializer.data
        cache.set(cache_key, result, getattr(settings, 'CACHE_TTL', 300))
        return Response(result)
