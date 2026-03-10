import logging


def setup_logging(logfile: str = "automation.log") -> None:
    """Configure root logger with file + console handlers."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(logfile),
            logging.StreamHandler(),
        ],
    )
