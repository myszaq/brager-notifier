from services.controller import Controller
from utils.logger import logger

if __name__ == "__main__":
    logger.info("BragerNotifier app started.")
    Controller().execute()
    logger.info("BragerNotifier app finished.")
