import logging
from urllib.parse import urlparse


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing any characters that are not alphanumeric or in (' ', '.', '_')
    """
    return "".join(c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename)


def estimate_processing_time(text: str) -> int:
    # TODO: temp change to account for parallel processing
    return int(len(text) * 0.003)  # 0.01 seconds per character


def get_domain(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc


def log_message(message: str) -> None:
    logging.info(message)
