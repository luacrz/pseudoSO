class Processo:
    def __init__(self, pid, tempo_inicializacao, prioridade, tempo_processador, 
                 blocos_memoria, num_impressora, req_scanner, req_modem, num_disco):
        self.pid = pid                                  # Identificador único do processo
        self.tempo_inicializacao = tempo_inicializacao  # Tempo em que o processo deve ser admitido no sistema
        self.prioridade = prioridade                    # P(0 = tempo real, 1 a 3 = usuário)
        self.tempo_processador = tempo_processador      # tempo total de CPU que o processo precisa(em quantums)
        self.blocos_memoria = blocos_memoria # quantos blocos de memória requistados
        self.num_impressora = num_impressora # Número de impressoras requisitadas (max. 2)
        self.req_scanner = req_scanner       # Indica se precisa de scanner (0 ou 1)
        self.req_modem = req_modem           # Corrigi um typo aqui (de req_modem para req_modem)
        self.num_disco = num_disco           # Número de discos SATA requisitados (0, 1 ou 2)
        self.tempo_executado = 0             # Tempo que já foi executado
        self.offset_memoria = None           # Offset de memória onde o processo foi alocado
        self.recursos_alocados = {           # Mapeia quais recursos foram alocados efetivamente
            'scanner': False,
            'impressora': [False, False],# Duas impressoras possíveis
            'modem': False,
            'disco': [False, False] # //
        }
        self.arquivos_criados = []  # Lista com nomes de arquivos criados por este processo
    
    def __str__(self): 
        # define o print()
        return (f"PID: {self.pid}, Prioridade: {self.prioridade}, "
                f"Offset Memória: {self.offset_memoria}, "
                f"Blocos Alocados: {self.blocos_memoria}, "
                f"Recursos: I{self.num_impressora}/S{self.req_scanner}/"
                f"M{self.req_modem}/D{self.num_disco}")
    
    def incrementar_tempo_executado(self):
        self.tempo_executado += 1
    
    def concluido(self): # Se True processo terminou execução
        return self.tempo_executado >= self.tempo_processador
    
    def necessita_recurso(self): 
        # Vai verificar se o processo precisa de algum recurso de E/S
        return (self.num_impressora > 0 or self.req_scanner > 0 or 
                self.req_modem > 0 or self.num_disco > 0)
    
    def alocar_recursos(self, recursos_disponiveis):
        # Aloca os recursos necessários para o processo
        recursos_alocados = True
        
        # Verificar scanner
        if self.req_scanner > 0:
            if recursos_disponiveis['scanner'] > 0:
                self.recursos_alocados['scanner'] = True
                recursos_disponiveis['scanner'] -= 1
            else:
                recursos_alocados = False
        
        # Verificar impressoras
        if self.num_impressora > 0:
            for i in range(2):
                if self.num_impressora > 0 and recursos_disponiveis['impressora'][i] > 0:
                    self.recursos_alocados['impressora'][i] = True
                    recursos_disponiveis['impressora'][i] -= 1
                    self.num_impressora -= 1
            # Se ainda faltou impressora, alocação falhou
            if self.num_impressora > 0:
                recursos_alocados = False
        
        # Verificar modem
        if self.req_modem > 0:
            if recursos_disponiveis['modem'] > 0:
                self.recursos_alocados['modem'] = True
                recursos_disponiveis['modem'] -= 1
            else:
                recursos_alocados = False
        
        # Verificar discos SATA
        if self.num_disco > 0:
            for i in range(2):
                if self.num_disco > 0 and recursos_disponiveis['disco'][i] > 0:
                    self.recursos_alocados['disco'][i] = True
                    recursos_disponiveis['disco'][i] -= 1
                    self.num_disco -= 1
            if self.num_disco > 0:
                recursos_alocados = False
        
        return recursos_alocados
    
    def liberar_recursos(self, recursos_disponiveis):
        # Libera os recursos alocados pelo processo
        if self.recursos_alocados['scanner']:
            recursos_disponiveis['scanner'] += 1
            self.recursos_alocados['scanner'] = False
        
        for i in range(2):
            if self.recursos_alocados['impressora'][i]:
                recursos_disponiveis['impressora'][i] += 1
                self.recursos_alocados['impressora'][i] = False
        
        if self.recursos_alocados['modem']:
            recursos_disponiveis['modem'] += 1
            self.recursos_alocados['modem'] = False
        
        for i in range(2):
            if self.recursos_alocados['disco'][i]:
                recursos_disponiveis['disco'][i] += 1
                self.recursos_alocados['disco'][i] = False