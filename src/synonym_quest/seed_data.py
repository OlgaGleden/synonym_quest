"""Seed-данные: 20 заданий Synonym Quest, по 4 на каждую из 5 категорий.

Используется `scripts/seed_tasks.py` для наполнения БД и тестами
`tests/test_seed_data.py` для валидации структуры. Сообщения и словари
подобраны так, чтобы покрыть все 5 механик:

    word_tyr           — Словесный тир
    context_detective  — Детектив контекста
    synonym_puzzle     — Синонимический пазл
    synonym_battle     — Битва синонимов
    boss               — Boss-уровень
"""

from __future__ import annotations


SEED_TASKS: list[dict] = [
    # ---- word_tyr (Словесный тир) --------------------------------------
    {
        "title": "Утренняя рутина",
        "task_type": "word_tyr",
        "difficulty_level": 1,
        "topic": "daily_routine",
        "is_boss_level": False,
        "full_text": "I usually ___ at seven. Then I ___ breakfast and ___ to work.",
        "correct_text": (
            "I usually wake up at seven. Then I have breakfast and go to work."
        ),
        "word_bank": ["wake up", "have", "go", "sleep", "skip", "drive"],
        "steps": [
            {"step_number": 1, "correct_word": "wake up",
             "context_hint": "Как обычно говорят про подъём утром"},
            {"step_number": 2, "correct_word": "have",
             "context_hint": "Глагол для приёма пищи"},
            {"step_number": 3, "correct_word": "go",
             "context_hint": "Движение к месту работы"},
        ],
    },
    {
        "title": "Разговор о погоде",
        "task_type": "word_tyr",
        "difficulty_level": 2,
        "topic": "weather",
        "is_boss_level": False,
        "full_text": (
            "It is quite ___ outside. The sky is ___ and the wind is ___."
        ),
        "correct_text": (
            "It is quite cold outside. The sky is grey and the wind is strong."
        ),
        "word_bank": ["cold", "grey", "strong", "warm", "blue", "weak"],
        "steps": [
            {"step_number": 1, "correct_word": "cold",
             "context_hint": "Противоположно warm"},
            {"step_number": 2, "correct_word": "grey",
             "context_hint": "Цвет неба в пасмурный день"},
            {"step_number": 3, "correct_word": "strong",
             "context_hint": "Про сильный ветер"},
        ],
    },
    {
        "title": "Ресторанная рецензия",
        "task_type": "word_tyr",
        "difficulty_level": 2,
        "topic": "food",
        "is_boss_level": False,
        "full_text": (
            "The soup was ___. The main course tasted ___. "
            "Dessert was absolutely ___."
        ),
        "correct_text": (
            "The soup was salty. The main course tasted delicious. "
            "Dessert was absolutely wonderful."
        ),
        "word_bank": [
            "salty", "delicious", "wonderful",
            "sweet", "boring", "terrible",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "salty",
             "context_hint": "Вкус пересоленного супа"},
            {"step_number": 2, "correct_word": "delicious",
             "context_hint": "Синоним very tasty"},
            {"step_number": 3, "correct_word": "wonderful",
             "context_hint": "Синоним прекрасного десерта"},
        ],
    },

    # ---- context_detective (Детектив контекста) ------------------------
    {
        "title": "Деловая встреча",
        "task_type": "context_detective",
        "difficulty_level": 3,
        "topic": "business",
        "is_boss_level": False,
        "full_text": (
            "The manager gave a ___ report. Her tone was ___ "
            "but the facts were ___."
        ),
        "correct_text": (
            "The manager gave a comprehensive report. Her tone was calm "
            "but the facts were alarming."
        ),
        "word_bank": [
            "comprehensive", "calm", "alarming",
            "short", "angry", "reassuring",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "comprehensive",
             "context_hint": "Отчёт, охватывающий всё"},
            {"step_number": 2, "correct_word": "calm",
             "context_hint": "Спокойный тон — контраст со alarming"},
            {"step_number": 3, "correct_word": "alarming",
             "context_hint": "Факты, вызывающие тревогу"},
        ],
    },
    {
        "title": "Путевые заметки",
        "task_type": "context_detective",
        "difficulty_level": 3,
        "topic": "travel",
        "is_boss_level": False,
        "full_text": (
            "The journey across the continent was ___. We visited "
            "___ cities and met ___ people."
        ),
        "correct_text": (
            "The journey across the continent was extensive. We visited "
            "numerous cities and met fascinating people."
        ),
        "word_bank": [
            "extensive", "numerous", "fascinating",
            "brief", "few", "boring",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "extensive",
             "context_hint": "Долгое, обширное путешествие"},
            {"step_number": 2, "correct_word": "numerous",
             "context_hint": "Синоним many"},
            {"step_number": 3, "correct_word": "fascinating",
             "context_hint": "Люди, с которыми интересно"},
        ],
    },
    {
        "title": "Конспект лекции",
        "task_type": "context_detective",
        "difficulty_level": 4,
        "topic": "education",
        "is_boss_level": False,
        "full_text": (
            "The professor's ___ explanation made a ___ topic seem ___."
        ),
        "correct_text": (
            "The professor's concise explanation made a complex topic seem simple."
        ),
        "word_bank": [
            "concise", "complex", "simple",
            "vague", "trivial", "confusing",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "concise",
             "context_hint": "Краткое, но содержательное объяснение"},
            {"step_number": 2, "correct_word": "complex",
             "context_hint": "Сложная тема — противоположна simple"},
            {"step_number": 3, "correct_word": "simple",
             "context_hint": "Какой тема стала после объяснения"},
        ],
    },

    # ---- synonym_puzzle (Синонимический пазл) --------------------------
    {
        "title": "Конференция",
        "task_type": "synonym_puzzle",
        "difficulty_level": 4,
        "topic": "conference",
        "is_boss_level": False,
        "full_text": (
            "The ___ was held in a ___ hall. Speakers presented ___ ideas. "
            "The audience asked ___ questions. At the end we had a ___ discussion."
        ),
        "correct_text": (
            "The conference was held in a spacious hall. Speakers presented "
            "innovative ideas. The audience asked thoughtful questions. "
            "At the end we had a lively discussion."
        ),
        "word_bank": [
            "conference", "spacious", "innovative", "thoughtful", "lively",
            "meeting", "cramped", "old", "silly", "dull",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "conference",
             "context_hint": "Большое мероприятие со спикерами"},
            {"step_number": 2, "correct_word": "spacious",
             "context_hint": "Просторный зал"},
            {"step_number": 3, "correct_word": "innovative",
             "context_hint": "Новаторские идеи"},
            {"step_number": 4, "correct_word": "thoughtful",
             "context_hint": "Вдумчивые вопросы аудитории"},
            {"step_number": 5, "correct_word": "lively",
             "context_hint": "Живая дискуссия в конце"},
        ],
    },
    {
        "title": "Путешествие",
        "task_type": "synonym_puzzle",
        "difficulty_level": 4,
        "topic": "travel",
        "is_boss_level": False,
        "full_text": (
            "Our ___ began at dawn. The ___ road wound through ___ hills. "
            "We stopped at a ___ village and tried ___ food."
        ),
        "correct_text": (
            "Our journey began at dawn. The winding road wound through "
            "rolling hills. We stopped at a charming village and tried local food."
        ),
        "word_bank": [
            "journey", "winding", "rolling", "charming", "local",
            "trip", "straight", "flat", "ugly", "imported",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "journey",
             "context_hint": "Долгая поездка, синоним trip"},
            {"step_number": 2, "correct_word": "winding",
             "context_hint": "Извилистая дорога"},
            {"step_number": 3, "correct_word": "rolling",
             "context_hint": "Холмистая местность (rolling hills)"},
            {"step_number": 4, "correct_word": "charming",
             "context_hint": "Очаровательная деревня"},
            {"step_number": 5, "correct_word": "local",
             "context_hint": "Местная кухня"},
        ],
    },
    {
        "title": "Вечер в кругу друзей",
        "task_type": "synonym_puzzle",
        "difficulty_level": 5,
        "topic": "daily_routine",
        "is_boss_level": False,
        "full_text": (
            "The ___ evening ended with a ___ meal. We talked about ___ "
            "plans and laughed at ___ stories. It was a truly ___ night."
        ),
        "correct_text": (
            "The warm evening ended with a splendid meal. We talked about "
            "ambitious plans and laughed at amusing stories. "
            "It was a truly memorable night."
        ),
        "word_bank": [
            "warm", "splendid", "ambitious", "amusing", "memorable",
            "cold", "dull", "modest", "sad", "ordinary",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "warm",
             "context_hint": "Тёплый вечер"},
            {"step_number": 2, "correct_word": "splendid",
             "context_hint": "Великолепная еда"},
            {"step_number": 3, "correct_word": "ambitious",
             "context_hint": "Амбициозные планы"},
            {"step_number": 4, "correct_word": "amusing",
             "context_hint": "Забавные истории"},
            {"step_number": 5, "correct_word": "memorable",
             "context_hint": "Незабываемый вечер"},
        ],
    },

    # ---- synonym_battle (Битва синонимов) ------------------------------
    {
        "title": "Пресс-релиз",
        "task_type": "synonym_battle",
        "difficulty_level": 4,
        "topic": "business",
        "is_boss_level": False,
        "full_text": (
            "The company ___ the launch yesterday. The CEO ___ the results. "
            "Analysts ___ the announcement."
        ),
        "correct_text": (
            "The company announced the launch yesterday. The CEO praised "
            "the results. Analysts welcomed the announcement."
        ),
        "word_bank": [
            "announced", "praised", "welcomed",
            "mentioned", "ignored", "doubted",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "announced",
             "context_hint": "Официально объявить о запуске"},
            {"step_number": 2, "correct_word": "praised",
             "context_hint": "Публично похвалить результаты"},
            {"step_number": 3, "correct_word": "welcomed",
             "context_hint": "Аналитики одобрили заявление"},
        ],
    },
    {
        "title": "Научное открытие",
        "task_type": "synonym_battle",
        "difficulty_level": 5,
        "topic": "science",
        "is_boss_level": False,
        "full_text": (
            "The team ___ the experiment. They ___ the outcome. "
            "Their results ___ the hypothesis."
        ),
        "correct_text": (
            "The team conducted the experiment. They predicted the outcome. "
            "Their results confirmed the hypothesis."
        ),
        "word_bank": [
            "conducted", "predicted", "confirmed",
            "skipped", "ignored", "refuted",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "conducted",
             "context_hint": "Провели эксперимент"},
            {"step_number": 2, "correct_word": "predicted",
             "context_hint": "Предсказали результат до его появления"},
            {"step_number": 3, "correct_word": "confirmed",
             "context_hint": "Результаты подтвердили гипотезу"},
        ],
    },
    {
        "title": "Газетная передовица",
        "task_type": "synonym_battle",
        "difficulty_level": 5,
        "topic": "politics",
        "is_boss_level": False,
        "full_text": (
            "The minister ___ the new policy. Critics ___ it. "
            "The public ___ with mixed feelings."
        ),
        "correct_text": (
            "The minister introduced the new policy. Critics opposed it. "
            "The public reacted with mixed feelings."
        ),
        "word_bank": [
            "introduced", "opposed", "reacted",
            "cancelled", "supported", "ignored",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "introduced",
             "context_hint": "Министр представил новую политику"},
            {"step_number": 2, "correct_word": "opposed",
             "context_hint": "Критики выступили против"},
            {"step_number": 3, "correct_word": "reacted",
             "context_hint": "Публика отреагировала неоднозначно"},
        ],
    },

    # ---- boss (Boss-уровень) -------------------------------------------
    {
        "title": "Квартальный отчёт",
        "task_type": "boss",
        "difficulty_level": 5,
        "topic": "business",
        "is_boss_level": True,
        "full_text": (
            "The quarterly report ___ a ___ growth in revenue. Management ___ "
            "the team's ___ efforts and ___ further investment."
        ),
        "correct_text": (
            "The quarterly report revealed a substantial growth in revenue. "
            "Management acknowledged the team's tireless efforts and "
            "recommended further investment."
        ),
        "word_bank": [
            "revealed", "substantial", "acknowledged", "tireless", "recommended",
            "hid", "trivial", "ignored", "lazy", "rejected",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "revealed",
             "context_hint": "Отчёт показал/раскрыл рост"},
            {"step_number": 2, "correct_word": "substantial",
             "context_hint": "Существенный рост"},
            {"step_number": 3, "correct_word": "acknowledged",
             "context_hint": "Руководство признало усилия"},
            {"step_number": 4, "correct_word": "tireless",
             "context_hint": "Неустанные усилия команды"},
            {"step_number": 5, "correct_word": "recommended",
             "context_hint": "Рекомендовали дальнейшие инвестиции"},
        ],
    },
    {
        "title": "Научный прорыв",
        "task_type": "boss",
        "difficulty_level": 5,
        "topic": "science",
        "is_boss_level": True,
        "full_text": (
            "Researchers ___ a ___ discovery. The findings ___ previous theories "
            "and ___ new questions. The scientific community ___ the breakthrough."
        ),
        "correct_text": (
            "Researchers announced a groundbreaking discovery. The findings "
            "challenged previous theories and raised new questions. "
            "The scientific community celebrated the breakthrough."
        ),
        "word_bank": [
            "announced", "groundbreaking", "challenged", "raised", "celebrated",
            "hid", "trivial", "confirmed", "answered", "ignored",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "announced",
             "context_hint": "Учёные объявили об открытии"},
            {"step_number": 2, "correct_word": "groundbreaking",
             "context_hint": "Прорывное открытие"},
            {"step_number": 3, "correct_word": "challenged",
             "context_hint": "Результаты оспорили прежние теории"},
            {"step_number": 4, "correct_word": "raised",
             "context_hint": "Поставили новые вопросы (raise questions)"},
            {"step_number": 5, "correct_word": "celebrated",
             "context_hint": "Сообщество отпраздновало прорыв"},
        ],
    },
    {
        "title": "Климатическая передовица",
        "task_type": "boss",
        "difficulty_level": 5,
        "topic": "ecology",
        "is_boss_level": True,
        "full_text": (
            "The editorial ___ urgent action. It ___ the government for ___ "
            "policies and ___ citizens to ___ consumption."
        ),
        "correct_text": (
            "The editorial demanded urgent action. It criticized the government "
            "for inadequate policies and urged citizens to reduce consumption."
        ),
        "word_bank": [
            "demanded", "criticized", "inadequate", "urged", "reduce",
            "ignored", "praised", "excellent", "forbade", "increase",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "demanded",
             "context_hint": "Передовица потребовала срочных действий"},
            {"step_number": 2, "correct_word": "criticized",
             "context_hint": "Раскритиковала правительство"},
            {"step_number": 3, "correct_word": "inadequate",
             "context_hint": "Неадекватная политика"},
            {"step_number": 4, "correct_word": "urged",
             "context_hint": "Призвала граждан (urge smb to do)"},
            {"step_number": 5, "correct_word": "reduce",
             "context_hint": "Сократить потребление"},
        ],
    },
]


