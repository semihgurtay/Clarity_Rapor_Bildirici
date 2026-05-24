import json
import logging
from openai import OpenAI
from config import settings

log = logging.getLogger("ReportGenerator")

REPORT_SYSTEM_PROMPT = """You are an expert UX, Conversion Rate Optimization (CRO), and SEO Analyst.
Your task is to analyze BOTH the Microsoft Clarity weekly insights data AND the Perplexity AI SEO visibility analysis for the e-commerce store "payitahtsaatcilik.com", and generate a concise, high-impact Telegram weekly report in Turkish.

## ANALYTICAL FOCUS:
1. **UX & Engagement Metrics:** Session duration, scroll depth, active time, click metrics from Clarity.
2. **Friction Metrics:** Quickback clicks, dead clicks, rage clicks from Clarity.
3. **Segmentation Insights:** Mobile vs. Desktop, source, channel, and device specific friction.
4. **SEO & AIO Visibility:** Summarize and highlight the key findings from the Perplexity SEO data provided.
5. **Actionable Recommendations:** What should the development, marketing, or UX team fix based on these combined UX and SEO metrics?

- Write a detailed, comprehensive report. There is no strict length limit since it will be exported to a Word document.
- Use standard Markdown tables for statistics and structured lists for readability.
- Use bold markdown (**text**) for headers and key values.
- Use emojis logically to make the report visually engaging.
- Provide a summary first, then key metrics in Markdown tables, then SEO insights, and finally actionable recommendations.

## DATA FORMAT:
You will receive:
1. A JSON structure containing Clarity UX data (overview, devices, sources, channels, browsers, urls).
2. A text block containing Perplexity AI SEO Analysis data.

Write the report in a highly professional, business-technical tone, keeping it strictly factual and actionable. Avoid generic fluff.
"""

class ReportGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_report(self, clarity_data: dict, seo_data: str) -> str:
        """Clarity ve SEO verilerini GPT-4o ile analiz ederek Türkçe rapor üret."""
        log.info("GPT-4o ile Clarity + SEO birleşik analiz raporu üretiliyor...")
        
        user_message = f"""Here is the Microsoft Clarity JSON data for the last 7 days:

{json.dumps(clarity_data, indent=2)}

---

Here is the Perplexity AI SEO & Visibility Analysis:

{seo_data}

---

Please write the combined weekly UX and SEO performance analysis report in Turkish. Make sure it is well-structured in Markdown format, as it will be saved as a Word document."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            report = response.choices[0].message.content
            log.info("Analiz raporu başarıyla üretildi.")
            return report
        except Exception as e:
            log.error(f"GPT rapor üretme hatası: {e}")
            raise
