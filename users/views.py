import json
import logging
import traceback
from django.conf import settings
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import stripe
from django.db.models import Q

from users import stripe_module
from users.models import CustomUser, ProviderProfile, SeekerProfile, SubscriptionPlan
from users.send_email import send_payment_failed_email, send_payment_success_email, send_verification_email
from users.stripe_config import create_stripe_customer
from users.swagger_decorators import (
                    checkout_payment, create_payment_plan_docs, fetch_subscription_plans_docs, get_user_profile,
                    matched_users_swagger, set_role_swagger, user_profile_swagger, users_login, users_register, verify_email
                    )
from .serializers import ProviderProfileSerializer, SeekerProfileSerializer, SubscriptionPlanSerializer, UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


logger = logging.getLogger("django")

class CheckHealth(APIView):
    permission_classes = [AllowAny] 
    def get(self, request):
        return Response({"message":"Backend is working fine"}, status=status.HTTP_200_OK)

class UserRegistrationView(APIView):

    permission_classes = [AllowAny] 

    @users_register()
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            create_stripe_customer(user)  
            uid = user.id
            token = jwt.encode({'uid': uid}, settings.SECRET_KEY, algorithm='HS256')  
            reponse_data = {
                "uid": uid,
                "token": token
            }

            send_verification_email(user)

            return Response({"message": "User registered successfully. Please check your email to verify your account.", "reponse_data":reponse_data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class VerifyEmailView(APIView):
    permission_classes = [AllowAny] 

    @verify_email()
    def get(self, request):
        token = request.GET.get('token')

        if not token:
            return Response({"error": "Invalid request. Token missing."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            uid = decoded_token.get('uid')

            user = CustomUser.objects.get(id=uid)
            user.is_email_verified = True
            user.save()

            return Response({'message': 'Email verified successfully!'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired!'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token!'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid User!'}, status=status.HTTP_404_NOT_FOUND)
        

class LoginAPIView(APIView):
    permission_classes = [AllowAny] 

    @users_login()
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.get(email=email)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_email_verified:
            return Response({"error": "Email is not verified. Please check your email to verify your account."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class SetRole(APIView):
    """API view to set user role."""
    permission_classes = [IsAuthenticated] 

    @set_role_swagger()
    def post(self, request, *agrs, **kwargs):
        """API view method to update user role."""

        user_role = request.data.get("user_role")
        if not user_role:
            return Response({"message":"Please provide user_role"}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        try:
            CustomUser.objects.get(id=user_id)
        except Exception as e:
            return Response({"message":"User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            CustomUser.objects.filter(id=user_id).update(role=user_role)
            return Response({"message":"User role updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":"Internal server error.", "error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated] 

    @user_profile_swagger()
    def post(self, request):
        user = request.user

        if user.role == 'seeker':
            serializer = SeekerProfileSerializer(data=request.data)
            if serializer.is_valid():
                SeekerProfile.objects.update_or_create(user=user, defaults=serializer.validated_data)
                return Response({"message": "Seeker profile saved.", "data":serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif user.role == 'provider':
            serializer = ProviderProfileSerializer(data=request.data)
            if serializer.is_valid():
                ProviderProfile.objects.update_or_create(user=user, defaults=serializer.validated_data)
                return Response({"message": "Provider profile saved.", "data":serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"message": "Role not set or unsupported."}, status=status.HTTP_400_BAD_REQUEST)
    
    @get_user_profile()
    def get(self, request):
        user = request.user  
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_email_verified": user.is_email_verified,
            "password": user.password,
            "stripe_customer_id": user.stripe_customer_id
        }

        return Response(user_data, status=status.HTTP_200_OK)


class MatchView(APIView):
    permission_classes = [IsAuthenticated]

    @matched_users_swagger()
    def get(self, request):
        user = request.user

        if user.role == 'seeker':

            try:
                seeker_profile = SeekerProfile.objects.get(user=user)
            except SeekerProfile.DoesNotExist:
                return Response({'error': 'Seeker profile not found.'}, status=404)

            industry = request.query_params.get('industry',)
            location = request.query_params.get('location',)

            providers = ProviderProfile.objects.filter(
                Q(service_types__icontains=industry) | Q(geoserved__icontains=location)
                
            )

            serializer = ProviderProfileSerializer(providers, many=True)
            return Response({'matches': serializer.data})
        
        if user.role == 'provider':
            try:
                provider_profile = ProviderProfile.objects.get(user=user)
            except ProviderProfile.DoesNotExist:
                return Response({'error': 'Provider profile not found.'}, status=404)

            industries = provider_profile.service_types  
            locations = provider_profile.geoserved      

            seekers = SeekerProfile.objects.filter(
                industry__in=industries,
                location__in=locations
            )

            serializer = SeekerProfileSerializer(seekers, many=True)
            return Response({'matches': serializer.data})
        
        
class SubscriptionPlanAPIView(APIView):


    @create_payment_plan_docs()
    def post(self, request, *args, **kwargs):
        """API view method to add plans."""
        required_fields = ["payment_type", "plan_name", "plan_description", "prod_id", "prod_price_id"]
        missing_fields = [field for field in required_fields if not request.data.get(field)]

        if missing_fields:
            return Response(
                {"message": f"Please provide {', '.join(missing_fields)}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        payment_type = request.data.get("payment_type")
        plan_name = request.data.get("plan_name")
        plan_description = request.data.get("plan_description")
        prod_id = request.data.get("prod_id")
        prod_price_id = request.data.get("prod_price_id")
        
        user_email = request.user.email
        if not CustomUser.objects.filter(email=user_email).exists():
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # if user_email != str(settings.ADMIN_EMAIL):
        #     return Response({"message": "Unauthorized user."}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            plan_data = SubscriptionPlan(
                payment_type=payment_type,
                plan_name = plan_name,
                description = plan_description,
                prod_id = prod_id,
                prod_price_id = prod_price_id,
            )
            plan_data.save()
            return Response({"message":"Plan saved successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message":"Interal server error.", "error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)     

    @fetch_subscription_plans_docs()
    def get(self, request, *args, **kwargs):
        """Fetch active subscription plans"""

        subscription_plans_all = SubscriptionPlan.objects.all()
        subscription_plans = [
            plan for plan in subscription_plans_all if plan.is_active]

        subscription_plans_serialized = SubscriptionPlanSerializer(
            subscription_plans, many=True).data

        return Response({"message": "Fetched subscription plans", "data": subscription_plans_serialized}, status=status.HTTP_200_OK) 
        
class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    @checkout_payment()
    def post(self, request):
        user = request.user
        payment_type = request.data.get('payment_type')
        price_id = request.data.get('price_id')
        
        if not all([payment_type, price_id]):
            return Response({'error': 'Missing required fields'}, status=400)
        
        if not user.stripe_customer_id:
            return Response({"error": "Stripe customer not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment' if payment_type == 'one_time' else 'subscription',
                success_url='http://127.0.0.1:8000/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://127.0.0.1:8000/cancel/',

            )
            return Response({'checkout_url': session.url})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class StripeWebhookAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request, *args, **kwargs):
        """Stripe webhook handler"""

        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        request_data = json.loads(request.body.decode('utf-8'))

        if webhook_secret:
            signature = request.headers.get('stripe-signature')

            try:
                event = stripe.Webhook.construct_event(
                    payload=request.body,
                    sig_header=signature,
                    secret=webhook_secret
                )
                data = event.get('data', {})
                event_type = event.get('type', '')
            except stripe.error.SignatureVerificationError:
                logger.error("Invalid Stripe signature")
                return Response({"message": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)
            except json.JSONDecodeError:
                logger.error("Invalid JSON payload")
                return Response({"message": "Invalid JSON payload"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                logger.error(f"Error parsing Stripe webhook: {traceback.format_exc()}")
                return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            data = request_data.get('data', {})
            event_type = request_data.get('type', '')

        data_object = data.get('object', {})
        stripe_customer_id = data_object.get('customer')
        subscription_id = data_object.get('subscription')
        stripe_status = data_object.get('status')
        billing_reason = data_object.get('billing_reason')
        start_date = None
        end_date = None
        prod_price_id = None

        # Log event
        logger.info(f"Received Stripe webhook event '{event_type}' for customer '{stripe_customer_id}'")

        lines = data_object.get("lines", {}).get("data", [])
        if lines and lines[0].get("price"):
            prod_price_id = lines[0]["price"].get("id")
            end_date = lines[0]["period"].get("end")
            start_date = lines[0]["period"].get("start", None)

        subscription_data = {
            "active": "",
            "stripe_customer_id": stripe_customer_id,
            "subscription_id": subscription_id,
            "stripe_status": stripe_status,
            "start_date": start_date,
            "end_date": end_date,
            "prod_price_id": prod_price_id,
            "billing_reason": billing_reason,
        }

        # Create/update subscription in DB
        stripe_obj = stripe_module.StripeClass()
        if event_type in [
            'customer.subscription.created',
            'customer.subscription.deleted',
            'customer.subscription.updated',
            'invoice.payment_succeeded',
            'invoice.payment_failed'
        ]:
            stripe_obj.create_or_update_subscription(event_type, subscription_data)

        # Send email notification
        try:
            customuser = CustomUser.objects.filter(stripe_customer_id=stripe_customer_id).first()
            if not customuser:
                raise CustomUser.DoesNotExist()

            if event_type == "invoice.payment_succeeded":
                send_payment_success_email(customuser)
            elif event_type == "invoice.payment_failed":
                send_payment_failed_email(customuser)

        except CustomUser.DoesNotExist:
            logger.error(f"User not found for Stripe customer ID: {stripe_customer_id}")
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.error(f"Error sending payment email: {traceback.format_exc()}")

        return Response({"message": "Success"}, status=status.HTTP_200_OK)