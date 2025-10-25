import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

DATA_FILE = "/tmp/users_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Handler untuk /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "👁️ <b>Sang Mata</b>\n\n"
        "✅ <b>Status: AKTIF</b>\n"
        "Bot siap memantau perubahan <b>nama</b> dan <b>username</b> Telegram.\n\n"
        "📝 <i>Catatan:</i>\n"
        "• Perubahan hanya terdeteksi saat kamu <b>mengirim pesan</b> ke bot.\n"
        "• Data disimpan sementara (akan reset saat server restart).\n\n"
        "Kirim pesan apa saja untuk mulai dilacak!"
    )
    await update.message.reply_text(welcome_msg, parse_mode="HTML")

# Handler untuk melacak perubahan pengguna
async def track_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    user_id = str(user.id)
    current = {
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or ""
    }

    users_db = load_data()

    if user_id not in users_db:
        users_db[user_id] = current
        save_data(users_db)
        return

    old = users_db[user_id]
    changes = []

    if old["first_name"] != current["first_name"]:
        changes.append(f"Nama: '{old['first_name']}' → '{current['first_name']}'")
    if old["last_name"] != current["last_name"]:
        changes.append(f"Nama belakang: '{old['last_name']}' → '{current['last_name']}'")
    if old["username"] != current["username"]:
        old_un = old["username"] or "(kosong)"
        new_un = current["username"] or "(kosong)"
        changes.append(f"Username: '@{old_un}' → '@{new_un}'")

    if changes:
        try:
            admin_id = int(os.getenv("ADMIN_TELEGRAM_ID"))
            msg = (
                f"👁️ <b>Sang Mata Melihat Perubahan!</b>\n\n"
                f"User: <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
                + "\n".join(changes)
            )
            await context.bot.send_message(chat_id=admin_id, text=msg, parse_mode="HTML")
            users_db[user_id] = current
            save_data(users_db)
        except Exception as e:
            print("Error kirim notifikasi:", e)

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN belum diatur di environment!")
    
    app = Application.builder().token(token).build()
    
    # Daftarkan handler
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.ALL, track_user))
    
    print("✅ Sang Mata aktif dan siap memantau...")
    app.run_polling()

if __name__ == "__main__":
    main()
