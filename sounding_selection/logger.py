import logging
import sys

output_file_handler = logging.FileHandler('sounding_selection_log', mode='w')
stdout_handler = logging.StreamHandler(sys.stdout)

log = logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s :: %(levelname)-5s :: %(message)s",
                    handlers=[output_file_handler, stdout_handler])
