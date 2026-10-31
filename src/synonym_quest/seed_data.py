"""Seed-данные: 20 заданий Synonym Quest, по 4 на каждую из 5 категорий.

Используется `scripts/seed_tasks.py` для наполнения БД и тестами
`tests/test_seed_data.py` для валидации структуры.

Поля шага:
    step_number     — порядковый номер (1..N без пропусков)
    correct_word    — ТОЛЬКО правильное слово (без пояснений)
    context_hint    — подсказка до ответа (💡)
    explanation     — пояснение после неверного ответа (📖)
"""

from __future__ import annotations


SEED_TASKS: list[dict] = [
    # ---- word_tyr ------------------------------------------------------
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
        "word_bank": ["wake up", "have", "go", "rouse", "ingest", "depart"],
        "steps": [
            {"step_number": 1, "correct_word": "wake up",
             "context_hint": "Как обычно говорят про подъём утром",
             "explanation": "Wake up — устойчивое выражение для «просыпаться»; "
                            "не путать с get up (встать с кровати) или rouse (формально)"},
            {"step_number": 2, "correct_word": "have",
             "context_hint": "Глагол для приёма пищи",
             "explanation": "Have breakfast — устойчивое сочетание для «завтракать». "
                            "Ingest — книжный синоним, в быту не используется"},
            {"step_number": 3, "correct_word": "go",
             "context_hint": "Движение к месту работы",
             "explanation": "Go to work — обычное сочетание. Depart — формальное, "
                            "чаще о транспорте («отправляться»)"},
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
        "word_bank": ["cold", "grey", "strong", "gelid", "dusky", "robust"],
        "steps": [
            {"step_number": 1, "correct_word": "cold",
             "context_hint": "Противоположно warm",
             "explanation": "Cold — базовое слово. Gelid — поэтическое, "
                            "«ледяной», в обычной речи не используется"},
            {"step_number": 2, "correct_word": "grey",
             "context_hint": "Цвет неба в пасмурный день",
             "explanation": "Grey (BrE) / gray (AmE) — серый цвет пасмурного неба. "
                            "Dusky — «сумеречный», про время суток, а не про цвет неба"},
            {"step_number": 3, "correct_word": "strong",
             "context_hint": "Про сильный ветер",
             "explanation": "Strong wind — устойчивое сочетание. Robust — «крепкий, "
                            "здоровый», про объекты и людей, но не про ветер"},
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
            "saline", "palatable", "commendable",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "salty",
             "context_hint": "Вкус пересоленного супа",
             "explanation": "Salty — обычное слово о вкусе. Saline — медицинский "
                            "термин («солевой раствор»), не о еде"},
            {"step_number": 2, "correct_word": "delicious",
             "context_hint": "Синоним very tasty",
             "explanation": "Delicious — про очень вкусную еду. Palatable — "
                            "«съедобный», скорее нейтрально-книжное"},
            {"step_number": 3, "correct_word": "wonderful",
             "context_hint": "Синоним прекрасного десерта",
             "explanation": "Wonderful — эмоционально сильное «прекрасный». "
                            "Commendable — «достойный похвалы», формально"},
        ],
    },

    # ---- context_detective --------------------------------------------
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
            "encyclopedic", "placid", "portentous",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "comprehensive",
             "context_hint": "Отчёт, охватывающий всё",
             "explanation": "Comprehensive — «всесторонний». Encyclopedic — "
                            "«энциклопедический», про объём знаний, не про отчёт"},
            {"step_number": 2, "correct_word": "calm",
             "context_hint": "Спокойный тон — контраст со alarming",
             "explanation": "Calm — «спокойный». Placid — «безмятежный», "
                            "книжное, часто о характере или воде"},
            {"step_number": 3, "correct_word": "alarming",
             "context_hint": "Факты, вызывающие тревогу",
             "explanation": "Alarming — «тревожный». Portentous — «зловещий, "
                            "предвещающий», слишком сильное для фактов"},
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
            "sweeping", "multifarious", "engrossing",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "extensive",
             "context_hint": "Долгое обширное путешествие",
             "explanation": "Extensive — «обширный, масштабный». Sweeping — "
                            "«размашистый», чаще про изменения или жесты"},
            {"step_number": 2, "correct_word": "numerous",
             "context_hint": "Синоним many",
             "explanation": "Numerous — формальный синоним many. Multifarious — "
                            "«многообразный», про разнообразие, не про количество"},
            {"step_number": 3, "correct_word": "fascinating",
             "context_hint": "Люди, с которыми интересно",
             "explanation": "Fascinating — «увлекательный». Engrossing — "
                            "«поглощающий внимание», чаще про книги/фильмы"},
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
            "curt", "labyrinthine", "facile",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "concise",
             "context_hint": "Краткое, но содержательное объяснение",
             "explanation": "Concise — «краткий и по делу». Curt — «отрывистый, "
                            "грубоватый» — про тон, не про содержание"},
            {"step_number": 2, "correct_word": "complex",
             "context_hint": "Сложная тема — противоположна simple",
             "explanation": "Complex — «сложный». Labyrinthine — «запутанный, "
                            "как лабиринт», слишком образно для темы лекции"},
            {"step_number": 3, "correct_word": "simple",
             "context_hint": "Какой тема стала после объяснения",
             "explanation": "Simple — «простой». Facile — «легковесный, "
                            "поверхностный», с негативным оттенком"},
        ],
    },

    # ---- synonym_puzzle ------------------------------------------------
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
            "colloquium", "voluminous", "heterodox", "pensive", "vivacious",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "conference",
             "context_hint": "Большое мероприятие со спикерами",
             "explanation": "Conference — «конференция». Colloquium — "
                            "«научный семинар», узкий академический формат"},
            {"step_number": 2, "correct_word": "spacious",
             "context_hint": "Просторный зал",
             "explanation": "Spacious — «просторный». Voluminous — «объёмный», "
                            "про одежду или книгу, не про зал"},
            {"step_number": 3, "correct_word": "innovative",
             "context_hint": "Новаторские идеи",
             "explanation": "Innovative — «новаторский». Heterodox — "
                            "«неортодоксальный», про отход от догмы"},
            {"step_number": 4, "correct_word": "thoughtful",
             "context_hint": "Вдумчивые вопросы аудитории",
             "explanation": "Thoughtful — «вдумчивый». Pensive — "
                            "«задумчивый», чаще о человеке, а не о вопросе"},
            {"step_number": 5, "correct_word": "lively",
             "context_hint": "Живая дискуссия в конце",
             "explanation": "Lively — «живой, оживлённый». Vivacious — "
                            "«жизнерадостный», про человека"},
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
            "voyage", "devious", "surging", "winsome", "parochial",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "journey",
             "context_hint": "Долгая поездка, синоним trip",
             "explanation": "Journey — «путешествие» (по суше). Voyage — "
                            "«плавание, полёт», морское или космическое"},
            {"step_number": 2, "correct_word": "winding",
             "context_hint": "Извилистая дорога",
             "explanation": "Winding — «извилистый». Devious — «окольный, "
                            "коварный», с негативным оттенком"},
            {"step_number": 3, "correct_word": "rolling",
             "context_hint": "Холмистая местность (rolling hills)",
             "explanation": "Rolling hills — устойчивое выражение. Surging — "
                            "«вздымающийся», про волны"},
            {"step_number": 4, "correct_word": "charming",
             "context_hint": "Очаровательная деревня",
             "explanation": "Charming — «очаровательный». Winsome — "
                            "«привлекательный, милый», книжное, чаще о человеке"},
            {"step_number": 5, "correct_word": "local",
             "context_hint": "Местная кухня",
             "explanation": "Local food — «местная кухня». Parochial — "
                            "«приходский, узколобый», не про еду"},
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
            "cordial", "palatial", "vigorous", "mirthful", "indelible",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "warm",
             "context_hint": "Тёплый вечер",
             "explanation": "Warm — «тёплый». Cordial — «сердечный», "
                            "про отношения, не про вечер"},
            {"step_number": 2, "correct_word": "splendid",
             "context_hint": "Великолепная еда",
             "explanation": "Splendid — «великолепный». Palatial — "
                            "«дворцовый», про здание, не про еду"},
            {"step_number": 3, "correct_word": "ambitious",
             "context_hint": "Амбициозные планы",
             "explanation": "Ambitious — «амбициозный». Vigorous — "
                            "«энергичный», про действие, не про план"},
            {"step_number": 4, "correct_word": "amusing",
             "context_hint": "Забавные истории",
             "explanation": "Amusing — «забавный». Mirthful — "
                            "«весёлый», книжное, чаще о человеке"},
            {"step_number": 5, "correct_word": "memorable",
             "context_hint": "Незабываемый вечер",
             "explanation": "Memorable — «запоминающийся». Indelible — "
                            "«неизгладимый», о следе или впечатлении, слишком сильно"},
        ],
    },

    # ---- synonym_battle ------------------------------------------------
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
            "proclaimed", "blessed", "countenanced",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "announced",
             "context_hint": "Официально объявить о запуске",
             "explanation": "Announced — «объявили». Proclaimed — "
                            "«провозгласили», слишком пафосно для релиза"},
            {"step_number": 2, "correct_word": "praised",
             "context_hint": "Публично похвалить результаты",
             "explanation": "Praised — «хвалили». Blessed — "
                            "«благословили», религиозный оттенок"},
            {"step_number": 3, "correct_word": "welcomed",
             "context_hint": "Аналитики одобрили заявление",
             "explanation": "Welcomed — «приветствовали». Countenanced — "
                            "«допустили, смирились», книжное"},
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
            "undertook", "prophesied", "buttressed",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "conducted",
             "context_hint": "Провели эксперимент",
             "explanation": "Conducted an experiment — устойчивое выражение. "
                            "Undertook — «предприняли», книжное"},
            {"step_number": 2, "correct_word": "predicted",
             "context_hint": "Предсказали результат до его появления",
             "explanation": "Predicted — «предсказали» (научный контекст). "
                            "Prophesied — «пророчили», мистический оттенок"},
            {"step_number": 3, "correct_word": "confirmed",
             "context_hint": "Результаты подтвердили гипотезу",
             "explanation": "Confirmed — «подтвердили». Buttressed — "
                            "«укрепили», образно, про аргументы"},
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
            "propounded", "gainsaid", "retaliated",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "introduced",
             "context_hint": "Министр представил новую политику",
             "explanation": "Introduced — «представил». Propounded — "
                            "«выдвинул», книжное, про теорию"},
            {"step_number": 2, "correct_word": "opposed",
             "context_hint": "Критики выступили против",
             "explanation": "Opposed — «выступили против». Gainsaid — "
                            "«отрицали», устаревшее"},
            {"step_number": 3, "correct_word": "reacted",
             "context_hint": "Публика отреагировала неоднозначно",
             "explanation": "Reacted — «отреагировала». Retaliated — "
                            "«нанесли ответный удар», слишком агрессивно"},
        ],
    },

    # ---- boss ----------------------------------------------------------
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
            "betrayed", "ponderous", "conceded", "sedulous", "prescribed",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "revealed",
             "context_hint": "Отчёт показал/раскрыл рост",
             "explanation": "Revealed — «показал, раскрыл». Betrayed — "
                            "«выдал (нечаянно)», с негативным оттенком"},
            {"step_number": 2, "correct_word": "substantial",
             "context_hint": "Существенный рост",
             "explanation": "Substantial — «существенный». Ponderous — "
                            "«тяжеловесный, неуклюжий»"},
            {"step_number": 3, "correct_word": "acknowledged",
             "context_hint": "Руководство признало усилия",
             "explanation": "Acknowledged — «признали». Conceded — "
                            "«уступили, признали с неохотой»"},
            {"step_number": 4, "correct_word": "tireless",
             "context_hint": "Неустанные усилия команды",
             "explanation": "Tireless — «неустанный». Sedulous — "
                            "«старательный», формальное и книжное"},
            {"step_number": 5, "correct_word": "recommended",
             "context_hint": "Рекомендовали дальнейшие инвестиции",
             "explanation": "Recommended — «рекомендовали». Prescribed — "
                            "«предписали», медицинский или строгий оттенок"},
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
            "proclaimed", "epochal", "gainsaid", "evoked", "commemorated",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "announced",
             "context_hint": "Учёные объявили об открытии",
             "explanation": "Announced — «объявили». Proclaimed — "
                            "«провозгласили», пафосно"},
            {"step_number": 2, "correct_word": "groundbreaking",
             "context_hint": "Прорывное открытие",
             "explanation": "Groundbreaking — «прорывное». Epochal — "
                            "«эпохальное», слишком громко"},
            {"step_number": 3, "correct_word": "challenged",
             "context_hint": "Результаты оспорили прежние теории",
             "explanation": "Challenged — «оспорили». Gainsaid — "
                            "«отрицали», устаревшее"},
            {"step_number": 4, "correct_word": "raised",
             "context_hint": "Поставили новые вопросы (raise questions)",
             "explanation": "Raise questions — устойчивое выражение. "
                            "Evoked — «вызывали», про воспоминания"},
            {"step_number": 5, "correct_word": "celebrated",
             "context_hint": "Сообщество отпраздновало прорыв",
             "explanation": "Celebrated — «отпраздновало». Commemorated — "
                            "«почтили память», про памятные даты"},
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
            "required", "reproved", "insubstantial", "adjured", "abate",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "demanded",
             "context_hint": "Передовица потребовала срочных действий",
             "explanation": "Demanded — «потребовала». Required — "
                            "«требовала» (нейтрально, о правилах)"},
            {"step_number": 2, "correct_word": "criticized",
             "context_hint": "Раскритиковала правительство",
             "explanation": "Criticized — «раскритиковала». Repreved — "
                            "«упрекнула», мягче"},
            {"step_number": 3, "correct_word": "inadequate",
             "context_hint": "Неадекватная политика",
             "explanation": "Inadequate — «неадекватная». Insubstantial — "
                            "«несущественная, бесплотная»"},
            {"step_number": 4, "correct_word": "urged",
             "context_hint": "Призвала граждан (urge smb to do)",
             "explanation": "Urged — «призвала». Adjured — "
                            "«заклинала», устаревшее и книжное"},
            {"step_number": 5, "correct_word": "reduce",
             "context_hint": "Сократить потребление",
             "explanation": "Reduce — «сократить». Abate — "
                            "«ослабить», про бурю или боль"},
        ],
    },
]


