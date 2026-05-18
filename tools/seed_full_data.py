#!/usr/bin/env python3
"""
Seed full test data into the running local WEP backend.

Usage:
    cd /Users/kerrodar/Dev/wep
    python tools/seed_full_data.py

Prerequisites:
    - Backend running on http://localhost:8023
    - Postgres and MinIO containers up (docker-compose up -d postgres minio)

What it creates:
    - 2 users (teacher + student)
    - 6 tests with varied question types and media
    - 10 images, 2 audio, 1 video, 2 answer files
    - 2 attempts by the student (1 completed, 1 in-progress)
"""

from __future__ import annotations

import asyncio
import io
import json
import os
import pathlib
import random
import struct
import sys
import time
import wave

import httpx

BASE_URL = "http://localhost:8023/api/v1"
ASSETS_DIR = pathlib.Path(__file__).with_suffix("").parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


# ───────────────────────── HTTP helpers ─────────────────────────

class ApiClient:
    def __init__(self, base: str = BASE_URL) -> None:
        self.client = httpx.AsyncClient(base_url=base, timeout=30.0)
        self._token: str | None = None

    @property
    def headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    async def post(self, path: str, json_data: dict | None = None, files: dict | None = None) -> httpx.Response:
        if files:
            resp = await self.client.post(path, files=files, headers={"Authorization": f"Bearer {self._token}"} if self._token else {})
        else:
            resp = await self.client.post(path, json=json_data, headers=self.headers)
        return resp

    async def get(self, path: str, params: dict | None = None) -> httpx.Response:
        return await self.client.get(path, params=params, headers=self.headers)

    async def patch(self, path: str, json_data: dict | None = None) -> httpx.Response:
        return await self.client.patch(path, json=json_data, headers=self.headers)

    async def close(self) -> None:
        await self.client.aclose()


# ───────────────────────── Asset download / generation ─────────────────────────

async def download_image(client: httpx.AsyncClient, seed: int, out_path: pathlib.Path) -> bool:
    """Download a 300x200 image from picsum (lightweight, ~10KB)."""
    url = f"https://picsum.photos/seed/{seed}/300/200"
    try:
        resp = await client.get(url, timeout=15.0)
        if resp.status_code == 200:
            out_path.write_bytes(resp.content)
            return True
    except Exception as exc:
        print(f"  [!] Image download failed: {exc}")
    return False


