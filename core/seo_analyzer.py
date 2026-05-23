import logging
import requests
from config import settings

log = logging.getLogger("SEOAnalyzer")

class SEOAnalyzer:
    """Perplexity API kullanarak sitenin haftalık SEO ve Arama Görünürlük Analizini yapar."""
    
    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def fetch_seo_insights(self, target_site: str = "payitahtsaatcilik.com") -> str:
        """Belirtilen site için Perplexity üzerinden güncel SEO ve AIO verisi toplar."""
        log.info(f"Perplexity API ile {target_site} için SEO ve AIO verileri çekiliyor...")
        
        prompt = f"""Bir uzman SEO ve AIO (AI Search Optimization) analisti olarak, şu an interneti tarayarak {target_site} sitesinin güncel arama motoru ve yapay zeka arama görünürlüğünü analiz etmeni istiyorum.
        
Özellikle şu sorulara odaklan:
1. Son zamanlarda bu site Google gibi geleneksel arama motorlarında veya yapay zeka arama araçlarında (Perplexity, ChatGPT, vb.) ne sıklıkla ve hangi bağlamda anılıyor?
2. Site ile ilgili öne çıkan son ürünler, lüks saat markaları (Rolex, Omega vb.) veya anahtar kelime fırsatları neler?
3. Sitenin dijital görünürlüğünde göze çarpan eksiklikler veya son gelişmeler neler?

Cevabını Markdown formatında, tamamen Türkçe olarak, teknik fakat anlaşılır bir dille, sadece gerçek ve anlık verilere dayanarak (gerçekten tarama yaparak) hazırla. Eğer spesifik bir veri bulamazsan, lüks saat e-ticareti özelinde genel ve güçlü tavsiyeler ver. Maksimum 500 kelime olsun."""

        payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "Sen gerçek zamanlı web araması yapabilen uzman bir SEO ve AIO analistisin."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.2
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            seo_content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            log.info("Perplexity SEO analizi başarıyla tamamlandı.")
            return seo_content
        except Exception as e:
            log.error(f"Perplexity API çağrısı sırasında hata oluştu: {e}")
            return f"SEO verisi çekilirken hata oluştu: {e}"
