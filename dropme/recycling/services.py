from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from recycling.models import PointsHistory, RecyclingTransaction
from django.contrib.auth import get_user_model

User = get_user_model()


class RecyclingService:
    """Core business logic for recycling transactions"""

    @staticmethod
    def calculate_points(material_type: str, weight_grams: float) -> int:
        """Calculate points based on material type and weight"""
        if weight_grams <= 0:
            raise ValueError("Weight must be greater than 0")
        
        # Get points per gram from settings
        material_points = settings.RECYCLING_RULES.get(material_type, {}).get('points', 1)
        return int(weight_grams * material_points)
    
    @staticmethod
    def check_duplicate_transaction(user, item_code: str) -> bool:
        """Check if item has already been recycled by this user"""
        return RecyclingTransaction.objects.filter(
            user=user,
            item_code=item_code
        ).exists()

    @staticmethod
    def check_rate_limit(user) -> dict:
        """Check if user has exceeded rate limits"""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check daily limit
        transactions_today = RecyclingTransaction.objects.filter(
            user=user,
            created_at__gte=today_start,
            status='completed'
        ).count()
        
        if transactions_today >= settings.MAX_TRANSACTIONS_PER_DAY:
            raise ValueError(
                f"Daily transaction limit reached ({settings.MAX_TRANSACTIONS_PER_DAY})"
            )
        
        # Check minimum interval between transactions
        last_transaction = RecyclingTransaction.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at').first()
        
        if last_transaction:
            time_diff = (now - last_transaction.created_at).total_seconds()
            if time_diff < settings.MIN_TRANSACTION_INTERVAL:
                remaining = settings.MIN_TRANSACTION_INTERVAL - time_diff
                raise ValueError(
                    f"Please wait {int(remaining)} seconds before next transaction"
                )
        
        return {
            'transactions_today': transactions_today,
            'remaining_today': settings.MAX_TRANSACTIONS_PER_DAY - transactions_today
        }

    @transaction.atomic
    def create_transaction(self, user, material_type: str, 
                          item_code: str, weight_grams: float, machine_id: str = None) -> RecyclingTransaction:
        """
        Create a recycling transaction with full validation and points update
        Uses database transaction to ensure data consistency
        """
        
        # Check for duplicate
        if self.check_duplicate_transaction(user, item_code):
            # Create failed transaction record
            failed_txn = RecyclingTransaction.objects.create(
                user=user,
                material_type=material_type,
                item_code=item_code,
                weight_grams=weight_grams,
                machine_id=machine_id,
                points_earned=0,
                status='duplicate',
                error_message='Item has already been recycled'
            )
            raise ValueError(
                "This item has already been recycled",
                transaction_id=str(failed_txn.id)
            )
        
        # Check rate limits
        rate_limit_info = self.check_rate_limit(user)
        
        # Calculate points based on weight
        points = self.calculate_points(material_type, weight_grams)
        
        # Create transaction
        txn = RecyclingTransaction.objects.create(
            user=user,
            material_type=material_type,
            item_code=item_code,
            weight_grams=weight_grams,
            machine_id=machine_id,
            points_earned=points,
            status='completed'
        )
        
        # Update user points
        user.total_points += points
        user.save(update_fields=['total_points', 'updated_at'])
        
        # Create points history record
        PointsHistory.objects.create(
            user=user,
            transaction=txn,
            transaction_type='earn',
            points_change=points,
            balance_after=user.total_points,
            description=f"Recycled {weight_grams}g of {material_type}"
        )
        
        return txn


    @staticmethod
    def get_user_stats(user) -> dict:
        """Get comprehensive user statistics"""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_transactions = RecyclingTransaction.objects.filter(
            user=user,
            status='completed'
        ).count()
        
        transactions_today = RecyclingTransaction.objects.filter(
            user=user,
            created_at__gte=today_start,
            status='completed'
        ).count()
        
        points_today = RecyclingTransaction.objects.filter(
            user=user,
            created_at__gte=today_start,
            status='completed'
        ).aggregate(total=models.Sum('points_earned'))['total'] or 0
        
        # Find favorite material type
        favorite = RecyclingTransaction.objects.filter(
            user=user,
            status='completed'
        ).values('material_type').annotate(
            count=models.Count('id')
        ).order_by('-count').first()
        
        return {
            'total_points': user.total_points,
            'total_transactions': total_transactions,
            'transactions_today': transactions_today,
            'points_earned_today': points_today,
            'favorite_material': favorite['material_type'] if favorite else None
        }


