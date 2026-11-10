from __future__ import annotations

import csv
import itertools
import math
import random
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median, pstdev
from typing import Callable

N = 30
ORCAMENTO = 10_000
EXECUCOES = 30
SEMENTE_BASE = 20261109
TEMPERATURA_INICIAL = 2.0
FATOR_RESFRIAMENTO = 0.999
TEMPERATURA_MINIMA = 1e-3
ORCAMENTO_CALIBRACAO = 2_000
EXECUCOES_CALIBRACAO = 5
AG_POPULACAO = 50
AG_CROSSOVER = 0.9
AG_MUTACAO = 0.02
AG_GERACOES = ORCAMENTO // AG_POPULACAO
AG_ELITISMO = 1
AG_TORNEIO = 3
AG_CROSSOVER_OPERADOR = "OX"
METODOS = (
    "Sorteio aleatorio",
    "Hill Climbing com reinicio",
    "Simulated Annealing",
    "Algoritmo Genetico",
)
DESLOCAMENTO_SEMENTE = {
    "Sorteio aleatorio": 0,
    "Hill Climbing com reinicio": 10_000,
    "Simulated Annealing": 20_000,
    "Algoritmo Genetico": 50_000,
}
APTIDAO_MAXIMA = math.comb(N, 2)

AVALIACOES = 0
Evento = Callable[[dict[str, object]], None]


def _checkpoint(
    cancel_event: threading.Event | None, pause_event: threading.Event | None
) -> bool:
    while pause_event is not None and not pause_event.wait(0.1):
        if cancel_event is not None and cancel_event.is_set():
            return False
    return cancel_event is None or not cancel_event.is_set()


def _emitir(
    callback: Evento | None,
    *,
    metodo: str,
    estado: list[int],
    conflitos_atuais: int,
    avaliacoes: int,
    melhor_conflitos: int,
    melhor_estado: list[int],
    mensagem: str,
    geracao: int = 0,
    fitness: int | None = None,
) -> None:
    if callback is None:
        return
    callback(
        {
            "metodo": metodo,
            "estado": estado.copy(),
            "conflitos": conflitos_atuais,
            "avaliacoes": avaliacoes,
            "melhor_conflitos": melhor_conflitos,
            "melhor_estado": melhor_estado.copy(),
            "mensagem": mensagem,
            "geracao": geracao,
            "fitness": (
                math.comb(len(estado), 2) - conflitos_atuais
                if fitness is None
                else fitness
            ),
        }
    )


def zerar() -> None:
    global AVALIACOES
    AVALIACOES = 0


def estado_aleatorio(n: int, rng: random.Random) -> list[int]:
    return rng.sample(range(n), n)


def validar_estado(estado: list[int] | tuple[int, ...]) -> None:
    if len(estado) < 1 or sorted(estado) != list(range(len(estado))):
        raise ValueError("O estado deve ser uma permutacao de 0 ate N-1.")


def conflitos(estado: list[int] | tuple[int, ...]) -> int:
    global AVALIACOES
    validar_estado(estado)
    AVALIACOES += 1

    descendentes: dict[int, int] = {}
    ascendentes: dict[int, int] = {}
    for coluna, linha in enumerate(estado):
        descendentes[linha - coluna] = descendentes.get(linha - coluna, 0) + 1
        ascendentes[linha + coluna] = ascendentes.get(linha + coluna, 0) + 1

    return sum(
        quantidade * (quantidade - 1) // 2
        for diagonais in (descendentes, ascendentes)
        for quantidade in diagonais.values()
    )


@dataclass
class Execucao:
    metodo: str
    execucao: int
    semente: int
    orcamento: int
    avaliacoes: int
    sucesso: bool
    avaliacoes_ate_solucao: int | None
    melhor_conflitos: int
    melhor_estado: str
    geracoes: int = 0
    configuracao: str = ""


@dataclass
class ExecucaoCalibracao:
    metodo: str
    configuracao: str
    execucao: int
    semente: int
    orcamento: int
    avaliacoes: int
    sucesso: bool
    avaliacoes_ate_solucao: int | None
    melhor_conflitos: int
    geracoes: int = 0


