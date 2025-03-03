# Generated by Django 4.2.16 on 2024-09-19 23:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="book",
            name="author",
        ),
        migrations.AlterUniqueTogether(
            name="bookrating",
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name="bookrating",
            name="book",
        ),
        migrations.RemoveField(
            model_name="bookrating",
            name="user",
        ),
        migrations.AlterUniqueTogether(
            name="bookreview",
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name="bookreview",
            name="book",
        ),
        migrations.RemoveField(
            model_name="bookreview",
            name="user",
        ),
        migrations.AlterUniqueTogether(
            name="borrowedbook",
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name="borrowedbook",
            name="book",
        ),
        migrations.RemoveField(
            model_name="borrowedbook",
            name="user",
        ),
        migrations.RemoveField(
            model_name="borrower",
            name="user",
        ),
        migrations.RemoveField(
            model_name="borrowingtransaction",
            name="book",
        ),
        migrations.RemoveField(
            model_name="borrowingtransaction",
            name="borrower",
        ),
        migrations.RemoveField(
            model_name="cart",
            name="user",
        ),
        migrations.RemoveField(
            model_name="cartitem",
            name="book",
        ),
        migrations.RemoveField(
            model_name="cartitem",
            name="cart",
        ),
        migrations.RemoveField(
            model_name="order",
            name="cart",
        ),
        migrations.RemoveField(
            model_name="order",
            name="user",
        ),
        migrations.DeleteModel(
            name="Author",
        ),
        migrations.DeleteModel(
            name="Book",
        ),
        migrations.DeleteModel(
            name="BookRating",
        ),
        migrations.DeleteModel(
            name="BookReview",
        ),
        migrations.DeleteModel(
            name="BorrowedBook",
        ),
        migrations.DeleteModel(
            name="Borrower",
        ),
        migrations.DeleteModel(
            name="BorrowingTransaction",
        ),
        migrations.DeleteModel(
            name="Cart",
        ),
        migrations.DeleteModel(
            name="CartItem",
        ),
        migrations.DeleteModel(
            name="Order",
        ),
    ]
