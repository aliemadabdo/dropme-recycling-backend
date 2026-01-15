from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from .models import RecyclingTransaction, PointsHistory
from .serializers import (
    RecyclingTransactionSerializer, RecyclingTransactionDetailSerializer,
    PointsHistorySerializer
)
from .services import RecyclingService

class CreateRecyclingTransactionView(APIView):
    """Create a new recycling transaction"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Create recycling transaction",
        description="Submit a new item for recycling and earn points",
        request=RecyclingTransactionSerializer,
        responses={201: RecyclingTransactionDetailSerializer}
    )
    def post(self, request):
        serializer = RecyclingTransactionSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        service = RecyclingService()
        
        try:
            transaction = service.create_transaction(
                user=request.user,
                material_type=serializer.validated_data['material_type'],
                item_code=serializer.validated_data['item_code'],
                weight_grams=serializer.validated_data['weight_grams'],
                machine_id=serializer.validated_data.get('machine_id')
            )
            
            return Response({
                'message': 'Transaction completed successfully',
                'transaction': RecyclingTransactionDetailSerializer(transaction).data,
                'user_points': request.user.total_points
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)


class TransactionListView(generics.ListAPIView):
    """List user's recycling transactions"""
    serializer_class = RecyclingTransactionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecyclingTransaction.objects.filter(
            user=self.request.user
        ).select_related('user')

    @extend_schema(
        summary="List user transactions",
        description="Get a list of all recycling transactions for the authenticated user"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TransactionDetailView(generics.RetrieveAPIView):
    """Get transaction details"""
    serializer_class = RecyclingTransactionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return RecyclingTransaction.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Get transaction details",
        description="Retrieve details of a specific transaction"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PointsHistoryView(generics.ListAPIView):
    """View points transaction history"""
    serializer_class = PointsHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PointsHistory.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Get points history",
        description="View the complete history of points earned and redeemed"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