class Contexto:
    def __init__(
        self,
        orcamento: int,
        *,
        callback: Evento | None = None,
        cancel_event: threading.Event | None = None,
        pause_event: threading.Event | None = None,
    ) -> None:
        self.orcamento = orcamento
        self.avaliacoes = 0
        self.melhor_conflitos: int | None = None
        self.melhor_estado: list[int] | None = None
        self.callback = callback
        self.cancel_event = cancel_event
        self.pause_event = pause_event
        self.cancelada = False

    @property
    def restante(self) -> int:
        return self.orcamento - self.avaliacoes

    def ativo(self) -> bool:
        self.cancelada = not _checkpoint(self.cancel_event, self.pause_event)
        return not self.cancelada

    def avaliar(
        self,
        estado: list[int],
        *,
        metodo: str,
        mensagem: str,
        geracao: int = 0,
    ) -> int:
        if self.restante <= 0:
            raise RuntimeError("Orcamento de avaliacoes esgotado.")
        resultado = conflitos(estado)
        self.avaliacoes += 1
        if self.melhor_conflitos is None or resultado < self.melhor_conflitos:
            self.melhor_conflitos = resultado
            self.melhor_estado = estado.copy()
        assert self.melhor_conflitos is not None
        assert self.melhor_estado is not None
        _emitir(
            self.callback,
            metodo=metodo,
            estado=estado,
            conflitos_atuais=resultado,
            avaliacoes=self.avaliacoes,
            melhor_conflitos=self.melhor_conflitos,
            melhor_estado=self.melhor_estado,
            mensagem=mensagem,
            geracao=geracao,
        )
        return resultado


def _resultado(
    metodo: str,
    indice: int,
    semente: int,
    orcamento: int,
    contexto: Contexto,
    avaliacoes_ate_solucao: int | None,
    geracoes: int = 0,
    configuracao: str = "",
) -> Execucao:
    assert contexto.melhor_conflitos is not None
    assert contexto.melhor_estado is not None
    assert contexto.avaliacoes == AVALIACOES
    return Execucao(
        metodo=metodo,
        execucao=indice,
        semente=semente,
        orcamento=orcamento,
        avaliacoes=contexto.avaliacoes,
        sucesso=contexto.melhor_conflitos == 0,
        avaliacoes_ate_solucao=avaliacoes_ate_solucao,
        melhor_conflitos=contexto.melhor_conflitos,
        melhor_estado=" ".join(map(str, contexto.melhor_estado)),
        geracoes=geracoes,
        configuracao=configuracao,
    )


def sorteio_aleatorio(
    n: int,
    orcamento: int,
    rng: random.Random,
    metodo: str,
    indice: int,
    semente: int,
    *,
    callback: Evento | None = None,
    cancel_event: threading.Event | None = None,
    pause_event: threading.Event | None = None,
) -> Execucao:
    zerar()
    contexto = Contexto(
        orcamento,
        callback=callback,
        cancel_event=cancel_event,
        pause_event=pause_event,
    )
    solucao_em = None
    while contexto.restante and (contexto.avaliacoes == 0 or contexto.ativo()):
        estado = estado_aleatorio(n, rng)
        if contexto.avaliar(
            estado,
            metodo=metodo,
            mensagem="Gerando e avaliando uma nova permutação",
        ) == 0:
            solucao_em = contexto.avaliacoes
            break
    return _resultado(metodo, indice, semente, orcamento, contexto, solucao_em)


