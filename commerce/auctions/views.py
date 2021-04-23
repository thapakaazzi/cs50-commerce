from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .models import User, AuctionListing, BidsListing, Comment, Watchlist, ValidationError


def index(request):
    auctions = AuctionListing.objects.filter(closed=False)
    
    return render(request, "auctions/index.html", {
        'items': auctions,
    })

def all_listing(request):
    auctions = AuctionListing.objects.all()
    
    return render(request, "auctions/index.html", {
        'items': auctions,
        'catagory' : True
    })


def catagory(request, filter):
    auctions = AuctionListing.objects.filter(catagory=filter).all
    return render(request, "auctions/index.html", {
        'items': auctions,
        'catagory' : True
    })

    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method=="POST":
        assert request.user.is_authenticated
        title =  request.POST['title']
        catagory = request.POST['category']
        min_bid = request.POST['min_bid']
        content = request.POST['description']
        url = request.POST['image_url']
        auction = AuctionListing(name=title, image=url, starting_bid=min_bid, catagory=catagory, description=content, owner=request.user)
        auction.save()
        
        return HttpResponseRedirect(reverse(index))
    return render(request, "auctions/create_listing.html")


@login_required
def listing(request, listing_id):
    item = AuctionListing.objects.get(pk=listing_id)
    comment = Comment.objects.filter(listing=listing_id).all()
    watchlist = Watchlist.objects.filter(user=request.user, item=item).all()
    
    if request.method == "POST":
        if  "comment_button" in request.POST:
            comment = Comment(author=request.user,
            content=request.POST['comment'],
            listing=item)
            comment.save()
            messages.add_message(request, messages.SUCCESS, "Your comment has been added!!")
            return HttpResponseRedirect(reverse('add_comment', args=[item.id]))


        if "add_watchlist" in request.POST:
            return HttpResponseRedirect(reverse('watchlist', args=[item.id]))

        if 'remove_watchlist' in request.POST:
            return HttpResponseRedirect(reverse( 'remove_watchlist', args=[item.id,] ))
        if "bid_button" in request.POST:
            if (int(request.POST['bid'])<10000000):
                try:
                    new_bid = BidsListing(listing=item,
                    offered_value=int(request.POST['bid']),
                    user=request.user)
                    new_bid.clean()
                    new_bid.save()
                    messages.add_message(request, messages.SUCCESS, "Your bid was made successfully!!!")
                except ValidationError:
                    messages.add_message(request, messages.WARNING, "Your bid is smaller than the current price!!!                                              ")
                return HttpResponseRedirect( reverse('bid', args=[item.id]))
            else:
                messages.add_message(request, messages.WARNING, 'Your bid is greater than 10,000,000')

    
    return render(request, "auctions/item.html", {
        'item': item,
        'comments': comment,
        'num': len(comment),
        'add_watchlist': False if watchlist else True,
        'bids_number':  item.no_of_bids,
        'close': True if item.owner==request.user else False
        })
    
    
@login_required
def my_listing(request):
    listing = AuctionListing.objects.filter(owner=request.user)
    return render(request, "auctions/index.html", {
        'items': listing
    })

@login_required
def add_comment(request, item_id):
    
    return HttpResponseRedirect(reverse('listing', args=[item_id]))


@login_required
def add_watchlist(request, listing_id):
    item = AuctionListing.objects.get(pk=listing_id)
    watchlist= Watchlist(user=request.user, 
    item=item )
    watchlist.save()
    messages.add_message(request, messages.SUCCESS, "Added to your watchlist!!!" )
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))


@login_required
def my_watchlist(request):
    my_watchlist = Watchlist.objects.filter(user=request.user).all()
    items=[]
    for item in my_watchlist:
        items.append(item.item)

    return render(request, "auctions/index.html", {
        'items': items
    })

@login_required
def remove_watchlist(request, listing_id):
    item = AuctionListing.objects.get(pk=listing_id)
    watchlist = Watchlist.objects.get(user=request.user, item=item)
    watchlist.delete()
    messages.add_message(request, messages.SUCCESS, "Removed from your watchlist!!!" )
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))


@login_required
def bid(request, listing_id):
    return HttpResponseRedirect(reverse('listing', args=[listing_id] ))


@login_required
def close_listing(request, listing_id):
    item = AuctionListing.objects.get(pk=listing_id)
    item.closed = True
    item.save()
    messages.add_message(request, messages.SUCCESS, f'Auctions is closed')
    if item.current_winning_bidder():
        messages.add_message(request, messages.SUCCESS, f'{item.current_winning_bidder} has own the acution!!!')
    else:
        messages.add_message(request, messages.SUCCESS, 'No one has bid for this acution!!!')
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

