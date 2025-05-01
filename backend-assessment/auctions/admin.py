from django.contrib import admin
from .models import Auction, Bid
from .forms import BidAdminForm

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'current_price', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    readonly_fields = ('current_price', 'winner')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    form = BidAdminForm
    list_display = ('auction', 'bidder', 'amount', 'timestamp')
    list_filter = ('auction', 'bidder')
    search_fields = ('auction__title', 'bidder__username')
