import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

file_storage = {"apps": [], "videos": [], "images": [], "others": []}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 Apps", callback_data="show_apps"),
         InlineKeyboardButton("🎬 Videos", callback_data="show_videos")],
        [InlineKeyboardButton("🖼️ Images", callback_data="show_images"),
         InlineKeyboardButton("📁 Others", callback_data="show_others")],
    ]
    await update.message.reply_text(
        "🤖 *স্বাগতম!*\nনিচের বাটন থেকে ফাইল ডাউনলোড করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_map = {
        "show_apps": ("apps", "📱 Apps"),
        "show_videos": ("videos", "🎬 Videos"),
        "show_images": ("images", "🖼️ Images"),
        "show_others": ("others", "📁 Others"),
    }
    if query.data in category_map:
        cat_key, cat_name = category_map[query.data]
        files = file_storage[cat_key]
        if not files:
            await query.edit_message_text(f"{cat_name} তে এখনো কোনো ফাইল নেই।")
            return
        await query.edit_message_text(f"{cat_name} - মোট {len(files)}টি ফাইল:")
        for file_info in files:
            await context.bot.copy_message(
                chat_id=query.message.chat_id,
                from_chat_id=file_info["chat_id"],
                message_id=file_info["message_id"],
                caption=file_info.get("caption", "")
            )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ শুধু অ্যাডমিন ফাইল আপলোড করতে পারবেন।")
        return
    msg = update.message
    file_info = {"chat_id": msg.chat_id, "message_id": msg.message_id, "caption": msg.caption or ""}
    if msg.document:
        file_name = msg.document.file_name or ""
        if file_name.endswith(".apk"):
            file_storage["apps"].append(file_info)
            await msg.reply_text("✅ App সেকশনে যোগ হয়েছে!")
        else:
            file_storage["others"].append(file_info)
            await msg.reply_text("✅ Others সেকশনে যোগ হয়েছে!")
    elif msg.video:
        file_storage["videos"].append(file_info)
        await msg.reply_text("✅ Video সেকশনে যোগ হয়েছে!")
    elif msg.photo:
        file_storage["images"].append(file_info)
        await msg.reply_text("✅ Image সেকশনে যোগ হয়েছে!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.PHOTO, handle_file))
    print("বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
