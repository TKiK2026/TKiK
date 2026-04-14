# TrumpScriptToPython

Jakub Białek  
jbialek@student.agh.edu.pl  

Piotr Bera  
pbera@student.agh.edu.pl  

## Założenia programu
Celem programu jest stworzenie translatora języka **TrumpScript** do języka **Python**.

Projekt zakłada implementację **interpretera**.

Program przyjmuje kod źródłowy w języku **TrumpScript** i generuje równoważny program w języku **Python**.

### Język implementacji 
*Python*

### Skaner i parser
*PLY*

### [Gramatyka](grammar.py)
### Tokeny
| Nazwa tokenu   | Regex / Definicja                 | Opis                                     |
|----------------|-----------------------------------|------------------------------------------|
| ID             | `[a-zA-Z_][a-zA-Z_0-9]*`          | Identyfikator (nazwy zmiennych itp.)     |
| STRING         | `\"[^\"]*\"`                      | Ciąg znaków w cudzysłowie                |
| NUMBER         | `\d+`                             | Liczba całkowita                         |
| PLUS           | `\+` lub słowo `plus`             | Operator dodawania                       |
| MINUS          | `-` lub słowo `minus`             | Operator odejmowania                     |
| TIMES          | `\*` lub słowo `times`            | Operator mnożenia                        |
| OVER           | `/` lub słowo `over`              | Operator dzielenia                       |
| ASSIGN_OP_SIGN | `=`                               | Operator przypisania                     |
| ASSIGN_OP_IS   | słowo `is`                        | Przypisanie (forma językowa)             |
| ASSIGN_OP_ARE  | słowo `are`                       | Przypisanie (forma językowa)             |
| MAKE           | słowo `make`                      | Tworzenie / deklaracja                   |
| PRINT          | słowa `say`, `tell`               | Wypisywanie danych                       |
| FACT           | słowo `fact`                      | Wartość logiczna prawda                  |
| LIE            | słowo `lie`                       | Wartość logiczna fałsz                   |
| IF             | słowo `if`                        | Instrukcja warunkowa                     |
| ELSE           | słowo `else`                      | Alternatywa warunku                      |
| GREATER        | słowa `more`, `greater`, `larger` | Operator większy (opisowy)               |
| LESS           | słowa `less`, `fewer`, `smaller`  | Operator mniejszy (opisowy)              |
| GT             | `>`                               | Operator większy niż                     |
| LT             | `<`                               | Operator mniejszy niż                    |
| GE             | `>=`                              | Operator większy lub równy               |
| LE             | `<=`                              | Operator mniejszy lub równy              |
| EQ             | `==`                              | Operator równości                        |
| AND            | słowo `and`                       | Operator logiczny AND                    |
| OR             | słowo `or`                        | Operator logiczny OR                     |
| AS_LONG_AS     | słowo `as long as`                | Pętla while                              |
| LPAREN         | `,`                               | Separator (zamiast nawiasu otwierającego) |
| RPAREN         | `;`                               | Separator (zamiast nawiasu zamykającego) |
| LBRACE         | `:`                               | Początek bloku                           |
| RBRACE         | `!`                               | Koniec bloku                             |
| QUESTION       | `\?`                              | Znak zapytania                           |
| AMERICA_GREAT  | `America\s+is\s+great\.`          | Zakończenie programu                     |
| (ignore)       | `' \t.'`                          | Ignorowane: spacje, taby, kropki         |
| newline        | `\n+`                             | Nowa linia (zliczanie numerów linii)     |
| error          | —                                 | Obsługa nieznanych znaków                |

