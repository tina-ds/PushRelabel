# Push–Relabel: алгоритмы максимального потока и проверка корректности

Проект решает задачу максимального потока с помощью нескольких стратегий алгоритма Push–Relabel. Исследовательский notebook был преобразован в тестируемый Python-модуль в `src/`, а результаты реализаций сопоставляются с независимым алгоритмом Edmonds–Karp. Основной акцент сделан на воспроизводимой проверке алгоритмического поведения, регрессионных тестах и явном публичном API.

## 1. Что реализовано

| Вариант | Фактически реализованная стратегия |
|---|---|
| FIFO baseline | FIFO-очередь активных вершин без эвристик |
| FIFO + global relabeling | FIFO и периодический пересчёт меток расстояния до стока |
| FIFO + gap relabeling | FIFO и gap-эвристика для пустого уровня высоты |
| FIFO + global + gap | Совместное использование global и gap relabeling |
| Highest-label | Выбор активной вершины с максимальной меткой; LIFO внутри одного уровня |

Тестируемый production-код использует только стандартную библиотеку Python. Оптимизация current arc в production-коде отсутствует.

## 2. Подтверждённая корректность

Проверка построена на стандартном модуле `unittest` и включает:

- 17 тестов;
- независимую эталонную реализацию Edmonds–Karp;
- 70 детерминированных графов с seed от `1000` до `1069`;
- графы размером от 2 до 10 вершин;
- целочисленные ёмкости от 1 до 20;
- циклы, рёбра в источник, рёбра из стока, встречные рёбра, графы без пути к стоку и несколько маршрутов;
- отдельное сопоставление каждого из пяти вариантов с Edmonds–Karp на общем наборе графов.

Это эмпирическая проверка на ограниченном детерминированном наборе, а не формальное доказательство для всех возможных графов.

## 3. Исправленные дефекты

1. **Неверный подсчёт потока при рёбрах, входящих в источник.** Итоговое значение могло учитывать служебные записи остаточной сети как часть потока.
2. **Незавершение global relabeling.** Повторный пересчёт меток мог снижать уже выросшие метки вершин, недостижимых от стока, и возвращать алгоритм в прежнее состояние.

Для обоих дефектов добавлены воспроизводимые регрессионные тесты.

## 4. Быстрый пример

Из корня репозитория настройте путь к модулю для текущей сессии Windows PowerShell:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
```

Выполните минимальный пример:

```powershell
python -B -c "from push_relabel import compute_max_flow; edges=[(0,1,3),(0,2,2),(1,2,1),(1,3,2),(2,3,3)]; print(compute_max_flow(4, edges, 0, 3))"
```

Ожидаемый результат:

```text
5
```

Тот же пример в читаемом виде:

```python
from push_relabel import compute_max_flow

edges = [
    (0, 1, 3),
    (0, 2, 2),
    (1, 2, 1),
    (1, 3, 2),
    (2, 3, 3),
]

maximum_flow = compute_max_flow(
    number_of_vertices=4,
    edges=edges,
    source=0,
    sink=3,
)

print(maximum_flow)  # 5
```

Функция `compute_max_flow` использует базовую FIFO-реализацию без эвристик.

## 5. Публичный API

Пакет экспортирует четыре объекта:

```python
from push_relabel import (
    Edge,
    PushRelabel,
    PushRelabelHighest,
    compute_max_flow,
)
```

- `Edge` — запись ребра остаточной сети.
- `PushRelabel` — FIFO-реализация с независимым включением global и gap relabeling.
- `PushRelabelHighest` — highest-label вариант с bucket-структурой активных вершин.
- `compute_max_flow` — функция для однократного расчёта базовым FIFO-вариантом.

Создание доступных вариантов:

```python
PushRelabel(n, use_global=False, use_gap=False)
PushRelabel(n, use_global=True, use_gap=False)
PushRelabel(n, use_global=False, use_gap=True)
PushRelabel(n, use_global=True, use_gap=True)
PushRelabelHighest(n)
```

## 6. Запуск тестов

Из корня репозитория в Windows PowerShell:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
python -B -m unittest discover -s .\tests -v
```

Текущий подтверждённый итог:

```text
Ran 17 tests
OK
```

## 7. Структура проекта

```text
PushRelabel/
├── README.md
├── push_relabel.ipynb
├── pushrelabel.ipynb
├── src/
│   └── push_relabel/
│       ├── __init__.py
│       ├── base.py
│       └── highest.py
└── tests/
    ├── test_base_correctness.py
    ├── test_base_against_reference.py
    ├── test_global_relabel_against_reference.py
    ├── test_gap_relabel_against_reference.py
    ├── test_global_gap_against_reference.py
    ├── test_highest_against_reference.py
    └── test_public_api.py
```

- `src/push_relabel/` содержит тестируемые реализации и публичный API.
- `tests/` содержит известные регрессии, эталонный Edmonds–Karp и сравнение вариантов на детерминированных графах.
- `push_relabel.ipynb` хранит историческое Python-исследование, а `pushrelabel.ipynb` — отдельную демонстрацию C++17 через Bash/G++.

## 8. Происхождение проекта

Проект начался как исследовательский notebook с последовательными вариантами Push–Relabel и сохранёнными экспериментальными результатами. Проверенные реализации были извлечены в `src/`, зависимости от состояния notebook kernel устранены на уровне модульного кода, а алгоритмическое поведение проверено независимо от сохранённых outputs.

Исторические графики и численные результаты notebook не используются как подтверждение заявлений о текущем Python-модуле.

## 9. Исторические ноутбуки

- `push_relabel.ipynb` — исторический Python research-notebook с графиками и экспериментами; чистый `Run All` пока не гарантируется.
- `pushrelabel.ipynb` — отдельная демонстрация C++17 через Bash/G++.
- Ноутбуки не являются частью тестируемого Python API.

## 10. Ограничения

- Пакет пока не устанавливается через `pip`.
- Для запуска из корня репозитория требуется `PYTHONPATH=src`.
- CI пока отсутствует.
- Зависимости notebook не зафиксированы.
- Current arc отсутствует в production-коде.
- Воспроизводимый performance benchmark пока не подготовлен.
- LICENSE пока отсутствует.

## 11. Дальнейшее развитие

- Добавить `pyproject.toml` и установку пакета.
- Настроить CI.
- Подготовить воспроизводимый benchmark harness.
- Зафиксировать зависимости notebook.
- Принять и документировать решение по лицензии.
