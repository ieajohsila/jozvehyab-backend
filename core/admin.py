from django.contrib import admin
from .models import User, Document, Transaction

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'username', 'credit', 'subscription_expires')
    search_fields = ('first_name', 'username', 'user_id')
    list_filter = ('subscription_expires',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')
    search_fields = ('title',)
    exclude = ('file_id',) # فایل آیدی را در فرم ویرایش نشان نده

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('user__first_name', 'user__username')