def hill_climbing_reinicio(
    n: int,
    orcamento: int,
    rng: random.Random,
    metodo: str,
    indice: int,
    semente: int,
    desempate_aleatorio: bool = True,
    *,
    callback: Evento | None = None,
    cancel_event: threading.Event | None = None,
    pause_event: threading.Event | None = None,
) -> Execucao:
    zerar()
    contexto = Contexto(
        orcamento,
        callback=callback,
        cancel_event=cancel_event,
        pause_event=pause_event,
    )
    solucao_em = None

    while contexto.restante:
        atual = estado_aleatorio(n, rng)
        if contexto.avaliacoes and not contexto.ativo():
            break
        valor_atual = contexto.avaliar(
            atual,
            metodo=metodo,
            mensagem="Hill Climbing: avaliando o estado atual",
        )
        if valor_atual == 0:
            solucao_em = contexto.avaliacoes
            break

        while contexto.restante:
            melhor_valor = valor_atual
            melhores: list[list[int]] = []
            orcamento_incompleto = False

            for i, j in itertools.combinations(range(n), 2):
                if not contexto.ativo():
                    orcamento_incompleto = True
                    break
                if not contexto.restante:
                    orcamento_incompleto = True
                    break
                vizinho = atual.copy()
                vizinho[i], vizinho[j] = vizinho[j], vizinho[i]
                valor = contexto.avaliar(
                    vizinho,
                    metodo=metodo,
                    mensagem="Hill Climbing: explorando trocas e procurando melhoria",
                )
                if valor == 0:
                    solucao_em = contexto.avaliacoes
                    break
                if valor < melhor_valor:
                    melhor_valor = valor
                    melhores = [vizinho]
                elif valor == melhor_valor and valor < valor_atual:
                    melhores.append(vizinho)

            if solucao_em is not None:
                break
            if orcamento_incompleto:
                break
            if not melhores:
                _emitir(
                    callback,
                    metodo=metodo,
                    estado=atual,
                    conflitos_atuais=valor_atual,
                    avaliacoes=contexto.avaliacoes,
                    melhor_conflitos=contexto.melhor_conflitos or valor_atual,
                    melhor_estado=contexto.melhor_estado or atual,
                    mensagem="Sem melhoria local; iniciando novo estado",
                )
                break
            atual = rng.choice(melhores) if desempate_aleatorio else melhores[0]
            valor_atual = melhor_valor

        if solucao_em is not None:
            break

    return _resultado(metodo, indice, semente, orcamento, contexto, solucao_em)


def simulated_annealing(
    n: int,
    orcamento: int,
    rng: random.Random,
    metodo: str,
    indice: int,
    semente: int,
    temperatura_inicial: float = TEMPERATURA_INICIAL,
    fator_resfriamento: float = FATOR_RESFRIAMENTO,
    temperatura_minima: float = TEMPERATURA_MINIMA,
    *,
    callback: Evento | None = None,
    cancel_event: threading.Event | None = None,
    pause_event: threading.Event | None = None,
) -> Execucao:
    if temperatura_inicial <= 0 or not 0 < fator_resfriamento < 1 or temperatura_minima <= 0:
        raise ValueError("Parametros de resfriamento invalidos.")

    zerar()
    contexto = Contexto(
        orcamento,
        callback=callback,
        cancel_event=cancel_event,
        pause_event=pause_event,
    )
    atual = estado_aleatorio(n, rng)
    valor_atual = contexto.avaliar(
        atual,
        metodo=metodo,
        mensagem="Simulated Annealing: avaliando vizinho",
    )
    temperatura = temperatura_inicial
    solucao_em = contexto.avaliacoes if valor_atual == 0 else None

    while solucao_em is None and contexto.restante and contexto.ativo():
        i, j = rng.sample(range(n), 2)
        vizinho = atual.copy()
        vizinho[i], vizinho[j] = vizinho[j], vizinho[i]
        valor_vizinho = contexto.avaliar(
            vizinho,
            metodo=metodo,
            mensagem="Simulated Annealing: avaliando vizinho",
        )
        diferenca = valor_atual - valor_vizinho
        if diferenca > 0 or rng.random() < math.exp(diferenca / temperatura):
            aceitou_piora = diferenca < 0
            atual = vizinho
            valor_atual = valor_vizinho
            if aceitou_piora:
                _emitir(
                    callback,
                    metodo=metodo,
                    estado=atual,
                    conflitos_atuais=valor_atual,
                    avaliacoes=contexto.avaliacoes,
                    melhor_conflitos=contexto.melhor_conflitos or valor_atual,
                    melhor_estado=contexto.melhor_estado or atual,
                    mensagem="Movimento pior aceito pela temperatura atual",
                )
        if contexto.melhor_conflitos == 0:
            solucao_em = contexto.avaliacoes
        temperatura = max(temperatura * fator_resfriamento, temperatura_minima)

    return _resultado(metodo, indice, semente, orcamento, contexto, solucao_em)


