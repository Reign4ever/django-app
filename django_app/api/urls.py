from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("users/", views.UserProfileListCreate.as_view(), name="user-view-create"),
    path("users/<int:pk>/", views.UserProfileRetrieveUpdateDestroy.as_view(), name="update"),
]