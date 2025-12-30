from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import requests
from io import BytesIO
from django.core.files import File

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to handle Google OAuth user creation"""
    
    def pre_social_login(self, request, sociallogin):
        """Called before social login - link existing email accounts"""
        if sociallogin.is_existing:
            return
        
        # Check if user with this email already exists
        if sociallogin.account.provider == 'google':
            email = sociallogin.account.extra_data.get('email')
            if email:
                try:
                    existing_user = User.objects.get(email=email)
                    # Connect the social account to existing user
                    sociallogin.connect(request, existing_user)
                except User.DoesNotExist:
                    pass
    
    def populate_user(self, request, sociallogin, data):
        """Populate user instance with data from Google"""
        user = super().populate_user(request, sociallogin, data)
        
        # Extract from Google data
        extra_data = sociallogin.account.extra_data
        
        # Set first name
        if 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
        
        # Set last name
        if 'family_name' in extra_data:
            user.last_name = extra_data['family_name']
        
        # Set username from email if not set
        if not user.username and user.email:
            base_username = user.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username
        
        # Set role to student by default
        user.role = 'student'
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """Save user to database with Google profile picture"""
        user = super().save_user(request, sociallogin, form)
        
        # Save Google ID
        if sociallogin.account.provider == 'google':
            user.google_id = sociallogin.account.uid
            
            # Download and save profile picture
            extra_data = sociallogin.account.extra_data
            if 'picture' in extra_data:
                picture_url = extra_data['picture']
                try:
                    # Download the image
                    response = requests.get(picture_url, timeout=10)
                    if response.status_code == 200:
                        # Create a file from the response content
                        img_temp = BytesIO(response.content)
                        filename = f"google_{user.google_id}.jpg"
                        user.profile_picture.save(filename, File(img_temp), save=False)
                except Exception as e:
                    # If download fails, just log it and continue
                    print(f"Failed to download profile picture: {e}")
            
            user.save()
        
        return user


@receiver(user_logged_in)
def user_logged_in_handler(sender, **kwargs):
    """Handle post-login actions for Google OAuth users"""
    request = kwargs['request']
    user = kwargs['user']
    
    # Update profile picture if it's a social login and picture is missing
    if hasattr(user, 'socialaccount_set'):
        social_accounts = user.socialaccount_set.filter(provider='google')
        if social_accounts.exists():
            social_account = social_accounts.first()
            extra_data = social_account.extra_data
            
            # Update profile picture if missing
            if not user.profile_picture and 'picture' in extra_data:
                picture_url = extra_data['picture']
                try:
                    response = requests.get(picture_url, timeout=10)
                    if response.status_code == 200:
                        img_temp = BytesIO(response.content)
                        filename = f"google_{user.google_id}.jpg"
                        user.profile_picture.save(filename, File(img_temp), save=True)
                except Exception as e:
                    print(f"Failed to update profile picture: {e}")

