"""
Вспомогательные функции
"""

import logging


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def filter_packages(packages, filter_substring):
    """Фильтрация пакетов по подстроке"""
    if not filter_substring:
        return packages

    return [pkg for pkg in packages if filter_substring not in pkg]