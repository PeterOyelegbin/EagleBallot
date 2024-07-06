"""eagleballot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from accounts.views import SignUpView, LogInView, LogOutView

# Swagger UI
schema_view = get_schema_view(
   openapi.Info(
      title="EagleBallot API",
      default_version='v1',
      description="Backend API for EagleBallot, a remote voting platform to enhance Nigeria elctoral process.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@eagleballot.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


# APP urls
router = DefaultRouter(trailing_slash=False)
router.register(r"v1/account/signup", SignUpView, basename="signup")
router.register(r"v1/account/login", LogInView, basename="login")
router.register(r"v1/account/logout", LogOutView, basename="logout")

# # Simple-jwt urls
# router.register(r"v1/token/", TokenObtainPairView, basename="token_obtain_pair")
# router.register(r"v1/token/refresh/", TokenRefreshView, basename="token_refresh")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
     # API DOCS URL
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # path('signup', SignUpView.as_view(), name='sign-up'),
    # path('login', LoginView.as_view(), name='log-in'),
]
