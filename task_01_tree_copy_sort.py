import argparse
import shutil
import sys
import time
from pathlib import Path
from typing import Optional, List

from colorama import init, Fore, Style

init(autoreset=True)

EXT_COLOR_MAP = {
    "txt":  Fore.GREEN,
    "log":  Fore.YELLOW,
    "jpg":  Fore.MAGENTA,
    "jpeg": Fore.MAGENTA,
    "png":  Fore.CYAN,
    "gif":  Fore.LIGHTMAGENTA_EX,
    "pdf":  Fore.RED,
    "doc":  Fore.LIGHTBLUE_EX,
    "xml":  Fore.LIGHTCYAN_EX,
    "yml":  Fore.LIGHTGREEN_EX,
}

DEFAULT_FILE_COLOR = Fore.WHITE
BRANCH_COLOR = Fore.LIGHTBLACK_EX  # │ ├── └──

# Збираємо всі помилки тут
ERRORS: List[str] = []


def warn(msg: str) -> None:
    """Записуємо WARN (виведемо пізніше)."""
    ERRORS.append(msg)


def print_progress_bar(progress: float, width=40):
    """Виводить прогрес-бар у консоль."""
    filled = int(width * progress)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    percent = int(progress * 100)

    sys.stdout.write(f"\rКопіювання файлів: [{bar}] {percent}%")
    sys.stdout.flush()


def parse_args():
    """Парсить аргументи командного рядка."""
    parser = argparse.ArgumentParser(
        description="Рекурсивно копіює файли з SRC до DST та сортує за розширеннями."
    )
    parser.add_argument("src")
    parser.add_argument("dst", nargs="?", default="dist")
    return parser.parse_args()


def get_extension_subdir(path: Path) -> str:
    """Повертає підкаталог для розширення файлу."""
    e = path.suffix.lower()
    return e.lstrip(".") if e else "no_extension"


def is_inside(child: Path, parent: Path) -> bool:
    """Перевіряє, чи є child всередині parent."""
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def collect_files_recursive(src: Path, out: List[Path], skip_dir: Optional[Path] = None):
    """Рекурсивно збирає файли з каталогу src у список out, пропускаючи skip_dir."""
    try:
        entries = list(src.iterdir())
    except PermissionError:
        warn(f"Немає доступу: {src}")
        return
    except OSError:
        warn(f"Помилка читання: {src}")
        return

    for item in entries:
        if skip_dir and item.resolve() == skip_dir.resolve():
            continue

        try:
            if item.is_dir():
                collect_files_recursive(item, out, skip_dir)
            elif item.is_file():
                out.append(item)
        except PermissionError:
            warn(f"Немає доступу: {item}")
        except OSError:
            warn(f"Помилка читання: {item}")


def display_tree(path: Path, indent: str = "", prefix: str = ""):
    """Виводить дерево файлів і каталогів, починаючи з path."""
    if path.is_dir():
        print(
            BRANCH_COLOR + indent + prefix + Style.RESET_ALL +
            Style.BRIGHT + path.name + Style.RESET_ALL
        )

        subindent = indent + ("    " if prefix else "")
        try:
            entries = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
        except Exception:
            warn(f"Немає доступу: {path}")
            print(subindent + "└── [недоступно]")
            return

        for i, item in enumerate(entries):
            is_last = i == len(entries) - 1
            p = "└── " if is_last else "├── "
            display_tree(item, subindent, p)

    else:
        color = EXT_COLOR_MAP.get(path.suffix.lstrip("."), DEFAULT_FILE_COLOR)
        print(
            BRANCH_COLOR + indent + prefix + Style.RESET_ALL +
            color + path.name + Style.RESET_ALL
        )


def main():
    args = parse_args()

    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()

    if not src.exists() or not src.is_dir():
        print(Fore.RED + f"[FATAL] SRC '{src}' не існує." + Style.RESET_ALL)
        return

    skip_dir = dst if dst == src or is_inside(dst, src) else None

    try:
        dst.mkdir(parents=True, exist_ok=True)
    except OSError:
        print(Fore.RED + f"[FATAL] Не вдалося створити '{dst}'" + Style.RESET_ALL)
        return

    # Зібрати всі файли з SRC
    files_to_copy: List[Path] = []
    collect_files_recursive(src, files_to_copy, skip_dir)

    total = len(files_to_copy)
    if total == 0:
        display_tree(dst)
        return

    # Визначаємо затримку для анімації прогрес-бару
    if total <= 20:
        delay = 0.20
    elif total <= 100:
        delay = 0.10
    else:
        delay = 0.03

    # Копіюємо файли з прогрес-баром
    for i, file_path in enumerate(files_to_copy, start=1):

        ext_dir = get_extension_subdir(file_path)
        target_dir = dst / ext_dir
        target_file = target_dir / file_path.name

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target_file)
        except PermissionError:
            warn(f"Немає доступу: {file_path}")
        except FileNotFoundError:
            warn(f"Файл не знайдено: {file_path}")
        except OSError:
            warn(f"Помилка копіювання: {file_path}")

        print_progress_bar(i / total)
        time.sleep(delay)

    print()

    # Вивести всі попередження
    if ERRORS:
        for e in ERRORS:
            print(Fore.RED + f"[WARN] {e}" + Style.RESET_ALL)
        print()

    # Вивести дерево DST
    print("[INFO] Структура DST у вигляді дерева:\n")
    display_tree(dst)


if __name__ == "__main__":
    main()
