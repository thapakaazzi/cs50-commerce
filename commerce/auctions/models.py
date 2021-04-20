from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _
from datetime import datetime


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_items")
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=900, default="")
    image= models.URLField(max_length=200, null=True, blank=True)
    starting_bid= models.DecimalField(max_digits=6, decimal_places=2)
    catagory = models.CharField(max_length=50, null=True)
    closed = models.BooleanField(default=False)

    
    def current_price(self):
        return max([bid.offered_value for bid in self.bids.all()]+[self.starting_bid])

    def no_of_bids(self):
        return len(self.bids.all())

    def current_winning_bidder(self):
        return self.bids.get(offered_value=self.current_price()).user if self.no_of_bids() > 0 else None

    def __str__(self):
        return f'{self.name} by {self.owner}: {self.description}'


class BidsListing(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    offered_value= models.DecimalField(max_digits=6, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")

    def clean(self):
        #for bidding to be higher than previous bids
        if self.offered_value and self.listing.current_price():
            if self.offered_value <= self.listing.current_price():
                raise ValidationError({'offered_value': _('Please make sure your bid value is higher than the current')})
    
    def __str__(self):
        return f'{self.user} has offered to pay ${self.offered_value} for {self.listing}'


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content=models.CharField(max_length=900)
    date= models.DateTimeField( default=datetime.now)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="auc_comments")

    def __str__(self):
        return f"{self.author} says {self.content} for {self.listing}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_item")
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="listed_item")
    

