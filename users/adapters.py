from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from .models import User


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to handle Google OAuth user creation"""
    
    def pre_social_login(self, request, sociallogin):
        """Called before social login"""
        if sociallogin.is_existing:
            return
        
        # Extract user data from Google
        if sociallogin.account.provider == 'google':
            user_data = sociallogin.account.extra_data
            
            # Save profile picture
            if 'picture' in user_data:
                sociallogin.user.profile_picture = user_data['picture']
            
            # Set role to student by default
            sociallogin.user.role = 'student'
    
    def populate_user(self, request, sociallogin):
        """Populate user instance with data"""
        user = super().populate_user(request, sociallogin)
        
        # Extract from Google data
        extra_data = sociallogin.account.extra_data
        
        if 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
        
        if 'family_name' in extra_data:
            user.last_name = extra_data['family_name']
        
        if 'picture' in extra_data:
            user.profile_picture = extra_data['picture']
        
        # Set role to student by default
        if not user.role:
            user.role = 'student'
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """Save user to database"""
        user = super().save_user(request, sociallogin, form)
        
        # Save Google ID
        if sociallogin.account.provider == 'google':
            user.google_id = sociallogin.account.uid
        
        user.save()
        return user


@receiver(user_logged_in)
def user_logged_in_handler(sender, **kwargs):
    """Handle post-login redirect for Google OAuth users"""
    request = kwargs['request']
    user = kwargs['user']
    
    # The redirect is handled by LOGIN_REDIRECT_URL setting
    # but we can add custom logic here if needed
    if hasattr(user, 'socialaccount_set'):
        social_accounts = user.socialaccount_set.all()
        if social_accounts.exists():
            # User logged in via social auth
            pass

