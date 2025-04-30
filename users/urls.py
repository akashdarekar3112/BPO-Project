from django.urls import path
from users.views import CheckHealth, CreateCheckoutSessionView, LoginAPIView, MatchView, SetRole, StripeWebhookAPIView, SubscriptionPlanAPIView, UserProfileView, UserRegistrationView, VerifyEmailView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('health', CheckHealth.as_view(), name='check-health'),
    path('register', UserRegistrationView.as_view(), name='user-register'),
    path('email_verification', VerifyEmailView.as_view(), name='email-verification'),
    path('login', LoginAPIView.as_view(), name='user-login'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('user_profile', UserProfileView.as_view(), name='user-profile'),
    path('set_role', SetRole.as_view(), name='set-role'),
    path('matches', MatchView.as_view(), name='get-matches'),
    path('ml/match', MatchView.as_view(), name='ml-matches'),
    path('subscription_plans', SubscriptionPlanAPIView.as_view(), name='subscription-plans'),
    path('checkout', CreateCheckoutSessionView.as_view(), name='checkout'),
    path('webhook', StripeWebhookAPIView.as_view(), name='webhook'),

]