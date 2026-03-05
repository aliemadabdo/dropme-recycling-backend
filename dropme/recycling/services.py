import logging
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from recycling.models import PointsHistory, RecyclingTransaction
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


class RecyclingService:
    """Core business logic for recycling transactions"""

    @staticmethod
    def calculate_points(material_type: str, weight_grams: float) -> int:
        """Calculate points based on material type and weight"""
        logger.debug(
            "Calculating points: material_type=%s, weight_grams=%s",
            material_type, weight_grams,
        )

        if weight_grams <= 0:
            logger.error("Weight must be greater than 0, got %s", weight_grams)
            raise ValueError("Weight must be greater than 0")
        
        # Get points per gram from settings
        material_points = settings.RECYCLING_RULES.get(material_type.upper(), {}).get('points', 1)
        calculated_points = int(weight_grams * material_points)
        logger.info(
            "Calculated points for %s (%sg * %spg): %s",
            material_type, weight_grams, material_points, calculated_points,
        )
        return calculated_points
    
    @staticmethod
    def check_duplicate_transaction(user, item_code: str) -> bool:
        """Check if item has already been recycled by this user"""
        duplicate = RecyclingTransaction.objects.filter(
            user=user,
            item_code=item_code
        ).exists()
        logger.debug(
            "Duplicate check for user=%s, item_code=%s: %s",
            getattr(user, 'id', None), item_code, duplicate
        )
        return duplicate

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
        logger.debug(
            "User %s transactions today: %d",
            getattr(user, 'id', None), transactions_today
        )
        if transactions_today >= settings.MAX_TRANSACTIONS_PER_DAY:
            logger.warning(
                "User %s exceeded max transactions per day (%d)",
                getattr(user, 'id', None), settings.MAX_TRANSACTIONS_PER_DAY
            )
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
            logger.debug(
                "User %s last completed transaction = %s (%ss ago)",
                getattr(user, 'id', None), last_transaction.created_at, time_diff
            )
            if time_diff < settings.MIN_TRANSACTION_INTERVAL:
                remaining = settings.MIN_TRANSACTION_INTERVAL - time_diff
                logger.warning(
                    "User %s transaction too fast: %ss since previous, must wait %ss",
                    getattr(user, 'id', None), time_diff, remaining
                )
                raise ValueError(
                    f"Please wait {int(remaining)} seconds before next transaction"
                )
        
        result = {
            'transactions_today': transactions_today,
            'remaining_today': settings.MAX_TRANSACTIONS_PER_DAY - transactions_today
        }
        logger.debug("Rate limit result for user %s: %s", getattr(user, 'id', None), result)
        return result

    def create_transaction(self, user, material_type: str,
                          item_code: str, weight_grams: float, machine_id: str = None) -> RecyclingTransaction:
        """
        Create a recycling transaction with full validation and points update
        Uses database transaction to ensure data consistency
        """
        logger.info(
            "Starting transaction for user=%s, material_type=%s, item_code=%s, weight_grams=%s, machine_id=%s",
            getattr(user, 'id', None), material_type, item_code, weight_grams, machine_id
        )
        # Check for duplicate
        if self.check_duplicate_transaction(user, item_code):
            logger.warning(
                "Duplicate transaction attempt by user=%s for item_code=%s",
                getattr(user, 'id', None), item_code
            )
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
            logger.info(
                "Created failed duplicate transaction record: id=%s", str(failed_txn.id)
            )
            raise ValueError("This item has already been recycled")
        
        with transaction.atomic():
            # Check rate limits
            rate_limit_info = self.check_rate_limit(user)
            logger.debug(
                "Rate limit info for user %s: %s",
                getattr(user, 'id', None), rate_limit_info
            )

            # Calculate points based on weight
            points = self.calculate_points(material_type, weight_grams)
            logger.info(
                "Points to be awarded: %d for user %s", points, getattr(user, 'id', None)
            )

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
            logger.info(
                "Created RecyclingTransaction: id=%s for user=%s", str(txn.id), getattr(user, 'id', None)
            )

            # Update user points
            user.total_points += points
            user.save(update_fields=['total_points', 'updated_at'])
            logger.info(
                "Updated user %s total_points to %s", getattr(user, 'id', None), user.total_points
            )

            # Create points history record
            PointsHistory.objects.create(
                user=user,
                transaction=txn,
                transaction_type='earn',
                points_change=points,
                balance_after=user.total_points,
                description=f"Recycled {weight_grams}g of {material_type}"
            )
            logger.info(
                "Created PointsHistory record for user=%s, transaction=%s", getattr(user, 'id', None), str(txn.id)
            )

            return txn

    @staticmethod
    def get_user_stats(user) -> dict:
        """Get comprehensive user statistics"""
        logger.debug("Getting stats for user %s", getattr(user, 'id', None))
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

        stats = {
            'total_points': user.total_points,
            'total_transactions': total_transactions,
            'transactions_today': transactions_today,
            'points_earned_today': points_today,
            'favorite_material': favorite['material_type'] if favorite else None
        }
        logger.debug("Stats for user %s: %s", getattr(user, 'id', None), stats)
        return stats