def generate_wav(path: pathlib.Path, duration_sec: float = 2.0) -> None:
    """Generate a simple sine-wave WAV file (no external deps)."""
    sample_rate = 8000
    num_samples = int(sample_rate * duration_sec)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        for i in range(num_samples):
            val = int(32767 * 0.3 * (1 if (i // 20) % 2 else -1))
            w.writeframes(struct.pack("<h", val))


def generate_txt(path: pathlib.Path, content: str = "Student answer file\n") -> None:
    path.write_text(content, encoding="utf-8")


def generate_pdf_stub(path: pathlib.Path) -> None:
    """Generate a minimal valid PDF (header + trailer)."""
    pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\ntrailer\n<< /Size 3 /Root 1 0 R >>\nstartxref\n110\n%%EOF\n"
    path.write_bytes(pdf)


# ───────────────────────── Seeding logic ─────────────────────────

async def create_user(api: ApiClient, email: str, password: str, first_name: str, last_name: str) -> dict:
    resp = await api.post("/auth/register", {
        "email": email, "password": password,
        "first_name": first_name, "last_name": last_name,
    })
    if resp.status_code == 201:
        data = resp.json()
        print(f"  [+] User registered: {email} (id={data['id']})")
        return data
    if resp.status_code == 409:
        print(f"  [=] User already exists: {email}")
        return {"email": email}
    print(f"  [!] Register failed: {resp.status_code} {resp.text}")
    return {}


async def login(api: ApiClient, email: str, password: str) -> bool:
    resp = await api.post("/auth/login", {"username_or_email": email, "password": password})
    if resp.status_code == 200:
        api._token = resp.json()["access_token"]
        print(f"  [+] Logged in: {email}")
        return True
    print(f"  [!] Login failed: {resp.status_code} {resp.text}")
    return False


async def upload_media(api: ApiClient, file_path: pathlib.Path, content_type: str) -> str | None:
    """Upload a file and return its public URL."""
    with file_path.open("rb") as f:
        files = {"file": (file_path.name, f, content_type)}
        resp = await api.post("/media/upload", files=files)
    if resp.status_code == 201:
        url = resp.json().get("url")
        print(f"  [+] Uploaded {file_path.name} -> {url}")
        return url
    print(f"  [!] Upload failed ({resp.status_code}): {resp.text[:200]}")
    return None


async def upload_answer_file(api: ApiClient, file_path: pathlib.Path, content_type: str) -> str | None:
    with file_path.open("rb") as f:
        files = {"file": (file_path.name, f, content_type)}
        resp = await api.post("/media/upload-answer", files=files)
    if resp.status_code == 201:
        url = resp.json().get("url")
        print(f"  [+] Uploaded answer {file_path.name} -> {url}")
        return url
    print(f"  [!] Upload-answer failed ({resp.status_code}): {resp.text[:200]}")
    return None


async def create_test(api: ApiClient, title: str, **kwargs) -> dict:
    body = {"title": title, **kwargs}
    resp = await api.post("/tests/", body)
    if resp.status_code == 201:
        data = resp.json()
        print(f"  [+] Test created: '{title}' (id={data['id']})")
        return data
    print(f"  [!] Create test failed: {resp.status_code} {resp.text[:300]}")
    return {}


async def add_question(api: ApiClient, test_id: int, **kwargs) -> dict:
    resp = await api.post(f"/tests/{test_id}/questions", kwargs)
    if resp.status_code == 201:
        data = resp.json()
        print(f"    [+] Question added: {kwargs.get('question_type')} (id={data['id']})")
        return data
    print(f"    [!] Add question failed: {resp.status_code} {resp.text[:300]}")
    return {}


async def start_attempt(api: ApiClient, test_id: int) -> dict:
    resp = await api.post("/attempts/", {"test_id": test_id})
    if resp.status_code == 201:
        data = resp.json()
        print(f"  [+] Attempt started: id={data['id']}")
        return data
    return {}


async def submit_answer(api: ApiClient, attempt_id: int, question_id: int, **kwargs) -> None:
    body = {"question_id": question_id, **kwargs}
    resp = await api.post(f"/attempts/{attempt_id}/answers", body)
    if resp.status_code in (200, 201):
        print(f"    [+] Answer submitted for q={question_id}")
    else:
        print(f"    [!] Answer submit failed: {resp.status_code} {resp.text[:200]}")


async def finish_attempt(api: ApiClient, attempt_id: int) -> dict:
    resp = await api.post(f"/attempts/{attempt_id}/finish", {})
    if resp.status_code == 200:
        data = resp.json()
        print(f"  [+] Attempt finished: score={data.get('score')}/{data.get('max_score')}")
        return data
    print(f"  [!] Finish attempt failed: {resp.status_code} {resp.text[:200]}")
    return {}


# ───────────────────────── Main flow ─────────────────────────

async def main() -> int:
    print("=" * 60)
    print("WEP Full Data Seeder")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)

    assets = {}
    dl_client = httpx.AsyncClient(timeout=20.0)

    # 1. Prepare assets -------------------------------------------------------
    print("\n--- Phase 1: Prepare assets ---")
    images_to_fetch = 10
    downloaded = 0
    for i in range(images_to_fetch):
        img_path = ASSETS_DIR / f"img_{i}.jpg"
        if not img_path.exists():
            ok = await download_image(dl_client, i, img_path)
            if ok:
                downloaded += 1
        else:
            downloaded += 1
    print(f"  [+] Images ready: {downloaded}/{images_to_fetch}")

    # Fallback: generate a tiny BMP if images missing
    if downloaded < 3:
        for i in range(5):
            bmp_path = ASSETS_DIR / f"img_{i}.bmp"
            if not bmp_path.exists():
                # Minimal 2x2 24-bit BMP (no deps)
                bmp = b"BM" + b"\x46\x00\x00\x00" + b"\x00\x00" + b"\x00\x00" + b"\x36\x00\x00\x00" + b"\x28\x00\x00\x00" + b"\x02\x00\x00\x00" + b"\x02\x00\x00\x00" + b"\x01\x00\x18\x00" + b"\x00\x00\x00\x00" + b"\x10\x00\x00\x00" + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" + bytes(16)
                bmp_path.write_bytes(bmp)
        print(f"  [+] Generated {5} fallback BMPs")

    # Audio (WAV) – no external deps
    wav_path = ASSETS_DIR / "audio_01.wav"
    if not wav_path.exists():
        generate_wav(wav_path, duration_sec=2.0)
        print(f"  [+] Generated WAV: {wav_path}")

    wav_path2 = ASSETS_DIR / "audio_02.wav"
    if not wav_path2.exists():
        generate_wav(wav_path2, duration_sec=1.5)
        print(f"  [+] Generated WAV: {wav_path2}")

    # Text answer files
    txt_path = ASSETS_DIR / "answer_01.txt"
    if not txt_path.exists():
        generate_txt(txt_path, "This is my essay answer.\nIt has multiple lines.\n")
        print(f"  [+] Generated TXT: {txt_path}")

    # PDF stub
    pdf_path = ASSETS_DIR / "answer_02.pdf"
    if not pdf_path.exists():
        generate_pdf_stub(pdf_path)
        print(f"  [+] Generated PDF stub: {pdf_path}")

    await dl_client.aclose()

    # 2. Create users and login ----------------------------------------------
    print("\n--- Phase 2: Create users ---")
    api = ApiClient()

    teacher = await create_user(api, "teacher@wep.dev", "TeacherPass123!", "Иван", "Преподаватель")
    student = await create_user(api, "student@wep.dev", "StudentPass123!", "Петр", "Студент")

    if not await login(api, "teacher@wep.dev", "TeacherPass123!"):
        print("[!] Cannot login as teacher. Abort.")
        return 1

    # 3. Upload media --------------------------------------------------------
    print("\n--- Phase 3: Upload media ---")
    for fpath in sorted(ASSETS_DIR.glob("img_*")):
        url = await upload_media(api, fpath, "image/jpeg")
        if url:
            assets[fpath.stem] = url

    wav_url = await upload_answer_file(api, wav_path, "audio/wav")
    if wav_url:
        assets["audio_01"] = wav_url

    wav2_url = await upload_answer_file(api, wav_path2, "audio/wav")
    if wav2_url:
        assets["audio_02"] = wav2_url

    txt_url = await upload_answer_file(api, txt_path, "text/plain")
    if txt_url:
        assets["answer_01"] = txt_url

    pdf_url = await upload_answer_file(api, pdf_path, "application/pdf")
    if pdf_url:
        assets["answer_02"] = pdf_url

    # 4. Create tests --------------------------------------------------------
    print("\n--- Phase 4: Create tests ---")

    tests: list[dict] = []

    # Test 1: Math with Typst formulas
    t1 = await create_test(api, "Математика: Производные", description="Вычислите производные\\n$f(x) = x^2$", is_public=True, track_time=True, time_limit_minutes=15, tag_names=["math", "calculus"], image_url=assets.get("img_0"))
    tests.append(t1)

    # Test 2: Physics with image question
    t2 = await create_test(api, "Физика: Механика", description="Задачи по кинематике и динамике", is_public=True, track_time=True, time_limit_minutes=20, tag_names=["physics", "mechanics"], image_url=assets.get("img_1"))
    tests.append(t2)

    # Test 3: CS with matching
    t3 = await create_test(api, "Информатика: Алгоритмы", description="Сопоставьте термины и определения", is_public=True, track_time=True, time_limit_minutes=10, tag_names=["cs", "algorithms"])
    tests.append(t3)

    # Test 4: English listening (audio)
    t4 = await create_test(api, "Английский: Аудирование", description="Прослушайте аудио и ответьте", is_public=True, track_time=True, time_limit_minutes=25, tag_names=["english", "listening"], image_url=assets.get("img_2"))
    tests.append(t4)

    # Test 5: Chemistry with file upload
    t5 = await create_test(api, "Химия: Органика", description="Загрузите решение в формате PDF", is_public=True, track_time=False, tag_names=["chemistry", "organic"], image_url=assets.get("img_3"))
    tests.append(t5)

    # Test 6: Geometry (essay + many questions)
    t6 = await create_test(api, "Геометрия", description="Доказательства и вычисления", is_public=True, track_time=True, time_limit_minutes=30, tag_names=["math", "geometry"])
    tests.append(t6)

    # 5. Add questions --------------------------------------------------------
    print("\n--- Phase 5: Add questions ---")

    if t1:
        # Single choice with image
        q1 = await add_question(api, t1["id"], question_type="SINGLE_CHOICE", text="Чему равна $f'(x)$ для $f(x)=x^3$?", points=2, options=[
            {"text": "$3x^2$", "is_correct": True, "order_number": 1},
            {"text": "$x^2$", "is_correct": False, "order_number": 2},
            {"text": "$3x$", "is_correct": False, "order_number": 3},
        ], image_url=assets.get("img_4"))

        await add_question(api, t1["id"], question_type="SINGLE_CHOICE", text="Производная $\\sin(x)$:", points=1, options=[
            {"text": "$\\cos(x)$", "is_correct": True, "order_number": 1},
            {"text": "$-\\sin(x)$", "is_correct": False, "order_number": 2},
        ])

        await add_question(api, t1["id"], question_type="TEXT", text="Запишите производную $e^x$:", points=1, correct_answer="$e^x$")

    if t2:
        await add_question(api, t2["id"], question_type="MULTIPLE_CHOICE", text="Какие силы действуют на тело на наклонной плоскости?", points=2, options=[
            {"text": "Сила тяжести", "is_correct": True, "order_number": 1},
            {"text": "Сила реакции опоры", "is_correct": True, "order_number": 2},
            {"text": "Сила Кулона", "is_correct": False, "order_number": 3},
            {"text": "Сила трения", "is_correct": True, "order_number": 4},
        ], image_url=assets.get("img_5"))

        await add_question(api, t2["id"], question_type="TEXT", text="Формула второго закона Ньютона:", points=1, correct_answer="F=ma")

    if t3:
        await add_question(api, t3["id"], question_type="MATCHING", text="Сопоставьте алгоритмы:", points=3,
            question_data={"matching_pairs": [
                {"id": 1, "term": "O(n)", "definition": "Линейный поиск"},
                {"id": 2, "term": "O(log n)", "definition": "Бинарный поиск"},
                {"id": 3, "term": "O(n log n)", "definition": "Быстрая сортировка"},
            ]},
            correct_answer="{\"1\": 1, \"2\": 2, \"3\": 3}"
        )

    if t4:
        await add_question(api, t4["id"], question_type="SINGLE_CHOICE", text="Что говорит о температуре?", points=2, options=[
            {"text": "Hot", "is_correct": True, "order_number": 1},
            {"text": "Cold", "is_correct": False, "order_number": 2},
        ])

    if t5:
        await add_question(api, t5["id"], question_type="FILE_UPLOAD", text="Загрузите решение реакции бромирования бензола:", points=5)

    if t6:
        await add_question(api, t6["id"], question_type="SINGLE_CHOICE", text="Теорема Пифагора:", points=1, options=[
            {"text": "$a^2+b^2=c^2$", "is_correct": True, "order_number": 1},
            {"text": "$a+b=c$", "is_correct": False, "order_number": 2},
        ], image_url=assets.get("img_6"))
        await add_question(api, t6["id"], question_type="ESSAY", text="Докажите, что сумма углов треугольника равна 180°:", points=5)

    # 6. Student attempts ----------------------------------------------------
    print("\n--- Phase 6: Student attempts ---")
    if not await login(api, "student@wep.dev", "StudentPass123!"):
        print("[!] Cannot login as student. Abort.")
        return 1

    # Complete test 1 (Math)
    if t1:
        att = await start_attempt(api, t1["id"])
        if att:
            attempt_id = att["id"]
            # Get questions list via test detail
            resp = await api.get(f"/tests/{t1['id']}")
            if resp.status_code == 200:
                qs = resp.json().get("questions", [])
                if len(qs) >= 1:
                    await submit_answer(api, attempt_id, qs[0]["id"], selected_option_ids=[qs[0]["options"][0]["id"]])
                if len(qs) >= 2:
                    await submit_answer(api, attempt_id, qs[1]["id"], selected_option_ids=[qs[1]["options"][0]["id"]])
                if len(qs) >= 3:
                    await submit_answer(api, attempt_id, qs[2]["id"], text_answer="$e^x$")
                await finish_attempt(api, attempt_id)

    # Complete test 5 (Chemistry) with FILE_UPLOAD
    if t5:
        att5 = await start_attempt(api, t5["id"])
        if att5:
            attempt_id_5 = att5["id"]
            resp = await api.get(f"/tests/{t5['id']}")
            if resp.status_code == 200:
                qs = resp.json().get("questions", [])
                if len(qs) >= 1:
                    await submit_answer(api, attempt_id_5, qs[0]["id"], file_answer=assets.get("answer_02"))
                await finish_attempt(api, attempt_id_5)

    # Attempt test 6 (Geometry) – leave in-progress
    if t6:
        att = await start_attempt(api, t6["id"])
        if att:
            attempt_id = att["id"]
            resp = await api.get(f"/tests/{t6['id']}")
            if resp.status_code == 200:
                qs = resp.json().get("questions", [])
                if len(qs) >= 1:
                    await submit_answer(api, attempt_id, qs[0]["id"], selected_option_ids=[qs[0]["options"][0]["id"]])
                # DO NOT finish – left in-progress

    # 7. Verification / Summary ---------------------------------------------
    print("\n--- Phase 7: Verification ---")

    if await login(api, "teacher@wep.dev", "TeacherPass123!"):
        # Stats for each test
        for t in tests:
            if not t:
                continue
            tid = t["id"]
            title = t["title"]
            resp = await api.get(f"/tests/{tid}")
            if resp.status_code == 200:
                data = resp.json()
                q_count = len(data.get("questions", []))
                print(f"  [check] '{title}': {q_count} questions")
            # Attempts
            resp_a = await api.get(f"/tests/{tid}/attempts")
            if resp_a.status_code == 200:
                attempts_data = resp_a.json()
                total = attempts_data.get("total", 0)
                print(f"          {total} attempts")

        # Student history
        await login(api, "student@wep.dev", "StudentPass123!")
        resp_h = await api.get("/attempts/")
        if resp_h.status_code == 200:
            history = resp_h.json()
            print(f"\n  Student history: {history.get('total', 0)} total attempts")

    await api.close()

    print("\n" + "=" * 60)
    print("Seeding complete!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n[!] Interrupted")
        sys.exit(130)
    except Exception as exc:
        print(f"\n[!] Fatal error: {exc}")
        sys.exit(1)
