from __future__ import annotations

import csv
import math
import queue
import random
import statistics
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from src import experimento as exp

ROOT = Path(__file__).resolve().parent
RESULTADOS_CSV = ROOT / "entrega" / "resultados.csv"
CALIBRACAO_CSV = ROOT / "entrega" / "calibracao.csv"
COLORS = {
    "navy": "#17324d",
    "blue": "#2878a8",
    "teal": "#238b78",
    "light": "#f2f6f9",
    "grid_light": "#f7f3e8",
    "grid_dark": "#c8d3df",
    "conflict": "#d1495b",
    "safe": "#2a7f62",
    "text": "#213547",
    "muted": "#5c6e7d",
    "white": "#ffffff",
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def summarize_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    summary = []
    for method in exp.METODOS:
        group = [row for row in rows if row.get("metodo") == method]
        if not group:
            continue
        successes = [row for row in group if row.get("sucesso", "").lower() == "true"]
        failures = [row for row in group if row.get("sucesso", "").lower() != "true"]
        costs = [
            int(row["avaliacoes_ate_solucao"])
            for row in successes
            if row.get("avaliacoes_ate_solucao")
        ]
        failed_conflicts = [int(row["melhor_conflitos"]) for row in failures]

        def metric(values: list[int], fn, empty: str = "n/d") -> str:
            return f"{fn(values):.1f}" if values else empty

        budgets = sorted({int(row["orcamento"]) for row in group})
        summary.append(
            {
                "metodo": method,
                "execucoes": len(group),
                "sucessos": len(successes),
                "taxa": 100 * len(successes) / len(group),
                "media": metric(costs, statistics.mean),
                "mediana": metric(costs, statistics.median),
                "desvio": metric(costs, statistics.pstdev),
                "minimo": str(min(costs)) if costs else "n/d",
                "maximo": str(max(costs)) if costs else "n/d",
                "conflitos_falha_media": metric(failed_conflicts, statistics.mean),
                "conflitos_falha_mediana": metric(failed_conflicts, statistics.median),
                "conflitos_falha_min": str(min(failed_conflicts)) if failed_conflicts else "n/d",
                "conflitos_falha_max": str(max(failed_conflicts)) if failed_conflicts else "n/d",
                "orcamento": " / ".join(map(str, budgets)),
                "custos_sucesso": costs,
                "conflitos_falhas": failed_conflicts,
            }
        )
    return summary


def choose_calibration(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    chosen: dict[str, dict[str, str]] = {}
    for method in ("Hill Climbing com reinicio", "Simulated Annealing", "Algoritmo Genetico"):
        configs = sorted(
            {row["configuracao"] for row in rows if row.get("metodo") == method}
        )
        scored = []
        for config in configs:
            group = [
                row for row in rows
                if row.get("metodo") == method and row.get("configuracao") == config
            ]
            success = [
                row for row in group
                if row.get("sucesso", "").lower() == "true"
            ]
            fail_values = [
                int(row["melhor_conflitos"])
                for row in group
                if row.get("sucesso", "").lower() != "true"
            ]
            success_costs = [
                int(row["avaliacoes_ate_solucao"])
                for row in success
                if row.get("avaliacoes_ate_solucao")
            ]
            score = (
                -len(success),
                statistics.mean(fail_values) if fail_values else float("inf"),
                statistics.mean(success_costs) if success_costs else float("inf"),
            )
            scored.append((score, config, group))
        if scored:
            _, config, group = min(scored, key=lambda item: item[0])
            chosen[method] = {"configuracao": config, "metodo": method}
    return chosen


def queens_in_conflict(state: list[int]) -> set[int]:
    involved: set[int] = set()
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            if abs(state[i] - state[j]) == j - i:
                involved.update((i, j))
    return involved


class TDE3Interface:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("N-Rainhas — TDE3")
        self.root.geometry("1220x790")
        self.root.minsize(1000, 680)
        self.root.configure(bg=COLORS["light"])
        self._worker: threading.Thread | None = None
        self._cancel_event: threading.Event | None = None
        self._pause_event: threading.Event | None = None
        self._progress: queue.Queue[dict[str, object]] = queue.Queue(maxsize=1)
        self._completion: queue.Queue[tuple[object, object]] = queue.Queue(maxsize=1)
        self._started_at = 0.0
        self._event_snapshot: dict[str, object] | None = None
        self._demo_seed = exp.SEMENTE_BASE + exp.DESLOCAMENTO_SEMENTE[
            "Simulated Annealing"
        ]
        self._results: list[dict[str, str]] = []
        self._calibration: list[dict[str, str]] = []
        self._summary: list[dict[str, object]] = []
        self._calibration_choice: dict[str, dict[str, str]] = {}
        self._load_data()
        self._configure_style()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.after(70, self._poll_worker)

    def _load_data(self) -> None:
        if not RESULTADOS_CSV.exists() or not CALIBRACAO_CSV.exists():
            raise FileNotFoundError(
                "Não encontrei entrega/resultados.csv e entrega/calibracao.csv. "
                "Execute python3 run.py antes de abrir a interface."
            )
        self._results = read_csv_rows(RESULTADOS_CSV)
        self._calibration = read_csv_rows(CALIBRACAO_CSV)
        self._summary = summarize_rows(self._results)
        self._calibration_choice = choose_calibration(self._calibration)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["light"])
        style.configure("Card.TFrame", background=COLORS["white"])
        style.configure(
            "TLabel", background=COLORS["light"], foreground=COLORS["text"],
            font=("TkDefaultFont", 10),
        )
        style.configure(
            "Title.TLabel", background=COLORS["light"], foreground=COLORS["navy"],
            font=("TkDefaultFont", 18, "bold"),
        )
        style.configure(
            "Section.TLabel", background=COLORS["white"], foreground=COLORS["navy"],
            font=("TkDefaultFont", 12, "bold"),
        )
        style.configure(
            "Metric.TLabel", background=COLORS["white"], foreground=COLORS["blue"],
            font=("TkDefaultFont", 17, "bold"),
        )
        style.configure(
            "TNotebook.Tab", padding=(12, 8), font=("TkDefaultFont", 9, "bold")
        )
        style.configure("Treeview", rowheight=25, font=("TkDefaultFont", 9))
        style.configure("Treeview.Heading", font=("TkDefaultFont", 9, "bold"))
        style.configure("Primary.TButton", foreground=COLORS["white"], background=COLORS["blue"])
        style.map("Primary.TButton", background=[("active", COLORS["navy"])])

    def _build_ui(self) -> None:
        header = ttk.Frame(self.root, padding=(18, 12, 18, 6))
        header.pack(fill="x")
        ttk.Label(
            header, text="N-Rainhas — Otimização com Busca Local e AG",
            style="Title.TLabel",
        ).pack(side="left")
        ttk.Label(
            header, text="TDE3 · trabalho individual · N=30",
            foreground=COLORS["muted"],
        ).pack(side="right", anchor="s")

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=(4, 12))
        self._tab_overview = ttk.Frame(self.tabs, padding=18)
        self._tab_model = ttk.Frame(self.tabs, padding=18)
        self._tab_methods = ttk.Frame(self.tabs, padding=18)
        self._tab_demo = ttk.Frame(self.tabs, padding=12)
        self._tab_results = ttk.Frame(self.tabs, padding=12)
        self._tab_analysis = ttk.Frame(self.tabs, padding=18)
        for frame, title in (
            (self._tab_overview, "Visão geral"),
            (self._tab_model, "Modelagem"),
            (self._tab_methods, "Algoritmos"),
            (self._tab_demo, "Demonstração"),
            (self._tab_results, "Resultados"),
            (self._tab_analysis, "Análise e limitações"),
        ):
            self.tabs.add(frame, text=title)
        self._build_overview()
        self._build_model()
        self._build_methods()
        self._build_demo()
        self._build_results()
        self._build_analysis()

    def _card(self, parent: ttk.Frame, title: str, text: str) -> ttk.Frame:
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        ttk.Label(card, text=title, style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            card, text=text, style="TLabel", background=COLORS["white"],
            justify="left", wraplength=850,
        ).pack(anchor="w", fill="x", pady=(8, 0))
        return card

    def _build_overview(self) -> None:
        ttk.Label(self._tab_overview, text="O problema", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            self._tab_overview,
            text=(
                "Encontrar uma disposição de 30 rainhas sem conflitos diagonais. "
                "Uma avaliação conta exatamente uma chamada à função de conflitos; "
                "por isso comparamos os métodos pelo mesmo orçamento de avaliações, "
                "não por segundos ou gerações."
            ),
            wraplength=1040, justify="left",
        ).pack(anchor="w", pady=(8, 16))
        cards = ttk.Frame(self._tab_overview)
        cards.pack(fill="x")
        for col, (title, text) in enumerate((
            ("Representação", "Permutação de 0 a 29\ns[c] = linha na coluna c"),
            ("Espaço", f"30! = {math.factorial(30):,}".replace(",", ".") + " estados"),
            ("Vizinhança", f"C(30,2) = {math.comb(30, 2)} trocas"),
            ("Objetivo", "Minimizar conflitos diagonais até 0"),
        )):
            card = self._card(cards, title, text)
            card.grid(row=0, column=col, sticky="nsew", padx=5)
            cards.columnconfigure(col, weight=1)

        methods = "\n".join(f"• {name}" for name in exp.METODOS)
        self._card(
            self._tab_overview, "Métodos avaliados", methods
        ).pack(fill="x", pady=(16, 10))
        self._card(
            self._tab_overview, "Como usar esta interface",
            "1. Escolha um algoritmo.\n"
            "2. Inicie uma demonstração ao vivo.\n"
            "3. Observe o tabuleiro, os conflitos e o contador.\n"
            "4. Consulte a comparação experimental carregada dos CSVs.\n\n"
            "A demonstração é uma execução avulsa; não altera os resultados oficiais.",
        ).pack(fill="x")
        ttk.Button(
            self._tab_overview, text="Preparar demonstração",
            style="Primary.TButton", command=self.preparar_demonstracao,
        ).pack(anchor="e", pady=(12, 0))

    def _build_model(self) -> None:
        text = (
            "REPRESENTAÇÃO\n"
            "O estado é uma permutação s de 0..29. s[c] indica a linha da rainha "
            "na coluna c. A permutação garante uma rainha por linha e coluna.\n\n"
            "CONFLITO DIAGONAL\n"
            "Rainhas nas colunas i e j conflitam se abs(s[i] - s[j]) == abs(i - j). "
            "A função objetivo conta pares em conflito e é minimizada até zero.\n\n"
            "ESPAÇO E VIZINHANÇA\n"
            "30! significa 30 × 29 × ... × 2 × 1: a quantidade de permutações possíveis "
            "(aprox. 2,65 × 10³²); o programa não enumera todo esse espaço. Uma troca de "
            "dois valores mantém a permutação e há C(30,2)=435 vizinhos.\n\n"
            "LEGENDA DO TABULEIRO\n"
            "Q verde: rainha sem conflito. Q vermelha: rainha envolvida em conflito. "
            "Casas claras e escuras: posições do tabuleiro."
        )
        self._card(self._tab_model, "Modelagem das N-Rainhas", text).pack(fill="x")

    def _build_methods(self) -> None:
        descriptions = (
            (
                "Sorteio aleatório",
                "Gera permutações aleatórias e avalia conflitos até encontrar zero ou "
                "atingir o orçamento. É a linha de base aleatória.",
            ),
            (
                "Hill Climbing com reinício",
                "Avalia trocas entre posições e escolhe uma melhoria estrita. Sem melhoria, "
                "reinicia com outro estado; pode ficar preso com conflitos restantes.",
            ),
            (
                "Simulated Annealing",
                "Escolhe uma troca aleatória, aceita melhorias e pode aceitar pioras segundo "
                "a temperatura. A temperatura diminui; não há garantia de ótimo.",
            ),
            (
                "Algoritmo Genético",
                f"Mantém população k={exp.AG_POPULACAO}; torneio t={exp.AG_TORNEIO}, "
                f"elitismo E={exp.AG_ELITISMO}, OX e mutação por swap. "
                f"Fitness maximizado: 435 − conflitos. Configuração final calibrada: "
                f"p_mut={self._selected_ag_mutation():.2f}.",
            ),
        )
        for title, body in descriptions:
            self._card(self._tab_methods, title, body).pack(fill="x", pady=5)
        glossary = (
            "Estado: uma configuração completa.  Vizinhança: configurações alcançáveis "
            "por uma troca.\nFunção objetivo: número de pares diagonais em conflito. "
            "Avaliação: uma chamada contabilizada da função.\nÓtimo local: estado sem "
            "melhoria imediata. Reinício: começar busca local em novo estado.\nTemperatura: "
            "controla aceitação de pioras no SA. Semente: torna sorteios reproduzíveis. "
            "Orçamento: limite de avaliações."
        )
        self._card(self._tab_methods, "Glossário", glossary).pack(fill="x", pady=(8, 0))

    def _selected_ag_mutation(self) -> float:
        selected = self._calibration_choice.get("Algoritmo Genetico", {}).get(
            "configuracao", "p_mut_0.02"
        )
        try:
            return float(selected.rsplit("_", 1)[1])
        except (ValueError, IndexError):
            return exp.AG_MUTACAO

    def _selected_alpha(self) -> float:
        selected = self._calibration_choice.get("Simulated Annealing", {}).get(
            "configuracao", "alfa_0.999"
        )
        try:
            return float(selected.rsplit("_", 1)[1])
        except (ValueError, IndexError):
            return exp.FATOR_RESFRIAMENTO

    def _selected_hc_tie(self) -> bool:
        selected = self._calibration_choice.get("Hill Climbing com reinicio", {}).get(
            "configuracao", "empate_aleatorio"
        )
        return selected == "empate_aleatorio"

    def _build_demo(self) -> None:
        controls = ttk.Frame(self._tab_demo)
        controls.pack(fill="x", pady=(0, 9))
        ttk.Label(controls, text="Método:").pack(side="left")
        self.method_var = tk.StringVar(value="Simulated Annealing")
        self.method_box = ttk.Combobox(
            controls, textvariable=self.method_var, values=exp.METODOS,
            state="readonly", width=31,
        )
        self.method_box.pack(side="left", padx=(5, 14))
        ttk.Label(controls, text="Semente:").pack(side="left")
        self.seed_var = tk.StringVar(value=str(self._demo_seed))
        ttk.Entry(controls, textvariable=self.seed_var, width=12).pack(side="left", padx=5)
        ttk.Label(controls, text=f"N={exp.N}  ·  orçamento={exp.ORCAMENTO:,}").pack(
            side="left", padx=12
        )
        self.start_button = ttk.Button(
            controls, text="Iniciar demonstração", style="Primary.TButton",
            command=self.iniciar_demonstracao,
        )
        self.start_button.pack(side="left", padx=4)
        self.pause_button = ttk.Button(
            controls, text="Pausar", command=self.alternar_pausa, state="disabled"
        )
        self.pause_button.pack(side="left", padx=4)
        self.cancel_button = ttk.Button(
            controls, text="Cancelar", command=self.cancelar_demonstracao, state="disabled"
        )
        self.cancel_button.pack(side="left", padx=4)
        ttk.Button(
            controls, text="Nova execução", command=self.nova_execucao
        ).pack(side="left", padx=4)

        notice = ttk.Label(
            self._tab_demo,
            text="Demonstração avulsa, fora das 30 execuções oficiais. Não modifica os CSVs.",
            foreground=COLORS["muted"],
        )
        notice.pack(anchor="w", pady=(0, 7))

        content = ttk.Frame(self._tab_demo)
        content.pack(fill="both", expand=True)
        board_panel = ttk.Frame(content, style="Card.TFrame", padding=8)
        board_panel.pack(side="left", fill="both", expand=True, padx=(0, 9))
        self.board = tk.Canvas(
            board_panel, width=540, height=540, background=COLORS["white"],
            highlightthickness=0,
        )
        self.board.pack(expand=True)
        legend = ttk.Label(
            board_panel, text="Q verde: sem conflito    Q vermelho: envolvida em conflito",
            background=COLORS["white"],
        )
        legend.pack(anchor="w")

        info = ttk.Frame(content, style="Card.TFrame", padding=12)
        info.pack(side="right", fill="y")
        self.demo_method_label = self._metric(info, "Método", "Simulated Annealing")
        self.eval_label = self._metric(info, "Avaliações", f"0 / {exp.ORCAMENTO:,}")
        self.conflict_label = self._metric(info, "Conflitos atuais", "—")
        self.best_label = self._metric(info, "Melhor valor", "—")
        self.fitness_label = self._metric(info, "Fitness do AG", "—")
        self.generation_label = self._metric(info, "Geração do AG", "—")
        self.status_label = self._metric(info, "Status", "Pronto")
        self.time_label = ttk.Label(info, text="Tempo decorrido: —", foreground=COLORS["muted"])
        self.time_label.pack(anchor="w", pady=(8, 10))
        ttk.Label(info, text="Estado atual", style="Section.TLabel").pack(anchor="w")
        self.state_text = tk.Text(info, width=43, height=6, wrap="word", state="disabled")
        self.state_text.pack(fill="x", pady=(5, 8))
        self.message_label = ttk.Label(
            info, text="Escolha um método e inicie.", wraplength=340,
            justify="left", foreground=COLORS["muted"],
        )
        self.message_label.pack(fill="x", anchor="w")
        self._draw_board(None)

    def _metric(self, parent: ttk.Frame, title: str, value: str) -> ttk.Label:
        ttk.Label(parent, text=title, style="Section.TLabel").pack(anchor="w", pady=(2, 0))
        label = ttk.Label(parent, text=value, style="Metric.TLabel")
        label.pack(anchor="w", pady=(0, 5))
        return label

    def _draw_board(self, state: list[int] | None) -> None:
        self.board.delete("all")
        size = min(self.board.winfo_width(), self.board.winfo_height())
        if size < 100:
            size = 540
        cell = size / exp.N
        conflicts = queens_in_conflict(state) if state is not None else set()
        for row in range(exp.N):
            for col in range(exp.N):
                x1, y1 = col * cell, row * cell
                x2, y2 = x1 + cell, y1 + cell
                color = COLORS["grid_light"] if (row + col) % 2 == 0 else COLORS["grid_dark"]
                self.board.create_rectangle(x1, y1, x2, y2, fill=color, outline="#aebbc8")
        if state is not None:
            font_size = max(8, int(cell * 0.68))
            for col, row in enumerate(state):
                color = COLORS["conflict"] if col in conflicts else COLORS["safe"]
                self.board.create_text(
                    (col + 0.5) * cell, (row + 0.5) * cell,
                    text="Q", fill=color, font=("TkDefaultFont", font_size, "bold"),
                )

    def preparar_demonstracao(self) -> None:
        self.method_var.set("Simulated Annealing")
        self.seed_var.set(str(self._demo_seed))
        self.tabs.select(self._tab_demo)
        self.status_label.configure(text="Pronto")
        self.eval_label.configure(text=f"0 / {exp.ORCAMENTO:,}")
        self.board.focus_set()

    def iniciar_demonstracao(self) -> None:
        if self._worker is not None and self._worker.is_alive():
            return
        try:
            seed = int(self.seed_var.get())
            if seed < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Semente inválida", "Informe uma semente inteira não negativa.")
            return
        method = self.method_var.get()
        self._cancel_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._started_at = time.monotonic()
        self._event_snapshot = None
        self._draw_board(None)
        self.demo_method_label.configure(text=method)
        self.eval_label.configure(text=f"0 / {exp.ORCAMENTO:,}")
        self.conflict_label.configure(text="—")
        self.best_label.configure(text="—")
        self.fitness_label.configure(text="—")
        self.generation_label.configure(text="—")
        self.status_label.configure(text="Executando")
        self.message_label.configure(text="Iniciando execução com a semente escolhida.")
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal", text="Pausar")
        self.cancel_button.configure(state="normal")
        self._set_state_text("Aguardando avaliações…")

        def publish(event: dict[str, object]) -> None:
            try:
                self._progress.put_nowait(event)
            except queue.Full:
                try:
                    self._progress.get_nowait()
                except queue.Empty:
                    pass
                try:
                    self._progress.put_nowait(event)
                except queue.Full:
                    pass

        def worker() -> None:
            try:
                result = exp.executar_demo(
                    method,
                    seed,
                    callback=publish,
                    cancel_event=self._cancel_event,
                    pause_event=self._pause_event,
                    desempate_hc=self._selected_hc_tie(),
                    alfa_sa=self._selected_alpha(),
                    mutacao_ag=self._selected_ag_mutation(),
                )
                self._completion.put((result, None))
            except Exception as error:
                self._completion.put((None, error))

        self._worker = threading.Thread(target=worker, name="tde3-demo", daemon=False)
        self._worker.start()

    def alternar_pausa(self) -> None:
        if self._pause_event is None:
            return
        if self._pause_event.is_set():
            self._pause_event.clear()
            self.pause_button.configure(text="Continuar")
            self.status_label.configure(text="Pausando…")
        else:
            self._pause_event.set()
            self.pause_button.configure(text="Pausar")
            self.status_label.configure(text="Executando")

    def cancelar_demonstracao(self) -> None:
        if self._cancel_event is not None:
            self._cancel_event.set()
        if self._pause_event is not None:
            self._pause_event.set()
        self.status_label.configure(text="Cancelando…")

    def nova_execucao(self) -> None:
        if self._worker is not None and self._worker.is_alive():
            self.cancelar_demonstracao()
            return
        try:
            self.seed_var.set(str(int(self.seed_var.get()) + 1))
        except ValueError:
            self.seed_var.set(str(self._demo_seed))
        self._draw_board(None)
        self.eval_label.configure(text=f"0 / {exp.ORCAMENTO:,}")
        self.conflict_label.configure(text="—")
        self.best_label.configure(text="—")
        self.fitness_label.configure(text="—")
        self.generation_label.configure(text="—")
        self.status_label.configure(text="Pronto")
        self._set_state_text("Nova execução pronta.")

    def _set_state_text(self, text: str) -> None:
        self.state_text.configure(state="normal")
        self.state_text.delete("1.0", "end")
        self.state_text.insert("1.0", text)
        self.state_text.configure(state="disabled")

    def _apply_event(self, event: dict[str, object]) -> None:
        self._event_snapshot = event
        method = str(event["metodo"])
        self.demo_method_label.configure(text=method)
        self.eval_label.configure(text=f"{event['avaliacoes']:,} / {exp.ORCAMENTO:,}")
        current_conflicts = (
            event["melhor_conflitos"]
            if method == "Algoritmo Genetico"
            else event["conflitos"]
        )
        self.conflict_label.configure(text=str(current_conflicts))
        self.best_label.configure(text=str(event["melhor_conflitos"]))
        self.fitness_label.configure(
            text=str(exp.fitness_de_conflitos(int(current_conflicts)))
            if method == "Algoritmo Genetico" else "—"
        )
        self.generation_label.configure(text=str(event["geracao"]) if method == "Algoritmo Genetico" else "—")
        self.message_label.configure(text=str(event["mensagem"]))
        state = (
            event["melhor_estado"]
            if method == "Algoritmo Genetico"
            else event["estado"]
        )
        if isinstance(state, list):
            self._draw_board(state)
            self._set_state_text(" ".join(map(str, state)))
        elapsed = time.monotonic() - self._started_at
        self.time_label.configure(text=f"Tempo decorrido: {elapsed:.1f} s (informativo)")

    def _poll_worker(self) -> None:
        try:
            while True:
                self._apply_event(self._progress.get_nowait())
        except queue.Empty:
            pass
        try:
            result, error = self._completion.get_nowait()
        except queue.Empty:
            result = error = None
        if error is not None:
            self.status_label.configure(text="Erro")
            self.message_label.configure(text=f"Execução interrompida por erro: {error}")
            self._finish_controls()
        elif result is not None:
            assert isinstance(result, exp.Execucao)
            if self._cancel_event is not None and self._cancel_event.is_set():
                status = "Cancelado"
                message = "Execução cancelada pelo usuário; os resultados oficiais não foram alterados."
            elif result.sucesso:
                status = "Sucesso"
                message = "Solução encontrada: 0 conflitos."
            elif result.avaliacoes >= result.orcamento:
                status = "Orçamento esgotado"
                message = "Orçamento de avaliações atingido."
            else:
                status = "Encerrado"
                message = "Execução encerrada sem solução."
            self.status_label.configure(text=status)
            self.eval_label.configure(text=f"{result.avaliacoes:,} / {result.orcamento:,}")
            self.conflict_label.configure(text=str(result.melhor_conflitos))
            self.best_label.configure(text=str(result.melhor_conflitos))
            if self.method_var.get() == "Algoritmo Genetico":
                self.fitness_label.configure(
                    text=str(exp.fitness_de_conflitos(result.melhor_conflitos))
                )
                self.generation_label.configure(text=str(result.geracoes))
            self._draw_board(list(map(int, result.melhor_estado.split())))
            self._set_state_text(result.melhor_estado)
            self.message_label.configure(text=message)
            self.time_label.configure(
                text=f"Tempo decorrido: {time.monotonic() - self._started_at:.1f} s (informativo)"
            )
            self._finish_controls()
        if self._worker is not None and not self._worker.is_alive():
            self._worker = None
        self.root.after(70, self._poll_worker)

    def _finish_controls(self) -> None:
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled", text="Pausar")
        self.cancel_button.configure(state="disabled")

    def _build_results(self) -> None:
        ttk.Label(
            self._tab_results,
            text="Valores carregados dos CSVs locais; abrir esta aba não executa experimentos.",
            foreground=COLORS["muted"],
        ).pack(anchor="w", pady=(0, 8))
        columns = (
            "method", "runs", "success", "rate", "mean", "median", "std",
            "min", "max", "failmean", "failrange", "budget",
        )
        self.results_tree = ttk.Treeview(
            self._tab_results, columns=columns, show="headings", height=5
        )
        headings = {
            "method": "Método", "runs": "Execuções", "success": "Sucessos",
            "rate": "Taxa", "mean": "Aval. média", "median": "Mediana",
            "std": "DP", "min": "Melhor", "max": "Pior",
            "failmean": "Conflitos falhas (média)", "failrange": "Mín–máx falhas",
            "budget": "Orçamento",
        }
        widths = {
            "method": 190, "runs": 70, "success": 75, "rate": 65, "mean": 95,
            "median": 80, "std": 70, "min": 75, "max": 75, "failmean": 150,
            "failrange": 120, "budget": 100,
        }
        for column in columns:
            self.results_tree.heading(column, text=headings[column])
            self.results_tree.column(column, width=widths[column], anchor="center")
        self.results_tree.pack(fill="x", expand=False)
        for row in self._summary:
            self.results_tree.insert(
                "", "end",
                values=(
                    row["metodo"], row["execucoes"],
                    f"{row['sucessos']}/{row['execucoes']}",
                    f"{row['taxa']:.1f}%", row["media"], row["mediana"],
                    row["desvio"], row["minimo"], row["maximo"],
                    row["conflitos_falha_media"],
                    f"{row['conflitos_falha_min']}–{row['conflitos_falha_max']}",
                    row["orcamento"],
                ),
            )
        below = ttk.Frame(self._tab_results)
        below.pack(fill="both", expand=True, pady=(10, 0))
        self.chart = tk.Canvas(
            below, width=440, height=230, background=COLORS["white"],
            highlightthickness=1, highlightbackground="#d6e0e8",
        )
        self.chart.pack(side="left", fill="both", expand=True, padx=(0, 9))
        cal_frame = ttk.Frame(below, style="Card.TFrame", padding=8)
        cal_frame.pack(side="right", fill="both", expand=True)
        ttk.Label(cal_frame, text="Calibração (CSV)", style="Section.TLabel").pack(anchor="w")
        cal_columns = ("method", "config", "success", "budget")
        self.cal_tree = ttk.Treeview(
            cal_frame, columns=cal_columns, show="headings", height=7
        )
        for col, heading, width in (
            ("method", "Método", 165), ("config", "Configuração", 130),
            ("success", "Sucessos", 75), ("budget", "Orçamento", 85),
        ):
            self.cal_tree.heading(col, text=heading)
            self.cal_tree.column(col, width=width, anchor="center")
        self.cal_tree.pack(fill="both", expand=True, pady=(5, 5))
        for method in exp.METODOS:
            groups: dict[str, list[dict[str, str]]] = {}
            for row in self._calibration:
                if row.get("metodo") == method:
                    groups.setdefault(row["configuracao"], []).append(row)
            for config, group in sorted(groups.items()):
                count = sum(row["sucesso"].lower() == "true" for row in group)
                budget = sorted({int(row["orcamento"]) for row in group})
                self.cal_tree.insert(
                    "", "end",
                    values=(method, config, f"{count}/{len(group)}", " / ".join(map(str, budget))),
                )
        selected_text = "\n".join(
            f"{method}: {detail['configuracao']}"
            for method, detail in self._calibration_choice.items()
        )
        ttk.Label(
            cal_frame, text=f"Configuração escolhida:\n{selected_text}",
            wraplength=430, justify="left",
        ).pack(anchor="w")
        self._draw_success_chart()
        self.chart.bind("<Configure>", lambda _event: self._draw_success_chart())

    def _draw_success_chart(self) -> None:
        self.chart.delete("all")
        width = max(self.chart.winfo_width(), 440)
        height = max(self.chart.winfo_height(), 230)
        left, right, top, bottom = 52, width - 18, 28, height - 46
        self.chart.create_text(
            left, 12, anchor="w", text="Taxa de sucesso observada",
            fill=COLORS["navy"], font=("TkDefaultFont", 10, "bold"),
        )
        self.chart.create_line(left, top, left, bottom, fill="#708090")
        self.chart.create_line(left, bottom, right, bottom, fill="#708090")
        for tick in (0, 25, 50, 75, 100):
            y = bottom - (bottom - top) * tick / 100
            self.chart.create_line(left - 4, y, right, y, fill="#e1e7ec")
            self.chart.create_text(left - 8, y, text=str(tick), anchor="e", fill=COLORS["muted"])
        n = max(1, len(self._summary))
        segment = (right - left) / n
        for index, row in enumerate(self._summary):
            x1 = left + segment * index + segment * 0.25
            x2 = left + segment * index + segment * 0.75
            y = bottom - (bottom - top) * float(row["taxa"]) / 100
            color = (COLORS["blue"], COLORS["teal"], "#8a6fb0", "#d18b36")[index % 4]
            self.chart.create_rectangle(x1, y, x2, bottom, fill=color, outline="")
            self.chart.create_text((x1 + x2) / 2, y - 10, text=f"{row['taxa']:.1f}%", fill=COLORS["text"])
            label = str(row["metodo"]).replace(" com ", "\ncom ")
            self.chart.create_text((x1 + x2) / 2, bottom + 22, text=label, width=segment, fill=COLORS["muted"])

    def _build_analysis(self) -> None:
        by_method = {str(row["metodo"]): row for row in self._summary}
        rates = sorted(
            self._summary, key=lambda row: float(row["taxa"]), reverse=True
        )
        best = rates[0] if rates else None
        ag_row = by_method.get("Algoritmo Genetico", {})
        text = (
            f"Maior taxa nesta amostra: {best['metodo']} ({best['taxa']:.1f}%), "
            "sem implicar superioridade universal.\n\n"
            "O sorteio aleatório é uma linha de base simples. O Hill Climbing pode ficar "
            "preso em um ótimo local porque só aceita melhorias estritas; reinícios tentam "
            "novas regiões. O Simulated Annealing pode aceitar pioras segundo a temperatura, "
            "mas o resfriamento geométrico não garante o ótimo.\n\n"
            f"O AG usa torneio t={exp.AG_TORNEIO}, elitismo E={exp.AG_ELITISMO}, OX e "
            "mutação swap. O elitismo mantém a melhor aptidão observada, mas não garante "
            "encontrar o ótimo global.\n\n"
            "Nenhum método tem garantia de encontrar solução dentro do orçamento. "
            "30 execuções e uma calibração piloto pequena limitam a generalização; "
            "os resultados são da amostra observada.\n\n"
            "A introdução da ficha menciona um ciclo genético que não aparece no notebook "
            "da Aula 8. Não foi localizado código executável da Aula 9; o roteiro "
            "CodigoAlgoritmoGenetico.md foi usado como especificação. Crossover aplica-se "
            "ao AG; HC e SA não usam recombinação.\n\n"
            f"AG na amostra: {ag_row.get('sucessos', 'n/d')}/{ag_row.get('execucoes', 'n/d')} "
            f"sucessos; melhor conflito médio nas falhas: "
            f"{ag_row.get('conflitos_falha_media', 'n/d')}."
        )
        self._card(self._tab_analysis, "Leitura cuidadosa dos resultados", text).pack(fill="x")

    def _close(self) -> None:
        if self._worker is not None and self._worker.is_alive():
            self.cancelar_demonstracao()
            self.root.after(70, self._close)
            return
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    try:
        TDE3Interface(root)
    except Exception as error:
        messagebox.showerror("Não foi possível abrir a interface", str(error))
        root.destroy()
        raise
    root.mainloop()


if __name__ == "__main__":
    main()
