from django.urls import path
from .views import (
    AuctionListView,
    AuctionCreateView,
    AuctionDetailView,
    BidCreateView,
    BidListAPIView,
    BidDetailView,
    AuctionEndView
)

urlpatterns = [
    path('', AuctionListView.as_view(), name='auction-list'),
    path('create/', AuctionCreateView.as_view(), name='auction-create'),
    path('<int:pk>/', AuctionDetailView.as_view(), name='auction-detail'),
    path('<int:pk>/end/', AuctionEndView.as_view(), name='auction-end'),
    path('bids/', BidListAPIView.as_view(), name='bids-list'),
    path('<int:pk>/bids/create/', BidCreateView.as_view(), name='bid-create'),
    path('bids/<int:pk>/', BidDetailView.as_view(), name='bid-detail'),
]
