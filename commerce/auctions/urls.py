from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('add-watchlist/<int:listing_id>', views.add_watchlist, name='add-watchlist'),
    path('remove-watchlist/<int:listing_id>', views.remove_watchlist, name="remove-watchlist"),
    path('create-listing', views.create_listing, name="create-listing"),
    path('listing/<int:listing_id>', views.listing, name="listing"),
    path('my-listing', views.my_listing, name="my-listing"),
    path('add_comment/<int:item_id>', views.add_comment, name="add_comment"),
    path('my-watchlist', views.my_watchlist, name="my-watchlist"),
    path('bid/<int:listing_id>', views.bid, name="bid"),
    path('close-listing/<int:listing_id>', views.close_listing, name="close-listing"),
    path('all-listing/', views.all_listing, name="all-listing"),
    path('catagory/<str:filter>', views.catagory, name="catagory")
]
