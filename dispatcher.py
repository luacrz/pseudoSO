import sys
from processo import Processo
from memoria import GerenciadorMemoria
from recursos import GerenciadorRecursos
from arquivos import GerenciadorArquivos
from filas import GerenciadorFilas

class Dispatcher:
    def __init__(self, processes_file, files_file):
        self.processes_file = processes_file
        self.files_file = files_file
        self.tempo_atual = 0
        self.pid_counter = 0  # PID começa em 0 conforme especificação
        self.processos = []
        self.processos_ativos = []
        self.gerenciador_memoria = GerenciadorMemoria()
        self.gerenciador_recursos = GerenciadorRecursos()
        self.gerenciador_arquivos = None
        self.gerenciador_filas = GerenciadorFilas()
        self.operacoes_arquivo = []
        self.operacao_counter = 1  # Contador para número das operações
    
    def carregar_processos(self):
        with open(self.processes_file, 'r') as f:
            for line in f:
                if line.strip():
                    parts = list(map(int, line.strip().split(',')))
                    processo = Processo(
                        pid=self.pid_counter,
                        tempo_inicializacao=parts[0],
                        prioridade=parts[1],
                        tempo_processador=parts[2],
                        blocos_memoria=parts[3],
                        num_impressora=parts[4],
                        req_scanner=parts[5],
                        req_modem=parts[6],
                        num_disco=parts[7]
                    )
                    self.processos.append(processo)
                    self.pid_counter += 1
    
    def carregar_arquivos_e_operacoes(self):
        with open(self.files_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            
            total_blocos = int(lines[0])
            self.gerenciador_arquivos = GerenciadorArquivos(total_blocos)
            
            num_arquivos = int(lines[1])
            arquivos_iniciais = []
            
            for i in range(2, 2 + num_arquivos):
                parts = lines[i].split(',')
                nome = parts[0].strip()
                bloco_inicial = int(parts[1])
                num_blocos = int(parts[2])
                arquivos_iniciais.append((nome, bloco_inicial, num_blocos))
            
            self.gerenciador_arquivos.carregar_arquivos_iniciais(arquivos_iniciais)
            
            for i in range(2 + num_arquivos, len(lines)):
                parts = lines[i].split(',')
                pid = int(parts[0])
                codigo = int(parts[1])
                nome = parts[2].strip()
                num_blocos = int(parts[3]) if codigo == 0 else 0
                self.operacoes_arquivo.append((pid, codigo, nome, num_blocos))
    
    def admitir_novos_processos(self):
        for processo in self.processos:
            if processo.tempo_inicializacao == self.tempo_atual:
                # Verificação dos limites máximos de memória
                if processo.prioridade == 0 and processo.blocos_memoria > 64:
                    print(f"Tempo {self.tempo_atual}: Erro - Processo {processo.pid} excede limite máximo de 64 blocos para tempo real")
                    continue
                elif processo.prioridade > 0 and processo.blocos_memoria > 960:
                    print(f"Tempo {self.tempo_atual}: Erro - Processo {processo.pid} excede limite máximo de 960 blocos para usuários")
                    continue

                # Verificação de disponibilidade de memória
                if not self.gerenciador_memoria.verificar_disponibilidade(processo):
                    print(f"Tempo {self.tempo_atual}: Falha - Memória insuficiente para o processo {processo.pid} (requer {processo.blocos_memoria} blocos contíguos)")
                    continue

                # Verificação de recursos de E/S
                if processo.necessita_recurso() and not self.gerenciador_recursos.verificar_disponibilidade(processo):
                    print(f"Tempo {self.tempo_atual}: Falha - Recursos de E/S indisponíveis para o processo {processo.pid}")
                    continue

                # Tentativa de alocação de memória
                if not self.gerenciador_memoria.alocar_memoria(processo):
                    print(f"Tempo {self.tempo_atual}: Falha - Não foi possível alocar memória para o processo {processo.pid}")
                    continue

                # Tentativa de alocação de recursos (se necessário)
                if processo.necessita_recurso():
                    if not self.gerenciador_recursos.alocar_recursos(processo):
                        self.gerenciador_memoria.liberar_memoria(processo)  # Libera a memória alocada
                        print(f"Tempo {self.tempo_atual}: Falha - Não foi possível alocar todos os recursos para o processo {processo.pid}")
                        continue

                # Se chegou até aqui, todas as alocações foram bem-sucedidas
                self.gerenciador_filas.adicionar_processo(processo)
                self.processos_ativos.append(processo)
                print(f"Tempo {self.tempo_atual}: Processo {processo.pid} admitido com sucesso")
                self.imprimir_info_processo(processo)

    
    def imprimir_info_processo(self, processo):
        """Imprime as informações do processo no formato especificado"""
        print("dispatcher =>")
        print(f"    PID: {processo.pid}")
        print(f"    offset: {processo.offset_memoria}")
        print(f"    blocks: {processo.blocos_memoria}")
        print(f"    priority: {processo.prioridade}")
        print(f"    time: {processo.tempo_processador}")
        print(f"    printers: {1 if processo.num_impressora > 0 else 0}")
        print(f"    scanners: {1 if processo.req_scanner > 0 else 0}")
        print(f"    modems: {1 if processo.req_modem > 0 else 0}")
        print(f"    drives: {1 if processo.num_disco > 0 else 0}")
        print(f"process {processo.pid} =>")
    
    def executar_processo(self, processo):
        """Executa um processo por 1 quantum e imprime as instruções"""
        #print(f"P{processo.pid} STARTED")
        #for i in range(1, processo.tempo_executado + 1):
        #    print(f"P{processo.pid} instruction {i}")
        
        #if processo.concluido():
        #    print(f"P{processo.pid} return SIGINT")
        #
        if processo.tempo_executado == 0:
            print(f"P{processo.pid} STARTED")

        # Instrução nova (1‑based)
        instr = processo.tempo_executado + 1
        print(f"P{processo.pid} instruction {instr}")

        # Avança o tempo de CPU já dentro da função
        processo.incrementar_tempo_executado()

        # Se concluiu, avisa e sinaliza retorno
        if processo.concluido():
            print(f"P{processo.pid} return SIGINT")
        

    def executar_operacoes_arquivo(self):
        print("\nSistema de arquivos =>")
        for pid, codigo, nome, num_blocos in self.operacoes_arquivo:
            # Verificar se o processo existe
            if pid >= len(self.processos):
                print(f"Operação {self.operacao_counter} => Falha: O processo {pid} não existe")
                self.operacao_counter += 1
                continue
            
            processo = self.processos[pid]
            
            if codigo == 0:  # Operação de criar arquivo
                if not self.gerenciador_arquivos.criar_arquivo(nome, num_blocos, pid):
                    print(f"Operação {self.operacao_counter} => Falha: O processo {pid} não pode criar o arquivo {nome} (falta de espaço)")
                else:
                    processo.arquivos_criados.append(nome)
                    bloco_inicial = self.gerenciador_arquivos.arquivos[nome][0]
                    num_blocos = self.gerenciador_arquivos.arquivos[nome][1]
                    print(f"Operação {self.operacao_counter} => Sucesso: O processo {pid} criou o arquivo {nome} (blocos {bloco_inicial}-{bloco_inicial+num_blocos-1})")
            
            elif codigo == 1:  # Operação de deletar arquivo
                if not self.gerenciador_arquivos.deletar_arquivo(nome, processo):
                    print(f"Operação {self.operacao_counter} => Falha: O processo {pid} não pode deletar o arquivo {nome} (permissão negada ou arquivo não existe)")
                else:
                    if nome in processo.arquivos_criados:
                        processo.arquivos_criados.remove(nome)
                    print(f"Operação {self.operacao_counter} => Sucesso: O processo {pid} deletou o arquivo {nome}")
            
            self.operacao_counter += 1
        # print("\nMapa de ocupação do disco:")
        self.gerenciador_arquivos.imprimir_mapa_disco()

    def executar(self):
        self.carregar_processos()
        self.carregar_arquivos_e_operacoes()
        
        print("=== Iniciando Simulação do Pseudo-SO ===")
        
        while self.processos_ativos or any(p.tempo_inicializacao >= self.tempo_atual for p in self.processos):
            print(f"\nTempo {self.tempo_atual}:")
            executou_algo = False
            
            # Admitir novos processos que iniciam neste tempo
            self.admitir_novos_processos()
            
            # Obter próximo processo para executar
            processo = self.gerenciador_filas.obter_proximo_processo()
            
            if processo:
                self.executar_processo(processo)
                #processo.incrementar_tempo_executado()
                executou_algo = True

                # Verificar se processo concluiu
                if processo.concluido():
                    self.gerenciador_memoria.liberar_memoria(processo)
                    self.gerenciador_recursos.liberar_recursos(processo)
                    self.processos_ativos.remove(processo)
                    self.gerenciador_filas.remover_processo(processo)
                else:
                    # Processo não concluído - rebaixar prioridade se for de usuário
                    if processo.prioridade > 0:
                        self.gerenciador_filas.rebaixar_prioridade(processo)
            # Aplicar aging para prevenir starvation
            self.gerenciador_filas.aplicar_aging()
            
            self.tempo_atual += 1
        
        # Executar operações de arquivo após todos os processos
        self.executar_operacoes_arquivo()
        
        print("\n=== Simulação Concluída ===")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python dispatcher.py processes.txt files.txt")
        sys.exit(1)
    
    dispatcher = Dispatcher(sys.argv[1], sys.argv[2])
    dispatcher.executar()