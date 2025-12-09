from django.db import models

class User(models.Model):
    user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام")
    username = models.CharField(max_length=50, blank=True, null=True, verbose_name="نام کاربری")
    subscription_expires = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ انقضای اشتراک")
    credit = models.IntegerField(default=0, help_text="موجودی کیف پول به تومان", verbose_name="اعتبار")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ عضویت")
    def __str__(self):
        return self.first_name or str(self.user_id)

class Document(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    price = models.IntegerField(default=0, verbose_name="قیمت تکی (تومان)")
    file_id = models.CharField(max_length=200, unique=True, verbose_name="شناسه فایل تلگرام")
    def __str__(self):
        return self.title

class Transaction(models.Model):
    TRANSACTION_TYPES = [('subscription', 'خرید اشتراک'), ('referral', 'پاداش معرفی'), ('credit_purchase', 'خرید اعتبار'), ('single_purchase', 'خرید تکی جزوه')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    amount = models.IntegerField(verbose_name="مبلغ (تومان)")
    type = models.CharField(max_length=50, choices=TRANSACTION_TYPES, verbose_name="نوع تراکنش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ تراکنش")
    def __str__(self):
        return f"{self.user} - {self.amount} - {self.get_type_display()}"
