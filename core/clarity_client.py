import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from config import settings

log = logging.getLogger("ClarityClient")

def _clean_and_sort_metric_data(data: list, limit: int = 15) -> list:
    """Clarity API'sinden gelen devasa listeleri en yüksek değerli ilk N öğeye göre filtreler."""
    if not isinstance(data, list):
        return data

    for metric in data:
        if not isinstance(metric, dict) or "information" not in metric:
            continue
        
        info = metric.get("information", [])
        if not isinstance(info, list) or not info:
            continue
            
        def get_sort_val(x):
            if not isinstance(x, dict):
                return 0
            # En yaygın sayısal anahtarları dene
            for k in ["pagesViews", "subTotal", "sessionsCount", "totalSessionCount"]:
                if k in x and x[k] is not None:
                    try:
                        return float(str(x[k]).replace("%", "").strip())
                    except ValueError:
                        pass
            # Herhangi bir sayısal değere bak
            for k, v in x.items():
                if v is None or k in ["Url", "url", "device", "browser", "os", "source", "medium", "channel"]:
                    continue
                if isinstance(v, (int, float)):
                    return v
                try:
                    return float(str(v).replace("%", "").strip())
                except ValueError:
                    pass
            return 0

        # Sırala ve sınırla
        sorted_info = sorted(info, key=get_sort_val, reverse=True)
        metric["information"] = sorted_info[:limit]

    return data

class ClarityClient:
    BASE_URL = "https://www.clarity.ms/export-data/api/v1/project-live-insights"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.CLARITY_API_TOKEN}",
            "Content-Type": "application/json"
        }
        # Requests Session & Retry Setup (ANA standardı)
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _fetch(self, num_of_days: int = 7, dimension1: str = None, dimension2: str = None) -> dict | list:
        """Microsoft Clarity Live Insights API'sinden veri çek."""
        params = {"numOfDays": num_of_days}
        if dimension1:
            params["dimension1"] = dimension1
        if dimension2:
            params["dimension2"] = dimension2

        try:
            log.info(f"Clarity API çağrısı yapılıyor: days={num_of_days}, dim1={dimension1}, dim2={dimension2}")
            response = self.session.get(self.BASE_URL, headers=self.headers, params=params, timeout=20)
            response.raise_for_status()
            raw_data = response.json()
            return _clean_and_sort_metric_data(raw_data)
        except Exception as e:
            log.error(f"Clarity veri çekme hatası (dim1={dimension1}): {e}")
            # Hata durumunda boş veri dönelim ki akış tamamen kırılmasın
            return {}

    def get_weekly_insights(self) -> dict:
        """Son 3 güne ait tüm kritik boyutlardaki verileri topla."""
        log.info("Son 3 günlük Clarity verileri toplanıyor...")
        
        # 1. Genel Bakış
        overview = self._fetch(num_of_days=3)
        
        # 2. Cihaz Kırılımı
        devices = self._fetch(num_of_days=3, dimension1="Device")
        
        # 3. Kaynak / Medium Kırılımı
        sources = self._fetch(num_of_days=3, dimension1="Source", dimension2="Medium")
        
        # 4. Kanal Kırılımı
        channels = self._fetch(num_of_days=3, dimension1="Channel")
        
        # 5. Tarayıcı Kırılımı
        browsers = self._fetch(num_of_days=3, dimension1="Browser")

        # 6. En Popüler URL'ler
        urls = self._fetch(num_of_days=3, dimension1="URL")

        return {
            "overview": overview,
            "devices": devices,
            "sources": sources,
            "channels": channels,
            "browsers": browsers,
            "urls": urls
        }