def aptidao_maxima(n: int) -> int:
    return math.comb(n, 2)


def fitness_de_conflitos(conflitos_count: int, n: int = N) -> int:
    limite = aptidao_maxima(n)
    if not 0 <= conflitos_count <= limite:
        raise ValueError("Quantidade de conflitos fora do intervalo teorico.")
    return limite - conflitos_count


def fitness(estado: list[int] | tuple[int, ...], n: int | None = None) -> int:
    tamanho = len(estado) if n is None else n
    return fitness_de_conflitos(conflitos(estado), tamanho)


def ox_crossover(
    pai1: list[int] | tuple[int, ...],
    pai2: list[int] | tuple[int, ...],
    rng: random.Random,
) -> list[int]:
    validar_estado(pai1)
    validar_estado(pai2)
    if len(pai1) != len(pai2):
        raise ValueError("Pais precisam ter o mesmo tamanho.")
    tamanho = len(pai1)
    if tuple(pai1) == tuple(pai2):
        return list(pai1)

    inicio, fim = sorted(rng.sample(range(tamanho + 1), 2))
    filho: list[int | None] = [None] * tamanho
    segmento = set(pai1[inicio:fim])
    filho[inicio:fim] = pai1[inicio:fim]
    ausentes = [
        pai2[pos % tamanho]
        for pos in range(fim, fim + tamanho)
        if pai2[pos % tamanho] not in segmento
    ]
    posicoes = [(pos % tamanho) for pos in range(fim, fim + tamanho) if filho[pos % tamanho] is None]
    for posicao, gene in zip(posicoes, ausentes):
        filho[posicao] = gene
    resultado = [int(gene) for gene in filho if gene is not None]
    validar_estado(resultado)
    return resultado


def mutacao_swap(
    cromossomo: list[int] | tuple[int, ...],
    probabilidade: float,
    rng: random.Random,
) -> list[int]:
    if not 0 <= probabilidade <= 1:
        raise ValueError("A probabilidade de mutacao deve estar entre 0 e 1.")
    validar_estado(cromossomo)
    mutado = list(cromossomo)
    tamanho = len(mutado)
    if tamanho < 2:
        return mutado
    for indice in range(tamanho):
        if rng.random() < probabilidade:
            outra = rng.randrange(tamanho - 1)
            if outra >= indice:
                outra += 1
            mutado[indice], mutado[outra] = mutado[outra], mutado[indice]
    validar_estado(mutado)
    return mutado


def selecao_torneio(
    populacao: list[list[int]],
    conflitos_populacao: list[int],
    rng: random.Random,
    tamanho_torneio: int = AG_TORNEIO,
) -> list[int]:
    if len(populacao) != len(conflitos_populacao) or not populacao:
        raise ValueError("Populacao e valores de conflitos precisam corresponder.")
    if tamanho_torneio < 1:
        raise ValueError("O torneio precisa conter pelo menos um individuo.")
    participantes = [rng.randrange(len(populacao)) for _ in range(tamanho_torneio)]
    vencedor = max(
        participantes,
        key=lambda indice: fitness_de_conflitos(
            conflitos_populacao[indice], len(populacao[indice])
        ),
    )
    return populacao[vencedor].copy()


def criar_proxima_geracao(
    populacao: list[list[int]],
    conflitos_populacao: list[int],
    rng: random.Random,
    *,
    elitismo: int = AG_ELITISMO,
    probabilidade_crossover: float = AG_CROSSOVER,
    probabilidade_mutacao: float = AG_MUTACAO,
    tamanho_torneio: int = AG_TORNEIO,
) -> list[list[int]]:
    if not 1 <= elitismo <= len(populacao):
        raise ValueError("Elitismo deve estar entre 1 e o tamanho da populacao.")
    if len(populacao) != len(conflitos_populacao):
        raise ValueError("Cada individuo precisa ter um valor de conflitos.")
    if not 0 <= probabilidade_crossover <= 1:
        raise ValueError("A probabilidade de crossover deve estar entre 0 e 1.")

    ordem = sorted(
        range(len(populacao)),
        key=lambda i: fitness_de_conflitos(conflitos_populacao[i], len(populacao[i])),
        reverse=True,
    )
    nova = [populacao[i].copy() for i in ordem[:elitismo]]
    while len(nova) < len(populacao):
        pai1 = selecao_torneio(
            populacao, conflitos_populacao, rng, tamanho_torneio
        )
        pai2 = selecao_torneio(
            populacao, conflitos_populacao, rng, tamanho_torneio
        )
        filho = (
            ox_crossover(pai1, pai2, rng)
            if rng.random() < probabilidade_crossover
            else pai1.copy()
        )
        nova.append(mutacao_swap(filho, probabilidade_mutacao, rng))
    return nova


