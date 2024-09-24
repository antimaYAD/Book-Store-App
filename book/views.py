from django.shortcuts import render

# Create your views here.
from .serializer import BookSerializer
from .models import Book
from rest_framework  import status
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from loguru import logger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class BookViews(viewsets.ModelViewSet):
    
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
    def get_queryset(self):
        return super().get_queryset()
    
    def list (self,request,*args, **kwargs):
        try:
            if pk in kwargs:  
                return self.retrieve(request,*args, **kwargs)
            queryset = self.get_queryset()
            serializer = BookSerializer(queryset, many=True)
            logger.info(f"The list of the book is shown successfully")
            return Response({"message":"List of the book","status":"Success","data":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error While get book list: {str(e)}")
            return Response({
                'error': 'An error occurred while retrieving book.',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            # Retrieve a single book by pk
            instance = self.get_object()
            serializer = BookSerializer(instance)
            
         
            logger.info(f"Book with ID {pk} retrieved successfully")
            
           
            return Response({"message": "Book retrieved", "status": "Success", "data": serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
           
            logger.error(f"Error while retrieving book with ID {pk}: {str(e)}")
            return Response({
                'error': f"An error occurred while retrieving the book with ID {pk}.",
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    
    
    @swagger_auto_schema(
        operation_description="Create a new book (Admin only)",
        request_body=BookSerializer,
        responses={
            201: openapi.Response('Book created successfully', BookSerializer),
            400: 'Bad Request',
            403: 'Forbidden'
        })
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        try:
            serializer = BookSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)  # Set the user to the current authenticated user
            logger.info("Book created successfully")
            return Response({"message": "Book created successfully", "status": "Success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error while creating book: {str(e)}")
            return Response({"error": "An error occurred while creating the book.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
    @swagger_auto_schema(
        operation_description="Update a  book (Admin only)",
        request_body=BookSerializer,
        responses={
            201: openapi.Response('Book Updated successfully', BookSerializer),
            400: 'Bad Request',
            403: 'Forbidden',
            404: 'Not Found',
            
            
        })  
    def update (self,request,pk=None,*args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        try:
            instance = self.get_object()
            serializer = BookSerializer(instance,data=request.data,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            logger.info("Book updated successfully")
            return Response({"message": "Book updated successfully", "status": "Success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error while updating book: {str(e)}")
            return Response({"error": "An error occurred while updating the book.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    @swagger_auto_schema(
        operation_description="Delete a book detail (Admin only)",
        request_body=BookSerializer,
        responses={
            201: openapi.Response('Book Detail successfully', BookSerializer),
            400: 'Bad Request',
            403: 'Forbidden'
        })    
        
    def destroy(self, request,pk=None, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        try:
            instance = self.get_object()
            instance.delete()
            logger.info("Book deleted successfully")
            return Response({"message": "Book deleted successfully", "status": "Success"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error while deleting book: {str(e)}")
            return Response({"error": "An error occurred while deleting the book.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)




    