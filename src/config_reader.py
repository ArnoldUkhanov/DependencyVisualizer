"""
Модуль для чтения конфигурации из CSV файла
"""

import csv
import os


class ConfigReader:
    def __init__(self, config_path):
        self.config_path = config_path

    def load_config(self):
        """Загрузка конфигурации из CSV файла"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Конфигурационный файл {self.config_path} не найден")

        config = {}

        print(f"Чтение конфигурации из {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8-sig') as file:  # ИЗМЕНИЛИ кодировку на utf-8-sig
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                print(f"Строка {i}: {row}")

                # Обработка параметров с очисткой и проверкой наличия ключей
                row_clean = {k.strip('\ufeff'): v for k, v in row.items()}  # Удаляем BOM из ключей

                # Используем оба варианта ключей на случай проблем
                package_name = row_clean.get('PackageName') or row_clean.get('\ufeffPackageName', '')

                config['package_name'] = package_name.strip()
                config['repository_url'] = row_clean.get('RepositoryUrl', '').strip()
                config['is_test_mode'] = row_clean.get('IsTestMode', '').strip().lower() == 'true'
                config['test_repository_path'] = row_clean.get('TestRepositoryPath', '').strip()
                config['package_version'] = row_clean.get('PackageVersion', '').strip()

                max_depth_str = row_clean.get('MaxDepth', '').strip()
                config['max_depth'] = int(max_depth_str) if max_depth_str else 3

                config['output_image_file'] = row_clean.get('OutputImageFileName', '').strip()
                config['show_ascii_tree'] = row_clean.get('ShowAsciiTree', '').strip().lower() == 'true'
                config['filter_substring'] = row_clean.get('FilterSubstring', '').strip()

        print(f"Прочитанная конфигурация: {config}")

        # Валидация
        if not config['package_name']:
            raise ValueError("Имя пакета не указано в конфигурации")

        return config