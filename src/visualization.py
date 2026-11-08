"""Создание Mermaid-диаграммы и ASCII-дерева."""


class VisualizationError(Exception):
    """Ошибка визуализации графа."""


def _escape_label(label):
    """Экранирует текст для Mermaid."""
    return label.replace('"', '\\"')


def _node_ids(graph):
    """Создаёт безопасные идентификаторы узлов."""
    nodes = set(graph)

    for dependencies in graph.values():
        nodes.update(dependencies)

    return {
        node: f"node{index}"
        for index, node in enumerate(sorted(nodes))
    }


def to_mermaid(graph):
    """Создаёт описание графа на языке Mermaid.

    Args:
        graph: Граф зависимостей.

    Returns:
        str: Текст Mermaid-диаграммы.
    """
    identifiers = _node_ids(graph)
    lines = ["graph TD"]

    for node in sorted(identifiers):
        identifier = identifiers[node]
        label = _escape_label(node)
        lines.append(f'    {identifier}["{label}"]')

    for parent in sorted(graph):
        for child in graph[parent]:
            lines.append(
                f"    {identifiers[parent]} --> "
                f"{identifiers[child]}"
            )

    return "\n".join(lines)


def _push_children(
    stack,
    graph,
    node,
    prefix,
    path,
):
    """Добавляет дочерние узлы в стек."""
    children = graph.get(node, [])

    if not children:
        return

    last_child = children[-1]

    for child in reversed(children):
        stack.append(
            (
                child,
                prefix,
                child == last_child,
                path,
            )
        )


def to_ascii_tree(graph, root):
    """Создаёт ASCII-дерево без рекурсии.

    Args:
        graph: Граф зависимостей.
        root: Корневой пакет.

    Returns:
        str: Дерево зависимостей.

    Raises:
        VisualizationError: Если корень отсутствует.
    """
    if root not in graph:
        raise VisualizationError(
            f"корневой пакет {root} отсутствует"
        )

    lines = [root]
    stack = []
    _push_children(
        stack,
        graph,
        root,
        "",
        {root},
    )

    while stack:
        node, prefix, is_last, path = stack.pop()
        branch = "└── " if is_last else "├── "

        if node in path:
            lines.append(
                f"{prefix}{branch}{node} (цикл)"
            )
            continue

        lines.append(f"{prefix}{branch}{node}")

        next_prefix = prefix
        next_prefix += "    " if is_last else "│   "
        next_path = path | {node}

        _push_children(
            stack,
            graph,
            node,
            next_prefix,
            next_path,
        )

    return "\n".join(lines)