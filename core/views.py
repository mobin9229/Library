from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Author, Book, Borrower, BorrowingTransaction, Cart, CartItem, Order, BookReview
from .serializers import AuthorSerializer, BookSerializer, BorrowerSerializer, BorrowingTransactionSerializer, CartSerializer, CartItemSerializer, OrderSerializer, UserSerializer, SignupSerializer, LoginSerializer, BookReviewSerializer, Book, BorrowingTransaction, BookRatingSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.http import JsonResponse
from .models import Cart, CartItem, BorrowedBook, BookRating
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.core.exceptions import ValidationError
from .managers import BorrowingManager
from .services import BookReturnService
from django.contrib.auth.decorators import login_required


  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_items = [{'id': item.book.id, 'title': item.book.title} for item in cart.items.all()]
        return Response({'cart_items': cart_items})
    return Response({'cart_items': []})


class BorrowBookViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        user = request.user
        try:
            book = Book.objects.get(pk=pk)

            borrowed_count = BorrowedBook.objects.filter(user=user).count()
            if borrowed_count >= 5:
                return Response({'status': 'error', 'message': 'You can only borrow up to 5 books at a time.'}, status=400)

            if book.stock <= 0:
                return Response({'status': 'error', 'message': 'Book not available'}, status=400)

            due_date = timezone.now() + timezone.timedelta(days=14)  
            BorrowedBook.objects.create(user=user, book=book, due_date=due_date)

            
            book.stock -= 1
            book.save()

            return Response({'status': 'success'})
        except Book.DoesNotExist:
            return Response({'status': 'error', 'message': 'Book not found'}, status=404)        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reserved_books(request):
    borrowed_books = BorrowedBook.objects.filter(user=request.user)
    books = [{'id': book.book.id, 'title': book.book.title} for book in borrowed_books]
    return Response({'reserved_books': books})




@api_view(['POST'])
@login_required
@permission_classes([IsAuthenticated])
def return_book_view(request, book_id):
    
    borrowed_book = get_object_or_404(BorrowedBook, book_id=book_id, user=request.user)

    
    try:
       
        borrowed_book.return_book()  
        
        
        book = borrowed_book.book
        book.stock += 1  
        book.save()

        
        borrowed_book.delete()

        return JsonResponse({'message': 'Book returned successfully'})
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



class BookRatingViewSet(viewsets.ModelViewSet):
    queryset = BookRating.objects.all()
    serializer_class = BookRatingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book')
        rating = request.data.get('rating')

        if not book_id or not rating:
            return Response({'error': 'Book and rating must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        
        if BookRating.objects.filter(book=book, user=user).exists():
            return Response({'error': 'You have already rated this book.'}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            rating_instance = BookRating(book=book, user=user, rating=rating)
            rating_instance.clean()  
            rating_instance.save()
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(BookRatingSerializer(rating_instance).data, status=status.HTTP_201_CREATED)




class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]

class BookRatingViewSet(viewsets.ModelViewSet):
    queryset = BookRating.objects.all()
    serializer_class = BookRatingSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book')
        rating = request.data.get('rating')

        if not book_id or not rating:
            return Response({'error': 'Book and rating must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        book = Book.objects.get(id=book_id)

        
        if BookRating.objects.filter(book=book, user=user).exists():
            return Response({'error': 'You have already rated this book'}, status=status.HTTP_400_BAD_REQUEST)

        rating_instance = BookRating.objects.create(book=book, user=user, rating=rating)

        return Response(BookRatingSerializer(rating_instance).data, status=status.HTTP_201_CREATED)



class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer

class BorrowingTransactionViewSet(viewsets.ModelViewSet):
    queryset = BorrowingTransaction.objects.all()
    serializer_class = BorrowingTransactionSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SignupViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"detail": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reserve_book(request):
    book_id = request.data.get('book_id')
    if not book_id:
        return Response({'detail': 'Book ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        book = Book.objects.get(id=book_id)

        
        if not BorrowingManager.can_user_reserve(request.user):
            return Response({'detail': 'You can only reserve up to 5 books.'}, status=status.HTTP_400_BAD_REQUEST)

        if BorrowingTransaction.objects.filter(book=book, borrower=request.user).exists():
            return Response({'detail': 'You have already reserved this book.'}, status=status.HTTP_400_BAD_REQUEST)

       
        transaction = BorrowingTransaction.objects.create(borrower=request.user, book=book)
        serializer = BorrowingTransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Book.DoesNotExist:
        return Response({'detail': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    cart_id = request.data.get('cart_id')
    if not cart_id:
        return Response({'detail': 'Cart ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cart = Cart.objects.get(id=cart_id)
        order = Order.objects.create(cart=cart, user=request.user, status='pending')

        
        send_mail(
            'Order Confirmation',
            f'Your order with ID {order.id} has been placed successfully.',
            'from@example.com',
            [request.user.email],
            fail_silently=False,
        )

        return Response({'detail': 'Order placed successfully.'}, status=status.HTTP_201_CREATED)
    except Cart.DoesNotExist:
        return Response({'detail': 'Cart not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request):
    book_id = request.data.get('book_id')
    rating = request.data.get('rating')
    comment = request.data.get('comment')

    if not book_id or not rating:
        return Response({'detail': 'Book ID and rating are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        book = Book.objects.get(id=book_id)
        review, created = BookReview.objects.update_or_create(
            book=book,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        serializer = BookReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Book.DoesNotExist:
        return Response({'detail': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    if cart:
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    return Response({'cart_items': [], 'total_items': 0})


