from django.conf import settings
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_customer(user):
    """Create Stripe customer and attach it to the user."""
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
            metadata={'user_id': user.id}
        )
        user.stripe_customer_id = customer.id
        user.save()