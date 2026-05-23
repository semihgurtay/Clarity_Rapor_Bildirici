import os
import sys
from dotenv import load_dotenv

# Proje kökünü sys.path'e ekle
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# _knowledge dizinindeki master.env dosyasını bul (3 üst klasör veya Workspace kökü)
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(_ROOT))
MASTER_ENV_PATH = os.path.join(WORKSPACE_ROOT, "_knowledge", "credentials", "master.env")

if os.path.exists(MASTER_ENV_PATH):
    load_dotenv(MASTER_ENV_PATH, override=True)
else:
    print(f"Uyarı: master.env bulunamadı! Aranan yol: {MASTER_ENV_PATH}")

class Settings:
    ENV: str = os.getenv("ENV", "production")
    IS_DRY_RUN: bool = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")

    # API Anahtarları (master.env'den)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_CHAT_ID: str = os.getenv("ADMIN_CHAT_ID", "")
    CLARITY_API_TOKEN: str = os.getenv("CLARITY_API_TOKEN", "")
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")

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
        if not self.PERPLEXITY_API_KEY:
            missing.append("PERPLEXITY_API_KEY")

        if missing:
            raise ValueError(f"Kritik ortam değişkenleri eksik: {', '.join(missing)}")

settings = Settings()
