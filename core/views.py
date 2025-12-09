from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import telegram
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from .models import User, Document

# --- راه‌اندازی اولیه ربات ---
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# ==================== توابع منطقی ربات (Async) ====================

async def handle_start(update: Update):
    user_data = update.effective_user
    user, created = await User.objects.aget_or_create(
        user_id=user_data.id,
        defaults={'first_name': user_data.first_name, 'username': user_data.username}
    )
    if created:
        print(f"کاربر جدید ثبت شد: {user.user_id}")

    keyboard = [[KeyboardButton("📚 لیست جزوات"), KeyboardButton("⭐ خرید اشتراک")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"سلام {user_data.mention_html()}! 👋\n\nبه ربات «جزوه‌یاب» خوش آمدید.",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def handle_list_documents(update: Update):
    documents = [doc async for doc in Document.objects.all()]
    if not documents:
        await bot.send_message(chat_id=update.effective_chat.id, text="متاسفانه در حال حاضر هیچ جزوه‌ای موجود نیست.")
        return

    await bot.send_message(chat_id=update.effective_chat.id, text="لیست جزوات موجود:")
    for doc in documents:
        keyboard = [[InlineKeyboardButton("📥 دریافت جزوه", callback_data=f"doc_{doc.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        price_text = f"{doc.price:,} تومان" if doc.price > 0 else "رایگان"
        message_text = f"📄 **عنوان:** {doc.title}\n💰 **قیمت:** {price_text}"
        await bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_show_subscription_options(update: Update):
    keyboard = [
        [InlineKeyboardButton("⭐ ۱ ماهه (۱۰۰ استار)", callback_data="subscribe_1_100")],
        [InlineKeyboardButton("⭐ ۳ ماهه (۲۵۰ استار)", callback_data="subscribe_3_250")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=update.effective_chat.id, text="لطفاً یکی از پلن‌های اشتراک زیر را انتخاب کنید:", reply_markup=reply_markup)

async def handle_button_callback(update: Update):
    query = update.callback_query
    await query.answer()
    
    user = await User.objects.aget(user_id=query.effective_user.id)
    is_subscribed = user.subscription_expires and user.subscription_expires.replace(tzinfo=None) > datetime.utcnow()

    if not is_subscribed:
        await bot.send_message(chat_id=query.effective_chat.id, text="❌ برای دسترسی به جزوات، ابتدا باید اشتراک تهیه کنید.\n\nلطفاً از منوی اصلی دکمه «⭐ خرید اشتراک» را انتخاب کنید.")
        return

    doc_id = int(query.data.split("_")[1])
    try:
        document = await Document.objects.aget(id=doc_id)
        await bot.send_document(chat_id=query.effective_chat.id, document=document.file_id)
    except Document.DoesNotExist:
        await query.edit_message_text(text="متاسفانه این جزوه یافت نشد.")

async def handle_subscription_invoice(update: Update):
    query = update.callback_query
    await query.answer()
    _, months, stars = query.data.split('_')
    title = f"اشتراک {months} ماهه جزوه‌یاب"
    description = f"دسترسی کامل به تمام جزوات به مدت {months} ماه"
    payload = f"jozvehyab-sub-{months}m"
    await bot.send_invoice(
        chat_id=query.effective_chat.id, title=title, description=description,
        payload=payload, currency="XTR", prices=[LabeledPrice(f"{months} ماه", int(stars))]
    )

async def handle_pre_checkout(update: Update):
    query = update.pre_checkout_query
    if query.invoice_payload.startswith('jozvehyab-sub-'):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="مشکلی در پرداخت پیش آمده است.")

async def handle_successful_payment(update: Update):
    payload = update.message.successful_payment.invoice_payload
    months = int(payload.split('-')[2][:-1])
    user = await User.objects.aget(user_id=update.effective_user.id)
    
    now = datetime.utcnow()
    current_expiry = user.subscription_expires.replace(tzinfo=None) if (user.subscription_expires and user.subscription_expires.replace(tzinfo=None) > now) else now
    new_expiry_date = current_expiry + timedelta(days=30 * months)
    
    user.subscription_expires = new_expiry_date
    await user.asave()
    
    await bot.send_message(chat_id=update.effective_chat.id, text=f"✅ پرداخت شما با موفقیت انجام شد! اشتراک شما تا تاریخ {new_expiry_date.strftime('%Y-%m-%d')} تمدید شد.")

# ==================== پردازشگر اصلی وبهوک (Async View) ====================

@csrf_exempt
async def telegram_webhook(request):
    if request.method == 'POST':
        try:
            update_data = json.loads(request.body)
            update = Update.de_json(update_data, bot)

            if update.message and update.message.text:
                text = update.message.text
                if text == '/start': await handle_start(update)
                elif text == '📚 لیست جزوات': await handle_list_documents(update)
                elif text == '⭐ خرید اشتراک': await handle_show_subscription_options(update)
            
            elif update.callback_query:
                data = update.callback_query.data
                if data.startswith('doc_'): await handle_button_callback(update)
                elif data.startswith('subscribe_'): await handle_subscription_invoice(update)

            elif update.pre_checkout_query:
                await handle_pre_checkout(update)
                
            elif update.message and update.message.successful_payment:
                await handle_successful_payment(update)
                
        except Exception as e:
            print(f"Error processing webhook: {e}")
            
        return JsonResponse({"status": "ok"})
        
    return JsonResponse({"status": "error", "message": "فقط درخواست POST مجاز است"})
