class GerenciadorArquivos:
    def __init__(self, total_blocos):
        self.total_blocos = total_blocos
        self.blocos = [0] * total_blocos  # 0 = livre, nome_arquivo = ocupado
        self.arquivos = {}  # nome_arquivo: (bloco_inicial, num_blocos, pid_criador)
    
    def carregar_arquivos_iniciais(self, arquivos_iniciais):
        for nome, bloco_inicial, num_blocos in arquivos_iniciais:
            self._alocar_arquivo(nome, bloco_inicial, num_blocos, pid_criador=None)
    
    def criar_arquivo(self, nome, num_blocos, pid):
        # Encontra espaço usando first-fit
        contador = 0
        bloco_inicial = None
        
        for i in range(self.total_blocos):
            if self.blocos[i] == 0:
                contador += 1
                if contador == num_blocos:
                    bloco_inicial = i - contador + 1
                    break
            else:
                contador = 0
        
        if bloco_inicial is not None:
            self._alocar_arquivo(nome, bloco_inicial, num_blocos, pid)
            return True
        return False
    
    def _alocar_arquivo(self, nome, bloco_inicial, num_blocos, pid_criador):
        for i in range(bloco_inicial, bloco_inicial + num_blocos):
            self.blocos[i] = nome
        self.arquivos[nome] = (bloco_inicial, num_blocos, pid_criador)
    
    def deletar_arquivo(self, nome, pid):
        if nome not in self.arquivos:
            return False
        
        bloco_inicial, num_blocos, pid_criador = self.arquivos[nome]
        
        # Verificar permissões
        if pid.prioridade == 0 or pid.pid == pid_criador:
            for i in range(bloco_inicial, bloco_inicial + num_blocos):
                self.blocos[i] = 0
            del self.arquivos[nome]
            return True
        return False
    
    def imprimir_mapa_disco(self):
        print("\nMapa de ocupação do disco:")
        linha = "|"
        for i in range(self.total_blocos):
            if self.blocos[i] == 0:
                linha += " 0 |"
            else:
                linha += f" {self.blocos[i]} |"
        print(linha)