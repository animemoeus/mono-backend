from rest_framework import serializers

from authentication import firebase


class LoginWithGoogleSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            firebase.validate_token(value)
        except Exception as e:
            msg = "Invalid token"
            raise serializers.ValidationError(msg) from e

        return value
