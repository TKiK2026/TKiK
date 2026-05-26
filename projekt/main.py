import tkinter as tk
import io
import sys
from utils.errors import LexerError, ParserError, SemanticError
from utils.parser import parse_code
from utils.transpiler import translate_to_python
from tkinter import font


def translate():
    """Tłumaczy kod TrumpScript na Python i zwraca wygenerowany kod (lub None w razie błędu)."""
    code = input_text.get("1.0", tk.END).strip()
    if not code:
        return None

    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)

    try:
        # Generowanie AST — parse_code resetuje numerację linii lexera.
        ast = parse_code(code)

        if ast is None:
            raise ParserError("Pusty program lub nierozpoznana składnia.")

        python_code = translate_to_python(ast)

        if python_code:
            output_text.insert(tk.END, python_code)
            output_text.config(fg="#79c0ff")
            status_var.set("Sukces")
            status_label.config(fg="#3fb950")
            return python_code
        else:
            output_text.insert(tk.END, "Pusty program.")
            output_text.config(fg="#8b949e")
            status_var.set("✓ Empty program")
            status_label.config(fg="#8b949e")
            return None

    except (LexerError, ParserError) as e:
        output_text.insert(tk.END, f"Błąd Składni (Syntax Error):\n{e}")
        output_text.config(fg="#f85149")
        status_var.set("✗ Syntax Error")
        status_label.config(fg="#f85149")
        return None

    except SemanticError as e:
        output_text.insert(tk.END, f"Błąd Semantyczny:\n{e}")
        output_text.config(fg="#f85149")
        status_var.set("✗ Semantic Error")
        status_label.config(fg="#f85149")
        return None

    except Exception as e:
        output_text.insert(tk.END, f"Nieoczekiwany Błąd:\n{e}")
        output_text.config(fg="#f85149")
        status_var.set("✗ Błąd")
        status_label.config(fg="#f85149")
        return None

    finally:
        output_text.config(state=tk.DISABLED)


def run_code():
    """Tłumaczy kod, a następnie wykonuje go i przechwytuje stdout."""
    python_code = translate()

    console_text.config(state=tk.NORMAL)
    console_text.delete("1.0", tk.END)

    if not python_code:
        console_text.insert(tk.END, "Nie można uruchomić: brak poprawnego kodu Python.")
        console_text.config(fg="#f85149")
        console_text.config(state=tk.DISABLED)
        return

    output_buffer = io.StringIO()
    sys.stdout = output_buffer
    sys.stderr = output_buffer

    try:
        exec(python_code, {"__builtins__": __builtins__}, {})
        success = True
    except Exception as e:
        print(f"\n[Błąd wykonania]:\n{e}", file=output_buffer)
        success = False
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    execution_result = output_buffer.getvalue()

    if execution_result:
        console_text.insert(tk.END, execution_result)
    else:
        console_text.insert(tk.END, "Program zakończył się bez wypisania danych (brak print).")

    if success:
        console_text.config(fg="#56d364")
        status_var.set("✓ Succes")
        status_label.config(fg="#3fb950")
    else:
        console_text.config(fg="#f85149")
        status_var.set("✗ Failed")
        status_label.config(fg="#f85149")

    console_text.config(state=tk.DISABLED)


def clear():
    input_text.delete("1.0", tk.END)

    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.config(state=tk.DISABLED)

    console_text.config(state=tk.NORMAL)
    console_text.delete("1.0", tk.END)
    console_text.config(state=tk.DISABLED)

    status_var.set("")
    input_text.focus()


def copy_output():
    content = output_text.get("1.0", tk.END).strip()
    if content:
        root.clipboard_clear()
        root.clipboard_append(content)
        status_var.set("Skopiowano do schowka")
        status_label.config(fg="#8b949e")


# --- OKNO GŁÓWNE ---
root = tk.Tk()
root.title("TrumpScript Translator & Runner")
root.geometry("1200x650")
root.state("normal")
root.minsize(900, 500)
root.configure(bg="#0d1117")

BG = "#0d1117"
BG2 = "#161b22"
BORDER = "#21262d"
FG = "#e6edf3"
FG_MUTED = "#8b949e"
FONT_CODE = ("JetBrains Mono", 11) if "JetBrains Mono" in tk.font.families() \
    else ("Courier New", 11)
FONT_UI = ("Segoe UI", 10)

# --- HEADER ---
header = tk.Frame(root, bg=BG2, height=48)
header.pack(fill=tk.X, side=tk.TOP)
header.pack_propagate(False)

tk.Label(
    header, text="TrumpScript IDE",
    bg=BG2, fg=FG, font=("Segoe UI", 13, "bold")
).pack(side=tk.LEFT, padx=16, pady=12)



# --- GŁÓWNY OBSZAR (Trzy równe panele za pomocą Grid) ---
main = tk.Frame(root, bg=BG)
main.pack(fill=tk.BOTH, expand=True)

# Konfiguracja kolumn Grid w kontenerze main
main.grid_columnconfigure(0, weight=1)  # Panel 1 (TrumpScript)
main.grid_columnconfigure(1, weight=0)  # Separator 1 (bardzo cienki)
main.grid_columnconfigure(2, weight=1)  # Panel 2 (Python)
main.grid_columnconfigure(3, weight=0)  # Separator 2 (bardzo cienki)
main.grid_columnconfigure(4, weight=1)  # Panel 3 (Konsola)
main.grid_rowconfigure(0, weight=1)

# 1. Panel lewy — TrumpScript
left = tk.Frame(main, bg=BG, bd=0)
left.grid(row=0, column=0, sticky="nsew")

