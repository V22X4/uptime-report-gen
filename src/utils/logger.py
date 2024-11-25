import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # File handler
    fh = RotatingFileHandler(
        "logs/app.log", 
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
