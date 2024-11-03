import logging

def setup_logging(debug: bool):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f'running in {log_level} level')
