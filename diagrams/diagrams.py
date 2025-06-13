from graphviz import Digraph

# 1. Общая архитектура системы с 4 микросервисами
system_arch = Digraph("Рекомендательная система", filename="diagrams/result/system_arch", format="png")
system_arch.attr(rankdir="LR", splines="ortho")

# Участник 1 - Ядро рекомендаций
with system_arch.subgraph(name="cluster_core") as c:
    c.attr(label="1. Ядро рекомендаций и управление профилями", style="filled", color="lightgrey")
    c.node(
        "core",
        """Core Service
    • Управление профилями
    • Гибридные рекомендации
    • Интеграция с TMDb/IMDb
    Технологии:
    FastAPI, PostgreSQL""",
        shape="box",
    )

# Участник 2 - Анализ поведения
with system_arch.subgraph(name="cluster_analytics") as c:
    c.attr(label="2. Анализ поведения и сбор событий", style="filled", color="lightblue")
    c.node(
        "analytics",
        """Analytics Service
    • Сбор событий
    • Кластеризация пользователей
    • Триггерные события
    Технологии:
    Kafka, ClickHouse, Elasticsearch""",
        shape="box",
    )

# Участник 3 - Уведомления
with system_arch.subgraph(name="cluster_notify") as c:
    c.attr(label="3. Персонализированные уведомления и интерактивный UI", style="filled", color="lightgreen")
    c.node(
        "notify",
        """
    • WebSocket-уведомления
    • Email/push-рассылки
    • Локализация
    Технологии:
    RabbitMQ, Celery""",
        shape="box",
    )

# Участник 4 - ML движок
with system_arch.subgraph(name="cluster_ml") as c:
    c.attr(label="4. ML-движок и контекстные рекомендации", style="filled", color="lightyellow")
    c.node(
        "ml",
        """ML Engine
    • Нейросетевые модели
    • Контекстные рекомендации
    • Оптимизация через Optuna
    Технологии:
    TensorFlow, PyTorch, MLflow""",
        shape="box",
    )

# Инфраструктурные компоненты
system_arch.node("kafka", "Kafka\n(шина событий)", shape="cylinder")
system_arch.node("redis", "Redis\n(кэш)", shape="cylinder")
system_arch.node("db", "PostgreSQL\n(данные)", shape="cylinder")

# Взаимодействия
system_arch.edge("core", "redis", label="Кэш рекомендаций")
system_arch.edge("core", "db", label="Сохранение рекомендаций")
system_arch.edge("core", "kafka", label="События оценок")
system_arch.edge("analytics", "kafka", label="Поток событий", dir="both")
system_arch.edge("analytics", "ml", label="Фичи для ML", style="dashed")
system_arch.edge("ml", "core", label="Обновление моделей")
system_arch.edge("core", "notify", label="Триггеры уведомлений")
system_arch.edge("notify", "kafka", label="События кликов")
system_arch.edge("ml", "kafka", label="Контекстные события")

system_arch.render(view=True)


# 2. Детализированные диаграммы для каждого участника
def create_service_diagram(service_name, title, components, interactions):
    diagram = Digraph(service_name, filename=f"diagrams/result/{service_name}_detail", format="png")
    diagram.attr(label=title, labelloc="t", fontsize="20")

    with diagram.subgraph(name=f"cluster_{service_name}_components") as c:
        c.attr(label="Компоненты", style="rounded,filled", color="lightgrey")
        for comp in components:
            c.node(comp["name"], comp["desc"], shape=comp.get("shape", "box"))

    with diagram.subgraph(name=f"cluster_{service_name}_tech") as c:
        c.attr(label="Технологии", style="rounded,filled", color="lightblue")
        for tech in components[0]["tech"].split("\n"):
            c.node(tech, tech, shape="plaintext")

    for interaction in interactions:
        diagram.edge(
            interaction["from"], interaction["to"], label=interaction["label"], style=interaction.get("style", "solid")
        )

    diagram.render(view=True)


# Участник 1 - Ядро рекомендаций
core_components = [
    {
        "name": "api_layer",
        "desc": """API Layer
        • POST /recommend
        • GET /profile/{id}
        • POST /rate""",
        "tech": "FastAPI\ngRPC\nPython-JWT",
    },
    {
        "name": "algorithms",
        "desc": """Алгоритмы
        • Совместная фильтрация
        • Основанный на действия польтзователя
        • Гибридные методы""",
        "tech": "Surprise\nscikit-learn\nTensorFlow",
    },
    {
        "name": "data_layer",
        "desc": """Data Layer
        • PostgreSQL
        • Redis""",
        "shape": "cylinder",
    },
]

core_interactions = [
    {"from": "api_layer", "to": "algorithms", "label": "Запрос рекомендаций"},
    {"from": "algorithms", "to": "data_layer", "label": "Загрузка данных"},
    {"from": "data_layer", "to": "api_layer", "label": "Ответ API", "style": "dashed"},
]

