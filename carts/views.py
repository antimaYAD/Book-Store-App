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
from rest_framework.decorators import action



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
                        'item_id':item.id,
                        'book_id': item.book.id,
                        'book_title': item.book.name, 
                        'quantity': item.quantity,
                        'price': item.price
                    })
                return Response({"message":"The actice cart of the user","status":"success","data":{"cart_detail":serializer.data,"cart_items": cart_items_data}},status=status.HTTP_200_OK)
            
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
            
            
    # @swagger_auto_schema(
    #     operation_description="Delete a cart or cart item. If `pk` is provided, it deletes the cart item; otherwise, it deletes the entire active cart.",
    #     responses={
    #         204: 'Cart or cart item deleted successfully',
    #         404: 'Cart or cart item not found',
    #         500: 'An unexpected error occurred'
    #     }
    # )
  
    def delete(self,request,pk=None,*args, **kwargs):
        try:
            if pk:
                return self.delete_cart_item(request, pk, *args, **kwargs)

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
        
        
    def delete_cart_item(self,request,pk,*args, **kwargs):
        try:
            active_cart = CartModel.objects.get(user=request.user,is_ordered=False)
            cart_item = CartItems.objects.get(id=pk,cart=active_cart)
            
            if not cart_item:
                return Response({"message":"No such item is found or add in the active cart"},status=status.HTTP_404_NOT_FOUND)
            cart_item.delete()
            logger.info(f"the item from the cart is delete")
             
            return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        except CartItems.DoesNotExist:
            return Response({"error": "Cart item not found in your active cart"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"A error occurred : str(e)")
            return Response({"error": "An error occurred while deleting the item"}, status=status.HTTP_400_BAD_REQUEST)
        
    
                


class OrderViews(APIView):
    
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def post (self,request,*args, **kwargs):
        try:
            
            instance = CartModel.objects.filter(user=request.user,is_ordered=False).first()
            
            if instance:
                cart_items = CartItems.objects.filter(cart=instance)
                if not cart_items.exists():
                     return Response({"message": "The cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
                 
                for item in cart_items:
                    if item.quantity > item.book.stock:
                        return Response(
                        {"message": f"Insufficient stock for the book {item.book.name}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                for item  in cart_items:
                    book = item.book
                    book.stock -= item.quantity
                    book.save()
                    
                instance.is_ordered = True
                instance.save()
                
                logger.info(f"Order created for user {request.user.id}")
                return Response({"message":"The order placed ","status":"Success"},status=status.HTTP_200_OK)
            
            return Response({"message": "No active cart to order."}, status=status.HTTP_400_BAD_REQUEST)
            
                
        except Exception as e:
            logger.error(f"An error occurred during ordering: {str(e)}")
            return Response(
                {"message": "An error occurred during the ordering process.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
            
    def get (self,request):
        
        try:
            instance =  CartModel.objects.filter(user=request.user,is_ordered=True)
            
            if not instance.exists():
                return Response({"message": " No order Found","status":"Error"},status=status.HTTP_404_NOT_FOUND)
            
            serializer = CartModelSerializer(instance,many=True)
            logger.info(f"The order details")
            return Response({"message": "Order details fetched successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An error occurred while retrieving orders: {str(e)}")
            return Response(
                {"message": "An error occurred while retrieving the orders.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
    def patch(self,request):
        
        try:
            instance = CartModel.objects.filter(user=request.user,is_ordered=True).first()
            
            if not instance:
                 return Response({"message": "No order found to cancel."}, status=status.HTTP_404_NOT_FOUND)
             
            cart_items = CartItems.objects.filter(cart=instance)
            
            for item in cart_items:
                book = item.book
                book.stock += item.quantity
                book.save()
                
            instance.delete()
            
            logger.info(f"The order is been cancel")
            return Response({"message": "Order cancelled successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An error occurred while cancelling the order: {str(e)}")
            return Response(
                {"message": "An error occurred while cancelling the order.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
            
            