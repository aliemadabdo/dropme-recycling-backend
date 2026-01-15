from django.db import models
from django.core.validators import MinValueValidator
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class RecyclingTransaction(models.Model):
    """Records each recycling action"""
    
    MATERIAL_CHOICES = [
        ('plastic', 'Plastic'),
        ('glass', 'Glass'),
        ('aluminum', 'Aluminum'),
        ('paper', 'Paper'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('duplicate', 'Duplicate'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    material_type = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    item_code = models.CharField(max_length=100, db_index=True, help_text="Barcode or QR code from item")
    weight_grams = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)], help_text="Weight in grams from sensor")
    points_earned = models.IntegerField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    machine_id = models.CharField(max_length=50, null=True, blank=True, help_text="ID of the recycling machine")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'recycling_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['item_code', 'user']),
            models.Index(fields=['status']),
        ]
        # Prevent duplicate item submissions
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'item_code'],
                name='unique_user_item'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.material_type} - {self.points_earned}pts"


class PointsHistory(models.Model):
    """Audit trail for points changes"""
    
    TRANSACTION_TYPES = [
        ('earn', 'Earned'),
        ('payout', 'Payout'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_history')
    transaction = models.ForeignKey(
        RecyclingTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='points_records'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    points_change = models.IntegerField()
    balance_after = models.IntegerField(validators=[MinValueValidator(0)])
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'points_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.points_change:+d} pts"