def _configuracao_ag(
    tamanho_populacao: int,
    probabilidade_crossover: float,
    probabilidade_mutacao: float,
    max_geracoes: int,
    elitismo: int,
    tamanho_torneio: int,
) -> str:
    return (
        f"k={tamanho_populacao};p_cross={probabilidade_crossover:g};"
        f"p_mut={probabilidade_mutacao:g};G={max_geracoes};E={elitismo};"
        f"torneio={tamanho_torneio};OX"
    )


def algoritmo_genetico(
    n: int,
    orcamento: int,
    rng: random.Random,
    metodo: str = "Algoritmo Genetico",
    indice: int = 1,
    semente: int = SEMENTE_BASE,
    *,
    tamanho_populacao: int = AG_POPULACAO,
    probabilidade_crossover: float = AG_CROSSOVER,
    probabilidade_mutacao: float = AG_MUTACAO,
    max_geracoes: int = AG_GERACOES,
    elitismo: int = AG_ELITISMO,
    tamanho_torneio: int = AG_TORNEIO,
    callback: Evento | None = None,
    cancel_event: threading.Event | None = None,
    pause_event: threading.Event | None = None,
) -> Execucao:
    if n < 4 or tamanho_populacao < 2:
        raise ValueError("N deve ser >= 4 e a populacao deve ter ao menos 2 individuos.")
    if orcamento < tamanho_populacao:
        raise ValueError("O orcamento deve comportar a avaliacao da populacao inicial.")
    if max_geracoes < 1 or not 1 <= elitismo < tamanho_populacao:
        raise ValueError("Limite de geracoes ou elitismo invalido.")
    if not 0 <= probabilidade_crossover <= 1 or not 0 <= probabilidade_mutacao <= 1:
        raise ValueError("Probabilidades devem estar entre 0 e 1.")

    zerar()
    contexto = Contexto(
        orcamento,
        callback=callback,
        cancel_event=cancel_event,
        pause_event=pause_event,
    )
    configuracao = _configuracao_ag(
        tamanho_populacao,
        probabilidade_crossover,
        probabilidade_mutacao,
        max_geracoes,
        elitismo,
        tamanho_torneio,
    )
    populacao = [estado_aleatorio(n, rng) for _ in range(tamanho_populacao)]
    conflitos_populacao: list[int] = []
    solucao_em = None
    geracao = 1

    for individuo in populacao:
        if contexto.avaliacoes and not contexto.ativo():
            break
        valor = contexto.avaliar(
            individuo,
            metodo=metodo,
            mensagem="Algoritmo Genético: avaliando indivíduo da população",
            geracao=geracao,
        )
        conflitos_populacao.append(valor)
        if valor == 0:
            solucao_em = contexto.avaliacoes
            break
    if len(conflitos_populacao) < tamanho_populacao or solucao_em is not None:
        return _resultado(
            metodo,
            indice,
            semente,
            orcamento,
            contexto,
            solucao_em,
            geracoes=geracao if conflitos_populacao else 0,
            configuracao=configuracao,
        )

    while (
        geracao < max_geracoes
        and contexto.restante >= tamanho_populacao
        and contexto.ativo()
    ):
        populacao = criar_proxima_geracao(
            populacao,
            conflitos_populacao,
            rng,
            elitismo=elitismo,
            probabilidade_crossover=probabilidade_crossover,
            probabilidade_mutacao=probabilidade_mutacao,
            tamanho_torneio=tamanho_torneio,
        )
        geracao += 1
        conflitos_populacao = []
        for individuo in populacao:
            if contexto.avaliacoes and not contexto.ativo():
                break
            valor = contexto.avaliar(
                individuo,
                metodo=metodo,
                mensagem="Algoritmo Genético: avaliando indivíduo da população",
                geracao=geracao,
            )
            conflitos_populacao.append(valor)
            if valor == 0:
                solucao_em = contexto.avaliacoes
                break
        if solucao_em is not None or len(conflitos_populacao) < tamanho_populacao:
            break

    return _resultado(
        metodo,
        indice,
        semente,
        orcamento,
        contexto,
        solucao_em,
        geracoes=geracao,
        configuracao=configuracao,
    )


