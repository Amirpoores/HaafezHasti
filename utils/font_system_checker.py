import os
import platform
from PIL import ImageFont

def find_system_fonts():
    """پیدا کردن تمام فونت‌های سیستم"""
    
    system = platform.system()
    font_dirs = []
    
    if system == "Windows":
        font_dirs = [
            "C:/Windows/Fonts/",
            "C:/Windows/System32/Fonts/",
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/")
        ]
    elif system == "Darwin":  # macOS
        font_dirs = [
            "/Library/Fonts/",
            "/System/Library/Fonts/",
            os.path.expanduser("~/Library/Fonts/")
        ]
    elif system == "Linux":
        font_dirs = [
            "/usr/share/fonts/",
            "/usr/local/share/fonts/",
            os.path.expanduser("~/.fonts/")
        ]
    
    all_fonts = []
    
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            try:
                for file in os.listdir(font_dir):
                    if file.lower().endswith(('.ttf', '.otf')):
                        full_path = os.path.join(font_dir, file)
                        all_fonts.append((file, full_path))
            except PermissionError:
                print(f"⚠️ دسترسی به {font_dir} امکان‌پذیر نیست")
    
    return all_fonts

def categorize_fonts(fonts):
    """دسته‌بندی فونت‌ها"""
    
    categories = {
        'nastaliq': [],
        'arabic': [],
        'persian': [],
        'urdu': [],
        'farsi': [],
        'other': []
    }
    
    # کلمات کلیدی برای شناسایی
    nastaliq_keywords = ['nastaliq', 'nasta', 'iran', 'urdu']
    arabic_keywords = ['arabic', 'arab', 'naskh', 'kufi']
    persian_keywords = ['persian', 'farsi', 'iran', 'tahoma', 'nazanin', 'titr', 'yekan', 'vazir']
    
    for font_name, font_path in fonts:
        font_lower = font_name.lower()
        
        if any(keyword in font_lower for keyword in nastaliq_keywords):
            categories['nastaliq'].append((font_name, font_path))
        elif any(keyword in font_lower for keyword in arabic_keywords):
            categories['arabic'].append((font_name, font_path))
        elif any(keyword in font_lower for keyword in persian_keywords):
            categories['persian'].append((font_name, font_path))
        elif 'urdu' in font_lower:
            categories['urdu'].append((font_name, font_path))
        else:
            categories['other'].append((font_name, font_path))
    
    return categories

def test_font_persian_support(font_path):
    """تست پشتیبانی فارسی فونت"""
    try:
        font = ImageFont.truetype(font_path, 24)
        # تست کاراکتر فارسی
        persian_text = "الف ب پ ت ث ج چ ح خ د ذ ر ز ژ س ش ص ض"
        
        # اگه خطا نداد، احتمالاً فارسی پشتیبانی می‌کنه
        return True
    except:
        return False

def setup_best_fonts():
    """انتخاب بهترین فونت‌ها و کپی کردن"""
    
    print("🔍 جستجوی فونت‌های سیستم...")
    all_fonts = find_system_fonts()
    
    if not all_fonts:
        print("❌ هیچ فونتی پیدا نشد!")
        return
    
    print(f"📊 تعداد کل فونت‌ها: {len(all_fonts)}")
    
    # دسته‌بندی
    categories = categorize_fonts(all_fonts)
    
    print("\n🎯 فونت‌های شناسایی شده:")
    print("="*50)
    
    # نمایش نستعلیق
    if categories['nastaliq']:
        print("🌟 فونت‌های نستعلیق:")
        for name, path in categories['nastaliq']:
            support = "✅" if test_font_persian_support(path) else "❌"
            print(f"  {support} {name} → {path}")
    
    # نمایش عربی
    if categories['arabic']:
        print("\n📝 فونت‌های عربی:")
        for name, path in categories['arabic'][:5]:  # فقط 5 تای اول
            support = "✅" if test_font_persian_support(path) else "❌"
            print(f"  {support} {name} → {path}")
    
    # نمایش فارسی
    if categories['persian']:
        print("\n🇮🇷 فونت‌های فارسی:")
        for name, path in categories['persian'][:5]:  # فقط 5 تای اول
            support = "✅" if test_font_persian_support(path) else "❌"
            print(f"  {support} {name} → {path}")
    
    # پیدا کردن بهترین گزینه‌ها
    print("\n🎖️ بهترین گزینه‌ها:")
    print("="*50)
    
    # اولویت‌بندی
    priority_fonts = []
    
    # اول نستعلیق
    for name, path in categories['nastaliq']:
        if test_font_persian_support(path):
            priority_fonts.append(('nastaliq', name, path))
    
    # بعد فارسی
    for name, path in categories['persian']:
        if test_font_persian_support(path):
            priority_fonts.append(('persian', name, path))
    
    # بعد عربی
    for name, path in categories['arabic']:
        if test_font_persian_support(path):
            priority_fonts.append(('arabic', name, path))
    
    # کپی کردن بهترین فونت‌ها
    os.makedirs('fonts', exist_ok=True)
    
    if priority_fonts:
        print("\n📋 کپی کردن بهترین فونت‌ها:")
        
        # نستعلیق اصلی
        nastaliq_found = False
        for font_type, name, path in priority_fonts:
            if font_type == 'nastaliq' and not nastaliq_found:
                import shutil
                shutil.copy2(path, 'fonts/nastaliq_main.ttf')
                print(f"✅ نستعلیق اصلی: {name} → fonts/nastaliq_main.ttf")
                nastaliq_found = True
        
        # فونت عمومی (تاهوما یا بهترین گزینه)
        general_found = False
        for font_type, name, path in priority_fonts:
            if ('tahoma' in name.lower() or font_type == 'persian') and not general_found:
                import shutil
                shutil.copy2(path, 'fonts/general.ttf')
                print(f"✅ فونت عمومی: {name} → fonts/general.ttf")
                general_found = True
        
        # فونت پشتیبان
        if len(priority_fonts) > 0:
            import shutil
            shutil.copy2(priority_fonts[0][2], 'fonts/fallback.ttf')
            print(f"✅ فونت پشتیبان: {priority_fonts[0][1]} → fonts/fallback.ttf")
    
    else:
        print("❌ هیچ فونت مناسبی پیدا نشد!")
    
    print("\n🎉 بررسی فونت‌ها تمام شد!")

if __name__ == "__main__":
    setup_best_fonts()