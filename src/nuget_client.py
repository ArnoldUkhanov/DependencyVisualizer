"""
Модуль для работы с NuGet API
"""

import requests
import json
import re

class NuGetClient:
    def __init__(self, config):
        self.config = config
        self.base_url = "https://api.nuget.org/v3/registration5-gz-semver2"
        self.session = requests.Session()

    def get_dependencies_from_nuget(self):
        """Получение зависимостей из NuGet API"""
        package_name = self.config['package_name']
        version = self.config['package_version']

        # Формируем URL для получения информации о пакете
        url = f"{self.base_url}/{package_name.lower()}/{version}.json"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            data = response.json()
            return self._extract_dependencies(data)

        except requests.RequestException as e:
            raise Exception(f"Ошибка при запросе к NuGet API: {e}")

    def _extract_dependencies(self, data):
        """Извлечение зависимостей из JSON ответа"""
        dependencies = []

        try:
            # NuGet API имеет сложную структуру, ищем зависимости
            items = data.get('items', [])
            for item in items:
                items_inner = item.get('items', [])
                for inner_item in items_inner:
                    catalog_entry = inner_item.get('catalogEntry', {})
                    dependency_groups = catalog_entry.get('dependencyGroups', [])

                    for group in dependency_groups:
                        deps = group.get('dependencies', [])
                        for dep in deps:
                            dep_id = dep.get('id')
                            if dep_id and self._should_include_dependency(dep_id):
                                dependencies.append(dep_id)

            # Если не нашли в обычной структуре, пробуем альтернативный путь
            if not dependencies and 'catalogEntry' in data:
                catalog_entry = data['catalogEntry']
                dependency_groups = catalog_entry.get('dependencyGroups', [])
                for group in dependency_groups:
                    deps = group.get('dependencies', [])
                    for dep in deps:
                        dep_id = dep.get('id')
                        if dep_id and self._should_include_dependency(dep_id):
                            dependencies.append(dep_id)

            return list(set(dependencies))  # Убираем дубликаты

        except Exception as e:
            raise Exception(f"Ошибка при разборе ответа NuGet: {e}")

    def _should_include_dependency(self, dependency_name):
        """Проверка, нужно ли включать зависимость (фильтрация)"""
        filter_substring = self.config['filter_substring']
        if filter_substring and filter_substring in dependency_name:
            return False
        return True

    def get_dependencies_from_test_file(self):
        """Получение зависимостей из тестового файла (для режима тестирования)"""
        test_file_path = self.config['test_repository_path']
        if not test_file_path:
            raise ValueError("Путь к тестовому файлу не указан")

        try:
            with open(test_file_path, 'r', encoding='utf-8-sig') as file:
                content = file.read().strip()

            # Парсинг тестового файла с зависимостями
            dependencies = []
            current_package = self.config['package_name']

            instructions = [inst.strip() for inst in content.split(';') if inst.strip()]

            for instruction in instructions:
                if '->' in instruction:
                    parts = instruction.split('->')
                    if len(parts) == 2:
                        package = parts[0].strip()
                        deps_str = parts[1].strip()

                        if package == current_package:
                            deps = [dep.strip() for dep in deps_str.split(',') if dep.strip()]
                            dependencies.extend(deps)

            return [dep for dep in dependencies if self._should_include_dependency(dep)]

        except Exception as e:
            raise Exception(f"Ошибка при чтении тестового файла: {e}")

    def get_package_dependencies(self, package_name, version=None):
        """Универсальный метод для получения зависимостей пакета"""
        if self.config['is_test_mode']:
            # В тестовом режиме читаем зависимости из тестового файла
            return self._get_dependencies_from_test_file_for_package(package_name)
        else:
            # Режим работы с реальным NuGet API
            original_name = self.config['package_name']
            original_version = self.config['package_version']

            self.config['package_name'] = package_name
            if version:
                self.config['package_version'] = version

            try:
                return self.get_dependencies_from_nuget()
            finally:
                self.config['package_name'] = original_name
                self.config['package_version'] = original_version

    def _get_dependencies_from_test_file_for_package(self, package_name):
        """Получение зависимостей для конкретного пакета из тестового файла"""
        test_file_path = self.config['test_repository_path']
        if not test_file_path:
            return []

        try:
            with open(test_file_path, 'r', encoding='utf-8-sig') as file:
                content = file.read().strip()

            dependencies = []
            instructions = [inst.strip() for inst in content.split(';') if inst.strip()]

            for instruction in instructions:
                if '->' in instruction:
                    parts = instruction.split('->')
                    if len(parts) == 2:
                        current_package = parts[0].strip()
                        deps_str = parts[1].strip()

                        if current_package == package_name:
                            deps = [dep.strip() for dep in deps_str.split(',') if dep.strip()]
                            dependencies.extend(deps)

            return [dep for dep in dependencies if self._should_include_dependency(dep)]

        except Exception as e:
            print(f"Ошибка при чтении тестового файла для пакета {package_name}: {e}")
            return []