def executar_experimentos(
    n: int = N,
    orcamento: int = ORCAMENTO,
    execucoes: int = EXECUCOES,
    semente_base: int = SEMENTE_BASE,
    desempate_hc: bool = True,
    alfa_sa: float = FATOR_RESFRIAMENTO,
    mutacao_ag: float = AG_MUTACAO,
) -> list[Execucao]:
    if n < 4 or orcamento < 1 or execucoes < 1:
        raise ValueError("N deve ser >= 4 e orcamento/execucoes devem ser positivos.")

    resultados: list[Execucao] = []
    for metodo in METODOS:
        for indice in range(1, execucoes + 1):
            semente = semente_base + DESLOCAMENTO_SEMENTE[metodo] + indice - 1
            rng = random.Random(semente)
            if metodo == "Sorteio aleatorio":
                resultado = sorteio_aleatorio(
                    n, orcamento, rng, metodo, indice, semente
                )
            elif metodo == "Hill Climbing com reinicio":
                resultado = hill_climbing_reinicio(
                    n, orcamento, rng, metodo, indice, semente, desempate_hc
                )
            elif metodo == "Simulated Annealing":
                resultado = simulated_annealing(
                    n,
                    orcamento,
                    rng,
                    metodo,
                    indice,
                    semente,
                    fator_resfriamento=alfa_sa,
                )
            else:
                resultado = algoritmo_genetico(
                    n,
                    orcamento,
                    rng,
                    metodo,
                    indice,
                    semente,
                    probabilidade_mutacao=mutacao_ag,
                )
            resultados.append(resultado)
    return resultados


def executar_demo(
    metodo: str,
    semente: int,
    orcamento: int = ORCAMENTO,
    *,
    callback: Evento | None = None,
    cancel_event: threading.Event | None = None,
    pause_event: threading.Event | None = None,
    desempate_hc: bool = True,
    alfa_sa: float = FATOR_RESFRIAMENTO,
    mutacao_ag: float = AG_MUTACAO,
) -> Execucao:
    if metodo not in METODOS:
        raise ValueError(f"Método desconhecido: {metodo}")
    rng = random.Random(semente)
    argumentos = {
        "callback": callback,
        "cancel_event": cancel_event,
        "pause_event": pause_event,
    }
    if metodo == "Sorteio aleatorio":
        return sorteio_aleatorio(
            N, orcamento, rng, metodo, 1, semente, **argumentos
        )
    if metodo == "Hill Climbing com reinicio":
        return hill_climbing_reinicio(
            N,
            orcamento,
            rng,
            metodo,
            1,
            semente,
            desempate_aleatorio=desempate_hc,
            **argumentos,
        )
    if metodo == "Simulated Annealing":
        return simulated_annealing(
            N,
            orcamento,
            rng,
            metodo,
            1,
            semente,
            fator_resfriamento=alfa_sa,
            **argumentos,
        )
    return algoritmo_genetico(
        N,
        orcamento,
        rng,
        metodo,
        1,
        semente,
        probabilidade_mutacao=mutacao_ag,
        callback=callback,
        cancel_event=cancel_event,
        pause_event=pause_event,
    )


