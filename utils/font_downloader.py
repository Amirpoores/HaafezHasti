import requests
import os

def download_fonts():
    """دانلود فونت‌های فارسی از منابع معتبر"""
    
    # فونت‌های جدید با لینک‌های کاربردی
    fonts = {
        'vazir': 'https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/Vazir-Regular.ttf',
        'iran_nastaliq': 'https://cdn.jsdelivr.net/gh/rastikerdar/iran-nastaliq-font@v4.0.0/dist/IranNastaliq-Regular.ttf',
        'noto_nastaliq': 'https://fonts.gstatic.com/s/notonastaliqurdu/v27/LhWjMVbXOfASNfMUVFWpZHQtUxTmMorFzLs.ttf'
    }
    
    os.makedirs('fonts', exist_ok=True)
    
    print("🔄 شروع دانلود فونت‌ها...")
    
    for font_name, url in fonts.items():
        try:
            print(f"📥 دانلود {font_name}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                font_path = f'fonts/{font_name}.ttf'
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ {font_name} دانلود شد ({len(response.content)} bytes)")
            else:
                print(f"❌ خطا در دانلود {font_name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا در دانلود {font_name}: {e}")
    
    print("🎉 پایان دانلود فونت‌ها!")

if __name__ == "__main__":
    download_fonts()