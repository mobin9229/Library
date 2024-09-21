from django.contrib import admin
from .models import Author, Book, Borrower, BorrowingTransaction, Cart, CartItem, Order
from .models import BorrowedBook, BookRating

class BookRatingAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating')  
    list_filter = ('book', 'rating')  
    search_fields = ('book__title', 'user__username')  

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'average_rating', 'is_available')

    def average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)  
        return 'No Ratings'

    average_rating.short_description = 'Average Rating'

    def is_available(self, obj):
        return 'Available' if obj.is_available else 'Not Available'
    
    is_available.short_description = 'Status'


admin.site.register(Book, BookAdmin)
admin.site.register(BookRating, BookRatingAdmin)

admin.site.register(Author)
admin.site.register(Borrower)
admin.site.register(BorrowingTransaction)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)


@admin.register(BorrowedBook)
class BorrowedBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrow_date')
    list_filter = ('user',)