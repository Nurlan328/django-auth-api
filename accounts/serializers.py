"""DRF serializers — validation and (de)serialization of API data.

The Django/DRF analogue of Pydantic schemas in the FastAPI version.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """What we return to the client (no password)."""

    # Expose Django's built-in date_joined under the name created_at.
    created_at = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    """What the client sends on registration."""

    password = serializers.CharField(write_only=True, min_length=6)
    created_at = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "created_at"]
        # role is read-only -> a user cannot make themselves an admin
        read_only_fields = ["id", "role", "created_at"]

    def create(self, validated_data):
        # create_user hashes the password for us
        return User.objects.create_user(**validated_data)
