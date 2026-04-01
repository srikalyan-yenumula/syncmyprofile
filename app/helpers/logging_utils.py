import datetime
import logging
import os
import sys

LOGS_DIR = os.path.join(os.getcwd(), "logs")
DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"
LOGGER = logging.getLogger(__name__)


def configure_console_output():
    """Makes console writes resilient on Windows terminals with limited encodings."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="backslashreplace")
            except Exception:
                pass


def configure_runtime_logging(level: str | None = None):
    """Configures application logging once the environment has been loaded."""
    configure_console_output()

    resolved_level_name = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    resolved_level = getattr(logging, resolved_level_name, logging.INFO)
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        logging.basicConfig(level=resolved_level, format=DEFAULT_LOG_FORMAT)
    else:
        root_logger.setLevel(resolved_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def safe_log_text(value, max_length: int | None = None) -> str:
    """Escapes text so log lines remain ASCII-safe on default Windows consoles."""
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if max_length is not None and len(text) > max_length:
        text = f"{text[:max_length]}... [truncated]"
    return text.encode("ascii", "backslashreplace").decode("ascii")


def ensure_logs_dir():
    """Ensures the logs directory exists."""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)


def log_analysis_details(data):
    """
    Logs the analysis details to a file.

    Args:
        data (dict): A dictionary containing all the data to log.
                     Expected keys: 'timestamp', 'type', 'inputs', 'prompts', 'final_prompt', 'output'
    """
    ensure_logs_dir()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_type = data.get("type", "unknown")
    filename = f"analysis_log_{analysis_type}_{timestamp}.txt"
    filepath = os.path.join(LOGS_DIR, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"=== ANALYSIS LOG - {timestamp} ===\n")
            f.write(f"Type: {analysis_type}\n\n")

            f.write("=== INPUTS ===\n")
            inputs = data.get("inputs", {})
            for key, value in inputs.items():
                f.write(f"{key}:\n{value}\n\n")

            f.write("=== SELECTED PROMPTS ===\n")
            prompts = data.get("prompts", {})
            for key, value in prompts.items():
                f.write(f"{key}:\n{value}\n\n")

            f.write("=== FINAL CONSTRUCTED PROMPT ===\n")
            f.write(f"{data.get('final_prompt', '')}\n\n")

            f.write("=== AI OUTPUT ===\n")
            f.write(f"{data.get('output', '')}\n\n")

        LOGGER.info("Analysis details logged to %s", safe_log_text(filepath))
        return filepath
    except Exception as e:
        LOGGER.error("Failed to log analysis details: %s", safe_log_text(e))
        return None
