#!/usr/bin/env python3
import os
import sys
import logging
import argparse

# Windows konsolunda Türkçe karakter ve emoji encoding hatalarını önle
sys.stdout.reconfigure(encoding='utf-8')

# Yerel DNS çözümleme sorunlarını aşmak için www.clarity.ms IP'sini el ile set et (SSL doğrulaması bozulmaz)
import socket
_orig_getaddrinfo = socket.getaddrinfo
def _patched_getaddrinfo(host, port, *args, **kwargs):
    if host == "www.clarity.ms":
        return _orig_getaddrinfo("20.250.198.32", port, *args, **kwargs)
    return _orig_getaddrinfo(host, port, *args, **kwargs)
socket.getaddrinfo = _patched_getaddrinfo

# Proje dizinini Python yoluna ekle
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config import settings
from core.clarity_client import ClarityClient
from core.report_generator import ReportGenerator
from infrastructure.telegram_sender import TelegramSender

# Logging Kurulumu
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("ClarityNotifier")

def main():
    parser = argparse.ArgumentParser(description="Haftalık Microsoft Clarity Telegram Raporlayıcı")
    parser.add_argument("--dry-run", action="store_true", help="Mesajı Telegram'a göndermeden sadece ekrana yazar")
    args = parser.parse_args()

    if args.dry_run:
        settings.IS_DRY_RUN = True
        log.info("🧪 DRY-RUN modu aktif. Telegram'a gönderim yapılmayacaktır.")

    try:
        # 1. Ayarları Doğrula
        settings.validate()
        
        # 2. Clarity Verilerini Çek
        client = ClarityClient()
        log.info("Clarity verileri çekiliyor...")
        clarity_data = client.get_weekly_insights()
        
        # 3. GPT-4o ile Analiz Yap
        generator = ReportGenerator()
        log.info("GPT-4o analiz raporu oluşturuluyor...")
        report_text = generator.generate_report(clarity_data)
        
        # 4. Çıktıyı Değerlendir
        if settings.IS_DRY_RUN:
            log.info("\n=== ÜRETİLEN RAPOR (DRY-RUN) ===")
            print(report_text)
            log.info("================================\n")
            log.info("Dry-run başarıyla tamamlandı.")
            return

        # 5. Telegram Bildirimi Gönder
        sender = TelegramSender()
        success = sender.send_message(report_text)
        
        if success:
            log.info("🎉 Haftalık Clarity raporu başarıyla Telegram üzerinden iletildi!")
            sys.exit(0)
        else:
            log.error("❌ Telegram bildirimi gönderilemedi.")
            sys.exit(1)

    except Exception as e:
        log.error(f"💥 Kritik Hata: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
