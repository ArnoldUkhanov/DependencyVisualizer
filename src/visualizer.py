"""
Модуль для визуализации графа зависимостей
"""

import subprocess
import os
import tempfile


class Visualizer:
    def __init__(self, config):
        self.config = config

    def generate_plantuml(self, graph):
        """Генерация кода PlantUML для графа"""
        plantuml_code = ["@startuml"]

        # Добавляем все узлы
        for node in graph.nodes:
            plantuml_code.append(f'["{node}"]')

        # Добавляем связи
        for from_node, to_nodes in graph.edges.items():
            for to_node in to_nodes:
                plantuml_code.append(f'["{from_node}"] --> ["{to_node}"]')

        plantuml_code.append("@enduml")
        return "\n".join(plantuml_code)

    def save_plantuml_image(self, plantuml_code):
        """Сохранение изображения графа с использованием PlantUML"""
        try:
            # Сохраняем PlantUML код в файл
            output_file = self.config['output_image_file']
            puml_file = output_file.replace('.png', '.puml')

            with open(puml_file, 'w', encoding='utf-8') as f:
                f.write(plantuml_code)

            print(f"PlantUML код сохранен в: {puml_file}")

            # Пытаемся сгенерировать изображение, если установлен PlantUML
            try:
                import subprocess
                result = subprocess.run([
                    'plantuml', '-tpng', puml_file
                ], capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    print(f"Изображение графа сохранено в: {output_file}")
                else:
                    print("PlantUML не установлен или произошла ошибка при генерации")
                    print("Для установки PlantUML:")
                    print("  Windows: choco install plantuml")
                    print("  Ubuntu: sudo apt-get install plantuml")
                    print(f"Затем выполните: plantuml {puml_file}")

            except (FileNotFoundError, subprocess.TimeoutExpired):
                print("PlantUML не установлен в системе")
                print("Вы можете:")
                print("1. Установить PlantUML (см. инструкции выше)")
                print("2. Использовать онлайн версию: https://www.plantuml.com/plantuml/")
                print("3. Открыть файл в IDE с поддержкой PlantUML")

        except Exception as e:
            print(f"Ошибка при сохранении PlantUML: {e}")
            # Сохраняем хотя бы код
            with open('graph.puml', 'w', encoding='utf-8') as f:
                f.write(plantuml_code)
            print("PlantUML код сохранен в graph.puml")

    def generate_ascii_tree(self, graph):
        """Генерация ASCII-дерева зависимостей"""
        if not graph.nodes:
            return "Граф пустой - зависимости не найдены"

        start_node = self.config['package_name']
        if start_node not in graph.nodes:
            return f"Начальный узел '{start_node}' не найден в графе"

        return self._build_ascii_tree(graph, start_node)

    def _build_ascii_tree(self, graph, node, prefix="", is_last=True):
        """Рекурсивное построение ASCII-дерева"""
        result = prefix
        result += "└── " if is_last else "├── "
        result += node + "\n"

        children = graph.get_edges(node)
        for i, child in enumerate(children):
            child_prefix = prefix + ("    " if is_last else "│   ")
            result += self._build_ascii_tree(graph, child, child_prefix, i == len(children) - 1)

        return result
