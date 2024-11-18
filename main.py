import flet as ft
from flet import *
from supabase import create_client
from datetime import datetime
import random

# Połączenie z Supabase
url = "XXX"
key = "XXX"
supabase = create_client(url, key)
total_points = 0

# Funkcja do pobierania danych z Supabase
def get_quiz_data():
    response = supabase.table("quizAPP").select("*").execute()
    if response.data:
        # Jeśli pytań jest mniej niż 30, zwracamy wszystkie dostępne
        questions = response.data
        return random.sample(questions, min(30, len(questions)))
    return []

# Funkcja zapisywania wyniku do Supabase
def save_result(points):
    result = supabase.table("quizAPP_wyniki").insert({
        "created_at": datetime.now().isoformat(),
        "poprawne_odp": points
    }).execute()
    return result

# Funkcja główna aplikacji
def main(page: ft.Page):
    page.theme_mode = "dark"
    page.scroll = "adaptive"

    ##################### NAGŁÓWEK #####################
    page.add(
        AppBar(
            title=Text("quizAPP by b0rygo", size=30),
            bgcolor="blue",
        )
    )

    # Tytuł na stronie głównej
    page.add(
        ft.Container(
            content=ft.Text(
                "QuizAPP!",
                size=50,
                weight=ft.FontWeight.BOLD,
                color="blue"
            ),
            alignment=ft.alignment.center,
            padding=20
        )
    )

    # Funkcja do przejścia na stronę quizu
    def go_to_quiz_page(e):
        quiz_data = get_quiz_data()
        selected_answers = []  # Lista przechowująca wybrane odpowiedzi
        quiz_page(quiz_data, 0,selected_answers)  # Rozpocznij od pierwszego pytania  # Rozpocznij od pierwszego pytania

    def quiz_page(quiz_data, question_index, selected_answers):
        global total_points

        # Czyścimy poprzednią zawartość
        page.clean()

        # Sprawdź, czy nie przekroczyliśmy liczby pytań
        if question_index >= len(quiz_data):
            # Wyświetl wynik
            page.add(ft.Text(f"Twój wynik: {total_points} / {len(quiz_data)}", size=30, weight=ft.FontWeight.BOLD,
                             color="green"))

            # Zapisz wynik w bazie danych
            save_result(total_points)

            # Dodaj przycisk powrotu do strony głównej
            back_button = ft.ElevatedButton("Powrót", on_click=lambda _: go_back(page))
            page.add(back_button)
            return

        # Pobieramy aktualne pytanie
        current_question = quiz_data[question_index]
        question_text = current_question.get("question", "Brak pytania")

        # Wyświetlamy pytanie
        question = ft.ResponsiveRow(
            controls=[
                ft.Text(
                    question_text,
                    size=32,
                    expand=True
                )
            ],
            alignment="center"
        )
        page.add(question)

        # Zbieranie dostępnych odpowiedzi
        answers = [
            current_question.get("a", None),
            current_question.get("b", None),
            current_question.get("c", None),
            current_question.get("d", None),
            current_question.get("e", None),
            current_question.get("f", None)
        ]

        # Filtrujemy odpowiedzi, które nie są None
        valid_answers = [ans for ans in answers if ans is not None]

        selected_answer_controls = []
        checkbox_controls = []  # Lista do przechowywania checkboxów z wartościami
        answer_texts = []  # Lista do przechowywania tekstów odpowiedzi

        # Tworzymy kontrolki dla odpowiedzi
        for i, answer in enumerate(valid_answers):
            # Tworzymy Checkbox z odpowiedzią
            checkbox = ft.Checkbox(
                label="",  # Checkbox bez etykiety, etykieta będzie w Text
                value=False  # Początkowa wartość zaznaczenia
            )

            # Tworzymy Text do wyświetlania odpowiedzi
            answer_text = ft.Text(
                answer,  # Treść odpowiedzi
                max_lines=2,  # Ograniczamy do 2 linii
                overflow="ellipsis",  # Jeśli tekst jest zbyt długi, dodajemy "..."
            )

            # Tworzymy Row, w którym znajduje się Checkbox oraz Text
            row = ft.Row(
                controls=[checkbox, answer_text],  # Używamy Row do umieszczenia Checkbox i Text
                alignment="start",  # Wyrównanie do lewej
                spacing=10  # Odstęp między Checkbox a Text
            )

            # Dodajemy kontrolkę Checkbox do listy checkbox_controls
            checkbox_controls.append(checkbox)
            # Dodajemy kontrolkę Text do listy answer_texts
            answer_texts.append(answer_text)

            # Dodajemy cały Row do listy kontrolki
            selected_answer_controls.append(row)

        # Wyświetlanie kontrolki w kolumnie
        page.add(ft.Column(controls=selected_answer_controls, alignment="center"))

        # Funkcja zbierająca odpowiedzi
        def collect_answers():
            global total_points
            correct_answers = 0
            selected_answers = []

            # Pobieramy odpowiedzi użytkownika
            for checkbox, answer_text in zip(checkbox_controls, answer_texts):  # Iterujemy po checkboxach i tekstach
                if checkbox.value:  # Sprawdzamy wartość zaznaczenia dla każdego checkboxa
                    # Sprawdzamy, czy odpowiedź jest poprawna na podstawie tekstu odpowiedzi
                    answer = answer_text.value.lower()  # Zmienione z answer_text.text na answer_text.value
                    right_answer = current_question.get("right_answer", "").lower()

                    if answer[0] in right_answer.split(","):  # Porównujemy pierwszą literę odpowiedzi
                        correct_answers += 1
                    selected_answers.append(answer)

            # Naliczanie punktów
            right_answer_list = current_question.get("right_answer", "").lower().split(",")
            if len(right_answer_list) == 1:
                points = 1 if correct_answers == 1 else 0
            elif len(right_answer_list) == 2:
                points = 1 if correct_answers == 2 else 0.5 if correct_answers == 1 else 0
            else:
                points = 0

            total_points += points

        # Funkcja do przejścia do następnego pytania
        def next_question(e):
            collect_answers()
            quiz_page(quiz_data, question_index + 1, selected_answers)

        # Przyciski "Dalej" i "Powrót"
        next_button = ft.ElevatedButton("Dalej", on_click=next_question)
        back_button = ft.ElevatedButton("Powrót", on_click=lambda _: go_back(page))

        page.add(
            ft.Row([back_button, next_button], alignment="center")
        )

    def go_back(page):
        global total_points
        total_points = 0
        page.clean()
        main(page)

    def wyniki(e):
        page.clean()
        results = supabase.table("quizAPP_wyniki").select("*").order("created_at", desc=True).execute()
        if results.data:
            for result in results.data:
                page.add(ft.Text(f"Wynik: {result['poprawne_odp']}, Data: {result['created_at']}"))
        else:
            page.add(ft.Text("Brak wyników."))

    # Przyciski na stronie głównej
    page.add(
        ft.SafeArea(
            ft.Column([
                ft.Row([
                    ft.ElevatedButton("START", on_click=go_to_quiz_page),
                    ft.ElevatedButton("Wyniki", on_click=wyniki)
                ], alignment="center"),
            ]),
        )
    )

# Uruchomienie aplikacji
ft.app(target=main)
