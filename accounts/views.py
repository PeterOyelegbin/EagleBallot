from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from .models import UserModel, OtpToken
from .serializers import SignUpSerializer, TokenSerializer, RegenerateTokenSerializer, LogInSerializer, LogOutSerializer
from .managers import verify_id, generate_otp, send_async_email
import threading


# Create your views here.
class SignUpView(viewsets.ViewSet):
    """
        User Signup Endpoint

        Register as a new user. 
    """
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=SignUpSerializer, responses={200: 'OK'})
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            userID = serializer.validated_data['voters_id']
            verify = verify_id(userID)
            if verify.json().get('statusCode') == 200:
                fn = 'Peter' #verify.json()['data']['firstName']
                ln = 'Oye' #verify.json()['data']['lastName']
                state = 'Lag' #verify.json()['data']['address']['state']
                user = serializer.save(first_name=fn, last_name=ln, state_of_resident=state)
                # generate token and save
                otp_code = generate_otp()
                OtpToken.objects.create(user=user, otp_code=otp_code)
                # Asynchronously send the token to the user email
                threading.Thread(target=send_async_email, args=(
                    "EagleBallot: Registration Token",
                    f"""Dear {user.first_name} {user.last_name},\n\nYour EagleBallot registration token is {otp_code} and expires in 10 minutes.\n\nThank you,\nEagleBallot""",
                    settings.EMAIL_HOST_USER,
                    [user.email]
                )).start()
                response_data = {
                    "success": verify.json().get('success'),
                    "status": verify.json().get('statusCode'),
                    "message": "Check your mail for OTP to complete signup process",
                    "data": serializer.data
                }
                return Response(response_data, status=int(verify.json().get('statusCode')))
            else:
                response_data = {
                    "success": verify.json().get('success'),
                    "status": verify.json().get('statusCode'),
                    "message": verify.json().get('message'),
                }
                return Response(response_data, status=int(verify.json().get('statusCode')))
        except Exception as e:
            response_data = {
                "success": False,
                "status": 400,
                "message": f"Validation error: {e}",
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class TokenValidationView(viewsets.ViewSet):
    """
        User Token Validation Endpoint

        Validate user token upon registration using 2FA.
    """
    serializer_class = TokenSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=TokenSerializer, responses={200: 'OK'})
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        voters_id = serializer.validated_data["voters_id"]
        otp_code = serializer.validated_data["otp_code"]
        try:
            user = UserModel.objects.get(voters_id=voters_id)
            otp_token = OtpToken.objects.get(user=user, otp_code=otp_code)
            if otp_token.is_valid():
                user.is_active = True
                user.save()
                otp_token.delete()
                response_data = {
                    "success": True,
                    "status": 200,
                    "message": "Signup successful",
                }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                'success': False,
                'status': 401,
                'message': 'Token has expired',
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
        except UserModel.DoesNotExist:
            response_data = {
                'success': False,
                'status': 404,
                'message': 'User not found',
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except OtpToken.DoesNotExist:
            response_data = {
                'success': False,
                'status': 401,
                'message': 'Invalid token',
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)


class RegenerateTokenView(viewsets.ViewSet):
    """
        Token Regeneration Endpoint

        Regenerate token upon registration using 2FA.
    """
    serializer_class = RegenerateTokenSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegenerateTokenSerializer, responses={200: 'OK'})
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserModel.objects.get(voters_id=serializer.validated_data["voters_id"])
            # Delete existing OTP
            old_otp = OtpToken.objects.get(user=user)
            old_otp.delete()
            # Regenerate OTP
            new_otp = generate_otp()
            OtpToken.objects.create(user=user, otp_code=new_otp)
            # Asynchronously send the OTP to the user email
            threading.Thread(target=send_async_email, args=(
                "EagleBallot: Registration Token",
                f"""Dear {user.first_name} {user.last_name},\n\nYour EaglesBallot registration token is {new_otp} and expires in 10 minutes.\n\nThank you,\nEagleBallot""",
                settings.EMAIL_HOST_USER,
                [user.email]
            )).start()
            response_data = {
                "success": True,
                "status": 200,
                "message": "An OTP has been sent to your mail",
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            response_data = {
                'success': False,
                'status': 404,
                'message': 'User not found',
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                'success': False,
                'status': 500,
                'message': f'An error {e} occurred. Please try again later.',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogInView(viewsets.ViewSet):
    """
        User Login Endpoint

        User log in with their email and password
    """
    serializer_class = LogInSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LogInSerializer, responses={200: 'OK'})
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            user = authenticate(username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                response_data = {
                    'success': True,
                    'status': 200,
                    'message': 'Login successful',
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'status': 401,
                    'message': 'Invalid credentials',
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            response_data = {
                'success': False,
                'status': 500,
                'message': f'An error {e} occurred during login',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogOutView(viewsets.ViewSet):
    """
        User Logout Endpoint

        Logs out user by blacklisting their refresh token.
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=LogOutSerializer, responses={205: 'RESET_CONTENT'})
    def create(self, request):
        try:
            serializer = LogOutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            response_data = {
                'success': True,
                'status': 205,
                'message': 'Logout successful',
            }
            return Response(response_data, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            response_data = {
                'success': False,
                'status': 400,
                'message': 'Refresh token is required',
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except (TokenError, InvalidToken) as e:
            response_data = {
                'success': False,
                'status': 400,
                'message': str(e),
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


# class SignUpView(generics.CreateAPIView):
#     """
#         User Signup Endpoint

#         Register as a new user. 
#     """
#     serializer_class = SignUpSerializer
#     permission_classes = [AllowAny]
    
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         serializer = self.serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         response = self.serializer_class(user)
#         response_data = {
#             "success": True,
#             "status": 201,
#             "message": "User successfully added",
#             "data": response.data
#         }
#         return Response(response_data, status=status.HTTP_201_CREATED)


# class LoginView(generics.CreateAPIView):
#     """
#         User Login Endpoint

#         User log in with their email and password
#     """
#     serializer_class = LogInSerializer
#     permission_classes = [AllowAny]

#     def create(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         email = serializer.validated_data['email']
#         password = serializer.validated_data['password']
#         user = authenticate(username=email, password=password)
#         if user is not None:
#             # refresh = RefreshToken.for_user(user)
#             response_data = {
#                 'success': True,
#                 'status': 200,
#                 'message': 'User Login Successful',
#                 # 'refresh_token': str(refresh),
#                 # 'access_token': str(refresh.access_token),
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         else:
#             response_data = {
#                 'success': False,
#                 'status': 401,
#                 'message': 'Invalid credentials',
#             }
#             return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
