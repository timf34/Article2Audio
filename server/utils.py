import logging
from urllib.parse import urlparse


def estimate_processing_time(text: str) -> int:
    return int(len(text) * 0.01)  # 0.01 seconds per character


def get_domain(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc


def log_message(message: str) -> None:
    logging.info(message)
