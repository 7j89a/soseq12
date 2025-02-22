import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# تعريف الهيدرات
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    "api": "1",
    "Connection": "keep-alive",
    "Host": "admin.joacademy.net",
    "lang": "ar",
    "Origin": "https://www.joacademy.com",
    "Referer": "https://www.joacademy.com/",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
}

# الثوابت
BASE_URL = "https://admin.joacademy.net/api/v2/user-course"

# معلومات API الخاصة بـ Telegram
API_ID = 20944746  # استبدل بـ API ID الخاص بك
API_HASH = "d169162c1bcf092a6773e685c62c3894"  # استبدل بـ API Hash الخاص بك
BOT_TOKEN = "7634563577:AAHta-v9rA7C9txh-eQD4eSt-zZetzAvQwM"  # استبدل بـ Token البوت الخاص بك

# إنشاء عميل Pyrogram
app = Client("my_bo2213t", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# قاموس لتخزين حالة المستخدم
user_state = {}

# قاموس لتخزين رموز Authorization لكل مستخدم
user_tokens = {}

# دالة لتقسيم النص إلى أجزاء
def split_text(text, max_length=4096):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

def fetch_courses(url, params=None, user_id=None):
    """ إرسال الطلب واستقبال البيانات """
    if user_id in user_tokens:
        headers["Authorization"] = f"Bearer {user_tokens[user_id]}"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") and "data" in data and "data" in data["data"]:
            courses = data["data"]["data"]
            if courses:
                message = "\n📚 **الدورات المتاحة:**\n"
                message += "=" * 50 + "\n"
                for course in courses:
                    message += f"🆔 **معرّف الدورة:** {course['id']}\n"
                    message += f"📌 **اسم الدورة:** {course['name']}\n"
                    message += f"👨‍🏫 **المدرس:** {course['teacher']['name']}\n"
                    message += f"📅 **تاريخ الإنشاء:** {course['created_at'][:10]}\n"
                    message += f"🎬 **مدة الدورة:** {course['duration']}\n"
                    message += f"🔗 **رابط المقدمة:** {course['intro']}\n"
                    message += f"🖼 **صورة الدورة:** {course['image']}\n"
                    message += f"📖 **عدد الحصص:** {course['total_classes']}\n"
                    message += "=" * 50 + "\n"
                return message
            else:
                return "❌ لا توجد دورات متاحة."
        else:
            return "❌ لم يتم العثور على بيانات."
    else:
        return f"⚠️ فشل الطلب مع رمز الحالة: {response.status_code}\nتفاصيل الخطأ: {response.text}"

def get_course_details(course_id, user_id=None):
    """
    إرسال طلب GET للحصول على تفاصيل الدورة باستخدام course_id.
    """
    if user_id in user_tokens:
        headers["Authorization"] = f"Bearer {user_tokens[user_id]}"
    url = f"{BASE_URL}/get-course-details-desktop"
    params = {
        "course_id": course_id,
        "uuid": "b0e46b36624bfce7d96ec60fe4b30815e2477fa0f402c5a7525bc86b5dac05c9"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️ فشل في جلب تفاصيل الدورة. رمز الحالة: {response.status_code}, الرد: {response.text}")
        return None

def get_unit_classes(course_id, unit_id, user_id=None):
    """
    إرسال طلب GET للحصول على تفاصيل الوحدة باستخدام course_id و unit_id.
    """
    if user_id in user_tokens:
        headers["Authorization"] = f"Bearer {user_tokens[user_id]}"
    url = f"{BASE_URL}/unit-classes-desktop"
    params = {
        "course_id": course_id,
        "unit_id": unit_id,
        "uuid": "b0e46b36624bfce7d96ec60fe4b30815e2477fa0f402c5a7525bc86b5dac05c9"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️ فشل في جلب تفاصيل الوحدة. رمز الحالة: {response.status_code}, الرد: {response.text}")
        return None

async def extract_all_videos(client, message, course_id, units, user_id=None):
    """
    استخراج جميع روابط الفيديو من جميع الوحدات وإرسالها بشكل متدرج.
    """
    await message.reply_text("🎥 جاري استخراج روابط الفيديو من جميع الوحدات...")

    for unit in units:
        unit_id = unit['id']
        unit_name = unit['name']
        await message.reply_text(f"🎬 **الوحدة:** {unit_name}")

        unit_classes = get_unit_classes(course_id, unit_id, user_id)
        if unit_classes and 'data' in unit_classes:
            for cls in unit_classes['data']:
                class_name = cls['name']
                video_url = cls.get('recording_url', 'لا يوجد رابط متاح')
                
                # إرسال كل فصل مع رابط الفيديو بشكل منفصل
                await message.reply_text(
                    f"📚 **الفصل:** {class_name}\n"
                    f"🔗 **رابط الفيديو:** {video_url}"
                )
        else:
            await message.reply_text("❌ لم يتم العثور على حصص أو فشل في جلب البيانات.")

    await message.reply_text("✅ تم استخراج جميع روابط الفيديو بنجاح.")

# بدء البوت مع الأزرار الإنلاين
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id
    
    # التحقق من وجود الرمز
    if user_id not in user_tokens:
        await message.reply_text("🔑 يرجى تعيين رمز الـ Authorization أولاً باستخدام الزر أدناه.")
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔑 تعيين الرمز", callback_data="set_token")]]
        )
    else:
        # إذا كان الرمز موجودًا، عرض جميع الأزرار
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔍 بحث عن دورة", callback_data="search")],
                [InlineKeyboardButton("📂 دوراتي", callback_data="mycourses")],
                [InlineKeyboardButton("📄 تفاصيل الدورة", callback_data="coursedetails")],
                [InlineKeyboardButton("🔑 تعيين الرمز", callback_data="set_token")]
            ]
        )
    
    await message.reply_text(
        "مرحبًا! أنا بوت الدورات التعليمية. اختر أحد الخيارات التالية:",
        reply_markup=keyboard
    )

