from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from drf_yasg.utils import swagger_auto_schema
from .serializers import SignUpSerializer, LogInSerializer, LogOutSerializer
from .managers import verify_id


# Create your views here.
class SignUpView(viewsets.ViewSet):
    """
        User Signup Endpoint

        Register as a new user. 
    """
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=SignUpSerializer, responses={200: SignUpSerializer})
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        userID = serializer.validated_data['voters_id']
        verify = verify_id(userID)
        if verify.json()['statusCode'] == 200:
            fn = verify.json()['data']['firstName']
            ln = verify.json()['data']['lastName']
            state = verify.json()['data']['address']['state']
            serializer.save(first_name=fn, last_name=ln, state_of_resident=state)
            response_data = {
                "success": verify.json()['success'],
                "status": verify.json()['statusCode'],
                "message": "Signup successful",
                "data": serializer.data
            }
            return Response(response_data, status=int(verify.json()['statusCode']))
        else:
            response_data = {
                "success": verify.json()['success'],
                "status": verify.json()['statusCode'],
                "message": verify.json()['message'],
            }
            return Response(response_data, status=int(verify.json()['statusCode']))


class LogInView(viewsets.ViewSet):
    """
        User Login Endpoint

        User log in with their email and password
    """
    serializer_class = LogInSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LogInSerializer, responses={200: 'OK',})
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            response_data = {
                'success': True,
                'status': 200,
                'message': 'Login Successful',
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


class LogOutView(viewsets.ViewSet):
    """
        User Logout Endpoint

        Logs out user by blacklisting their refresh token.
    """
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=LogOutSerializer, responses={205: 'RESET_CONTENT',})
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
                'message': 'Logout Successful',
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
