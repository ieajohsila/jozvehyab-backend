from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        # در فاز بعدی، منطق ربات به اینجا منتقل خواهد شد
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error", "message": "فقط درخواست POST مجاز است"})
