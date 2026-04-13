from services.controller import Controller
from utils.logger import logger

if __name__ == "__main__":
    logger.info("BragerReportingTool v.1.6 app started.")
    Controller().execute()
    logger.info("BragerReportingTool app finished.")
