import logging
import json
import random
import os
import tempfile
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import BadRequest

# Bot token and channel username
BOT_TOKEN = "7993719241:AAE6ItGn4ciaJv8c_Hjwlt01lTqhuqj9j8Q"  # Replace with your bot token
CHANNEL_USERNAME = "@megasaruku0"  # Replace with your channel username

# File to save and load user data
DATA_FILE = "users_data.json"

# Initialize bot and set up logging
bot = Bot(token=BOT_TOKEN)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined list of items (url and image pairs)
ITEMS = [
    {"url": "https://xpshort.com/XOVwc", "image": "https://ibb.co/rb0dHzC"},
    {"url": "https://xpshort.com/ZEq6U7", "image": "https://ibb.co/G9w84Sq"},
    {"url": "https://xpshort.com/7Sk6", "image": "https://ibb.co/0CsV3JQ"},
    {"url": "https://xpshort.com/3YozfHw", "image": "https://ibb.co/CpybSMk"},
    {"url": "https://xpshort.com/Fc1B", "image": "https://ibb.co/7NGTRnb"},
    {"url": "https://xpshort.com/KocqkUY", "image": "https://ibb.co/hMWnPWf"},
    {"url": "https://xpshort.com/2Xsk", "image": "https://ibb.co/DbxHSWh"},
    {"url": "https://xpshort.com/oRUh", "image": "https://ibb.co/KsJwPwf"},
    {"url": "https://xpshort.com/E9uC", "image": "https://ibb.co/9tLFYCJ"},
    {"url": "https://xpshort.com/Zufbw", "image": "https://ibb.co/ThNxxwH"},
    {"url": "https://xpshort.com/x4fy33", "image": "https://ibb.co/1MgD33R"},
    {"url": "https://xpshort.com/wyDYGvfa", "image": "https://ibb.co/HVx5vyK"},
    {"url": "https://xpshort.com/VXL59", "image": "https://ibb.co/H7jw0Nz"},
    {"url": "https://xpshort.com/KkGFdy", "image": "https://ibb.co/NYx3qWY"},
    {"url": "https://xpshort.com/FGffFNC", "image": "https://ibb.co/fMK7jPV"},
    {"url": "https://xpshort.com/MZMPf", "image": "https://ibb.co/3cW59W0"},
    {"url": "https://xpshort.com/T7MdpKwp", "image": "https://ibb.co/mHTqkY0"},
    {"url": "https://xpshort.com/0zqS", "image": "https://ibb.co/ch9nCSs"},
    {"url": "https://xpshort.com/mPg0lb", "image": "https://ibb.co/8949FH8"},
]

ACCESS_DENIED_PHOTO = "https://upload.wikimedia.org/wikipedia/en/thumb/6/68/Telegram_access_denied.jpg/800px-Telegram_access_denied.jpg?20200919053248"

# Load user data from file
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save user data to file
def save_data():
    with open(DATA_FILE, "w") as file:
        json.dump(users_data, file)

# Initialize user data
users_data = load_data()

# Check if the user has joined the channel
def check_channel_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

# Start command with referral tracking and storing user's name
def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    referrer_id = context.args[0] if context.args else None

    # Get user's first and last names
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name if update.effective_user.last_name else ""

    if user_id not in users_data:
        users_data[user_id] = {"first_name": first_name, "last_name": last_name, "referrals": 0, "is_vip": False}
        
        # Check if the user was referred
        if referrer_id and referrer_id != user_id and referrer_id in users_data:
            users_data[referrer_id]["referrals"] += 1
            save_data()  # Save after updating referral count

            # Grant VIP status if referrals reach 50
            if users_data[referrer_id]["referrals"] >= 50 and not users_data[referrer_id]["is_vip"]:
                users_data[referrer_id]["is_vip"] = True
                save_data()  # Save VIP status
                bot.send_message(chat_id=int(referrer_id), text="Congratulations! You've earned VIP status!")

    save_data()  # Save new user info

    # Generate and send welcome message or access denied message
    if check_channel_membership(user_id):
        referral_link = f"https://t.me/{bot.username}?start={user_id}"
        welcome_message = f"Welcome to the bot, {first_name} {last_name}! 🎉\n\n" \
                          f"Here are the commands you can use:\n\n" \
                          f"/gen - Get a random item\n" \
                          f"/alive - Check if the bot is running\n" \
                          f"/help - Get help\n" \
                          f"/vip - Access VIP content\n\n" \
                          f"Your referral link: {referral_link}"
        update.message.reply_text(welcome_message)
    else:
        keyboard = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        caption = "Access Denied 🚫\n\nYou must join the channel to use the bot."
        update.message.reply_photo(photo=ACCESS_DENIED_PHOTO, caption=caption, reply_markup=reply_markup)

