from argparse import ArgumentParser
import logging
from logging.handlers import RotatingFileHandler

from constants import (
    BASE_DIR, DATE_FORMAT, ENCODING,
    LOG_FORMAT, OutputTypeChoices
    )


def configure_argument_parser(available_modes):
    parser = ArgumentParser(
        description='Парсер документации Python'
        )
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
        )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
        )
    parser.add_argument(
        '-o', '--output',
        choices=tuple(
            o_type.value for o_type in OutputTypeChoices
            ),
        help='Дополнительные способы вывода данных'
        )
    return parser


def configure_logging():
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6,
        backupCount=5, encoding=ENCODING
        )
    logging.basicConfig(
        datefmt=DATE_FORMAT, format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(
            rotating_handler, logging.StreamHandler()
            )
        )
