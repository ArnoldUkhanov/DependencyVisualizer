#!/usr/bin/env python3
"""
Главный модуль для варианта №26
Визуализация графа зависимостей для NuGet пакетов
"""

import os
import sys
from src.config_reader import ConfigReader
from src.nuget_client import NuGetClient
from src.graph_builder import GraphBuilder
from src.visualizer import Visualizer
from src.utils import setup_logging


def main():
    """Основная функция программы"""
    setup_logging()

    try:
        # Этап 1: Чтение конфигурации
        print("=== ЭТАП 1: Чтение конфигурации ===")
        config_reader = ConfigReader('config.csv')
        config = config_reader.load_config()

        # Вывод параметров (требование этапа 1)
        print("\nНастроенные параметры:")
        for key, value in config.items():
            print(f"  {key}: {value}")

        # Этап 2: Сбор данных о зависимостях
        print("\n=== ЭТАП 2: Сбор данных о зависимостях ===")
        nuget_client = NuGetClient(config)

        if config['is_test_mode']:
            print("Режим тестирования: использование тестового репозитория")
            dependencies = nuget_client.get_dependencies_from_test_file()
        else:
            print(f"Получение зависимостей для пакета {config['package_name']} версии {config['package_version']}")
            dependencies = nuget_client.get_dependencies_from_nuget()

        print("Прямые зависимости:")
        for dep in dependencies:
            print(f"  - {dep}")

        # Этап 3: Построение графа зависимостей
        print("\n=== ЭТАП 3: Построение графа зависимостей ===")
        graph_builder = GraphBuilder(nuget_client, config)
        graph = graph_builder.build_dependency_graph()

        print(f"Построен граф с {len(graph.nodes)} узлами и {len(graph.edges)} связями")

        # Этап 4: Дополнительные операции
        print("\n=== ЭТАП 4: Дополнительные операции ===")
        load_order = graph_builder.get_load_order()
        print("Порядок загрузки зависимостей:")
        for i, package in enumerate(load_order, 1):
            print(f"  {i}. {package}")

        # Этап 5: Визуализация
        print("\n=== ЭТАП 5: Визуализация ===")
        visualizer = Visualizer(config)

        # PlantUML визуализация
        plantuml_code = visualizer.generate_plantuml(graph)
        visualizer.save_plantuml_image(plantuml_code)

        # ASCII-дерево
        if config['show_ascii_tree']:
            print("\nASCII-дерево зависимостей:")
            ascii_tree = visualizer.generate_ascii_tree(graph)
            print(ascii_tree)

        print("\n✅ Все этапы выполнены успешно!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()