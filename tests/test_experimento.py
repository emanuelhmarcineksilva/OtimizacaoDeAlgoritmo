import random
import hashlib
import threading
import unittest

from src import experimento as exp
import interface


class ExperimentoTests(unittest.TestCase):
    def setUp(self):
        exp.zerar()

    def test_funcao_objetivo_conhecida_e_contador(self):
        solucao_oito = [0, 4, 7, 5, 2, 6, 1, 3]
        self.assertEqual(exp.conflitos(solucao_oito), 0)
        self.assertEqual(exp.AVALIACOES, 1)
        self.assertEqual(exp.conflitos(list(range(8))), 28)
        self.assertEqual(exp.AVALIACOES, 2)

    def test_funcao_objetivo_rejeita_estado_invalido(self):
        with self.assertRaises(ValueError):
            exp.conflitos([0, 0, 1])
        self.assertEqual(exp.AVALIACOES, 0)

    def test_gerador_e_troca_preservam_permutacao(self):
        estado = exp.estado_aleatorio(30, random.Random(11))
        exp.validar_estado(estado)
        estado[2], estado[17] = estado[17], estado[2]
        exp.validar_estado(estado)

    def test_metodos_respeitam_orcamento_e_schema_comum(self):
        resultados = exp.executar_experimentos(n=8, orcamento=200, execucoes=2)
        self.assertEqual(len(resultados), 8)
        for resultado in resultados:
            self.assertLessEqual(resultado.avaliacoes, resultado.orcamento)
            self.assertGreaterEqual(resultado.avaliacoes, 1)
            self.assertEqual(resultado.sucesso, resultado.melhor_conflitos == 0)
            self.assertEqual(resultado.sucesso, resultado.avaliacoes_ate_solucao is not None)
            exp.validar_estado(list(map(int, resultado.melhor_estado.split())))

    def test_reprodutibilidade_por_semente(self):
        primeira = exp.executar_experimentos(n=10, orcamento=300, execucoes=2)
        segunda = exp.executar_experimentos(n=10, orcamento=300, execucoes=2)
        self.assertEqual(primeira, segunda)

    def test_simulated_annealing_usa_orcamento_quando_nao_acha_solucao(self):
        resultado = exp.simulated_annealing(
            n=30,
            orcamento=5,
            rng=random.Random(1),
            metodo="Simulated Annealing",
            indice=1,
            semente=1,
        )
        self.assertFalse(resultado.sucesso)
        self.assertEqual(resultado.avaliacoes, 5)

    def test_resumo_mantem_falhas_e_custos_de_sucesso(self):
        resultados = exp.executar_experimentos(n=8, orcamento=200, execucoes=3)
        resumo = exp.resumir(resultados)
        self.assertEqual(len(resumo), 4)
        for linha in resumo:
            self.assertEqual(linha["execucoes"], 3)
            self.assertLessEqual(float(linha["taxa_sucesso_pct"]), 100)
            self.assertEqual(linha["orcamento_por_execucao"], "200")

    def test_calibracao_tem_esforco_simetrico_e_reprodutivel(self):
        primeira, escolhidas = exp.calibrar_metodos(n=8, orcamento=50, execucoes=2)
        segunda, escolhidas_2 = exp.calibrar_metodos(n=8, orcamento=50, execucoes=2)
        self.assertEqual(primeira, segunda)
        self.assertEqual(escolhidas, escolhidas_2)
        self.assertEqual(len(primeira), 12)
        por_metodo = {}
        for resultado in primeira:
            por_metodo.setdefault(resultado.metodo, []).append(resultado)
            self.assertLessEqual(resultado.avaliacoes, resultado.orcamento)
        self.assertEqual(
            len(por_metodo["Hill Climbing com reinicio"]),
            len(por_metodo["Simulated Annealing"]),
        )
        self.assertEqual(
            {r.orcamento for r in por_metodo["Hill Climbing com reinicio"]},
            {r.orcamento for r in por_metodo["Simulated Annealing"]},
        )


