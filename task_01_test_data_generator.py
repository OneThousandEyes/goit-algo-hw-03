#!/usr/bin/env python3
from pathlib import Path
import random
import shutil
from typing import Optional

from faker import Faker

fake = Faker()

EXTENSIONS = [
    "txt", "log", "jpg", "jpeg", "png",
    "gif", "pdf", "doc", "xml", "yml",
]

# ---------------------------
# Генератори читабельних імен
# ---------------------------

def readable_filename() -> str:
    """
    Генерує людське ім’я файлу, напр:
      project_report_012
      travel_photo_003
      user_notes_044
    """
    w1 = fake.word().replace(" ", "_")
    w2 = fake.word().replace(" ", "_")
    num = random.randint(1, 999)
    return f"{w1}_{w2}_{num:03d}"


def readable_dir_name() -> str:
    """
    Генерує людське ім’я каталогу, напр:
      project_data
      system_logs
      client_profiles
    """
    w1 = fake.word().replace(" ", "_")
    w2 = fake.word().replace(" ", "_")
    return f"{w1}_{w2}"


# ---------------------------
# Ввід з клавіатури з дефолтами
# ---------------------------

def ask_int_with_default(prompt: str, default: int, min_value: int = 1) -> int:
    """
    Питає в користувача ціле число.
    Якщо ввід порожній — повертає default.
    Якщо ввід некоректний або < min_value — питає ще раз.
    """
    while True:
        raw = input(f"{prompt} (Enter = {default}): ").strip()
        if raw == "":
            return default
        try:
            value = int(raw)
            if value < min_value:
                print(f"[ERROR] Значення має бути ≥ {min_value}. Спробуйте ще раз.")
                continue
            return value
        except ValueError:
            print("[ERROR] Потрібно ввести ціле число. Спробуйте ще раз.")


# ---------------------------
# Створення каталогу src
# ---------------------------

def create_src_dir(base_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Створює каталог 'src' у base_dir.
    Якщо 'src' вже існує — запитує, чи видалити перед генерацією.
    Повертає Path або None, якщо користувач відмовився.
    """
    if base_dir is None:
        base_dir = Path.cwd()

    src_dir = base_dir / "src"

    if src_dir.exists():
        print(f"[WARN] Каталог '{src_dir}' вже існує.")
        ans = input("Видалити його перед генерацією? [y/N]: ").strip().lower()
        if ans not in ("y", "yes", "т", "так"):
            print("[INFO] Генерацію скасовано користувачем.")
            return None

        try:
            shutil.rmtree(src_dir)
            print(f"[INFO] Старий каталог '{src_dir}' видалено.")
        except Exception as e:
            print(f"[ERROR] Не вдалося видалити '{src_dir}': {e}")
            return None

    try:
        src_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Не вдалося створити каталог '{src_dir}': {e}")
        return None

    return src_dir


# ---------------------------
# Генерація дерева
# ---------------------------

def generate_random_tree(
    root: Path,
    max_depth: int = 3,
    max_dirs_per_level: int = 3,
    max_files_per_level: int = 6,
    min_depth: int = 2,
    min_dirs_per_level: int = 2,
    min_files_per_level: int = 2,
) -> None:
    """Створює читабельну випадкову структуру каталогів і файлів
       з гарантованими мінімальними значеннями глибини/каталогів/файлів.
    """

    def _gen(directory: Path, depth: int):
        # Якщо глибина вже перевищила max_depth — зупиняємось
        if depth > max_depth:
            return

        # ------------------------------------------
        # Визначаємо кількість підкаталогів
        # ------------------------------------------
        if depth < min_depth:
            # Поки не досягли мінімальної глибини — ТІЛЬКИ створюємо каталоги
            num_dirs = random.randint(min_dirs_per_level, max_dirs_per_level)
        else:
            # Після досягнення мінімальної глибини — випадковий вибір
            num_dirs = random.randint(0, max_dirs_per_level)

        # ------------------------------------------
        # Створюємо підкаталоги
        # ------------------------------------------
        subdirs = []
        for _ in range(num_dirs):
            dname = readable_dir_name()
            subdir = directory / dname
            try:
                subdir.mkdir(exist_ok=True)
                subdirs.append(subdir)
            except Exception as e:
                print(f"[ERROR] Не вдалося створити каталог '{subdir}': {e}")

        # Рекурсивно генеруємо структуру в кожному підкаталозі
        for sub in subdirs:
            _gen(sub, depth + 1)

        # ------------------------------------------
        # Визначаємо кількість файлів
        # ------------------------------------------
        if depth < min_depth:
            # Поки не досягли мінімальної глибини —
            # створюємо гарантовано мінімум min_files_per_level
            num_files = random.randint(min_files_per_level, max_files_per_level)
        else:
            # Далі — випадковість, але мінімум 1 файл теж можна вимагати
            num_files = random.randint(min_files_per_level, max_files_per_level)

        # ------------------------------------------
        # Створюємо файли
        # ------------------------------------------
        for _ in range(num_files):
            ext = random.choice(EXTENSIONS)
            fname = f"{readable_filename()}.{ext}"
            fpath = directory / fname

            try:
                if ext in {"jpg", "jpeg", "png", "gif"}:
                    fpath.write_bytes(b"\x89PNG\r\nFAKE_IMAGE_DATA")
                else:
                    fpath.write_text(
                        f"Generated test file: {fname}\n",
                        encoding="utf-8",
                    )
            except Exception as e:
                print(f"[ERROR] Не вдалося записати файл '{fpath}': {e}")

    # Старт рекурсії з кореня
    _gen(root, 1)



# ---------------------------
# MAIN
# ---------------------------

def main() -> None:
    random.seed()

    print("=== Генератор тестових даних у каталог 'src' ===")

    # Запитуємо параметри з клавіатури
    max_depth = ask_int_with_default(
        "Максимальна глибина вкладеності директорій", default=3
    )
    max_dirs = ask_int_with_default(
        "Максимальна кількість підкаталогів на одному рівні", default=3
    )
    max_files = ask_int_with_default(
        "Максимальна кількість файлів на одному рівні", default=6
    )

    print(
        f"\n[INFO] Використовуємо параметри:\n"
        f"  max_depth = {max_depth}\n"
        f"  max_dirs  = {max_dirs}\n"
        f"  max_files = {max_files}\n"
    )

    src_dir = create_src_dir()
    if src_dir is None:
        return

    print(f"[INFO] Генерую структуру у '{src_dir}'...\n")

    generate_random_tree(
        root=src_dir,
        max_depth=max_depth,
        max_dirs_per_level=max_dirs,
        max_files_per_level=max_files,
    )

    print("\n[INFO] Готово! Тестові дані створено.")


if __name__ == "__main__":
    main()