# معالجة الضغط على الأزرار الإنلاين
@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    await callback_query.answer()  # إغلاق شريط التحميل

    # التحقق من وجود الرمز
    if user_id not in user_tokens and data != "set_token":
        await callback_query.message.reply_text("🔑 يرجى تعيين رمز الـ Authorization أولاً باستخدام الزر أدناه.")
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔑 تعيين الرمز", callback_data="set_token")]]
        )
        await callback_query.message.reply_text(
            "اختر أحد الخيارات التالية:",
            reply_markup=keyboard
        )
        return

    if data == "search":
        user_state[user_id] = "search"  # تحديث حالة المستخدم
        await callback_query.message.reply_text("🔍 الرجاء إدخال نص للبحث:")
    elif data == "mycourses":
        try:
            my_courses_url = "https://admin.joacademy.net/api/v2/courses/user"
            params = {"page": 1, "per_page": 12, "status": "true", "visiable": "true"}
            result = fetch_courses(my_courses_url, params, user_id)
            for part in split_text(result):
                await callback_query.message.reply_text(part)
        except Exception as e:
            await callback_query.message.reply_text(f"❌ حدث خطأ أثناء عرض الدورات: {str(e)}")
    elif data == "coursedetails":
        user_state[user_id] = "coursedetails"  # تحديث حالة المستخدم
        await callback_query.message.reply_text("📄 الرجاء إدخال رقم الدورة:")
    elif data == "set_token":
        user_state[user_id] = "set_token"  # تحديث حالة المستخدم
        await callback_query.message.reply_text("🔑 الرجاء إدخال رمز الـ Authorization الخاص بك:")

# معالجة الرسائل النصية بناءً على حالة المستخدم
@app.on_message(filters.text & ~filters.command("start"))
async def handle_text_message(client, message: Message):
    user_id = message.from_user.id
    if user_id in user_state:
        state = user_state[user_id]
        if state == "search":
            search_query = message.text
            search_url = "https://admin.joacademy.net/api/v2/courses/user"
            params = {"page": 1, "per_page": 12, "status": "true", "search": search_query}
            result = fetch_courses(search_url, params, user_id)
            for part in split_text(result):
                await message.reply_text(part)
            del user_state[user_id]  # حذف حالة المستخدم بعد الانتهاء
        elif state == "coursedetails":
            course_id = message.text
            course_details = get_course_details(course_id, user_id)
            if course_details and 'data' in course_details:
                units = course_details['data'].get('units', [])
                if units:
                    await message.reply_text("✅ تم العثور على الوحدات التالية:")
                    for unit in units:
                        await message.reply_text(
                            f"🆔 **معرّف الوحدة:** {unit['id']}\n"
                            f"📌 **اسم الوحدة:** {unit['name']}"
                        )
                    
                    # استخراج روابط جميع الوحدات تلقائيًا وإرسالها بشكل متدرج
                    await extract_all_videos(client, message, course_id, units, user_id)
                else:
                    await message.reply_text("❌ لا توجد وحدات في هذه الدورة.")
            else:
                await message.reply_text("❌ تعذر جلب تفاصيل الدورة.")
            del user_state[user_id]  # حذف حالة المستخدم بعد الانتهاء
        elif state == "set_token":
            user_tokens[user_id] = message.text  # تخزين الرمز
            await message.reply_text("✅ تم تعيين الرمز بنجاح!")
            del user_state[user_id]  # حذف حالة المستخدم بعد الانتهاء

# إظهار رسالة عند تشغيل البوت
print("✅ تم تشغيل البوت بنجاح!")

# تشغيل البوت
app.run()