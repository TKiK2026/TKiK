# TrumpScriptToPython

Jakub Białek  
jbialek@student.agh.edu.pl  

Piotr Bera  
pbera@student.agh.edu.pl  

## Założenia programu
Celem programu jest stworzenie translatora języka **TrumpScript** do języka **Python**.

Projekt zakłada implementację **kompilatora**.

Program przyjmuje kod źródłowy w języku **TrumpScript** i generuje równoważny kod w języku **Python**.

### Język implementacji 
*Python*

### Skaner i parser
*PLY*

### Tokeny
| Nazwa tokenu   | Regex / Definicja          | Opis                                 |
|----------------|----------------------------|--------------------------------------|
| ID             | `[a-zA-Z_][a-zA-Z_0-9]*`   | Identyfikator (nazwy zmiennych itp.) |
| STRING         | `\"[^\"]*\"`               | Ciąg znaków w cudzysłowie            |
| NUMBER         | `\d+`                      | Liczba całkowita                     |
| PLUS           | `\+` lub `plus`            | Operator dodawania                   |
| MINUS          | `-` lub `minus`            | Operator odejmowania                 |
| TIMES          | `\*` lub `times`           | Operator mnożenia                    |
| OVER           | `/` lub `over`             | Operator dzielenia                   |
| ASSIGN_OP_SIGN | `=`                        | Operator przypisania                 |
| ASSIGN_OP_WORD | `is` lub `are`             | Przypisanie (forma językowa)         |
| MAKE           | `make`                     | Tworzenie / deklaracja               |
| PRINT          | `say` lub `tell`           | Wypisywanie danych                   |
| FACT           | `fact`                     | Wartość logiczna prawda              |
| LIE            | `lie`                      | Wartość logiczna fałsz               |
| IF             | `if`                       | Instrukcja warunkowa                 |
| ELSE           | `else`                     | Alternatywa warunku                  |
| GREATER        | `more`, `greater`, `larger` | Operator większy (opisowy)           |
| LESS           | `less`, `fewer`, `smaller` | Operator mniejszy (opisowy)          |
| GT             | `>`                        | Operator większy niż                 |
| LT             | `<`                        | Operator mniejszy niż                |
| GE             | `>=`                       | Operator większy lub równy           |
| LE             | `<=`                       | Operator mniejszy lub równy          |
| EQ             | `==`                       | Operator równości                    |
| AND            | `and`                      | Operator logiczny AND                |
| OR             | `or`                       | Operator logiczny OR                 |
| NOT            | `~`                        | Operator logiczny negacji            |
| AS_LONG_AS     | `as long as`               | Pętla while                          |
| BREAK          | `stop`                     | break                                |
| LPAREN         | `,`                        | nawias otwierający                   |
| RPAREN         | `;`                        | nawiasu zamykający                   |
| LBRACE         | `:`                        | Początek bloku instrukcji if oraz as long as |
| RBRACE         | `!`                        | Koniec bloku instrukcji if oraz as long as |
| QUESTION       | `\?`                       | Znak zapytania                       |
| AMERICA_GREAT  | `America\s+is\s+great\.`   | Zakończenie programu                 |
| (ignore)       | `' \t'`                    | Ignorowane: spacje, taby             |
| newline        | `\n+`                      | Nowa linia (zliczanie numerów linii) |
| error          | —                          | Obsługa nieznanych znaków            |


### [Gramatyka](grammar.py)

### Instrukcja obsługi

Aby uruchomić kompilator, należy włączyć plik:

```text
main.py
```

Po uruchomieniu aplikacji pojawi się okno podzielone na **3 sekcje**:

1. **Kod źródłowy w TrumpScript**  
   Pole przeznaczone do wpisania programu w języku TrumpScript.

2. **Przetłumaczony kod Python**  
   Wyświetla kod automatycznie przetłumaczony z TrumpScript na język Python.

3. **Wynik działania programu**  
   Konsola prezentująca rezultat wykonania programu.

---

#### Dostępne przyciski

#### `copy`
Kopiuje wygenerowany kod Python do schowka.

---

#### `translate`
Tłumaczy kod z języka **TrumpScript** na język **Python** bez uruchamiania programu.

---

#### `run`
- tłumaczy kod z TrumpScript na Python,
- uruchamia wygenerowany program,
- wyświetla wynik działania w konsoli.

---

#### `clear`
Czyści wszystkie pola aplikacji:
- kod źródłowy,
- wygenerowany kod Python,
- wynik działania programu.

---

#### Status operacji

W **prawym dolnym rogu** aplikacji znajduje się pasek statusu, który informuje o wyniku ostatnio wykonanej operacji, np.:

- poprawne tłumaczenie kodu,
- pomyślne uruchomienie programu,
- błędy składni lub wykonania.


### Przykładowy kod w języku TrumpScript
```text
make wall "test"
america is "great"
make wall_test wall is "test"?
make america_test america is "great"?
result is ,wall_test and america_test;
as long as result:
    say "Jestem w pętli"
    make result lie
!
say result

America is great.
```

### Przetłumaczony kod na język Python
```Python
wall = "test"
america = "great"
wall_test = wall == "test"
america_test = america == "great"
result = wall_test and america_test
while result:
    print("Jestem w pętli")
    result = False
print(result)
```

### Wynik działania programu
```text
Jestem w pętli
False
```
