from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from django.shortcuts import redirect
from django.contrib.auth import login


class GoogleOAuth2CallbackView(OAuth2CallbackView):
    """Custom callback view for Google OAuth2 to handle post-login redirect"""
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        # If login was successful and user is authenticated, redirect to dashboard
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        return response
