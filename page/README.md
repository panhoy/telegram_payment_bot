# Telegram Payment Bot Setup

## Requirements

Create a `requirements.txt` file:

```txt
python-telegram-bot==20.7
qrcode[pil]==7.4.2
pillow==10.1.0
```

## Setup Instructions

### 1. Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name for your bot
4. Choose a username (must end with 'bot')
5. Copy the bot token you receive

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Bot

1. Open the Python file
2. Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token
3. Save the file

### 4. Run the Bot

```bash
python telegram_bot.py
```

## How It Works

### User Flow:
1. **Start**: User sends `/start` command
2. **USDT ID**: User sends their USDT ID
3. **Amount Selection**: Bot shows buttons ($3, $5, $10, $15)
4. **QR Code**: Bot generates and sends QR code for selected amount
5. **Payment Proof**: User sends screenshot of payment
6. **Confirmation**: Bot sends "Thank you" message

### Features:
- ✅ Interactive payment buttons
- ✅ QR code generation for each amount
- ✅ Screenshot handling
- ✅ User session management
- ✅ Back navigation
- ✅ Error handling

## Bot Commands

- `/start` - Start the bot and show welcome message

## File Structure

```
telegram_payment_bot/
├── telegram_bot.py          # Main bot file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Customization Options

### 1. Change Payment Amounts
Edit the keyboard buttons in `handle_usdt_id()` function:

```python
keyboard = [
    [
        InlineKeyboardButton("💰 $2", callback_data=f"payment_2_{usdt_id}"),
        InlineKeyboardButton("💰 $7", callback_data=f"payment_7_{usdt_id}")
    ],
    # Add more buttons as needed
]
```

### 2. Customize QR Code Content
Modify the `payment_data` in `handle_payment_button()`:

```python
payment_data = f"Custom payment info\nAmount: ${amount}\nWallet: {usdt_id}"
```

### 3. Add Database Storage
Replace the `user_data` dictionary with a proper database:

```python
import sqlite3
# Add database operations instead of using user_data dict
```

### 4. Add Admin Notifications
Send payment notifications to admin:

```python
ADMIN_CHAT_ID = "your_admin_chat_id"

await context.bot.send_message(
    chat_id=ADMIN_CHAT_ID,
    text=f"New payment: ${amount} from user {user_id}"
)
```

## Security Notes

- ⚠️ This bot stores data in memory (resets on restart)
- ⚠️ For production, use a database
- ⚠️ Add payment verification logic
- ⚠️ Implement proper error handling
- ⚠️ Add rate limiting to prevent spam

## Testing

1. Start your bot
2. Send `/start` to your bot
3. Send any text as USDT ID
4. Click payment buttons
5. Send any photo as payment proof
6. Verify "Thank you" message appears

## Troubleshooting

### Common Issues:

1. **Bot not responding**: Check if bot token is correct
2. **QR code not generating**: Install PIL/Pillow properly
3. **Buttons not working**: Verify callback data format
4. **Photos not processed**: Check photo handler registration

### Debug Mode:
Add this to enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
```