def _executar_calibracao(
    metodo: str,
    configuracao: str,
    n: int,
    orcamento: int,
    indice: int,
    semente: int,
    desempate_hc: bool | None = None,
    alfa_sa: float | None = None,
    mutacao_ag: float | None = None,
) -> ExecucaoCalibracao:
    rng = random.Random(semente)
    if metodo == "Hill Climbing com reinicio":
        resultado = hill_climbing_reinicio(
            n,
            orcamento,
            rng,
            metodo,
            indice,
            semente,
            desempate_aleatorio=bool(desempate_hc),
        )
    elif metodo == "Simulated Annealing":
        resultado = simulated_annealing(
            n,
            orcamento,
            rng,
            metodo,
            indice,
            semente,
            fator_resfriamento=float(alfa_sa),
        )
    else:
        resultado = algoritmo_genetico(
            n,
            orcamento,
            rng,
            metodo,
            indice,
            semente,
            probabilidade_mutacao=float(mutacao_ag),
        )
    return ExecucaoCalibracao(
        metodo=metodo,
        configuracao=configuracao,
        execucao=indice,
        semente=semente,
        orcamento=orcamento,
        avaliacoes=resultado.avaliacoes,
        sucesso=resultado.sucesso,
        avaliacoes_ate_solucao=resultado.avaliacoes_ate_solucao,
        melhor_conflitos=resultado.melhor_conflitos,
        geracoes=resultado.geracoes,
    )


def calibrar_metodos(
    n: int = N,
    orcamento: int = ORCAMENTO_CALIBRACAO,
    execucoes: int = EXECUCOES_CALIBRACAO,
    semente_base: int = SEMENTE_BASE,
) -> tuple[list[ExecucaoCalibracao], dict[str, bool | float]]:
    if orcamento < 1 or execucoes < 1:
        raise ValueError("Orcamento e execucoes de calibracao devem ser positivos.")
    configuracoes = {
        "Hill Climbing com reinicio": [
            ("empate_aleatorio", {"desempate_hc": True}, True),
            ("primeiro_empate", {"desempate_hc": False}, False),
        ],
        "Simulated Annealing": [
            ("alfa_0.999", {"alfa_sa": 0.999}, 0.999),
            ("alfa_0.99", {"alfa_sa": 0.99}, 0.99),
        ],
        "Algoritmo Genetico": [
            ("p_mut_0.02", {"mutacao_ag": 0.02}, 0.02),
            ("p_mut_0.05", {"mutacao_ag": 0.05}, 0.05),
        ],
    }
    deslocamentos = {
        "Hill Climbing com reinicio": 30_000,
        "Simulated Annealing": 40_000,
        "Algoritmo Genetico": 60_000,
    }
    resultados: list[ExecucaoCalibracao] = []
    escolhidas: dict[str, bool | float] = {}

    for metodo, opcoes in configuracoes.items():
        grupos: list[list[ExecucaoCalibracao]] = []
        for nome_configuracao, parametros, valor_escolha in opcoes:
            grupo = []
            for indice in range(1, execucoes + 1):
                semente = semente_base + deslocamentos[metodo] + indice - 1
                grupo.append(
                    _executar_calibracao(
                        metodo,
                        nome_configuracao,
                        n,
                        orcamento,
                        indice,
                        semente,
                        **parametros,
                    )
                )
            resultados.extend(grupo)
            grupos.append(grupo)

        def pontuacao(grupo: list[ExecucaoCalibracao]) -> tuple[int, float]:
            sucessos = [r for r in grupo if r.sucesso]
            media = (
                sum(r.avaliacoes_ate_solucao or 0 for r in sucessos) / len(sucessos)
                if sucessos
                else float("inf")
            )
            media_melhor = sum(r.melhor_conflitos for r in grupo) / len(grupo)
            return -len(sucessos), (media_melhor if not sucessos else media)

        selecionado = min(range(len(grupos)), key=lambda i: pontuacao(grupos[i]))
        escolhidas[metodo] = opcoes[selecionado][2]

    return resultados, escolhidas


