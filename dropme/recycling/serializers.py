from rest_framework import serializers
from .models import RecyclingTransaction, PointsHistory


class RecyclingTransactionSerializer(serializers.ModelSerializer):
    """Serializer for creating recycling transactions"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = RecyclingTransaction
        fields = ['id', 'user', 'material_type', 'item_code', 'machine_id', 'points_earned', 'status', 'created_at']
        read_only_fields = ['id', 'points_earned', 'status', 'created_at']

    def validate_item_code(self, value):
        """Validate item code format"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Item code cannot be empty")
        if len(value) > 100:
            raise serializers.ValidationError("Item code is too long")
        return value.strip()

    def validate_material_type(self, value):
        """Validate material type"""
        from django.conf import settings
        
        valid_types = [choice[0] for choice in RecyclingTransaction.MATERIAL_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid material type. Must be one of: {', '.join(valid_types)}"
            )
        return value


class RecyclingTransactionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for transaction retrieval"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = RecyclingTransaction
        fields = [
            'id', 'user', 'user_username', 'material_type', 'item_code', 
            'points_earned', 'status', 'machine_id', 'created_at', 'updated_at',
            'error_message'
        ]
        read_only_fields = fields


class PointsHistorySerializer(serializers.ModelSerializer):
    """Serializer for points history"""
    class Meta:
        model = PointsHistory
        fields = [
            'id', 'transaction_type', 'points_change', 'balance_after',
            'description', 'created_at'
        ]
        read_only_fields = fields

