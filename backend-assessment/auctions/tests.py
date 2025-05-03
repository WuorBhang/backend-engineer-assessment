from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from auctions.models import Auction, Bid


User = get_user_model()

class AuctionModelTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password456')

        # Create an auction
        self.auction = Auction.objects.create(
            title="Test Auction",
            description="This is a test auction.",
            starting_price=100.00,
            start_time=timezone.now() - timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=1),
            creator=self.user1
        )

    def test_auction_creation(self):
        """Test that an auction is created correctly."""
        self.assertEqual(self.auction.title, "Test Auction")
        self.assertEqual(self.auction.current_price, 100.00)
        self.assertTrue(self.auction.is_active)

    def test_update_status_active(self):
        """Test that the auction remains active if the end time is in the future."""
        self.auction.update_status()
        self.assertTrue(self.auction.is_active)

    def test_update_status_inactive(self):
        """Test that the auction becomes inactive if the end time has passed."""
        self.auction.end_time = timezone.now() - timezone.timedelta(hours=1)
        self.auction.update_status()
        self.assertFalse(self.auction.is_active)

    def test_current_price_initialization(self):
        """Test that the current price is initialized to the starting price."""
        auction = Auction.objects.create(
            title="New Auction",
            description="Another test auction.",
            starting_price=50.00,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1),
            creator=self.user1
        )
        self.assertEqual(auction.current_price, 50.00)

    def test_winner_assignment(self):
        """Test that the winner can be assigned after the auction ends."""
        self.auction.is_active = False
        self.auction.winner = self.user2
        self.auction.save()
        self.assertEqual(self.auction.winner, self.user2)


class BidModelTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password456')

        # Create an auction
        self.auction = Auction.objects.create(
            title="Test Auction",
            description="This is a test auction.",
            starting_price=100.00,
            start_time=timezone.now() - timezone.timedelta(days=1),
            end_time=timezone.now() + timezone.timedelta(days=1),
            creator=self.user1
        )

    def test_bid_creation(self):
        """Test that a bid is created correctly."""
        bid = Bid.objects.create(
            auction=self.auction,
            bidder=self.user2,
            amount=150.00
        )
        self.assertEqual(bid.amount, 150.00)
        self.assertEqual(self.auction.current_price, 150.00)

    def test_invalid_bid_amount(self):
        """Test that a bid with an invalid amount raises an error."""
        with self.assertRaises(ValueError):
            Bid.objects.create(
                auction=self.auction,
                bidder=self.user2,
                amount=90.00  # Less than the current price
            )

    def test_bids_ordering(self):
        """Test that bids are ordered by amount in descending order."""
        Bid.objects.create(auction=self.auction, bidder=self.user2, amount=150.00)
        Bid.objects.create(auction=self.auction, bidder=self.user1, amount=200.00)
        bids = list(Bid.objects.all())
        self.assertEqual(bids[0].amount, 200.00)
        self.assertEqual(bids[1].amount, 150.00)

    def test_bid_updates_current_price(self):
        """Test that placing a valid bid updates the auction's current price."""
        Bid.objects.create(auction=self.auction, bidder=self.user2, amount=150.00)
        self.assertEqual(self.auction.current_price, 150.00)
        Bid.objects.create(auction=self.auction, bidder=self.user1, amount=200.00)
        self.assertEqual(self.auction.current_price, 200.00)