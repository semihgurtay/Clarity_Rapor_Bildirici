import os
import sys
from dotenv import load_dotenv

# Proje kökünü sys.path'e ekle
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# .env dosyasını yükle (Lokal geliştirme için)
env_path = os.path.join(_ROOT, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

class Settings:
    ENV: str = os.getenv("ENV", "production")
    IS_DRY_RUN: bool = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

    # API Anahtarları
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_CHAT_ID: str = os.getenv("ADMIN_CHAT_ID", "")
    CLARITY_API_TOKEN: str = os.getenv("CLARITY_API_TOKEN", "")

    def validate(self):
        """Kritik ayarların varlığını kontrol et (Fail-Fast)."""
        if self.IS_DRY_RUN:
            # Dry-run modunda sadece API tokenları ve openai key yeterlidir
            missing = []
            if not self.OPENAI_API_KEY:
                missing.append("OPENAI_API_KEY")
            if not self.CLARITY_API_TOKEN:
                missing.append("CLARITY_API_TOKEN")
            if missing:
                raise ValueError(f"Dry-run modunda kritik eksik değişkenler var: {', '.join(missing)}")
            return

        missing = []
        if not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not self.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.ADMIN_CHAT_ID:
            missing.append("ADMIN_CHAT_ID")
        if not self.CLARITY_API_TOKEN:
            missing.append("CLARITY_API_TOKEN")

        if missing:
            raise ValueError(f"Kritik ortam değişkenleri eksik: {', '.join(missing)}")

settings = Settings()
