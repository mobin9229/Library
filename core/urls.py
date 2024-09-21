from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthorViewSet, BookViewSet, BorrowerViewSet, BorrowingTransactionViewSet,
    CartViewSet, CartItemViewSet, OrderViewSet, UserViewSet, LoginViewSet, SignupViewSet, reserve_book ,
    add_review, BorrowBookViewSet, view_cart, BookRatingViewSet, return_book_view
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse


router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)
router.register(r'book-ratings', BookRatingViewSet)
router.register(r'borrowers', BorrowerViewSet)
router.register(r'borrowingtransactions', BorrowingTransactionViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cartitems', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'user', UserViewSet)
router.register(r'signup', SignupViewSet, basename='signup')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'borrow-book', BorrowBookViewSet, basename='borrow_book')


urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reserve-book/', reserve_book, name='reserve_book'),
    path('add-review/', add_review, name='add_review'),
    path('return-book/<int:book_id>/', return_book_view, name='return_book'),
   # path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    #path('borrow_book/<int:book_id>/', borrow_book, name='borrow_book'),
    path('cart/', view_cart, name='view_cart'),
  ##  path('api/user/', user_info, name='user_info'),
]

