from django.urls import path
from .views import (
    CreateRecyclingTransactionView,
    TransactionListView,
    TransactionDetailView,
    PointsHistoryView,
)

app_name = 'recycling'

urlpatterns = [
    
    # Recycling transactions
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/create/', CreateRecyclingTransactionView.as_view(), name='transaction-create'),
    path('transactions/<uuid:id>/', TransactionDetailView.as_view(), name='transaction-detail'),
    
    # Points history
    path('points/history/', PointsHistoryView.as_view(), name='points-history'),
]