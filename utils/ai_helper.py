import requests
import logging

logger = logging.getLogger(__name__)
GROQ_API_KEY = "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"

def get_hafez_interpretation_groq(ghazal_text, ghazal_number=None, interpretation_type="fal"):
    """تفسیر حافظ با Groq"""
    try:
        print(f"🔄 درخواست تفسیر غزل {ghazal_number}...")
        
        if interpretation_type == "fal":
            prompt = f"""
این غزل حافظ را به شکل فال تفسیر کن:

{ghazal_text}

جواب را دقیقاً در این قالب بده:

🔮 وضعیت: [مثبت/منفی/مشروط]
💫 تفسیر: [2-3 جمله تفسیر فال]
🌟 راهنمایی: [یک جمله پیشنهاد عملی]
            """
        else:
            prompt = f"این غزل حافظ را تحلیل کن:\n\n{ghazal_text}"

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "تو یک تفسیرگر ماهر فال حافظ هستی. جواب کوتاه و مفید بده."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 250,
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=data, timeout=20)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            interpretation = result['choices'][0]['message']['content'].strip()
            print(f"✅ تفسیر دریافت شد!")
            return interpretation
        else:
            print(f"❌ خطای API: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        return None

def get_fallback_interpretation(ghazal_text, ghazal_number):
    """تفسیر پیش‌فرض"""
    import random
    
    interpretations = [
        f"🔮 وضعیت: مثبت\n💫 تفسیر: غزل {ghazal_number} نشان‌دهنده امید و روشنایی است که در راه شما قرار دارد\n🌟 راهنمایی: با صبر و اعتماد به خود ادامه دهید",
        f"🔮 وضعیت: مشروط\n💫 تفسیر: غزل {ghazal_number} درباره تأمل و تفکر در تصمیم‌گیری‌های مهم زندگی است\n🌟 راهنمایی: عجله نکنید و با دقت تصمیم بگیرید",
        f"🔮 وضعیت: مثبت\n💫 تفسیر: این غزل حکایت از عشق، وفاداری و استقامت در برابر مشکلات دارد\n🌟 راهنمایی: به راه خود ادامه دهید، موفقیت نزدیک است",
        f"🔮 وضعیت: مشروط\n💫 تفسیر: غزل {ghazal_number} در مورد تعادل بین امید و احتیاط در زندگی صحبت می‌کند\n🌟 راهنمایی: متعادل باشید و از افراط و تفریط دوری کنید",
        f"🔮 وضعیت: مثبت\n💫 تفسیر: این غزل نشان‌دهنده زیبایی‌ها و برکات زندگی است که در انتظار شما قرار دارد\n🌟 راهنمایی: قدردان نعمت‌های موجود باشید"
    ]
    
    return random.choice(interpretations)

# تست
if __name__ == "__main__":
    sample_text = "الا یا ایها الساقی ادر کاسا و ناولها\nکه عشق آسان نمود اول ولی افتاد مشکل‌ها"
    
    print("🔮 تست تفسیر AI:")
    result = get_hafez_interpretation_groq(sample_text, 1, "fal")
    
    if result:
        print(f"✅ نتیجه AI:\n{result}")
    else:
        print("❌ AI کار نکرد - استفاده از fallback")
        fallback = get_fallback_interpretation(sample_text, 1)
        print(f"🔄 Fallback:\n{fallback}")