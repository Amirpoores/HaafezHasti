from PIL import Image, ImageDraw, ImageFont
import requests
import os
import arabic_reshaper
from bidi.algorithm import get_display

class FalImageGenerator:
    def __init__(self):
        self.fonts_dir = 'fonts'
        self.output_dir = 'static/images'
        os.makedirs(self.output_dir, exist_ok=True)
        
    def reshape_persian_text(self, text):
        """تنظیم متن فارسی برای نمایش درست"""
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            display_text = get_display(reshaped_text)
            return display_text
        except Exception as e:
            print(f"خطا در تنظیم متن: {e}")
            return text
    
    def download_background_image(self, url, filename):
        """دانلود عکس پس‌زمینه"""
        try:
            response = requests.get(url)
            image_path = os.path.join(self.output_dir, filename)
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ پس‌زمینه دانلود شد: {image_path}")
            return image_path
        except Exception as e:
            print(f"❌ خطا در دانلود عکس: {e}")
            return None
    
    def create_fal_image(self, ghazal_text, interpretation, ghazal_number, background_url=None):
        """تولید عکس فال با فونت نستعلیق"""
        
        print(f"🎨 شروع تولید عکس فال برای غزل {ghazal_number}...")
        
        # دانلود پس‌زمینه
        if background_url:
            bg_path = self.download_background_image(background_url, f'bg_temp_{ghazal_number}.jpg')
            if not bg_path:
                print("❌ خطا در دانلود پس‌زمینه")
                return None
        else:
            print("❌ URL پس‌زمینه ارائه نشده")
            return None
        
        try:
            # باز کردن عکس پس‌زمینه
            background = Image.open(bg_path)
            
            # تنظیم سایز
            target_size = (900, 700)
            background = background.resize(target_size, Image.Resampling.LANCZOS)
            
            # ایجاد لایه برای متن
            overlay = Image.new('RGBA', target_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # بارگذاری فونت‌ها
            try:
                # فونت نستعلیق برای غزل
                if os.path.exists(f'{self.fonts_dir}/nastaliq_main.ttf'):
                    title_font = ImageFont.truetype(f'{self.fonts_dir}/nastaliq_main.ttf', 32)
                    ghazal_font = ImageFont.truetype(f'{self.fonts_dir}/nastaliq_main.ttf', 28)
                    print("✅ فونت نستعلیق اصلی بارگذاری شد")
                elif os.path.exists(f'{self.fonts_dir}/general.ttf'):
                    title_font = ImageFont.truetype(f'{self.fonts_dir}/general.ttf', 32)
                    ghazal_font = ImageFont.truetype(f'{self.fonts_dir}/general.ttf', 28)
                    print("✅ فونت عمومی (تاهوما) بارگذاری شد")
                else:
                    title_font = ImageFont.load_default()
                    ghazal_font = ImageFont.load_default()
                    print("⚠️ از فونت پیش‌فرض استفاده می‌شود")
                
                # فونت تفسیر
                if os.path.exists(f'{self.fonts_dir}/general.ttf'):
                    interp_font = ImageFont.truetype(f'{self.fonts_dir}/general.ttf', 20)
                else:
                    interp_font = ImageFont.load_default()
                    
            except Exception as e:
                print(f"⚠️ خطا در بارگذاری فونت: {e}")
                title_font = ImageFont.load_default()
                ghazal_font = ImageFont.load_default()
                interp_font = ImageFont.load_default()
            
            # مختصات
            center_x = target_size[0] // 2
            y_pos = 100
            
            # عنوان
            title = "🔮 فال حافظ"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            
            # سایه عنوان
            draw.text((center_x - title_width//2 + 3, y_pos + 3), title, 
                     font=title_font, fill=(0, 0, 0, 180))
            # متن عنوان
            draw.text((center_x - title_width//2, y_pos), title, 
                     font=title_font, fill=(139, 69, 19, 255))
            
            y_pos += 80
            
            # متن غزل
            ghazal_lines = ghazal_text.split('\n')
            for line in ghazal_lines:
                if line.strip():
                    # تنظیم متن فارسی
                    persian_line = self.reshape_persian_text(line.strip())
                    
                    # محاسبه عرض
                    line_bbox = draw.textbbox((0, 0), persian_line, font=ghazal_font)
                    line_width = line_bbox[2] - line_bbox[0]
                    
                    # سایه
                    draw.text((center_x - line_width//2 + 3, y_pos + 3), persian_line, 
                             font=ghazal_font, fill=(0, 0, 0, 150))
                    
                    # متن اصلی
                    draw.text((center_x - line_width//2, y_pos), persian_line, 
                             font=ghazal_font, fill=(44, 24, 16, 255))
                    
                    y_pos += 50
            
            y_pos += 50
            
            # تفسیر
            if interpretation and interpretation.strip():
                # کادر تفسیر
                box_left = 80
                box_right = target_size[0] - 80
                box_top = y_pos
                box_height = 140
                box_bottom = box_top + box_height
                
                # پس‌زمینه کادر
                draw.rounded_rectangle([box_left, box_top, box_right, box_bottom], 
                                     radius=20, fill=(255, 255, 255, 240))
                draw.rounded_rectangle([box_left, box_top, box_right, box_bottom], 
                                     radius=20, outline=(76, 175, 80, 255), width=4)
                
                # عنوان تفسیر
                interp_title = "💫 تفسیر فال:"
                draw.text((box_left + 25, box_top + 20), interp_title, 
                         font=interp_font, fill=(76, 175, 80, 255))
                
                # متن تفسیر
                interp_text = self.reshape_persian_text(interpretation)
                
                # تقسیم به خطوط
                max_width = box_right - box_left - 50
                words = interp_text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    test_bbox = draw.textbbox((0, 0), test_line, font=interp_font)
                    test_width = test_bbox[2] - test_bbox[0]
                    
                    if test_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # رسم خطوط
                text_y = box_top + 60
                for line in lines[:3]:  # حداکثر 3 خط
                    draw.text((box_left + 25, text_y), line, 
                             font=interp_font, fill=(44, 24, 16, 255))
                    text_y += 30
            
            # ترکیب نهایی
            background = background.convert('RGBA')
            final_image = Image.alpha_composite(background, overlay)
            final_image = final_image.convert('RGB')
            
            # ذخیره
            output_path = os.path.join(self.output_dir, f'fal_ghazal_{ghazal_number}.jpg')
            final_image.save(output_path, 'JPEG', quality=95)
            
            print(f"✅ عکس فال ذخیره شد: {output_path}")
            
            # حذف فایل موقت
            if os.path.exists(bg_path):
                os.remove(bg_path)
            
            return output_path
            
        except Exception as e:
            print(f"❌ خطا در تولید عکس: {e}")
            return None

# تست
def test_fal_generator():
    print("🧪 شروع تست تولید عکس فال با فونت نستعلیق...")
    
    generator = FalImageGenerator()
    
    # متن نمونه
    ghazal_text = """الا یا ایها الساقی ادر کاسا و ناولها
که عشق آسان نمود اول ولی افتاد مشکل‌ها"""
    
    interpretation = """🔮 وضعیت: مثبت
💫 تفسیر: این غزل نشان‌دهنده شروع مسیری نو در زندگی شماست
🌟 راهنمایی: با صبر و اعتماد به خود ادامه دهید"""
    
    background_url = "https://s3.afranet.net/gapgpt-main-2/user_files/7f7fec7c-47ce-46bb-9bb3-8a15fe7e41e2.png"
    
    result = generator.create_fal_image(
        ghazal_text=ghazal_text,
        interpretation=interpretation,
        ghazal_number=1,
        background_url=background_url
    )
    
    if result:
        print(f"🎉 تست موفق! عکس با فونت نستعلیق در {result} ذخیره شد")
        print(f"📁 فایل: {os.path.abspath(result)}")
    else:
        print("❌ تست ناموفق")
    
    return result

if __name__ == "__main__":
    test_fal_generator()