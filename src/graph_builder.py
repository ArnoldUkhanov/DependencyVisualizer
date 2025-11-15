"""
Модуль для построения графа зависимостей с использованием BFS с рекурсией
"""

from collections import deque, defaultdict


class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)

    def add_edge(self, from_node, to_node):
        """Добавление связи в граф"""
        self.nodes.add(from_node)
        self.nodes.add(to_node)
        self.edges[from_node].append(to_node)

    def get_edges(self, node):
        """Получение исходящих связей для узла"""
        return self.edges.get(node, [])


class GraphBuilder:
    def __init__(self, nuget_client, config):
        self.nuget_client = nuget_client
        self.config = config
        self.visited = set()

    def build_dependency_graph(self):
        """Построение полного графа зависимостей с использованием BFS с рекурсией"""
        graph = Graph()
        start_package = self.config['package_name']
        max_depth = self.config['max_depth']

        # Используем BFS с рекурсией
        queue = deque([(start_package, 0)])  # (package, current_depth)
        self.visited.clear()

        self._bfs_recursive(graph, queue, max_depth)

        return graph

    def _bfs_recursive(self, graph, queue, max_depth):
        """Рекурсивная реализация BFS для обхода зависимостей"""
        if not queue:
            return

        current_package, current_depth = queue.popleft()

        # Если достигнута максимальная глубина или узел уже обработан —
        # просто переходим к следующему элементу очереди
        if current_depth >= max_depth or current_package in self.visited:
            self._bfs_recursive(graph, queue, max_depth)
            return

        self.visited.add(current_package)

        # Получаем зависимости текущего пакета
        try:
            dependencies = self.nuget_client.get_package_dependencies(current_package)

            for dep in dependencies:
                if dep not in self.visited:
                    graph.add_edge(current_package, dep)
                    queue.append((dep, current_depth + 1))

        except Exception as e:
            print(f"Предупреждение: не удалось получить зависимости для {current_package}: {e}")

        # Рекурсивный вызов для следующего элемента в очереди
        self._bfs_recursive(graph, queue, max_depth)

    def get_load_order(self):
        """Получение порядка загрузки зависимостей (топологическая сортировка)"""
        graph = self.build_dependency_graph()
        return self._topological_sort(graph)

    def _topological_sort(self, graph):
        """Топологическая сортировка графа"""
        visited = set()
        temp_visited = set()
        result = []

        def visit(node):
            if node in temp_visited:
                return  # Циклическая зависимость
            if node not in visited:
                temp_visited.add(node)
                for neighbor in graph.get_edges(node):
                    visit(neighbor)
                temp_visited.remove(node)
                visited.add(node)
                result.append(node)

        for node in graph.nodes:
            if node not in visited:
                visit(node)

        return result[::-1]  # Разворачиваем для правильного порядка
