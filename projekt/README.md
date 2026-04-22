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

### [Gramatyka](grammar.py)

### Przykładowy kod
```text
make wall "test"
america is "great"
make wall_test wall is "test"?
make america_test america is "great"?
result is ,wall_test and america_test;
as long as result==fact:
    say "Jestem w pętli"
    make result lie
!
say result

America is great.
```

### Tokeny
| Nazwa tokenu   | Regex / Definicja          | Opis                                         |
|----------------|----------------------------|----------------------------------------------|
| ID             | `[a-zA-Z_][a-zA-Z_0-9]*`   | Identyfikator (nazwy zmiennych itp.)         |
| STRING         | `\"[^\"]*\"`               | Ciąg znaków w cudzysłowie                    |
| NUMBER         | `\d+`                      | Liczba całkowita                             |
| PLUS           | `\+` lub `plus`            | Operator dodawania                           |
| MINUS          | `-` lub `minus`            | Operator odejmowania                         |
| TIMES          | `\*` lub `times`           | Operator mnożenia                            |
| OVER           | `/` lub `over`             | Operator dzielenia                           |
| ASSIGN_OP_SIGN | `=`                        | Operator przypisania                         |
| ASSIGN_OP_WORD | `is` lub `are`             | Przypisanie (forma językowa)                 |
| MAKE           | `make`                     | Tworzenie / deklaracja                       |
| PRINT          | `say` lub `tell`           | Wypisywanie danych                           |
| FACT           | `fact`                     | Wartość logiczna prawda                      |
| LIE            | `lie`                      | Wartość logiczna fałsz                       |
| IF             | `if`                       | Instrukcja warunkowa                         |
| ELSE           | `else`                     | Alternatywa warunku                          |
| GREATER        | `more`, `greater`, `larger` | Operator większy (opisowy)                   |
| LESS           | `less`, `fewer`, `smaller` | Operator mniejszy (opisowy)                  |
| GT             | `>`                        | Operator większy niż                         |
| LT             | `<`                        | Operator mniejszy niż                        |
| GE             | `>=`                       | Operator większy lub równy                   |
| LE             | `<=`                       | Operator mniejszy lub równy                  |
| EQ             | `==`                       | Operator równości                            |
| AND            | `and`                      | Operator logiczny AND                        |
| OR             | `or`                       | Operator logiczny OR                         |
| AS_LONG_AS     | `as long as`               | Pętla while                                  |
| LPAREN         | `,`                        | nawias otwierający                           |
| RPAREN         | `;`                        | nawiasu zamykający                           |
| LBRACE         | `:`                        | Początek bloku instrukcji if oraz as long as |
| RBRACE         | `!`                        | Koniec bloku instrukcji if oraz as long as   |
| QUESTION       | `\?`                       | Znak zapytania                               |
| AMERICA_GREAT  | `America\s+is\s+great\.`   | Zakończenie programu                         |
| (ignore)       | `' \t'`                    | Ignorowane: spacje, taby, kropki             |
| newline        | `\n+`                      | Nowa linia (zliczanie numerów linii)         |
| error          | —                          | Obsługa nieznanych znaków                    |