# ---- Дополнительные задания: 4-й набор по механикам ------------------------

APPEND_TASKS: list[dict] = [
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
            "onerous", "gruelling", "taxing",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "difficult",
             "context_hint": "Задача, которую трудно решить",
             "explanation": "Difficult — базовое «трудный». Onerous — "
                            "«обременительный», формальное"},
            {"step_number": 2, "correct_word": "hard",
             "context_hint": "Синоним difficult",
             "explanation": "Hard — простой и частотный синоним difficult. "
                            "Gruelling — «изнурительный», слишком сильно"},
            {"step_number": 3, "correct_word": "challenging",
             "context_hint": "Инструкции, требующие усилий",
             "explanation": "Challenging — «требующий усилий, бросающий вызов». "
                            "Taxing — «утомительный», книжное"},
        ],
    },
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
            "commodious", "sagacious", "taciturn",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "large",
             "context_hint": "Класс для тридцати учеников должен быть большим",
             "explanation": "Large — базовое «большой». Commodious — "
                            "«поместительный», книжное"},
            {"step_number": 2, "correct_word": "clever",
             "context_hint": "Миа быстро решила головоломку — она умная",
             "explanation": "Clever — «умный, сообразительный». Sagacious — "
                            "«проницательный», формальное"},
            {"step_number": 3, "correct_word": "silent",
             "context_hint": "Не шуметь, пока спит ребёнок",
             "explanation": "Silent — «тихий, молчащий». Taciturn — "
                            "«неразговорчивый» (о человеке), не о действии"},
        ],
    },
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
            "blizzarding", "furious", "gelid", "homely",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "chilly",
             "context_hint": "Прохладное утро, но не мороз",
             "explanation": "Chilly — «прохладно». Blizzarding — "
                            "«с метелью», не про утро"},
            {"step_number": 2, "correct_word": "fierce",
             "context_hint": "Сильный, резкий ветер",
             "explanation": "Fierce — «свирепый, сильный». Furious — "
                            "«яростный», обычно о человеке"},
            {"step_number": 3, "correct_word": "freezing",
             "context_hint": "Озеро почти замёрзло",
             "explanation": "Freezing — «ледяной». Gelid — "
                            "«студёный», поэтическое"},
            {"step_number": 4, "correct_word": "cozy",
             "context_hint": "Уютный плед дома",
             "explanation": "Cozy — «уютный». Homely — "
                            "«домашний, простой» (BrE) или «некрасивый» (AmE)"},
        ],
    },
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
            "ogled", "fancied", "creating",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "looked",
             "context_hint": "Посмотрел в окно — look out of the window",
             "explanation": "Look out of the window — устойчивое выражение. "
                            "Ogled — «пялился», грубовато"},
            {"step_number": 2, "correct_word": "enjoyed",
             "context_hint": "Получал удовольствие от еды и атмосферы",
             "explanation": "Enjoyed — «получал удовольствие». Fancied — "
                            "«хотел, желал» (BrE)"},
            {"step_number": 3, "correct_word": "making",
             "context_hint": "Прокладывали путь к столу — make one's way",
             "explanation": "Make one's way — «прокладывать путь». "
                            "Creating — «создавали», не по смыслу"},
        ],
    },
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
            "contrive", "reckoned", "fractured", "Notwithstanding", "furnishes",
        ],
        "steps": [
            {"step_number": 1, "correct_word": "manage",
             "context_hint": "Суметь добиться — manage to do smth",
             "explanation": "Manage to do — «суметь». Contrive — "
                            "«ухитриться», книжное"},
            {"step_number": 2, "correct_word": "considered",
             "context_hint": "Её подачу считают одной из лучших",
             "explanation": "Considered — «считается». Reckoned — "
                            "«полагают», разговорно"},
            {"step_number": 3, "correct_word": "broke",
             "context_hint": "Побила рекорд турнира — break a record",
             "explanation": "Break a record — «побить рекорд». "
                            "Fractured — «сломала» (физически)"},
            {"step_number": 4, "correct_word": "Although",
             "context_hint": "Хотя она была в двух очках от поражения",
             "explanation": "Although — «хотя», обычный союз. "
                            "Notwithstanding — «несмотря на», очень формальное"},
            {"step_number": 5, "correct_word": "provides",
             "context_hint": "Благотворительная организация обеспечивает возможности",
             "explanation": "Provides — «обеспечивает». Furnishes — "
                            "«снабжает», формальное, чаще о мебели"},
        ],
    },
]

SEED_TASKS.extend(APPEND_TASKS)


__all__ = ["SEED_TASKS"]