create_service_diagram(
    "core_service", "Участник 1: Ядро рекомендаций и управление профилями", core_components, core_interactions
)

# Участник 2 - Аналитика поведения
analytics_components = [
    {
        "name": "ingestion",
        "desc": """Сбор данных
        • REST API
        • Kafka Consumer""",
        "tech": "FastAPI\nKafka\nClickHouse\nMongoDB",
    },
    {
        "name": "processing",
        "desc": """Обработка
        • Кластеризация
        • Анализ временных рядов
        • Триггеры""",
        "tech": "scikit-learn\nProphet\nElasticsearch",
    },
    {
        "name": "storage",
        "desc": """Хранение
        • MongoDB
        • ClickHouse
        • Elasticsearch""",
        "shape": "cylinder",
    },
]

analytics_interactions = [
    {"from": "ingestion", "to": "processing", "label": "Сырые события"},
    {"from": "processing", "to": "storage", "label": "Аналитика"},
    {"from": "storage", "to": "ingestion", "label": "Обратная связь", "style": "dashed"},
]

create_service_diagram(
    "analytics_service", "Участник 2: Анализ поведения и сбор событий", analytics_components, analytics_interactions
)

# Участник 3 - Уведомления
notification_components = [
    {
        "name": "channels",
        "desc": """Каналы
        • WebSocket
        • Email
        • Push""",
        "tech": "Flask-SocketIO\nsmtplib\nnotify2",
    },
    {
        "name": "templates",
        "desc": """Шаблоны
        • Jinja2
        • A/B тесты""",
        "tech": "Jinja2\ni18n\nCelery",
    },
    {
        "name": "queues",
        "desc": """Очереди
        • RabbitMQ
        • Celery Tasks""",
        "shape": "cylinder",
    },
]

notification_interactions = [
    {"from": "queues", "to": "channels", "label": "Задачи отправки"},
    {"from": "templates", "to": "channels", "label": "Персонализация"},
    {"from": "channels", "to": "queues", "label": "Статусы", "style": "dashed"},
]

create_service_diagram(
    "notification_service",
    "Участник 3: Персонализированные уведомления и интерактивный UI",
    notification_components,
    notification_interactions,
)

# Участник 4 - ML движок
ml_components = [
    {
        "name": "models",
        "desc": """Модели
        • DeepFM
        • BERT
        • RLlib""",
        "tech": "TensorFlow\nPyTorch\nАналог ML",
    },
    {
        "name": "training",
        "desc": """Обучение
        • Optuna
        • MLflow
        • Feature Store""",
        "tech": "Optuna\nMLflow\nPandas",
    },
    {
        "name": "serving",
        "desc": """Сервинг
        • FastAPI
        • Celery
        • Redis""",
        "shape": "cylinder",
    },
]

ml_interactions = [
    {"from": "training", "to": "models", "label": "Обученные модели"},
    {"from": "models", "to": "serving", "label": "Предсказания"},
    {"from": "serving", "to": "training", "label": "Метрики", "style": "dashed"},
]

create_service_diagram(
    "ml_service", "Участник 4: ML-движок и контекстные рекомендации", ml_components, ml_interactions
)


# 3. Сценарии взаимодействия
def create_scenario_diagram(scenario_name, title, steps):
    scenario = Digraph(scenario_name, filename=f"diagrams/result/{scenario_name}_flow", format="png")
    scenario.attr(rankdir="LR", label=title, labelloc="t", fontsize="20")

    for i, step in enumerate(steps, 1):
        scenario.node(f"step{i}", f'{i}. {step["name"]}', shape="box")
        if i > 1:
            scenario.edge(f"step{i-1}", f"step{i}", label=step.get("label", ""))

    scenario.render(view=True)


# Сценарий 1: Оценка фильма
rating_steps = [
    {"name": "Пользователь оценивает фильм", "label": "POST /rate"},
    {"name": "Core Service обновляет профиль"},
    {"name": "Событие отправляется в Kafka"},
    {"name": "ML Engine обрабатывает событие"},
    {"name": "Обновленные рекомендации в Redis"},
    {"name": "Уведомление через WebSocket"},
]

create_scenario_diagram("rating_scenario", "Сценарий: Пользователь оценил фильм", rating_steps)

# Сценарий 2: Поиск фильмов
search_steps = [
    {"name": 'Пользователь ищет "комедии"'},
    {"name": "Analytics Service фиксирует поиск"},
    {"name": "Kafka → ML Engine → Core Service"},
    {"name": "Персонализированные результаты"},
    {"name": "Push-уведомление о новинках"},
]

create_scenario_diagram("search_scenario", "Сценарий: Поиск фильмов", search_steps)