class AlgoritmoGeneticoTests(unittest.TestCase):
    def setUp(self):
        exp.zerar()

    def test_cromossomos_iniciais_sao_permutacoes_de_30(self):
        for seed in range(10):
            exp.validar_estado(exp.estado_aleatorio(30, random.Random(seed)))

    def test_ox_preserva_permutacoes_com_pais_iguais_e_diferentes(self):
        rng = random.Random(21)
        pai1 = list(range(30))
        pai2 = list(reversed(range(30)))
        for _ in range(100):
            filho = exp.ox_crossover(pai1, pai2, rng)
            exp.validar_estado(filho)
        self.assertEqual(exp.ox_crossover(pai1, pai1, rng), pai1)

    def test_mutacao_swap_preserva_permutacao_e_taxa_zero(self):
        cromossomo = exp.estado_aleatorio(30, random.Random(3))
        self.assertEqual(
            exp.mutacao_swap(cromossomo, 0, random.Random(4)), cromossomo
        )
        exp.validar_estado(exp.mutacao_swap(cromossomo, 1, random.Random(5)))

    def test_elitismo_preserva_melhor_e_fitness_non_decreasing(self):
        rng = random.Random(6)
        populacao = [
            [0, 4, 7, 5, 2, 6, 1, 3],
            [0, 1, 2, 3, 4, 5, 6, 7],
            exp.estado_aleatorio(8, rng),
            exp.estado_aleatorio(8, rng),
        ]
        conflitos_antes = [exp.conflitos(individuo) for individuo in populacao]
        melhor_antes = max(
            exp.fitness_de_conflitos(c, 8) for c in conflitos_antes
        )
        melhor_individuo = populacao[conflitos_antes.index(min(conflitos_antes))]
        proxima = exp.criar_proxima_geracao(
            populacao,
            conflitos_antes,
            rng,
            elitismo=1,
            probabilidade_crossover=1,
            probabilidade_mutacao=1,
        )
        self.assertIn(melhor_individuo, proxima)
        conflitos_depois = [exp.conflitos(individuo) for individuo in proxima]
        melhor_depois = max(
            exp.fitness_de_conflitos(c, 8) for c in conflitos_depois
        )
        self.assertGreaterEqual(melhor_depois, melhor_antes)

    def test_torneio_retorna_individuo_da_populacao(self):
        populacao = [list(range(8)), list(reversed(range(8)))]
        conflitos_pop = [exp.conflitos(individuo) for individuo in populacao]
        selecionado = exp.selecao_torneio(
            populacao, conflitos_pop, random.Random(7), tamanho_torneio=3
        )
        self.assertIn(selecionado, populacao)

    def test_fitness_e_alvo_estao_corretos(self):
        solucao = [0, 4, 7, 5, 2, 6, 1, 3]
        estado_ruim = list(range(8))
        self.assertGreater(exp.fitness(solucao), exp.fitness(estado_ruim))
        self.assertEqual(exp.fitness_de_conflitos(0, 30), 435)
        self.assertEqual(exp.fitness(solucao), 28)
        self.assertEqual(exp.AVALIACOES, 3)

    def test_ag_contador_orcamento_e_geracoes(self):
        eventos = []
        resultado = exp.algoritmo_genetico(
            30,
            12,
            random.Random(8),
            semente=8,
            tamanho_populacao=5,
            max_geracoes=10,
            callback=eventos.append,
        )
        self.assertEqual(resultado.avaliacoes, 10)
        self.assertEqual(exp.AVALIACOES, 10)
        self.assertEqual(resultado.geracoes, 2)
        self.assertEqual(len(eventos), resultado.avaliacoes)
        self.assertLessEqual(resultado.avaliacoes, resultado.orcamento)

    def test_ag_respeita_limite_de_geracoes(self):
        resultado = exp.algoritmo_genetico(
            30,
            100,
            random.Random(9),
            semente=9,
            tamanho_populacao=4,
            max_geracoes=3,
        )
        self.assertEqual(resultado.geracoes, 3)
        self.assertEqual(resultado.avaliacoes, 12)

    def test_ag_reprodutivel_com_mesma_semente(self):
        def executar():
            return exp.algoritmo_genetico(
                30,
                200,
                random.Random(10),
                semente=10,
                tamanho_populacao=10,
                max_geracoes=20,
            )

        self.assertEqual(executar(), executar())

    def test_ag_retorna_melhor_individuo_mesmo_sem_solucao(self):
        resultado = exp.algoritmo_genetico(
            30,
            10,
            random.Random(11),
            semente=11,
            tamanho_populacao=10,
            max_geracoes=20,
        )
        self.assertFalse(resultado.sucesso)
        self.assertGreater(resultado.melhor_conflitos, 0)
        exp.validar_estado(list(map(int, resultado.melhor_estado.split())))

    def test_ag_encontra_solucao_n8_com_semente_fixa(self):
        resultado = exp.algoritmo_genetico(
            8,
            5_000,
            random.Random(17),
            semente=17,
            tamanho_populacao=50,
            probabilidade_mutacao=0.02,
            max_geracoes=100,
        )
        self.assertTrue(resultado.sucesso)
        self.assertEqual(resultado.melhor_conflitos, 0)
        self.assertLessEqual(resultado.avaliacoes, 5_000)

    def test_cancelamento_de_ag_encerra_sem_avaliacoes_ocultas(self):
        cancel = threading.Event()
        cancel.set()
        eventos = []
        resultado = exp.algoritmo_genetico(
            30,
            500,
            random.Random(18),
            semente=18,
            tamanho_populacao=50,
            cancel_event=cancel,
            callback=eventos.append,
        )
        self.assertEqual(resultado.avaliacoes, 1)
        self.assertEqual(len(eventos), 1)
        self.assertEqual(exp.AVALIACOES, 1)


class InterfaceDataTests(unittest.TestCase):
    def test_leitura_dos_csvs_nao_os_modifica_e_resume_quatro_metodos(self):
        resultado_path = interface.RESULTADOS_CSV
        calibracao_path = interface.CALIBRACAO_CSV
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (resultado_path, calibracao_path)
        }
        rows = interface.read_csv_rows(resultado_path)
        calibracao = interface.read_csv_rows(calibracao_path)
        ga_row = dict(rows[0])
        ga_row.update(metodo="Algoritmo Genetico", sucesso="False", melhor_conflitos="3")
        calibration_row = dict(calibracao[0])
        calibration_row.update(
            metodo="Algoritmo Genetico", configuracao="p_mut_0.02",
            sucesso="False", melhor_conflitos="3",
        )
        summary = interface.summarize_rows(rows + [ga_row])
        choices = interface.choose_calibration(calibracao + [calibration_row])
        self.assertEqual(len(summary), 4)
        self.assertEqual(
            {row["metodo"] for row in summary}, set(exp.METODOS)
        )
        self.assertIn("Algoritmo Genetico", choices)
        self.assertEqual(
            before[resultado_path], hashlib.sha256(resultado_path.read_bytes()).hexdigest()
        )
        self.assertEqual(
            before[calibracao_path], hashlib.sha256(calibracao_path.read_bytes()).hexdigest()
        )

    def test_destaque_de_conflitos_nao_avalia_funcao_objetivo(self):
        exp.zerar()
        conflicts = interface.queens_in_conflict([0, 1, 2, 3])
        self.assertEqual(conflicts, {0, 1, 2, 3})
        self.assertEqual(exp.AVALIACOES, 0)


if __name__ == "__main__":
    unittest.main()
