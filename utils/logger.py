import os
import logging
import sys
from utils.paths import get_user_data_dir

def SetupLogger():
    # Define log directory
    log_dir = os.path.join(get_user_data_dir(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "gesturex.log")
    
    # Create main logger
    logger = logging.getLogger("GestureX")
    logger.setLevel(logging.DEBUG)
    
    # Check if handlers already exist to avoid duplicate logs
    if not logger.handlers:
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    logger.info("Logging initialized.")
    return logger
