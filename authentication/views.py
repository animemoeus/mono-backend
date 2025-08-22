from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication import firebase
from authentication.serializers import LoginWithGoogleSerializer
from backend.users.models import User


class LoginWithGoogleView(APIView):
    serializer_class = LoginWithGoogleSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data.get("token")
        user_info = firebase.get_user_info(token)

        user, _ = User.objects.get_or_create(
            email=user_info.get("email"),
            defaults={
                "username": f"{user_info.get('email')}",
                "name": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}",
            },
        )

        # Activate the user if they are not already active
        if not user.is_active:
            user.is_active = True
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )
