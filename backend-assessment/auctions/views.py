from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Auction, Bid
from .serializers import (
    AuctionSerializer,
    CreateAuctionSerializer,
    PlaceBidSerializer,
    BidSerializer
)
from django.shortcuts import get_object_or_404

__all__ = [
    'AuctionListView',
    'AuctionCreateView',
    'AuctionDetailView',
    'BidCreateView',
    'BidListView',
    'BidDetailView',
    'AuctionEndView'
]

class AuctionListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AuctionSerializer

    def get_queryset(self):
        queryset = Auction.objects.all()
        if self.request.query_params.get('active'):
            queryset = queryset.filter(is_active=True)
        return queryset

class AuctionCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateAuctionSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class AuctionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        if serializer.instance.creator != self.request.user:
            raise permissions.PermissionDenied("You can only update your own auctions")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.creator != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own auctions")
        instance.delete()

# class BidListView(generics.ListAPIView):
#     serializer_class = BidSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         auction_id = self.kwargs.get('pk')
#         return Bid.objects.filter(auction_id=auction_id)

class BidListAPIView(generics.ListAPIView):
    serializer_class = BidSerializer

    def get_queryset(self):
        # Optionally filter by auction ID (if passed in the query params)
        auction_id = self.request.query_params.get('auction')
        if auction_id:
            return Bid.objects.filter(auction_id=auction_id)
        return Bid.objects.all()

class BidDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if serializer.instance.bidder != self.request.user:
            raise permissions.PermissionDenied("You can only update your own bids")
        if not serializer.instance.auction.is_active:
            raise ValueError("Cannot update bid on closed auction")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.bidder != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own bids")
        if not instance.auction.is_active:
            raise ValueError("Cannot delete bid on closed auction")
        instance.delete()

class BidCreateView(generics.CreateAPIView):
    serializer_class = PlaceBidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_auction(self):
        return get_object_or_404(Auction, pk=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        auction = self.get_auction()
        if not auction.is_active:
            return Response(
                {"detail": "This auction is closed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            bid = serializer.save(
                auction=auction,
                bidder=request.user
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            BidSerializer(bid, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED
        )

class AuctionEndView(generics.UpdateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        auction = self.get_object()
        
        if not auction.is_active:
            return Response(
                {"detail": "Auction is already closed."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if auction.creator != request.user:
            raise permissions.PermissionDenied("Only the auction creator can end the auction")

        auction.is_active = False
        highest_bid = auction.bids.order_by('-amount').first()
        if highest_bid:
            auction.winner = highest_bid.bidder
        auction.save()

        return Response(
            AuctionSerializer(auction).data,
            status=status.HTTP_200_OK
        )
