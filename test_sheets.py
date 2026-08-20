import asyncio
import os
import sys

# Load env vars from appex-adipec-concierge-1.env
from dotenv import load_dotenv
load_dotenv("appex-adipec-concierge-1.env")

# We need to add the bot directory to path to import sheets
sys.path.append(os.path.join(os.getcwd(), "adipec-apex-club-Telegram-Bot"))

from bot.sheets import sheets_lookup_phone

async def main():
    phone = "+7 771 671 34 60"
    print(f"Looking up {phone}...")
    result = await sheets_lookup_phone(phone)
    if result:
        print("Found:", result)
    else:
        print("Not found (returned None)")

if __name__ == "__main__":
    asyncio.run(main())
