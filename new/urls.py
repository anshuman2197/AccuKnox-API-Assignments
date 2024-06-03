from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('send_friend_request/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('accept_friend_request/<int:pk>/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('reject_friend_request/<int:pk>/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('list_friends/', ListFriendsView.as_view(), name='list-friends'),
    path('pending_friend_requests/', ListPendingFriendRequestsView.as_view(), name='pending-friend-requests'),
]
  