from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .models import UserProfile, Event
from .serializers import UserProfileSerializer, EventSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email    = request.data.get("email", "")
        name     = request.data.get("name", "")
        phone    = request.data.get("phone", "")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user  = User.objects.create_user(username=username, password=password, email=email)
        token = Token.objects.create(user=user)
        UserProfile.objects.create(user=user, name=name, email=email, phone=phone)

        return Response({"token": token.key, "username": username}, status=status.HTTP_201_CREATED)


class UserProfileListCreate(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def delete(self, request, *args, **kwargs):
        UserProfile.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"


def index(request):
    return render(request, 'index.html')



class EventListCreate(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Event.objects.all()

    def perform_create(self, serializer):
        serializer.save()


class EventRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.all()
