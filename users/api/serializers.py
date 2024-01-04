from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .utils import validate_email as email_is_valid
from django.contrib.auth import authenticate
UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    # class Meta:
    #     model = UserModel
    #     fields = (
    #         'email',
    #         'username',
    #         'password',
    #         'tokens',
    #         'is_staff',
    #         'is_active',
    #     )
    #     read_only_fields = ('tokens', 'is_staff')

    # def validate_email(self, data):
    #     print(data.get("email"))
    #     if data['email'] is None:
    #         raise serializers.ValidationError("Email is required")
    #     return data['email']

    # def validate_password(self, data):
    #     print(data.get("password"))
    #     if data['password'] is None:
    #         raise serializers.ValidationError("Password is required")
    #     return data['password']

    # def validate(self, data):
    #     # The `validate` method is where we make sure that the current
    #     # instance of `LoginSerializer` has "valid". In the case of logging a
    #     # user in, this means validating that they've provided an email
    #     # and password and that this combination matches one of the users in
    #     # our database.
    #     print(data)
    #     if data['email'] is None:
    #         raise serializers.ValidationError("Email is required")
    #     if data['password'] is None:
    #         raise serializers.ValidationError("Password is required")
    #     email = data['email']
    #     password = data['password']
    #     print(email, " ", password)

    #     # Raise an exception if an
    #     # email is not provided.
    #     # if email is None:
    #     #     raise serializers.ValidationError(
    #     #         'An email address is required to log in.'
    #     #     )

    #     # Raise an exception if a
    #     # password is not provided.
    #     # if password is None:
    #     #     raise serializers.ValidationError(
    #     #         'A password is required to log in.'
    #     #     )

    #     # The `authenticate` method is provided by Django and handles checking
    #     # for a user that matches this email/password combination. Notice how
    #     # we pass `email` as the `username` value since in our User
    #     # model we set `USERNAME_FIELD` as `email`.
    #     # user = authenticate(username=email, password=password)
    #     # print(user)
    #     # If no user was found matching this email/password combination then
    #     # `authenticate` will return `None`. Raise an exception in this case.
    #     # if user is None:
    #     #     raise serializers.ValidationError(
    #     #         'A user with this email and password was not found.'
    #     #     )

    # Django provides a flag on our `User` model called `is_active`. The
    # purpose of this flag is to tell us whether the user has been banned
    # or deactivated. This will almost never be the case, but
    # it is worth checking. Raise an exception in this case.
    # if not user.is_active:
    #     raise serializers.ValidationError(
    #         'This user has been deactivated.'
    #     )

    #     # The `validate` method should return a dictionary of validated data.
    #     # This is the data that is passed to the `create` and `update` methods
    #     # that we will see later on.
    #     # print(user.token)
    # return {
    #     'email': user.email,
    #     'username': user.username,
    #     'token': user.token
    # }


class UserSerializer(serializers.ModelSerializer[UserModel]):
    """Handle serialization and deserialization of User objects."""

    password = serializers.CharField(
        max_length=128, min_length=8, write_only=True)

    class Meta:
        model = UserModel
        fields = (
            'email',
            'username',
            'password',
            'tokens',
            'is_staff',
            'is_active',
        )
        read_only_fields = ('tokens', 'is_staff')

    def update(self, instance, validated_data):  # type: ignore
        """Perform an update on a User."""

        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class LogoutSerializer(serializers.Serializer[UserModel]):
    refresh = serializers.CharField()

    def validate(self, attrs):  # type: ignore
        """Validate token."""
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):  # type: ignore
        """Validate save backlisted token."""

        try:
            RefreshToken(self.token).blacklist()

        except TokenError as ex:
            raise exceptions.AuthenticationFailed(ex) from ex
