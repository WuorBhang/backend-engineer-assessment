from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Auction(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions_created')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctions_won')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.current_price:
            self.current_price = self.starting_price
        super().save(*args, **kwargs)

    def update_status(self):
        now = timezone.now()
        if self.end_time <= now and self.is_active:
            self.is_active = False
            self.save()

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids_made')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount']

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new bids
            if self.amount <= self.auction.current_price:
                raise ValueError("Bid must be higher than current price")
            self.auction.current_price = self.amount
            self.auction.save()
        super().save(*args, **kwargs)
