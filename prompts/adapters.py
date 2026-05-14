from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect

from prompts.models import AllowedEmail


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        """
        pass

    def populate_user(self, request, sociallogin, data):
        """
        Hook to populate user instance with data from social provider.
        """
        user = super().populate_user(request, sociallogin, data)

        # Set username from email (before @ symbol)
        if not user.username and user.email:
            # Get the part before @ in email
            base_username = user.email.split('@')[0]

            # Make sure it's unique by appending numbers if needed
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user.username = username

        # Set first_name and last_name from Google data if available
        if 'given_name' in data:
            user.first_name = data['given_name']
        if 'family_name' in data:
            user.last_name = data['family_name']

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Save the user and assign to EarthRISE group if email is in allowed list.
        This is called after the user is created.
        """
        user = super().save_user(request, sociallogin, form)

        # Check if user's email is in the allowed emails list
        if user.email and AllowedEmail.objects.filter(email__iexact=user.email).exists():
            try:
                earthrise_group = Group.objects.get(name='EarthRISE')
                user.groups.add(earthrise_group)
                print(f"Added {user.email} to EarthRISE group")
            except Group.DoesNotExist:
                print("Warning: EarthRISE group does not exist")

        return user
