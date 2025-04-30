import logging
import traceback
import stripe
from django.conf import settings

from .models import SubscriptionMaster, SubscriptionPlan

logger = logging.getLogger("django")

class StripeClass:
    def __init__(self) -> None:
        self.api_key = settings.STRIPE_SECRET_KEY

    def create_customer(self, user_name, email):
        """Create Stripe customer"""
        try:
            stripe.api_key = self.api_key
            response = stripe.Customer.create(name=user_name, email=email)
            return response
        except Exception as e:
            logger.error(f"An error occurred while creating Stripe customer: {str(e)}")
            logger.error(traceback.format_exc())

    def create_or_update_subscription(self, event_type, data):
        """Create or update subscription"""
        try:
            stripe.api_key = self.api_key

            stripe_customer_id = data.get('stripe_customer_id')
            subscription_id = data.get('subscription_id')
            stripe_status = data.get('stripe_status')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            billing_reason = data.get('billing_reason')
            prod_price_id = data.get('prod_price_id')
            is_active = stripe_status in ('active', 'paid')

            # Ensure required fields
            required_fields = [stripe_customer_id, subscription_id, stripe_status, start_date, end_date]
            if not all(required_fields):
                logger.error(f"Missing required subscription fields: {data}")
                return

            # Get subscription plan
            if not prod_price_id:
                logger.error("Missing prod_price_id in Stripe data.")
                return

            try:
                subscription_plan = SubscriptionPlan.objects.get(prod_price_id=prod_price_id)
            except SubscriptionPlan.DoesNotExist:
                logger.error(f"SubscriptionPlan not found for prod_price_id: {prod_price_id}")
                return

            # (Optional) Get user if needed
            from users.models import CustomUser
            try:
                user = CustomUser.objects.get(stripe_customer_id=stripe_customer_id)
            except CustomUser.DoesNotExist:
                logger.error(f"User not found for stripe_customer_id: {stripe_customer_id}")
                return
            except CustomUser.MultipleObjectsReturned:
                logger.error(f"Multiple users found for stripe_customer_id: {stripe_customer_id}")
                return

            subscription_instance, created = SubscriptionMaster.objects.update_or_create(
                stripe_customer_id=stripe_customer_id,
                defaults={
                    # 'user': user,  # include only if your model needs it
                    'subscription_plan': subscription_plan,
                    'subscription_id': subscription_id,
                    'stripe_status': stripe_status,
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_active': is_active,
                    'billing_reason': billing_reason,
                }
            )

            logger.info(f"Subscription {'created' if created else 'updated'}: {subscription_instance}")

        except Exception as e:
            logger.error(f"An error occurred while creating or updating subscription: {str(e)}")
            logger.error(traceback.format_exc())