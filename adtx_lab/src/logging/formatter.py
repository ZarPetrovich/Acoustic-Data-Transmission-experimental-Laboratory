import logging
import colorama

class CustomFormatter(logging.Formatter):
    """A custom log formatter that adds color using colorama."""

    # Use colorama's constants for readability and reliability
    # Note: Using Fore.CYAN for INFO as it's often more visible than grey on dark terminals
    grey = colorama.Fore.CYAN
    green = colorama.Fore.GREEN
    yellow = colorama.Fore.YELLOW
    red = colorama.Fore.RED
    bold_red = colorama.Style.BRIGHT + colorama.Fore.RED
    reset = colorama.Style.RESET_ALL

    # Define the base format string
    base_format = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    # Create a dictionary mapping log levels to formatted strings
    FORMATS = {
        logging.DEBUG: grey + base_format + reset,
        logging.INFO: green + base_format + reset,
        logging.WARNING: yellow + base_format + reset,
        logging.ERROR: red + base_format + reset,
        logging.CRITICAL: bold_red + base_format + reset
    }

    def format(self, record):
        """Overrides the default format method to apply the correct color."""
        # Find the correct format string for the record's level
        log_fmt = self.FORMATS.get(record.levelno)

        # Use the parent class's formatter with the chosen format string
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)