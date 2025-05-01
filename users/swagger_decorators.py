from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def users_register():
    return swagger_auto_schema(
        operation_description="Register a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'first_name', 'last_name', 'password', 'confirm_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User's email address"),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="User's first name"),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="User's last name"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description="Confirm password"),
            }
        ),
        tags=["Auth"]
    )
def verify_email():
    return swagger_auto_schema(
        operation_description="Verify the user's email with a unique token",
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Unique token sent to user's email for verification")
        ],
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Verification success message"),
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request, missing parameters or invalid data"
            ),
            404: openapi.Response(
                description="User not found or invalid verification token"
            ),
        },
        tags=["Auth"]
    )

def users_login():
    return swagger_auto_schema(
        operation_description="Login a user with email and password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User's email address"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
            }
        ),
        responses={
            200: openapi.Response(
                description="Login successful, returns user details and token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Login status message"),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description="JWT access token"),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
                        'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Email verification status"),
                        'role': openapi.Schema(type=openapi.TYPE_STRING, description="User's role (seeker/provider/admin/none)")
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request, invalid credentials or missing parameters"
            ),
            401: openapi.Response(
                description="Unauthorized, invalid email or password"
            ),
        },
        tags=["Auth"]
    )

def set_role_swagger():
    return swagger_auto_schema(
        operation_description="Set the role for a user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_role"],
            properties={
                'user_role': openapi.Schema(type=openapi.TYPE_STRING, description="The role to assign to the user (e.g., 'admin', 'seeker', 'provider')"),
            }
        ),
        responses={
            200: openapi.Response(
                description="User role updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                    }
                ),
            ),
            400: openapi.Response(
                description="Bad request, missing 'user_role' parameter",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                    }
                ),
            ),
            401: openapi.Response(
                description="Unauthorized access, user not authenticated",
            ),
        },
        tags=["User Profile"]
    )

def user_profile_swagger():
    return swagger_auto_schema(
        operation_description="Create or update user profile information.\n\n"
                              "**If role is `seeker`**, provide: `industry`, `location`, `rating_report_url`.\n"
                              "**If role is `provider`**, provide: `service_types`, `geoserved`, `subscription_tier`.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            # required=["first_name", "last_name"],
            properties={

                # Seeker-specific fields
                'industry': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="(Seeker only) Industry the user belongs to"
                ),
                'location': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="(Seeker only) Location of the user"
                ),
                'rating_report_url': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="(Seeker only) URL to a rating or report"
                ),

                # Provider-specific fields
                'service_types': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="(Provider only) List of service types the provider offers"
                ),
                'geoserved': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="(Provider only) List of geographic areas the provider serves"
                ),
                'subscription_tier': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="(Provider only) Subscription tier of the provider"
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="User profile created or updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                    }
                ),
            ),
            400: openapi.Response(
                description="Bad request, invalid or missing parameters",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message"),
                    }
                ),
            ),
            401: openapi.Response(description="Unauthorized access, user not authenticated"),
        },
        tags=["User Profile"]
    )

def get_user_profile():
    return swagger_auto_schema(
        operation_description="Get user profile.",
        responses={200: "User profile details."},
        tags=["User Profile"]
    )


# Custom Swagger decorator for matched users endpoint
def matched_users_swagger():
    return swagger_auto_schema(
        operation_description="""
        Get matched users based on industry and location.
        
        For Seekers:
        - Returns matching providers based on industry and location
        - Both parameters are required
        - Matches against provider's service_types and geoserved fields
        - Returns match scores (0-100) based on exact and partial matches
        
        For Providers:
        - Returns matching seekers based on provider's service_types and geoserved
        - No query parameters needed as it uses provider's profile
        - Returns match scores (0-100) based on exact and partial matches
        
        ML Endpoint (/ml/match):
        - Same interface but uses ML-enhanced matching logic
        - Currently stubbed to return same results as rule-based matching
        
        Response includes:
        - matches: List of matched profiles with match scores
        - matching_type: 'rule-based' or 'ml'
        - total_matches: Total number of matches found
        
        Results are cached for 5 minutes for better performance.
        """,
        manual_parameters=[
            openapi.Parameter(
                'industry',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Industry to match (required for seekers)',
                required=False
            ),
            openapi.Parameter(
                'location',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Location to match (required for seekers)',
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description='Successful match response',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'matches': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                                    'match_score': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='Match score from 0-100'
                                    ),
                                    'industry': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='For seeker profiles'
                                    ),
                                    'location': openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='For seeker profiles'
                                    ),
                                    'service_types': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_STRING),
                                        description='For provider profiles'
                                    ),
                                    'geoserved': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_STRING),
                                        description='For provider profiles'
                                    ),
                                }
                            )
                        ),
                        'matching_type': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=['rule-based', 'ml']
                        ),
                        'total_matches': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Total number of matches found'
                        )
                    }
                )
            ),
            400: 'Bad Request - Missing required parameters or invalid role',
            404: 'Not Found - Profile not found'
        },
        tags=["Matches"]
    )


def create_payment_plan_docs():
    return swagger_auto_schema(
        operation_description="Create a new payment plan with required details.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "payment_type", "plan_name", "plan_description", "prod_id", "prod_price_id"
            ],
            properties={
                "payment_type": openapi.Schema(type=openapi.TYPE_STRING, description="Type of payment (e.g., 'monthly', 'yearly')"),
                "plan_name": openapi.Schema(type=openapi.TYPE_STRING, description="Name of the subscription plan"),
                "plan_description": openapi.Schema(type=openapi.TYPE_STRING, description="Description of the plan"),
                "prod_id": openapi.Schema(type=openapi.TYPE_STRING, description="Stripe product ID"),
                "prod_price_id": openapi.Schema(type=openapi.TYPE_STRING, description="Stripe product price ID"),
            }
        ),
        tags=["Subscription"]
    )

def fetch_subscription_plans_docs():
    return swagger_auto_schema(
        operation_description="Fetch all active subscription plans.",
        responses={200: "List of active subscription plans."},
        tags=["Subscription"]
    )

def checkout_payment():
    return swagger_auto_schema(
        operation_description="Subscribe to a plan using selected payment type and price ID.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["payment_type", "price_id"],
            properties={
                'payment_type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of payment method"),
                'price_id': openapi.Schema(type=openapi.TYPE_STRING, description="Stripe Price ID for the subscription plan"),
            },
        ),
        responses={200: "Subscription created successfully", 400: "Invalid input"},
        tags=["Subscription"]
    )

def resend_verification_email():
    return swagger_auto_schema(
        operation_description="Resend verification email to user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User's email address"),
            }
        ),
        responses={
            200: openapi.Response(
                description="Verification email resent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request, missing email or email already verified"
            ),
            404: openapi.Response(
                description="User not found"
            ),
            500: openapi.Response(
                description="Internal server error"
            ),
        },
        tags=["Auth"]
    )