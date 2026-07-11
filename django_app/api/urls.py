from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("mobile/token/", views.MobileLoginView.as_view(), name="mobile-login"),
    path("mobile/register/", views.MobileRegisterView.as_view(), name="mobile-register"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("", views.index, name="index"),
    path("users/", views.UserProfileListCreate.as_view(), name="user-view-create"),
    path("users/<int:pk>/", views.UserProfileRetrieveUpdateDestroy.as_view(), name="update"),
    path("events/", views.EventListCreate.as_view(), name="event-list-create"),
    path("events/<int:pk>/", views.EventRetrieveUpdateDestroy.as_view(), name="event-detail"),
]