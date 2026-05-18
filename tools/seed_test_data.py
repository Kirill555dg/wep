#!/usr/bin/env python3
"""Complete test data with tests, questions, tags for WEP"""
import os
import sys
import asyncio
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import httpx

API_URL = "http://localhost:8023/api/v1"

# Complete test data with questions and tags
TESTS_DATA = [
    {
        "title": "Математический анализ",
        "description": "Производные, интегралы и пределы",
        "is_public": True,
        "time_limit_minutes": 30,
        "tags": ["математика", "анализ", "формулы"],
        "questions": [
            {
                "question_type": "single_choice",
                "text": "Чему равна производная функции f(x) = x³?",
                "options": [
                    {"text": "3x²", "is_correct": True},
                    {"text": "3x", "is_correct": False},
                    {"text": "x³", "is_correct": False},
                    {"text": "∂x/∂x", "is_correct": False}
                ],
                "points": 1
            },
            {
                "question_type": "single_choice",
                "text": "Что такое ∫ₐᵇ f(x)dx?",
                "options": [
                    {"text": "Определенный интеграл", "is_correct": True},
                    {"text": "Неопределенный интеграл", "is_correct": False},
                    {"text": "Дифференциал", "is_correct": False},
                    {"text": "Производная", "is_correct": False}
                ],
                "points": 1
            },
            {
                "question_type": "single_choice",
                "text": "lim(x→∞) (1+1/x)ˣ = ?",
                "options": [
                    {"text": "e", "is_correct": True},
                    {"text": "1", "is_correct": False},
                    {"text": "∞", "is_correct": False},
                    {"text": "0", "is_correct": False}
                ],
                "points": 2
            }
        ]
    },
    {
        "title": "Физика: Классическая механика",
        "description": "Законы Ньютона, кинематика, динамика",
        "is_public": True,
        "time_limit_minutes": 25,
        "tags": ["физика", "механика", "ньютон"],
        "questions": [
            {
                "question_type": "single_choice",
                "text": "Второй закон: F = ma. При F=10Н, a=2м/с², масса = ?",
                "options": [
                    {"text": "5 кг", "is_correct": True},
                    {"text": "2 кг", "is_correct": False},
                    {"text": "20 кг", "is_correct": False},
                    {"text": "0.2 кг", "is_correct": False}
                ],
                "points": 1
            },
            {
                "question_type": "text",
                "text": "Сформулируйте первый закон Ньютона",
                "points": 2
            }
        ]
    },
    {
        "title": "Геометрия планиметрия",
        "description": "Фигуры, площади, периметры",
        "is_public": True,
        "time_limit_minutes": 20,
        "tags": ["геометрия", "математика", "школа"],
        "questions": [
            {
                "question_type": "single_choice",
                "text": "Фигура с 4 равными сторонами и углами?",
                "options": [
                    {"text": "Квадрат", "is_correct": True},
                    {"text": "Прямоугольник", "is_correct": False},
                    {"text": "Ромб", "is_correct": False},
                    {"text": "Трапеция", "is_correct": False}
                ],
                "points": 1
            },
            {
                "question_type": "single_choice",
                "text": "Площадь прямоугольника 5×8 = ?",
                "options": [
                    {"text": "40", "is_correct": True},
                    {"text": "13", "is_correct": False},
                    {"text": "26", "is_correct": False},
                    {"text": "20", "is_correct": False}
                ],
                "points": 1
            }
        ]
    },
    {
        "title": "Контрольная по алгебре (Школа)",
        "description": "Линейные уравнения, квадратные уравнения",
        "is_public": False,
        "time_limit_minutes": 45,
        "tags": ["алгебра", "школа", "уравнения"],
        "questions": [
            {
                "question_type": "single_choice",
                "text": "Решите: 2x + 5 = 15",
                "options": [
                    {"text": "x = 5", "is_correct": True},
                    {"text": "x = 10", "is_correct": False},
                    {"text": "x = 7.5", "is_correct": False},
                    {"text": "x = 20", "is_correct": False}
                ],
                "points": 1
            },
            {
                "question_type": "single_choice",
                "text": "x² - 9 = 0. Корни?",
                "options": [
                    {"text": "3 и -3", "is_correct": True},
                    {"text": "3 только", "is_correct": False},
                    {"text": "-3 только", "is_correct": False},
                    {"text": "9 и -9", "is_correct": False}
                ],
                "points": 2
            }
        ]
    }
]

