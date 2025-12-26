from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Place(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    address = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['name', 'address'], name='unique_place_name_address')
        ]
        indexes = [
            models.Index(fields=['name', 'address']),
        ]

    def __str__(self):
        return f"{self.name} - {self.address}"


class Review(models.Model):
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_index=True
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'place'], name='unique_user_place_review')
        ]

    def __str__(self):
        return f"Review by {self.user.name} for {self.place.name}"
