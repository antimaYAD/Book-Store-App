from django.shortcuts import render

# Create your views here.
from .models import CartItems,CartModel
from .serializer import CartItemsSerializer,CartModelSerializer
from rest_framework  import status
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from loguru import logger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from book.models import Book
from django.db import models



class CartsViews(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get (self,request,*args, **kwargs):
        try:
            instance = CartModel.objects.get(user=request.user,is_ordered=False)
            
            if  instance :
                serializer = CartModelSerializer(instance)
                cart_items = CartItems.objects.filter(cart=instance)  
            
                
                cart_items_data = []  
                for item in cart_items:
                    cart_items_data.append({
                        'book_id': item.book.id,
                        'book_title': item.book.name, 
                        'quantity': item.quantity,
                        'price': item.price
                    })
                return Response({"message":"The actice cart of the user","status":"success","data":{"cart_detail":serializer.data,"cart_items":cart_items_data}},status=status.HTTP_200_OK)
            
        except CartModel.DoesNotExist:
            
            logger.warning(f"User {request.user.id} does not have any active cart.")
            return Response(
                {
                    "message": "No active cart found for the user",
                    "status": "error"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            
            logger.error(f"An error occurred while retrieving the cart: {str(e)}")
            return Response(
                {
                    "message": "An unexpected error occurred",
                    "status": "error",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request ,*args, **kwargs):
        try:
            
            book_id = request.data.get('book_id')
            quantity = request.data.get('quantity')
            
            if not book_id or not quantity:
                return Response({"message": "book_id and quantity are required."}, status=status.HTTP_400_BAD_REQUEST)
            
            book = Book.objects.get(id=book_id)
            if not book:
                return Response({"message": "Book does not exist in the database."}, status=status.HTTP_400_BAD_REQUEST)
                
            instance = CartModel.objects.filter(user=request.user, is_ordered=False).first()
            
            seializer = CartModelSerializer(instance)
            if instance:
                cart_items, items_create = CartItems.objects.get_or_create(cart=instance,book=book)
                
                if items_create:
                    cart_items.quantity = quantity
                    cart_items.price = book.price * quantity
                    cart_items.save()
                    logger.info(f"Added book {book_id} to the cart  for user {request.user.id}")
                else:
                    # If the item is already in the cart, update the quantity and price
                    cart_items.quantity += quantity
                    cart_items.price = book.price * cart_items.quantity
                    cart_items.save()
                    logger.info(f"Updated book {book_id} in the cartfor user {request.user.id}")

                # Update the cart's total price and quantity
                instance.total_quantity = CartItems.objects.filter(cart=instance).aggregate(total=models.Sum('quantity'))['total'] or 0
                instance.total_price = CartItems.objects.filter(cart=instance).aggregate(total=models.Sum('price'))['total'] or 0
                instance.save()
                
                return Response(
                    {
                        "message": "The user already has an active cart",
                        "status": "success",
                        "data": seializer.data  
                    },
                    status=status.HTTP_200_OK)
            
            cart = CartModel.objects.create(user=request.user)  # Initialize cart variable here
            CartItems.objects.create(cart=cart, book=book, quantity=quantity, price=book.price * quantity)

            # Set the cart's total price and quantity
            cart.total_quantity = quantity
            cart.total_price = book.price * quantity
            cart.save()

            logger.info(f"A new cart is created for user {request.user.id}")  # Now, 'cart' is defined
            
            serializer = CartModelSerializer(cart)  # Serialize the new cart
            
            return Response(
                {
                    "message": "New cart created successfully",
                    "status": "success",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
                
            

        except Exception as e:
           
            logger.error(f"An error occurred: {str(e)}")
            return Response(
                {
                    "message": "An error occurred while creating the cart",
                    "status": "error",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
    def delete(self,request,*args, **kwargs):
        try:
            instance = CartModel.objects.filter(user=request.user,is_ordered=False).first()
            
            if not instance:
                logger.warning(f"No active cart found for user {request.user.id}")
                return Response({"message": "No active cart found."}, status=status.HTTP_404_NOT_FOUND)
                    
            # Delete the cart
            instance.delete()
            logger.info(f"Cart deleted successfully for user {request.user.id}")
            
            return Response({"message": "Cart deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
        except Exception as e:
            # Handle any other unexpected errors
            logger.error(f"An unexpected error occurred while deleting cart for user {request.user.id}: {str(e)}")
            return Response({"message": "An unexpected error occurred.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        
                