left_header = tk.Frame(left, bg=BG2, height=32)
left_header.pack(fill=tk.X)
left_header.pack_propagate(False)
tk.Label(
    left_header, text="TrumpScript",
    bg=BG2, fg=FG_MUTED, font=("Segoe UI", 9, "bold")
).pack(side=tk.LEFT, padx=12, pady=7)

input_text = tk.Text(
    left,
    bg=BG, fg=FG, insertbackground=FG,
    font=FONT_CODE, relief=tk.FLAT,
    padx=12, pady=12,
    undo=True,
    wrap=tk.WORD,
)
input_text.pack(fill=tk.BOTH, expand=True)

left_scroll_x = tk.Scrollbar(left, orient=tk.HORIZONTAL, command=input_text.xview)
left_scroll_x.pack(fill=tk.X)
input_text.config(xscrollcommand=left_scroll_x.set)

# Separator pionowy 1
sep1 = tk.Frame(main, bg=BORDER, width=1)
sep1.grid(row=0, column=1, sticky="ns")

# 2. Panel środkowy — Python
middle = tk.Frame(main, bg=BG, bd=0)
middle.grid(row=0, column=2, sticky="nsew")

middle_header = tk.Frame(middle, bg=BG2, height=32)
middle_header.pack(fill=tk.X)
middle_header.pack_propagate(False)
tk.Label(
    middle_header, text="Translated to Python",
    bg=BG2, fg=FG_MUTED, font=("Segoe UI", 9, "bold")
).pack(side=tk.LEFT, padx=12, pady=7)

copy_btn = tk.Button(
    middle_header, text="kopiuj",
    bg=BG2, fg=FG_MUTED,
    relief=tk.FLAT, font=("Segoe UI", 9),
    cursor="hand2",
    command=copy_output,
    activebackground=BG2, activeforeground=FG,
    bd=0, padx=6
)
copy_btn.pack(side=tk.RIGHT, padx=8, pady=4)

output_text = tk.Text(
    middle,
    bg=BG, fg="#79c0ff", insertbackground=FG,
    font=FONT_CODE, relief=tk.FLAT,
    padx=12, pady=12,
    state=tk.DISABLED,
    wrap=tk.WORD,
)
output_text.pack(fill=tk.BOTH, expand=True)

middle_scroll_x = tk.Scrollbar(middle, orient=tk.HORIZONTAL, command=output_text.xview)
middle_scroll_x.pack(fill=tk.X)
output_text.config(xscrollcommand=middle_scroll_x.set)

# Separator pionowy 2
sep2 = tk.Frame(main, bg=BORDER, width=1)
sep2.grid(row=0, column=3, sticky="ns")

# 3. Panel prawy — Wynik (Konsola)
right = tk.Frame(main, bg=BG, bd=0)
right.grid(row=0, column=4, sticky="nsew")

right_header = tk.Frame(right, bg=BG2, height=32)
right_header.pack(fill=tk.X)
right_header.pack_propagate(False)
tk.Label(
    right_header, text="Console (result)",
    bg=BG2, fg=FG_MUTED, font=("Segoe UI", 9, "bold")
).pack(side=tk.LEFT, padx=12, pady=7)

console_text = tk.Text(
    right,
    bg="#090d16", fg="#56d364", insertbackground=FG,
    font=FONT_CODE, relief=tk.FLAT,
    padx=12, pady=12,
    state=tk.DISABLED,
    wrap=tk.WORD,
)
console_text.pack(fill=tk.BOTH, expand=True)

right_scroll_x = tk.Scrollbar(right, orient=tk.HORIZONTAL, command=console_text.xview)
right_scroll_x.pack(fill=tk.X)
console_text.config(xscrollcommand=right_scroll_x.set)

# --- TOOLBAR ---
toolbar = tk.Frame(root, bg=BG2, height=48, bd=0)
toolbar.pack(fill=tk.X, side=tk.BOTTOM)
toolbar.pack_propagate(False)

tk.Frame(toolbar, bg=BORDER, height=1).pack(fill=tk.X, side=tk.TOP)

# Przycisk TRANSLATE
translate_btn = tk.Button(
    toolbar,
    text="⇄  Translate",
    bg="#21262d", fg=FG,
    activebackground=BORDER, activeforeground="#ffffff",
    font=("Segoe UI", 10, "bold"),
    relief=tk.FLAT, cursor="hand2",
    padx=16, pady=4,
    command=translate,
)
translate_btn.pack(side=tk.LEFT, padx=12, pady=10)

# Przycisk RUN
run_btn = tk.Button(
    toolbar,
    text="▶  Run",
    bg="#238636", fg="#ffffff",
    activebackground="#2ea043", activeforeground="#ffffff",
    font=("Segoe UI", 10, "bold"),
    relief=tk.FLAT, cursor="hand2",
    padx=20, pady=4,
    command=run_code,
)
run_btn.pack(side=tk.LEFT, padx=6, pady=10)

# Przycisk CZYSZCZENIA
clear_btn = tk.Button(
    toolbar,
    text="Clear",
    bg=BG2, fg=FG_MUTED,
    activebackground=BG2, activeforeground=FG,
    font=FONT_UI,
    relief=tk.FLAT, cursor="hand2",
    padx=12, pady=4,
    bd=1,
    command=clear,
)
clear_btn.pack(side=tk.LEFT, padx=12, pady=10)

status_var = tk.StringVar()
status_label = tk.Label(
    toolbar, textvariable=status_var,
    bg=BG2, fg=FG_MUTED,
    font=("Segoe UI", 10)
)
status_label.pack(side=tk.RIGHT, padx=16)



root.mainloop()
