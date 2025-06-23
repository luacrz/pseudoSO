class GerenciadorMemoria:
    def __init__(self):
        self.tamanho_total = 1024
        self.blocos_tempo_real = 64
        self.blocos_usuario = 960
        self.memoria_tempo_real = [False] * self.blocos_tempo_real  # False = livre, True = ocupado
        self.memoria_usuario = [False] * self.blocos_usuario
        self.processo_por_bloco = {}  # Mapeia bloco para PID
    
    def alocar_memoria(self, processo):
        if processo.prioridade == 0:  # Processo de tempo real
            return self._alocar_tempo_real(processo)
        else:  # Processo de usuário
            return self._alocar_usuario(processo)
    
    def _alocar_tempo_real(self, processo):
        blocos_necessarios = processo.blocos_memoria
        offset = self._first_fit(self.memoria_tempo_real, blocos_necessarios)
        
        if offset is not None:
            for i in range(offset, offset + blocos_necessarios):
                self.memoria_tempo_real[i] = True
                self.processo_por_bloco[i] = processo.pid
            processo.offset_memoria = offset
            return True
        return False
    
    def _alocar_usuario(self, processo):
        blocos_necessarios = processo.blocos_memoria
        offset = self._first_fit(self.memoria_usuario, blocos_necessarios)
        
        if offset is not None:
            for i in range(offset, offset + blocos_necessarios):
                self.memoria_usuario[i] = True
                self.processo_por_bloco[i + self.blocos_tempo_real] = processo.pid
            processo.offset_memoria = offset + self.blocos_tempo_real
            return True
        return False
    
    def _first_fit(self, memoria, blocos_necessarios):
        contador = 0
        for i in range(len(memoria)):
            if not memoria[i]:
                contador += 1
                if contador == blocos_necessarios:
                    return i - contador + 1
            else:
                contador = 0
        return None
    
    def liberar_memoria(self, processo):
        if processo.prioridade == 0:  # Tempo real
            for i in range(processo.offset_memoria, processo.offset_memoria + processo.blocos_memoria):
                self.memoria_tempo_real[i] = False
                del self.processo_por_bloco[i]
        else:  # Usuário
            offset = processo.offset_memoria - self.blocos_tempo_real
            for i in range(offset, offset + processo.blocos_memoria):
                self.memoria_usuario[i] = False
                del self.processo_por_bloco[i + self.blocos_tempo_real]
    
    def verificar_disponibilidade(self, processo):
        if processo.prioridade == 0:
            return self._verificar_tempo_real(processo.blocos_memoria)
        else:
            return self._verificar_usuario(processo.blocos_memoria)
    
    def _verificar_tempo_real(self, blocos):
        return self._first_fit(self.memoria_tempo_real, blocos) is not None
    
    def _verificar_usuario(self, blocos):
        return self._first_fit(self.memoria_usuario, blocos) is not None