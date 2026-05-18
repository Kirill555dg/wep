"""
Сид данных для базы WEP:
- Пользователи (учителя и студенты)
- Теги
- Тесты с медиа-файлами
- Вопросы разных типов (single, multiple, text, matching, file_upload)
"""
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

from app.core import get_password_hash
from app.models import User, Tag, Test, Question, Option, TestTag
from app.db.session import AsyncSessionLocal, ASYNC_DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SyncBase = declarative_base()
engine = create_engine(ASYNC_DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'))
SyncSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
from app.schemas.test_constructor import QuestionType

ASSETS_DIR = Path(__file__).parent.parent / 'tools' / 'assets'
MEDIA_BASE_URL = 'http://localhost:9000/media/wep'


def get_file_url(filename):
    if filename.startswith('http'):
        return filename
    if Path(filename).exists():
        return f'{MEDIA_BASE_URL}/{filename}'
    return filename


def hash_asset_file(filepath):
    if not Path(filepath).exists():
        return None

    with open(filepath, 'rb') as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
        return file_hash.hexdigest()


def seed_users():
    db = SyncSessionLocal()

    existing = db.query(User).count()
    if existing > 0:
        print('Users already exist, skipping...')
        db.close()
        return []

    users = [
        {
            'email': 'teacher1@edu.ru',
            'username': 'teacher_mikhail',
            'password': 'password123',
            'first_name': 'Михаил',
            'last_name': 'Иванов',
            'middle_name': 'Сергеевич',
        },
        {
            'email': 'teacher2@edu.ru',
            'username': 'teacher_anastasia',
            'password': 'password123',
            'first_name': 'Анастасия',
            'last_name': 'Петрова',
            'middle_name': 'Алексеевна',
        },
        {
            'email': 'student1@edu.ru',
            'username': 'student_alex',
            'password': 'password123',
            'first_name': 'Александр',
            'last_name': 'Козлов',
            'middle_name': None,
        },
        {
            'email': 'student2@edu.ru',
            'username': 'student_elena',
            'password': 'password123',
            'first_name': 'Елена',
            'last_name': 'Сидорова',
            'middle_name': None,
        },
    ]

    created_users = []
    for user_data in users:
        user = User(
            email=user_data['email'],
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            middle_name=user_data['middle_name'],
            full_name=f"{user_data['last_name']} {user_data['first_name']} {user_data.get('middle_name', '')}".strip(),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
from app.models import LoginData
        login = LoginData(
            user=user,
            hashed_password=get_password_hash(user_data['password']),
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.add(login)
        created_users.append(user)

    db.commit()
    print(f'Created {len(created_users)} users')
    db.close()

    return created_users


def seed_tags():
    db = SyncSessionLocal()

    existing = db.query(Tag).count()
    if existing > 0:
        print('Tags already exist, skipping...')
        db.close()
        return []

    tags_data = [
        {'name': 'Математика', 'slug': 'mathematics'},
        {'name': 'Физика', 'slug': 'physics'},
        {'name': 'Химия', 'slug': 'chemistry'},
        {'name': 'История', 'slug': 'history'},
        {'name': 'География', 'slug': 'geography'},
        {'name': 'Практикум', 'slug': 'lab'},
    ]

    created_tags = []
    for tag_data in tags_data:
        tag = Tag(**tag_data)
        db.add(tag)
        created_tags.append(tag)

    db.commit()
    print(f'Created {len(created_tags)} tags')
    db.close()

    return created_tags


def seed_tests(users, tags):
    db = SyncSessionLocal()

    existing = db.query(Test).count()
    if existing > 0:
        print('Tests already exist, skipping...')
        db.close()
        return []

    teacher1 = users[0]
    teacher2 = users[1]
    math_tag = tags[0]
    physics_tag = tags[1]
    chem_tag = tags[2]

    tests_data = [
        {
            'author': teacher1,
            'title': 'Линейная алгебра: базовые понятия',
            'description': 'Тест по основам линейной алгебры. Определители, матрицы и векторы.',
            'is_public': True,
            'time_limit_minutes': 30,
            'attempt_limit': 3,
            'track_time': True,
            'tags': [math_tag],
            'media_files': [get_file_url('img_0.bmp'), get_file_url('img_1.bmp')],
        },
        {
            'author': teacher1,
            'title': 'Кинематика точки',
            'description': 'Определения и формулы для описания движения материальной точки.',
            'is_public': True,
            'time_limit_minutes': 20,
            'attempt_limit': None,
            'track_time': True,
            'tags': [physics_tag],
            'media_files': [get_file_url('img_2.bmp')],
        },
        {
            'author': teacher2,
            'title': 'Органическая химия: алканы',
            'description': 'Строение, номенклатура и свойства алифатических углеводородов.',
            'is_public': True,
            'time_limit_minutes': 15,
            'attempt_limit': 2,
            'track_time': False,
            'tags': [chem_tag],
            'media_files': [get_file_url('img_3.bmp'), get_file_url('img_4.bmp'), get_file_url('audio_01.wav')],
        },
        {
            'author': teacher2,
            'title': 'Практикум по дифференциальным уравнениям',
            'description': 'Черновой тест для отработки решения дифференциальных уравнений.',
            'is_public': False,
            'time_limit_minutes': None,
            'attempt_limit': None,
            'track_time': True,
            'tags': [math_tag, physics_tag],
            'media_files': [],
        },
    ]

    created_tests = []
    for test_data in tests_data:
        test = Test(
            author_id=test_data['author'].id,
            title=test_data['title'],
            description=test_data['description'],
            is_public=test_data['is_public'],
            time_limit_minutes=test_data['time_limit_minutes'],
            attempt_limit=test_data['attempt_limit'],
            track_time=test_data['track_time'],
            completion_message='Спасибо за прохождение теста! Ваш результат доступен в истории.',
            image_url=None,
            media_files=test_data['media_files'],
            questions_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(test)
        test_data['test_obj'] = test
        created_tests.append(test)

    db.flush()

    for test_data in tests_data:
        test_obj = test_data['test_obj']
        for tag in test_data['tags']:
            test_tag = TestTag(test_id=test_obj.id, tag_id=tag.id)
            db.add(test_tag)

    db.commit()
    print(f'Created {len(created_tests)} tests')
    db.close()

    return [t['test_obj'] for t in tests_data]


def seed_questions(tests):
    db = SyncSessionLocal()

    existing = db.query(Question).count()
    if existing > 0:
        print('Questions already exist, skipping...')
        db.close()
        return []

    questions_data = []

    test1 = tests[0]
    questions_data.extend([
        {
            'test': test1,
            'type': QuestionType.SINGLE,
            'text': 'Что такое определитель квадратной матрицы?',
            'points': 2,
            'media_files': [get_file_url('img_0.bmp')],
            'options': [
                {'text': 'Число, вычисляемое из элементов квадратной матрицы', 'is_correct': True},
                {'text': 'Произведение матрицы на число', 'is_correct': False},
                {'text': 'Сумма элементов главной диагонали', 'is_correct': False},
                {'text': 'Матрица, обратная данной', 'is_correct': False},
            ],
        },
        {
            'test': test1,
            'type': QuestionType.MULTIPLE,
            'text': 'Какие операции определены для матриц одинакового размера?',
            'points': 3,
            'media_files': [],
            'options': [
                {'text': 'Сложение', 'is_correct': True},
                {'text': 'Умножение на число', 'is_correct': True},
                {'text': 'Взятие корня', 'is_correct': False},
                {'text': 'Вычитание', 'is_correct': True},
            ],
        },
        {
            'test': test1,
            'type': QuestionType.TEXT,
            'text': 'Запишите формулу для вычисления определителя матрицы 2×2: $\\det(A) = ad - bc$',
            'points': 2,
            'media_files': [get_file_url('img_1.bmp')],
        },
    ])

    test2 = tests[1]
    questions_data.extend([
        {
            'test': test2,
            'type': QuestionType.SINGLE,
            'text': 'Какой вектор называется вектором скорости?',
            'points': 1,
            'media_files': [get_file_url('img_2.bmp')],
            'options': [
                {'text': 'Производная радиус-вектора по времени', 'is_correct': True},
                {'text': 'Вторая производная координаты по времени', 'is_correct': False},
                {'text': 'Интеграл скорости по времени', 'is_correct': False},
                {'text': 'Сумма векторов перемещения', 'is_correct': False},
            ],
        },
        {
            'test': test2,
            'type': QuestionType.MATCHING,
            'text': 'Сопоставьте физические величины с их единицами измерения',
            'points': 2,
            'media_files': [],
            'options': [
                {'text': 'Скорость', 'is_correct': True, 'match_key': 'a'},
                {'text': 'Ускорение', 'is_correct': True, 'match_key': 'b'},
                {'text': 'м/с', 'is_correct': True, 'match_key': 'a'},
                {'text': 'м/с²', 'is_correct': True, 'match_key': 'b'},
            ],
        },
    ])

    test3 = tests[2]
    questions_data.extend([
        {
            'test': test3,
            'type': QuestionType.MULTIPLE,
            'text': 'Выберите правильные утверждения об алканах:',
            'points': 3,
            'media_files': [get_file_url('img_3.bmp'), get_file_url('img_4.bmp'), get_file_url('audio_01.wav')],
            'options': [
                {'text': 'Общая формула $C_nH_{2n+2}$', 'is_correct': True},
                {'text': 'Имеют двойные связи', 'is_correct': False},
                {'text': 'Предельные углеводороды', 'is_correct': True},
                {'text': 'Реагируют с кислородом', 'is_correct': True},
            ],
        },
    ])

    test4 = tests[3]
    questions_data.extend([
        {
            'test': test4,
            'type': QuestionType.FILE_UPLOAD,
            'text': 'Решите дифференциальное уравнение $y\' = 2y + 3$ и загрузите файл с решением в формате .pdf или .txt',
            'points': 5,
            'media_files': [],
            'options': [],
        },
    ])

    created_questions = []
    for q_data in questions_data:
        question = Question(
            test_id=q_data['test'].id,
            question_type=q_data['type'],
            text=q_data['text'],
            points=q_data['points'],
            media_files=q_data.get('media_files', []),
            order=len(qs for qs in questions_data if qs['test'] == q_data['test']) - len(qs for qs in created_questions if qs['test_id'] == q_data['test'].id),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            explanation=None,
        )
        db.add(question)
        q_data['question_obj'] = question
        created_questions.append(question)

    db.flush()

    for q_data in questions_data:
        question_obj = q_data['question_obj']
        for opt_data in q_data.get('options', []):
            option = Option(
                question_id=question_obj.id,
                text=opt_data['text'],
                is_correct=opt_data['is_correct'],
                match_key=opt_data.get('match_key'),
                order=len(opt for opt in q_data.get('options', []) if opt == opt_data),
            )
            db.add(option)

    for test in tests:
        test.questions_count = len([q for q in questions_data if q['test'].id == test.id])

    db.commit()
    print(f'Created {len(created_questions)} questions')
    db.close()

    return created_questions


def seed_all():
    print('Starting database seed...')
    users = seed_users()
    tags = seed_tags()
    tests = seed_tests(users, tags)
    seed_questions(tests)
    print('Database seed completed!')


if __name__ == '__main__':
    seed_all()
