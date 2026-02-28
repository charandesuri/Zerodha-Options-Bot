import logging
import os

# Create logs folder
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    print(message)
    logging.info(message)

def log_error(message):
    print("ERROR:", message)
    logging.error(message)