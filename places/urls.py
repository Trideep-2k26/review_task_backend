from django.urls import path
from .views import ReviewCreateView, PlaceSearchView, PlaceDetailView

urlpatterns = [
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('places/search/', PlaceSearchView.as_view(), name='place-search'),
    path('places/<int:pk>/', PlaceDetailView.as_view(), name='place-detail'),
]