def salvar_resultados(resultados: list[Execucao], destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    campos = list(asdict(resultados[0]).keys())
    with destino.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        for resultado in resultados:
            escritor.writerow(asdict(resultado))


def salvar_calibracao(resultados: list[ExecucaoCalibracao], destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    campos = list(asdict(resultados[0]).keys())
    with destino.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        for resultado in resultados:
            escritor.writerow(asdict(resultado))


def _estatisticas(valores: list[int]) -> tuple[str, str, str]:
    if not valores:
        return "n/a", "n/a", "n/a"
    return (
        f"{sum(valores) / len(valores):.1f}",
        str(min(valores)),
        str(max(valores)),
    )


def _distribuicao(valores: list[int]) -> tuple[str, str]:
    if not valores:
        return "n/a", "n/a"
    return f"{median(valores):.1f}", f"{pstdev(valores):.1f}"


def resumir(resultados: list[Execucao]) -> list[dict[str, str | int]]:
    resumo = []
    for metodo in METODOS:
        grupo = [r for r in resultados if r.metodo == metodo]
        sucesso = [r for r in grupo if r.sucesso]
        falhas = [r for r in grupo if not r.sucesso]
        custos = [r.avaliacoes_ate_solucao for r in sucesso]
        assert all(custo is not None for custo in custos)
        custo_media, custo_melhor, custo_pior = _estatisticas(
            [int(custo) for custo in custos if custo is not None]
        )
        custo_mediana, custo_desvio = _distribuicao(
            [int(custo) for custo in custos if custo is not None]
        )
        falhas_media, falhas_melhor, falhas_pior = _estatisticas(
            [r.melhor_conflitos for r in falhas]
        )
        falhas_mediana, falhas_desvio = _distribuicao(
            [r.melhor_conflitos for r in falhas]
        )
        orcamento_metodos = sorted({r.orcamento for r in grupo})
        resumo.append(
            {
                "metodo": metodo,
                "execucoes": len(grupo),
                "sucessos": len(sucesso),
                "taxa_sucesso_pct": f"{100 * len(sucesso) / len(grupo):.1f}",
                "avaliacoes_sucesso_media": custo_media,
                "avaliacoes_sucesso_melhor": custo_melhor,
                "avaliacoes_sucesso_pior": custo_pior,
                "avaliacoes_sucesso_mediana": custo_mediana,
                "avaliacoes_sucesso_desvio_padrao": custo_desvio,
                "conflitos_falhas_media": falhas_media,
                "conflitos_falhas_melhor": falhas_melhor,
                "conflitos_falhas_pior": falhas_pior,
                "conflitos_falhas_mediana": falhas_mediana,
                "conflitos_falhas_desvio_padrao": falhas_desvio,
                "orcamento_por_execucao": "/".join(map(str, orcamento_metodos)),
                "geracoes_maximas_observadas": max((r.geracoes for r in grupo), default=0),
            }
        )
    return resumo


def salvar_resumo(resumo: list[dict[str, str | int]], destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(resumo[0].keys()))
        escritor.writeheader()
        escritor.writerows(resumo)


def main() -> None:
    raiz = Path(__file__).resolve().parents[1]
    resultados = executar_experimentos()
    assert all(r.avaliacoes <= r.orcamento for r in resultados)
    salvar_resultados(resultados, raiz / "entrega" / "resultados.csv")
    salvar_resumo(resumir(resultados), raiz / "entrega" / "tabela_resumo.csv")
    for linha in resumir(resultados):
        print(
            f"{linha['metodo']}: sucesso {linha['sucessos']}/{linha['execucoes']} "
            f"({linha['taxa_sucesso_pct']}%), "
            f"avaliacoes ate solucao media/melhor/pior="
            f"{linha['avaliacoes_sucesso_media']}/"
            f"{linha['avaliacoes_sucesso_melhor']}/"
            f"{linha['avaliacoes_sucesso_pior']}; "
            f"conflitos nas falhas media/melhor/pior="
            f"{linha['conflitos_falhas_media']}/"
            f"{linha['conflitos_falhas_melhor']}/"
            f"{linha['conflitos_falhas_pior']}"
        )
    print(f"N={N}, espaco={math.factorial(N)} estados, vizinhos={N * (N - 1) // 2}")
    print(f"CSV bruto: {raiz / 'entrega' / 'resultados.csv'}")


if __name__ == "__main__":
    main()
