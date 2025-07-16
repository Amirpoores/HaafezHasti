import requests
import logging

logger = logging.getLogger(__name__)

# API Key گراک
GROQ_API_KEY = "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"

def get_hafez_interpretation_groq(ghazal_text, ghazal_number=None, interpretation_type="fal"):
    """تفسیر حافظ با Groq - بهبود یافته"""
    try:
        if interpretation_type == "fal":
            prompt = f"""
شما یک استاد عرفان و تفسیرگر ماهر فال حافظ هستید. این غزل را به عنوان فال تفسیر کنید:

{ghazal_text}

لطفاً پاسخ را در این قالب دقیق ارائه دهید:

🔮 **وضعیت کلی:** [یک کلمه یا عبارت کوتاه مثل: مثبت، منفی، مشروط، صبر کن، عالی]

💫 **تفسیر فال:**
[2-3 جمله تفسیر عرفانی با زبان ساده و روان]

🌟 **راهنمایی عملی:**
[یک جمله پیشنهاد عملی برای فال‌گیرنده]

فقط متن فارسی و بدون توضیحات اضافه.
            """
        else:
            prompt = f"""
این غزل حافظ را به زبان ساده توضیح دهید:

{ghazal_text}

💎 **خلاصه معنا:**
[خلاصه‌ای از معنای کلی غزل]

🌹 **پیام اصلی:**
[پیام اصلی که حافظ می‌خواهد منتقل کند]
            """

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": "شما یک استاد ادبیات فارسی و عرفان هستید. با زبان محترم، سلیس و روان پاسخ دهید."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 300,
            "temperature": 0.7,
            "stream": False
        }

        response = requests.post(url, headers=headers, json=data, timeout=25)

        if response.status_code == 200:
            result = response.json()
            interpretation = result['choices'][0]['message']['content']
            return interpretation.strip()
        else:
            return None

    except Exception as e:
        logger.error(f"خطا در تفسیر: {str(e)}")
        return None

# تست تابع
if __name__ == "__main__":
    sample_text = "الا یا ایها الساقی ادر کاسا و ناولها\nکه عشق آسان نمود اول ولی افتاد مشکل‌ها"
    
    print("🔮 تست تفسیر فال:")
    result = get_hafez_interpretation_groq(sample_text, 1, "fal")
    if result:
        print(result)
    else:
        print("❌ خطا در تفسیر")