# Command to generate random item
def gen(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if check_channel_membership(user_id):
        item = random.choice(ITEMS)
        try:
            caption = f"Enjoy mawa...❤️: [Click Here]({item['url']})"
            update.message.reply_photo(photo=item["image"], caption=caption, parse_mode='Markdown')
        except BadRequest as e:
            logger.error(f"Failed to send photo: {e}")
            update.message.reply_text("Oops! There was an issue with sending the photo. Please try again later.")
    else:
        keyboard = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        caption = "Access Denied 🚫\n\nYou must join the channel to use the bot."
        update.message.reply_photo(photo=ACCESS_DENIED_PHOTO, caption=caption, reply_markup=reply_markup)

# Alive command
def alive(update: Update, context: CallbackContext):
    update.message.reply_text("The bot is alive! 😊")

# Help command
def help_command(update: Update, context: CallbackContext):
    help_message = "Here are the commands you can use:\n\n" \
                   "/gen - Get a random item 🎁\n" \
                   "/alive - Check if the bot is running 🏃‍♂️\n" \
                   "/help - Get help ❓\n" \
                   "/vip - Access VIP content 🌟\n" \
                   "/referral - See your referral count 👥"
    update.message.reply_text(help_message)

# VIP command
def vip(update: Update, context: CallbackContext):
    message = (
    "To unlock VIP status, you need to refer 25 members! 🎉\n"
    "\n"
    "What does VIP status give you?\n"
    "- Access to ad-free content\n"
    "- Exclusive links without interruptions\n"
    "\n"
    "If you're interested in a VIP subscription:\n"
    "- Monthly: ₹100\n"
    "- Lifetime: ₹300\n"
    "\n"
    "For more information or assistance, please contact: @Vip_support0bot 📩"
)


    user_id = str(update.effective_user.id)
    if user_id in users_data and users_data[user_id]["is_vip"]:
        update.message.reply_text("Welcome, VIP! Enjoy your exclusive content 🔥")
    else:
        update.message.reply_text(message)
# Command to show referral counts and provide a referral button
def referral(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id in users_data:
        referrals = users_data[user_id]["referrals"]
        referral_link = f"https://t.me/{bot.username}?start={user_id}"  # Unique referral link

        referral_message = f"You have referred {referrals} people. 🎉\n\n" \
                           f"Share your referral link:\n{referral_link}"

        # Create a button to share the referral link
        keyboard = [[InlineKeyboardButton("Refer a Friend", url=f"https://t.me/share/url?url={referral_link}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the message with the button
        update.message.reply_text(referral_message, reply_markup=reply_markup)
    else:
        update.message.reply_text("You have not referred anyone yet. 👀")

# Command for bot owner to view user data
def data(update: Update, context: CallbackContext):
    if update.effective_user.id == 1134468682:  # Replace with your Telegram user ID
        # Create a temporary file to save the user data
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file.write(json.dumps(users_data, indent=4).encode('utf-8'))
            temp_file_path = temp_file.name

        # Send the temporary file to the admin
        with open(temp_file_path, 'rb') as file:
            context.bot.send_document(chat_id=update.effective_user.id, document=file, filename='user_data.json', caption='User Data')

        # Optionally delete the temporary file after sending
        os.remove(temp_file_path)
    else:
        update.message.reply_text("You do not have permission to access this data.")

# Error handler
def error_handler(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    # Set up the updater and dispatcher
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("gen", gen))
    dispatcher.add_handler(CommandHandler("alive", alive))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("vip", vip))
    dispatcher.add_handler(CommandHandler("referral", referral))
    dispatcher.add_handler(CommandHandler("data", data))
    
    # Log all errors
    dispatcher.add_error_handler(error_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
