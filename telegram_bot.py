import logging
import qrcode
import io
import base64
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token - Replace with your actual bot token
BOT_TOKEN = "7836377853:AAHvTlYlqK-TbvbwVRzvG5oPotaFdNntn3A"

# Photo URL for start command - Replace with your actual photo URL
START_PHOTO_URL = "https://i.pinimg.com/736x/dd/cb/03/ddcb0341971d4836da7d12c399149675.jpg"

# Payment amount specific photo URLs
PAYMENT_PHOTOS = {
    "3": "https://i.pinimg.com/736x/37/62/f1/3762f112c8f2179a2663e997c1419619.jpg",
    "5": "https://i.pinimg.com/736x/14/70/c4/1470c436182cf4c4142bfa343b45c844.jpg",
    "10": "https://i.pinimg.com/736x/6a/3d/98/6a3d98a08550c0d823623279e458411a.jpg",
    "15": "https://i.pinimg.com/736x/b5/96/76/b5967687b83a2bc141c8735dc232ca5e.jpg"
}

# Store user data temporarily (in production, use a database)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler - sends photo and download button"""
    
    # Create download button
    keyboard = [
        [InlineKeyboardButton("📱 Download UDID Profile", url="https://udid.tech/download-profile")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Send photo with download button
        await update.message.reply_photo(
            photo=START_PHOTO_URL,
            caption="🎉 **Welcome to Payment Bot!** 🎉\n\n"
                   "📱 First, download your UDID profile using the button below\n"
                   "📧 Then send me your UDID to start payment process\n\n"
                   "💡 **How to get UDID:**\n"
                   "1. Click the download button\n"
                   "2. Install the profile on your device\n"
                   "3. Copy your UDID and send it here",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        # Fallback if photo fails to load
        await update.message.reply_text(
            "🎉 **Welcome to Payment Bot!** 🎉\n\n"
            "📱 First, download your UDID profile using the button below\n"
            "📧 Then send me your UDID to start payment process\n\n"
            "💡 **How to get UDID:**\n"
            "1. Click the download button\n"
            "2. Install the profile on your device\n"
            "3. Copy your UDID and send it here",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        logger.warning(f"Failed to send photo: {e}")

async def handle_udid_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle UDID input and show payment options"""
    user_id = update.effective_user.id
    udid = update.message.text.strip()
    
    # Basic UDID validation (UDIDs are typically 40 characters long)
    if len(udid) < 20:
        await update.message.reply_text(
            "❌ **Invalid UDID Format**\n\n"
            "Please make sure you copied the complete UDID.\n"
            "UDID should be a long string of letters and numbers.\n\n"
            "Use /start to get the download link again.",
            parse_mode='Markdown'
        )
        return
    
    # Store UDID
    user_data[user_id] = {'udid': udid}
    
    # Create payment amount buttons
    keyboard = [
        [
            InlineKeyboardButton("💰 $3", callback_data=f"payment_3_{udid}"),
            InlineKeyboardButton("💰 $5", callback_data=f"payment_5_{udid}")
        ],
        [
            InlineKeyboardButton("💰 $10", callback_data=f"payment_10_{udid}"),
            InlineKeyboardButton("💰 $15", callback_data=f"payment_15_{udid}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ **UDID Received Successfully!**\n\n"
        f"📱 UDID: `{udid[:20]}...`\n\n"
        f"💳 **Select Payment Amount:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def generate_qr_code(data: str) -> io.BytesIO:
    """Generate QR code for payment data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create QR code image

async def handle_payment_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle payment button clicks"""
    query = update.callback_query
    await query.answer()
    
    # Parse callback data
    callback_data = query.data
    parts = callback_data.split('_')
    action = parts[0]  # 'payment'
    amount = parts[1]  # '3', '5', '10', '15'
    udid = '_'.join(parts[2:])  # remaining parts as UDID
    
    if action == 'payment':
        # Get the specific photo URL for this payment amount
        payment_photo_url = PAYMENT_PHOTOS.get(amount, START_PHOTO_URL)
        
        # Create payment data for QR code
        payment_data = f"UDID Payment Request\nAmount: ${amount} USD\nUDID: {udid}\nPayment ID: PAY_{amount}_{udid[:8]}\nScan to complete payment"
        
        # Generate QR code
        qr_buffer = generate_qr_code(payment_data)
        
        # Create back button
        keyboard = [[InlineKeyboardButton("🔙 Back to Payment Options", callback_data=f"back_{udid}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            # Send the specific payment photo first
            await query.message.reply_photo(
                photo=payment_photo_url,
                caption=f"💳 **Payment Information - ${amount} USD**\n\n"
                       f"📱 **UDID:** `{udid[:20]}...`\n"
                       f"🆔 **Payment ID:** PAY_{amount}_{udid[:8]}\n\n"
                       f"📋 **Payment QR Code will be sent next**",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            # Fallback if photos fail to load
            await query.message.reply_text(
                f"💳 **Payment QR Code Generated**\n\n"
                f"💰 **Amount:** ${amount} USD\n"
                f"📱 **UDID:** `{udid[:20]}...`\n"
                f"🆔 **Payment ID:** PAY_{amount}_{udid[:8]}\n\n"
                f"📋 **Instructions:**\n"
                f"1. Complete the ${amount} payment\n"
                f"2. Take a screenshot of payment confirmation\n"
                f"3. Send the screenshot back to this bot\n\n"
                f"⏰ Payment is valid for 30 minutes",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.warning(f"Failed to send payment photos: {e}")
        
        # Store current payment info
        user_id = query.from_user.id
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['pending_amount'] = amount
        user_data[user_id]['udid'] = udid
        user_data[user_id]['payment_id'] = f"PAY_{amount}_{udid[:8]}"
    
    elif action == 'back':
        # Show payment buttons again
        keyboard = [
            [
                InlineKeyboardButton("💰 $3", callback_data=f"payment_3_{udid}"),
                InlineKeyboardButton("💰 $5", callback_data=f"payment_5_{udid}")
            ],
            [
                InlineKeyboardButton("💰 $10", callback_data=f"payment_10_{udid}"),
                InlineKeyboardButton("💰 $15", callback_data=f"payment_15_{udid}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ **UDID:** `{udid[:20]}...`\n\n"
            f"💳 **Select Payment Amount:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_payment_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle payment screenshot submission"""
    user_id = update.effective_user.id
    
    if user_id in user_data and 'pending_amount' in user_data[user_id]:
        amount = user_data[user_id]['pending_amount']
        udid = user_data[user_id]['udid']
        payment_id = user_data[user_id].get('payment_id', 'N/A')
        
        # Send thank you confirmation
        await update.message.reply_text(
            f"🎉 **THX YOU!** 🎉\n\n"
            f"✅ **Payment Screenshot Received**\n"
            f"💰 **Amount:** ${amount} USD\n"
            f"📱 **UDID:** `{udid[:20]}...`\n"
            f"🆔 **Payment ID:** {payment_id}\n\n"
            f"🔄 **Status:** Processing...\n"
            f"⏰ **Processing Time:** 5-10 minutes\n\n"
            f"📧 You will receive confirmation once payment is verified.\n"
            f"Thank you for your business! 🙏\n\n"
            f"💡 Use /start for new payments",
            parse_mode='Markdown'
        )
        
        # Clear pending payment
        if 'pending_amount' in user_data[user_id]:
            del user_data[user_id]['pending_amount']
        if 'payment_id' in user_data[user_id]:
            del user_data[user_id]['payment_id']
            
        # Log payment for admin tracking
        logger.info(f"Payment received: User {user_id}, Amount ${amount}, UDID {udid[:20]}..., Payment ID {payment_id}")
        
        # Optional: Send notification to admin (uncomment and add admin chat ID)
        # ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"
        # try:
        #     await context.bot.send_message(
        #         chat_id=ADMIN_CHAT_ID,
        #         text=f"💰 New Payment Received!\n"
        #              f"User: {update.effective_user.username or update.effective_user.first_name}\n"
        #              f"Amount: ${amount}\n"
        #              f"UDID: {udid[:20]}...\n"
        #              f"Payment ID: {payment_id}"
        #     )
        # except Exception as e:
        #     logger.warning(f"Failed to send admin notification: {e}")
        
    else:
        await update.message.reply_text(
            "❌ **No Pending Payment Found**\n\n"
            "Please start a new payment process:\n"
            "1. Use /start command\n"
            "2. Send your UDID\n"
            "3. Select payment amount\n"
            "4. Then send payment screenshot",
            parse_mode='Markdown'
        )

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle other text messages as potential UDID"""
    message_text = update.message.text.strip()
    
    # Skip if it's a command
    if message_text.startswith('/'):
        return
    
    # Check if user already has a pending payment
    user_id = update.effective_user.id
    if user_id in user_data and 'pending_amount' in user_data[user_id]:
        await update.message.reply_text(
            "⏳ **Payment In Progress**\n\n"
            "You have a pending payment. Please:\n"
            "📸 Send your payment screenshot, or\n"
            "🔄 Use /start to begin a new session",
            parse_mode='Markdown'
        )
        return
    
    # Treat as UDID input
    await handle_udid_input(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    await update.message.reply_text(
        "🤖 **Payment Bot Help** 🤖\n\n"
        "**Commands:**\n"
        "• /start - Start new payment session\n"
        "• /help - Show this help message\n\n"
        "**How to use:**\n"
        "1. Send /start to begin\n"
        "2. Download UDID profile\n"
        "3. Send your UDID to bot\n"
        "4. Select payment amount ($3, $5, $10, $15)\n"
        "5. View payment information and scan QR code\n"
        "6. Complete payment and send screenshot as proof\n"
        "7. Receive confirmation\n\n"
        "Need help? Contact support.",
        parse_mode='Markdown'
    )

def main() -> None:
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_payment_button))
    application.add_handler(MessageHandler(filters.PHOTO, handle_payment_screenshot))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other_messages))
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    print("🤖 Starting Telegram UDID Payment Bot...")
    print("📋 Setup checklist:")
    print("   ✅ Replace BOT_TOKEN with your actual bot token")
    print("   ✅ Replace START_PHOTO_URL with your photo URL")
    print("   ✅ Payment-specific photos configured:")
    print("      💰 $3  -> Custom photo")
    print("      💰 $5  -> Custom photo") 
    print("      💰 $10 -> Custom photo")
    print("      💰 $15 -> Custom photo")
    print("   ✅ Optionally add ADMIN_CHAT_ID for notifications")
    print("🚀 Bot is ready to start!")
    main()