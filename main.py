from services.controller import Controller
from utils.logger import logger

if __name__ == "__main__":
    logger.info("BragerReportingTool app started.")
    Controller().execute()
    logger.info("BragerReportingTool app finished.")
