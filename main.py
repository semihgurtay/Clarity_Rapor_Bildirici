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
        
        # 4. Word (.docx) dosyasını yerel diskte üret
        from core.docx_generator import parse_markdown_to_docx
        from datetime import datetime
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        docx_filename = f"Payitaht_Saatcilik_Clarity_Analiz_Raporu_{date_str}.docx"
        docx_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), docx_filename)
        
        log.info(f"Word belgesi oluşturuluyor: {docx_path}")
        parse_markdown_to_docx(report_text, docx_path)
        
        # 5. Çıktıyı Değerlendir
        if settings.IS_DRY_RUN:
            log.info("\n=== ÜRETİLEN RAPOR (DRY-RUN) ===")
            print(report_text)
            log.info("================================\n")
            log.info(f"Word belgesi yerelde bırakıldı: {docx_path}")
            log.info("Dry-run başarıyla tamamlandı.")
            return

        # 6. Telegram üzerinden Word dosyasını gönder
        sender = TelegramSender()
        caption = f"📊 <b>payitahtsaatcilik.com - Haftalık Clarity UX ve Performans Raporu</b> ({date_str})"
        success = sender.send_document(docx_path, caption=caption)
        
        # Dosya gönderildikten sonra temizlik yap
        try:
            os.remove(docx_path)
            log.info("Yerel Word belgesi temizlendi.")
        except Exception as remove_err:
            log.warning(f"Yerel dosya silinemedi: {remove_err}")
        
        if success:
            log.info("🎉 Haftalık Clarity raporu (Word) başarıyla Telegram üzerinden iletildi!")
            sys.exit(0)
        else:
            log.error("❌ Telegram'dan dosya gönderilemedi.")
            sys.exit(1)

    except Exception as e:
        log.error(f"💥 Kritik Hata: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
