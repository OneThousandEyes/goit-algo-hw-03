import turtle
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def koch_curve(t, order, size):
    """Малює криву Коха за допомогою черепашки t та рекурсії."""
    if order == 0:
        t.forward(size)
    else:
        for angle in [60, -120, 60, 0]:
            koch_curve(t, order - 1, size / 3)
            t.left(angle)


def draw_koch_snowflake(order: int, size: int = 300):
    """Малює сніжинку Коха заданого рівня рекурсії та розміру."""
    console.print(f"[bold cyan]Малюю сніжинку Коха...[/bold cyan]")
    console.print(f"[yellow]Рівень рекурсії:[/yellow] {order}")
    console.print(f"[yellow]Розмір фігури:[/yellow] {size} px\n")

    window = turtle.Screen()
    window.bgcolor("white")

    t = turtle.Turtle()
    t.speed(0)
    t.penup()
    t.goto(-size / 2, size / 3)
    t.pendown()

    for _ in range(3):
        koch_curve(t, order, size)
        t.right(120)

    window.mainloop()


def ask_int_with_default(prompt: str, default: int, min_val: int, max_val: int) -> int:
    """Обробка введенного цілого числа з клавіатури."""
    while True:
        console.print(
            f"{prompt} [значення за замовчуванням: [bold]{default}[/bold]] "
            f"(діапазон: {min_val}–{max_val}): ",
            end=""
        )
        raw = input().strip()

        if raw == "":
            return default

        try:
            value = int(raw)
        except ValueError:
            console.print("[red]Потрібно ввести ціле число.[/red]")
            continue

        if not (min_val <= value <= max_val):
            console.print(
                f"[red]Число має бути в діапазоні {min_val}–{max_val}.[/red]"
            )
            continue

        return value


def main():
    console.print(
        Panel(
            Text("Фрактал: Сніжинка Коха", justify="center", style="bold magenta"),
            expand=False
        )
    )

    order = ask_int_with_default(
        "Введіть рівень рекурсії", default=3, min_val=0, max_val=8
    )
    size = ask_int_with_default(
        "Введіть розмір сніжинки у пікселях", default=300, min_val=50, max_val=600
    )

    draw_koch_snowflake(order, size)


if __name__ == "__main__":
    main()
