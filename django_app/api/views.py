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


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        import secrets
        import traceback
        from django.core.cache import cache
        from django.core.mail import send_mail

        print(f"[ForgotPassword] POST received with data: {request.data}")

        try:
            email = request.data.get("email")
            if not email:
                return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(email=email).first()
            if not user:
                profile = UserProfile.objects.filter(email=email).first()
                if profile:
                    user = profile.user

            print(f"[ForgotPassword] user object: {user}")

            if not user:
                return Response({"message": "If an account exists with this email, a reset link has been sent."}, status=status.HTTP_200_OK)

            print(f"[ForgotPassword] user found, proceeding")

            token = secrets.token_urlsafe(32)
            print(f"[ForgotPassword] Token generated: {token[:10]}...")

            cache.set(f"password_reset_{token}", user.id, timeout=3600)
            print(f"[ForgotPassword] Token cached")

            reset_link = f"https://django-app-tnbd.onrender.com/api/reset-password/?token={token}"
            print(f"[ForgotPassword] Sending email to {email}")

            import resend
            resend.api_key = os.environ.get("RESEND_API_KEY")
            resend.Emails.send({
                "from": "VoiceSchedule <onboarding@resend.dev>",
                "to": [email],
                "subject": "VoiceSchedule Password Reset",
                "text": f"Click the link below to reset your password:\n\n{reset_link}\n\nThis link expires in 1 hour.",
            })

            print(f"[ForgotPassword] Email sent successfully")
            return Response({"message": "If an account exists with this email, a reset link has been sent."}, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(f"[ForgotPassword] GLOBAL ERROR: {traceback.format_exc()}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"error": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)
        from django.core.cache import cache
        user_id = cache.get(f"password_reset_{token}")
        if not user_id:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Token is valid.", "token": token}, status=status.HTTP_200_OK)

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        if not token or not new_password:
            return Response({"error": "Token and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
        from django.core.cache import cache
        user_id = cache.get(f"password_reset_{token}")
        if not user_id:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            cache.delete(f"password_reset_{token}")
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "Both old and new password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        if not user.check_password(old_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        new_token = Token.objects.create(user=user)
        return Response(
            {"message": "Password updated successfully.", "token": new_token.key},
            status=status.HTTP_200_OK
        )


class CreateSuperUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        secret = request.data.get("secret")
        if secret != "myapp-admin-2026":
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        username = request.data.get("username")
        password = request.data.get("password")
        if User.objects.filter(username=username).exists():
            u = User.objects.get(username=username)
            u.is_staff = True
            u.is_superuser = True
            u.set_password(password)
            u.save()
            return Response({"message": f"{username} is now a superuser with updated password."})
        u = User.objects.create_superuser(username=username, password=password)
        Token.objects.get_or_create(user=u)
        return Response({"message": f"Superuser {username} created."}, status=status.HTTP_201_CREATED)


class UserProfileListCreate(generics.ListCreateAPIView):
    serializer_class = UserProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        UserProfile.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)


def index(request):
    return render(request, 'index.html')


class EventListCreate(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EventRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)
