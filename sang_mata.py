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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👁️ <b>Sang Mata</b>\n\n"
        "✅ <b>Status: AKTIF</b>\n"
        "Bot siap memantau perubahan nama & username.\n\n"
        "📝 Kirim pesan apa saja untuk mulai dilacak!"
    )
    await update.message.reply_text(msg, parse_mode="HTML")

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
            alert = (
                f"👁️ <b>Sang Mata Melihat!</b>\n\n"
                f"User: <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
                + "\n".join(changes)
            )
            await context.bot.send_message(chat_id=admin_id, text=alert, parse_mode="HTML")
            users_db[user_id] = current
            save_data(users_db)
        except Exception as e:
            print("Error:", e)

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ Token tidak ditemukan!")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.ALL, track_user))

    # Jalankan sebagai webhook di Render
    port = int(os.environ.get("PORT", 8000))
    webhook_url = os.getenv("RENDER_EXTERNAL_URL")
    
    if webhook_url:
        # Render otomatis setel RENDER_EXTERNAL_URL
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=f"{webhook_url}/{token}"
        )
    else:
        # Untuk testing lokal
        app.run_polling()

if __name__ == "__main__":
    main()
