from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import UserProfile, Event
from .serializers import UserProfileSerializer, EventSerializer
from rest_framework.permissions import AllowAny

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.all()