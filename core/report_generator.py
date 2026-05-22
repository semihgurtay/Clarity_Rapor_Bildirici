import json
import logging
from openai import OpenAI
from config import settings

log = logging.getLogger("ReportGenerator")

REPORT_SYSTEM_PROMPT = """You are an expert UX and Conversion Rate Optimization (CRO) Analyst.
Your task is to analyze the Microsoft Clarity weekly insights data for the e-commerce store "payitahtsaatcilik.com" (selling luxury wrist watches) and generate a concise, high-impact Telegram weekly report in Turkish.

## ANALYTICAL FOCUS:
1. **Engagement Metrics:** Session duration, scroll depth, active time, click metrics.
2. **Friction Metrics:** Quickback clicks (high bounce on details), dead clicks, rage clicks.
3. **Segmentation Insights:** Mobile vs. Desktop share, in-app browser performance (Instagram/Facebook browser is huge for ad traffic), and device/browser specific friction.
4. **Actionable Recommendations:** What should the development or UX team fix based on these metrics?

## TELEGRAM FORMATTING RULES (HTML mode):
- Keep the message concise. Max 3500 characters so it fits in a single Telegram message easily.
- Use ONLY Telegram supported HTML tags: <b>...</b> for bold, <i>...</i> for italic, <code>...</code> for code, <u>...</u> for underline, and <s>...</s> for strikethrough.
- Do NOT use unsupported HTML tags like <table>, <tr>, <td>, <div>, <p>, <ul>, <li>. Telegram will reject them and return 400.
- Use emojis, indentations, and newlines to structure the report and key metrics instead of HTML tables or list tags.
- Do not use markdown syntax like **, * or `_` since parse_mode is HTML.
- Provide a summary first, then key metrics in a structured text layout, then actionable insights.

## DATA FORMAT:
You will receive a JSON structure containing:
- overview: general stats
- devices: stats per device
- sources: stats per source/medium
- channels: stats per marketing channel
- browsers: stats per browser
- urls: top pages visited

Write the report in a highly professional, business-technical tone, keeping it strictly factual and actionable. Avoid generic fluff.
"""

class ReportGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_report(self, clarity_data: dict) -> str:
        """Clarity verilerini GPT-4o ile analiz ederek Türkçe Telegram raporu üret."""
        log.info("GPT-4o ile Clarity analiz raporu üretiliyor...")
        
        user_message = f"""Here is the Microsoft Clarity JSON data for the last 7 days:

{json.dumps(clarity_data, indent=2)}

Please write the weekly performance and UX analysis report in Turkish. Make sure it follows the Telegram HTML format rules. Keep it under 3500 characters."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            report = response.choices[0].message.content
            log.info("Analiz raporu başarıyla üretildi.")
            return report
        except Exception as e:
            log.error(f"GPT rapor üretme hatası: {e}")
            raise
