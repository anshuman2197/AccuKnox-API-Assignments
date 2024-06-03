from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser,FriendRequest
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .serializers import UserSerializer, FriendRequestSerializer
from rest_framework.pagination import PageNumberPagination


# Search by name
class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if '@' in query:
            users = CustomUser.objects.filter(email=query)
        else:
            users = CustomUser.objects.filter(
                Q(username__icontains=query)
            )
        
        paginator = PageNumberPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# Sending Request
class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user_id')
        to_user = CustomUser.objects.get(id=to_user_id)
        from_user = request.user

        one_minute_ago = timezone.now() - timedelta(minutes=1)
        if from_user.sent_friend_requests.filter(timestamp__gte=one_minute_ago).count() >= 3:
            return Response({"error": "You have reached the limit of 3 friend requests per minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        friend_request, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
        if not created:
            return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

# Accept Friendrequest
class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        try:
            print(FriendRequest.objects.all().values())
            friend_request = FriendRequest.objects.get(id=pk, to_user=request.user)
            friend_request.status = 'accepted'
            friend_request.save()
            return Response(FriendRequestSerializer(friend_request).data)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

# Reject request
class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        try:
            friend_request = FriendRequest.objects.get(id=pk, to_user=request.user)
            friend_request.status = 'rejected'
            friend_request.save()
            return Response(FriendRequestSerializer(friend_request).data)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)

# See List of friends
class ListFriendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        friends = CustomUser.objects.filter(
            Q(sent_friend_requests__to_user=user, sent_friend_requests__status='accepted') |
            Q(received_friend_requests__from_user=user, received_friend_requests__status='accepted')
        ).distinct()
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)

# see list of pending request
class ListPendingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pending_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)



# User should  be able to signup with ther email only.
# No Otp Verification required.
# Valid Email format is Sufficient.
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Should Login with there email and password.
# Email Should be case Insensitive.
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        email = request.data.get('email', '').lower() 
        password = request.data.get('password')

        user = None
        if '@' in email:
            try:
                user = CustomUser.objects.get(email=email)
            except ObjectDoesNotExist:
                pass

        if user:
            authenticated_user = authenticate(email=email, password=password)
            if authenticated_user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)

# It will logout the application
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

