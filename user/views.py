from django.shortcuts import render
from .models import Customer
from rest_framework  import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.reverse import reverse
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from  rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.decorators import api_view
from .serializer import UserLoginSerializer,UserRegistrationSerializer
import jwt


# Create your views here.
class RegistrationUserView(APIView):
    
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user=serializer.save()
            token = RefreshToken.for_user(user)
            access_token = str(token.access_token)
            
            link=reverse('verify_email',args=[access_token],request=request)
            email_subject = 'Verify your email address'
            email_body = f'Use this token to verify your email: {link}'
            
             # Send email
            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
          
            return Response({"message": "User created successfully", "status": "Success","data":serializer.data}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
              return Response({"message": str(e), "status": "Error"}, status=status.HTTP_400_BAD_REQUEST)
          
          
          
class LoginUserView(APIView):
    def post(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
                 # Retrieve the authenticated user from the serializer context
            user = serializer.context['user']
            token = RefreshToken.for_user(user)
            
            return Response({"Message": "Login successful",
                             "status": "Success",
                             "data":{'refresh':str(token),
                                     'access':str(token.access_token)}},
                            status=status.HTTP_200_OK)
            
            
        except Exception as e:
            return Response({"message": str(e), "status": "Error"}, status=status.HTTP_400_BAD_REQUEST)
     

            
@api_view(["GET"])
def verify_email(request,token):
    try:
        
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
        user = Customer.objects.get(id=payload['user_id'])
        user.is_verified = True
        user.save()

        return Response({"Message": "User email verified successfully"}, status=status.HTTP_200_OK)
    
    
    except Exception as e:
        return Response({"Message": "Invalid token or user not found", "Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
             
            
            