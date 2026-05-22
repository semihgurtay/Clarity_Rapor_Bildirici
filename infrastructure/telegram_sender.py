import logging
import requests
from config import settings

log = logging.getLogger("TelegramSender")

class TelegramSender:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.ADMIN_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, text: str) -> bool:
        """HTML formatında Telegram mesajı gönder."""
        if not self.bot_token or not self.chat_id:
            log.warning("Telegram token veya Chat ID eksik, gönderim yapılmadı.")
            return False

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        try:
            log.info(f"Telegram mesajı gönderiliyor (Chat ID: {self.chat_id})...")
            response = requests.post(url, json=payload, timeout=15)
            
            # Rate limit kontrolü
            if response.status_code == 429:
                retry_after = response.json().get("parameters", {}).get("retry_after", 5)
                log.warning(f"Telegram rate limit! {retry_after} saniye bekleniyor...")
                import time
                time.sleep(retry_after)
                response = requests.post(url, json=payload, timeout=15)

            if response.status_code != 200:
                # HTML parse hatası alırsak plain text fallback ile tekrar deneyelim
                log.warning(f"Telegram HTML parse hatası olabilir (Status: {response.status_code}). Plain text fallback deneniyor...")
                payload.pop("parse_mode", None)
                response = requests.post(url, json=payload, timeout=15)

            response.raise_for_status()
            log.info("Telegram bildirimi başarıyla gönderildi.")
            return True
        except Exception as e:
            log.error(f"Telegram mesaj gönderimi başarısız: {e}")
            return False

    def send_document(self, file_path: str, caption: str = "") -> bool:
        """Belge/Dosya gönder."""
        if not self.bot_token or not self.chat_id:
            log.warning("Telegram token veya Chat ID eksik, dosya gönderilmedi.")
            return False

        url = f"{self.base_url}/sendDocument"
        try:
            log.info(f"Telegram dosya gönderimi başlatıldı: {file_path}")
            with open(file_path, "rb") as doc:
                files = {"document": doc}
                data = {
                    "chat_id": self.chat_id,
                    "caption": caption,
                    "parse_mode": "HTML"
                }
                response = requests.post(url, data=data, files=files, timeout=30)
                response.raise_for_status()
                log.info("Telegram belgesi başarıyla gönderildi.")
                return True
        except Exception as e:
            log.error(f"Telegram dosya gönderimi başarısız: {e}")
            return False
