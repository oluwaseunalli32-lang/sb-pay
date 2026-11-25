import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Sample quiz data (you can replace this with a database or API)
QUIZ = {
    "What is the capital of France?": "Paris",
    "What is 12 × 8?": "96",
    "Who wrote 'Hamlet'?": "Shakespeare",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the EduBot!\n"
        "Use /quiz to get a question, and reply with your answer."
    )

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Pick the first unanswered question (simple example)
    for question, answer in QUIZ.items():
        context.user_data["current_question"] = question
        context.user_data["current_answer"] = answer
        await update.message.reply_text(f"❓ {question}")
        return
    await update.message.reply_text("You've answered all questions! 🎉")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_q = context.user_data.get("current_question")
    correct_a = context.user_data.get("current_answer")

    if not current_q:
        await update.message.reply_text("Use /quiz to start a quiz.")
        return

    user_answer = update.message.text.strip()
    if user_answer.lower() == correct_a.lower():
        await update.message.reply_text("✅ Correct! Well done.")
        # Remove answered question
        QUIZ.pop(current_q, None)
    else:
        await update.message.reply_text(
            f"❌ Not quite. The correct answer is: {correct_a}"
        )

    context.user_data.pop("current_question", None)
    context.user_data.pop("current_answer", None)

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    # Handle plain text messages as answers
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    logger.info("Starting EduBot polling...")
    app.run_polling()  # Long-polling works well in a background worker

if __name__ == "__main__":
    main()
