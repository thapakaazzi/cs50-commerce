from django.contrib import admin
from .models import User, AuctionListing, BidsListing, Comment, Watchlist

# Register your models here.

admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(BidsListing)
admin.site.register(Comment)
admin.site.register(Watchlist)