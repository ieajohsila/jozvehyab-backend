import os
import requests
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Sets the Telegram webhook for the bot'

    def handle(self, *args, **options):
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        # --- تغییر در این خط اعمال شده است ---
        render_url = os.environ.get('RENDER_EXTERNAL_URL') 

        if not token or not render_url:
            self.stdout.write(self.style.ERROR('Token or Render URL not found in environment variables.'))
            return

        webhook_url = f"{render_url}/bot/telegram_webhook/"
        telegram_api_url = f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}"

        try:
            response = requests.get(telegram_api_url)
            response.raise_for_status()
            result = response.json()
            if result.get('ok'):
                self.stdout.write(self.style.SUCCESS(f"Webhook set successfully to {webhook_url}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to set webhook: {result.get('description')}"))
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"HTTP Request failed: {e}"))