# ---- Дополнительные задания: 4-й набор по механикам ------------------------
# Добавлены для расширения ротации (было 3 на механику, стало 4).

APPEND_TASKS: list[dict] = [
    # ---- word_tyr: 4-е задание ----------------------------------------
    {
        "title": "Сложный тест",
        "task_type": "word_tyr",
        "difficulty_level": 3,
        "topic": "education",
        "is_boss_level": False,
        "full_text": (
            "The final puzzle was ___; nobody could solve it. "
            "The task was ___ and the instructions were ___."
        ),
        "correct_text": (
            "The final puzzle was difficult; nobody could solve it. "
            "The task was hard and the instructions were challenging."
        ),
        "word_bank": [
            "difficult", "hard", "challenging",
            "easy", "simple", "clear",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "difficult",
             "context_hint": "Задача, которую трудно решить"},
            {"step_number": 2, "correct_word": "hard",
             "context_hint": "Синоним difficult"},
            {"step_number": 3, "correct_word": "challenging",
             "context_hint": "Инструкции, требующие усилий"},
        ],
    },

    # ---- context_detective: 4-е задание --------------------------------
    {
        "title": "В классе",
        "task_type": "context_detective",
        "difficulty_level": 3,
        "topic": "education",
        "is_boss_level": False,
        "full_text": (
            "We need a ___ classroom for thirty students. "
            "Mia is very ___; she solved the puzzle in a minute. "
            "Please stay ___ while the baby is sleeping."
        ),
        "correct_text": (
            "We need a large classroom for thirty students. "
            "Mia is very clever; she solved the puzzle in a minute. "
            "Please stay silent while the baby is sleeping."
        ),
        "word_bank": [
            "large", "clever", "silent",
            "pretty", "hard", "noisy",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "large",
             "context_hint": "Класс для тридцати учеников должен быть большим"},
            {"step_number": 2, "correct_word": "clever",
             "context_hint": "Миа быстро решила головоломку — она умная"},
            {"step_number": 3, "correct_word": "silent",
             "context_hint": "Не шуметь, пока спит ребёнок"},
        ],
    },

    # ---- synonym_puzzle: 4-е задание -----------------------------------
    {
        "title": "Холодный день",
        "task_type": "synonym_puzzle",
        "difficulty_level": 4,
        "topic": "weather",
        "is_boss_level": False,
        "full_text": (
            "Yesterday morning was quite ___, so I put on a warm coat. "
            "The wind was ___ and shook the trees. The lake was almost ___, "
            "so we didn't go swimming. At home, we sat under a ___ blanket "
            "and drank tea."
        ),
        "correct_text": (
            "Yesterday morning was quite chilly, so I put on a warm coat. "
            "The wind was fierce and shook the trees. The lake was almost "
            "freezing, so we didn't go swimming. At home, we sat under a "
            "cozy blanket and drank tea."
        ),
        "word_bank": [
            "chilly", "fierce", "freezing", "cozy",
            "warm", "gentle", "boiling", "uncomfortable",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "chilly",
             "context_hint": "Прохладное утро, но не мороз"},
            {"step_number": 2, "correct_word": "fierce",
             "context_hint": "Сильный, резкий ветер"},
            {"step_number": 3, "correct_word": "freezing",
             "context_hint": "Озеро почти замёрзло"},
            {"step_number": 4, "correct_word": "cozy",
             "context_hint": "Уютный плед дома"},
        ],
    },

    # ---- synonym_battle: 4-е задание -----------------------------------
    {
        "title": "Мой день",
        "task_type": "synonym_battle",
        "difficulty_level": 4,
        "topic": "daily_routine",
        "is_boss_level": False,
        "full_text": (
            "When I ___ out of my window, it was getting dark. "
            "I ___ the food and the atmosphere. Suddenly I saw Victor "
            "and Peter ___ their way to my table."
        ),
        "correct_text": (
            "When I looked out of my window, it was getting dark. "
            "I enjoyed the food and the atmosphere. Suddenly I saw Victor "
            "and Peter making their way to my table."
        ),
        "word_bank": [
            "looked", "enjoyed", "making",
            "watched", "preferred", "doing",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "looked",
             "context_hint": "Посмотрел в окно — look out of the window"},
            {"step_number": 2, "correct_word": "enjoyed",
             "context_hint": "Получал удовольствие от еды и атмосферы"},
            {"step_number": 3, "correct_word": "making",
             "context_hint": "Прокладывали путь к столу — make one's way"},
        ],
    },

    # ---- boss: 4-е задание ---------------------------------------------
    {
        "title": "Известная спортсменка",
        "task_type": "boss",
        "difficulty_level": 5,
        "topic": "sports",
        "is_boss_level": True,
        "full_text": (
            "How did Victoria Green ___ to get all of those cups? "
            "Her serve is ___ one of the best in women's tennis. "
            "At Wimbledon she ___ the tournament's record. "
            "___ she was two points away from losing, she did not give up. "
            "Her charity ___ educational opportunities for underprivileged youth."
        ),
        "correct_text": (
            "How did Victoria Green manage to get all of those cups? "
            "Her serve is considered one of the best in women's tennis. "
            "At Wimbledon she broke the tournament's record. "
            "Although she was two points away from losing, she did not give up. "
            "Her charity provides educational opportunities for underprivileged youth."
        ),
        "word_bank": [
            "manage", "considered", "broke", "Although", "provides",
            "succeed", "convinced", "pushed", "However", "predicts",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "manage",
             "context_hint": "Суметь добиться — manage to do smth"},
            {"step_number": 2, "correct_word": "considered",
             "context_hint": "Её подачу считают одной из лучших"},
            {"step_number": 3, "correct_word": "broke",
             "context_hint": "Побила рекорд турнира — break a record"},
            {"step_number": 4, "correct_word": "Although",
             "context_hint": "Хотя она была в двух очках от поражения"},
            {"step_number": 5, "correct_word": "provides",
             "context_hint": "Благотворительная организация обеспечивает возможности"},
        ],
    },
]

SEED_TASKS.extend(APPEND_TASKS)


__all__ = ["SEED_TASKS"]