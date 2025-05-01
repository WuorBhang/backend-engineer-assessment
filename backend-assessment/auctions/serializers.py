from rest_framework import serializers
from .models import Auction, Bid
from authentication.serializers import UserSerializer

class BidSerializer(serializers.ModelSerializer):
    bidder = UserSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'bidder', 'amount', 'timestamp']
        read_only_fields = ['id', 'bidder', 'timestamp']

class AuctionSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    winner = UserSerializer(read_only=True)
    bids = BidSerializer(many=True, read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Auction
        fields = [
            'id', 'title', 'description', 'starting_price', 'current_price',
            'start_time', 'end_time', 'creator', 'winner', 'is_active', 'bids'
        ]
        read_only_fields = ['id', 'creator', 'current_price', 'winner', 'is_active']

class CreateAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'starting_price', 'start_time', 'end_time']

class PlaceBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['amount']