async def create_test_complete(client, token, test_data):
    """Create test with questions, options, tags"""
    
    # Create test
    test = await client.post(
        f"{API_URL}/tests/",
        json={
            "title": test_data["title"],
            "description": test_data["description"],
            "is_public": test_data["is_public"],
            "time_limit_minutes": test_data["time_limit_minutes"]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    test_id = test.json()["id"]
    print(f"✅ Test: {test_data['title']} (id={test_id}, public={test_data['is_public']})")
    
    # Create questions
    for q_data in test_data["questions"]:
        question = await client.post(
            f"{API_URL}/tests/{test_id}/questions/",
            json={
                "question_type": q_data["question_type"],
                "text": q_data["text"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if question.status_code != 201:
            print(f"  ❌ Question failed")
            continue
        
        question_id = question.json()["id"]
        print(f"  ✅ Q: {q_data['text'][:60]}... (id={question_id})")
        
        # Add options for single_choice 
        if q_data["question_type"] == "single_choice":
            for opt_data in q_data["options"]:
                await client.post(
                    f"{API_URL}/tests/{test_id}/questions/{question_id}/options/",
                    json={"text": opt_data["text"], "is_correct": opt_data["is_correct"]},
                    headers={"Authorization": f"Bearer {token}"}
                )
            print(f"    Options added: {len(q_data['options'])}")
        
        # Add tags if they exist
        if test_data.get("tags"):
            for tag in test_data["tags"]:
                try:
                    await client.post(
                        f"{API_URL}/tests/{test_id}/tags/",
                        json={"name": tag},
                        headers={"Authorization": f"Bearer {token}"}
                    )
                except:
                    pass
            print(f"  🏷️  Tags: {', '.join(test_data['tags'])}")
    
    return test_id

async def create_complete_test_data():
    """Create users, tests with all properties"""
    async with httpx.AsyncClient() as client:
        timestamp = random.randint(10000, 99999)
        
        # Create teacher
        print("👥 Creating teacher...")
        await client.post(f"{API_URL}/auth/register", json={
            "email": f"teacher{timestamp}@test.edu",
            "password": " testpass123",
            "first_name": "Учитель",
            "last_name": "Тестовый",
            "username": f"teacher{timestamp}"
        })
        
        # Login
        login = await client.post(f"{API_URL}/auth/login", json={
            "username_or_email": f"teacher{timestamp}@test.edu",
            "password": " testpass123"
        })
        token = login.json()["access_token"]
        print(f"✅ Logged in: teacher{timestamp}@test.edu")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create tests
        print(f"\n📚 Creating {len(TESTS_DATA)} tests...")
        
        created_tests = []
        total_questions = 0
        
        for test_data in TESTS_DATA:
            # Create test
            test = await client.post(
                f"{API_URL}/tests/",
                json={
                    "title": test_data["title"],
                    "description": test_data["description"],
                    "is_public": test_data["is_public"],
                    "time_limit_minutes": test_data["time_limit_minutes"]
                },
                headers=headers
            )
            
            test_id = test.json()["id"]
            q_count = len(test_data["questions"])
            
            print(f"  ✅ {test_data['title']} (id={test_id})")
            
            # Create questions and options
            for q_data in test_data["questions"]:
                question = await client.post(
                    f"{API_URL}/tests/{test_id}/questions/",
                    json={"question_type": q_data["question_type"], "text": q_data["text"]},
                    headers=headers
                )
                
                if question.status_code != 201:
                    print(f"  ❌ Question error: {question.status_code}")
                    continue
                    
                question_id = question.json()["id"]
                
                if q_data["question_type"] == "single_choice":
                    for opt in q_data["options"]:
                        await client.post(
                            f"{API_URL}/tests/{test_id}/questions/{question_id}/options/",
                            json={"text": opt["text"], "is_correct": opt["is_correct"]},
                            headers=headers
                        )
            
            # Add tags
            for tag in test_data.get("tags", []):
                await client.post(
                    f"{API_URL}/tests/{test_id}/tags/",
                    json={"name": tag},
                    headers=headers
                )
            
            created_tests.append({
                "id": test_id,
                "title": test_data["title"],
                "is_public": test_data["is_public"],
                "questions_count": q_count,
                "tags": test_data.get("tags", [])
            })
            total_questions += q_count
        
        # Create student
        print(f"\n👤 Creating student...")
        await client.post(f"{API_URL}/auth/register", json={
            "email": f"student{timestamp}@test.edu",
            "password": " testpass123",
            "first_name": "Студент",
            "last_name": "Тестовый",
            "username": f"student{timestamp}"
        })
        
        # Verify
        print(f"\n📊 Results:")
        print(f"  Tests: {len(created_tests)}")
        print(f"  Total questions: {total_questions}")
        print(f"  Public: {sum(1 for t in created_tests if t['is_public'])}")
        print(f"  Private: {sum(1 for t in created_tests if not t['is_public'])}")
        
        print(f"\n🔐 Credentials:")
        print(f"  Teacher: teacher{timestamp}@test.edu / testpass123")
        print(f"  Student: student{timestamp}@test.edu / testpass123")
        
        print(f"\n✅ All data created in database!")

async def main():
    await create_complete_test_data()

if __name__ == "__main__":
    asyncio.run(main())
