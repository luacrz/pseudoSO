# Gerencia os dispositivos de E/S

class GerenciadorRecursos:
    def __init__(self):
        self.recursos = {
            'scanner': 1,       # 1 scanner disponível
            'impressora': [1, 1],  # 2 impressoras disponíveis
            'modem': 1,         # 1 modem disponível
            'disco': [1, 1]     # 2 dispositivos SATA disponíveis
        }
    
    def verificar_disponibilidade(self, processo):
        # Verifica se há recursos suficientes para o processo
        recursos_suficientes = True
        
        if processo.req_scanner > 0 and self.recursos['scanner'] < processo.req_scanner:
            recursos_suficientes = False
        
        impressoras_disponiveis = sum(self.recursos['impressora'])
        if processo.num_impressora > 0 and impressoras_disponiveis < processo.num_impressora:
            recursos_suficientes = False
        
        if processo.req_modem > 0 and self.recursos['modem'] < processo.req_modem:
            recursos_suficientes = False
        
        discos_disponiveis = sum(self.recursos['disco'])
        if processo.num_disco > 0 and discos_disponiveis < processo.num_disco:
            recursos_suficientes = False
        
        return recursos_suficientes
    
    def alocar_recursos(self, processo):
        # Tenta alocar os recursos para o processo
        return processo.alocar_recursos(self.recursos)
    
    def liberar_recursos(self, processo):
        # Libera os recursos alocados pelo processo
        processo.liberar_recursos(self.recursos)