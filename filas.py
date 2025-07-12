from collections import deque

class GerenciadorFilas:
    def __init__(self):
        self.fila_tempo_real = deque()  # Prioridade 0 (FIFO)
        self.filas_usuario = [          # Prioridades 1, 2, 3
            deque(),  # Prioridade 1 (mais alta)
            deque(),  # Prioridade 2
            deque()   # Prioridade 3 (mais baixa)
        ]
        self.contador_aging = {}  # PID: contador para aging 
    
    def adicionar_processo(self, processo):
        # Processos de tempo real vão direto pra fila_tempo_real
        if processo.prioridade == 0:
            self.fila_tempo_real.append(processo)
        else:
            # Processos novos começam na fila de prioridade 0
            fila_prioridade = processo.prioridade - 1 # 1 → 0, 2 → 1, 3 → 2
            self.filas_usuario[fila_prioridade].append(processo)
            self.contador_aging[processo.pid] = 0
    
    def obter_proximo_processo(self):
        # Verifica fila de tempo real primeiro
        if self.fila_tempo_real:
            return self.fila_tempo_real[0]  # FIFO, não remove ainda
        
        # Verifica filas de usuário da maior para menor prioridade
        for i in range(3):
            if self.filas_usuario[i]:
                processo = self.filas_usuario[i].popleft()
                self.contador_aging[processo.pid] = 0  # Resetar contador de aging
                return processo
        
        return None
    
    def rebaixar_prioridade(self, processo):
        if processo.prioridade > 0:  # Só para processos de usuário
            nova_prioridade = min(processo.prioridade + 1, 3)
            processo.prioridade = nova_prioridade
            self.filas_usuario[nova_prioridade - 1].append(processo)
    
    def aplicar_aging(self):
        # Incrementa contadores e promove processos se necessário
        for fila_idx in [2, 1]:  # Começa pelas filas de menor prioridade
            for processo in list(self.filas_usuario[fila_idx]):
                self.contador_aging[processo.pid] += 1
                
                # Se o processo esperou muito, promove para fila de prioridade maior
                if self.contador_aging[processo.pid] >= 5:  # Threshold de aging
                    self.filas_usuario[fila_idx].remove(processo)
                    nova_fila = max(fila_idx - 1, 0)
                    self.filas_usuario[nova_fila].append(processo)
                    self.contador_aging[processo.pid] = 0
    
    def remover_processo(self, processo):
        if processo.prioridade == 0:
            if processo in self.fila_tempo_real:
                self.fila_tempo_real.remove(processo)
        else:
            fila_idx = processo.prioridade - 1
            if processo in self.filas_usuario[fila_idx]:
                self.filas_usuario[fila_idx].remove(processo)
            if processo.pid in self.contador_aging:
                del self.contador_aging[processo.pid]