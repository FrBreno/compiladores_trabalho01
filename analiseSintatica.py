gramatica = {"S'":["S $"], "S":["( L )", "x"], "L":["S", "L , S"]}

class No:
    id = 0

    def __init__(self, id, gerador=None, prods=None):
        self.id = id
        self.producoes = []
        self.marcador = []
        self.simbsSaindo = {}
        self.reducao = False
        self.acc = False
        
        if gerador is not None and prods is not None:
            self.adicionarProducoes(gerador, prods)

    def __eq__(self, other):
        return self.producoes == other.producoes and self.marcador == other.marcador
    
    def __str__(self):
        return f'Estado {self.id}:\nProduções: {self.producoes}\nMarcadores: {self.marcador}\nSímbolos de saída: {self.simbsSaindo}\nRedução: {self.reducao}\nAceitação: {self.acc}\n'
    
    # Getters:
    def getId(self):
        return self.id

    def getProducoes(self):
        return self.producoes
    
    def getMarcador(self):
        return self.marcador

    def getSimbsSaindo(self):
        return self.simbsSaindo

    def isReducao(self):
        return self.reducao
    
    def isAcc(self):
        return self.acc
    
    # Setters:
    def setProducoes(self, prods):
        self.producoes.append(prods)

    def setMarcador(self, marc):
        self.marcador.append(marc)
    
    def setSimbSaindo(self, key, value):
        self.simbsSaindo[key] = value

    def setReducao(self, value):
        self.reducao = value

    def setAcc(self, value):
        self.acc = value


    def construirProducoes(self, geradores, gramatica):
        inter = 0
        # Análise de cada produção no nó (inclusive aquelas que são inseridas nesse processo):
        while inter < len(self.getProducoes()):
            producoes = self.getProducoes()
            marcador = self.getMarcador()

            if marcador[inter] < len(producoes[inter]):
                simb = producoes[inter][marcador[inter]]
                # Adiciona as produções para símbolos não terminais marcados no nó:
                if simb in geradores:
                    self.adicionarProducoes(simb, gramatica[simb])
            else:
                # Caso o marcador esteja no final da produção analisada:
                self.setReducao(True)
                # Se o nó é for um estado de aceitação:
                if (producoes[inter][marcador[inter] - 1] == '$'):
                    self.setAcc(True)
            inter += 1

    def construirEstados(self, nos, geradores, gramatica):
        saidas = {}     # Guarda os símbolos que 'saem' do estado para um novo estado.
        marcadorSaidas = {}
        producoes = self.getProducoes()
        marcador = self.getMarcador()
        inter = 0

        # Para cada produção no estado:
        while inter < len(producoes):
            # Se não for uma produção que está reduzindo:
            if marcador[inter] < len(producoes[inter]):
                simb = producoes[inter][marcador[inter]]
                # Adiciona o símbolo em 'saidas' e avança o marcador:
                if simb in saidas:
                    saidas[simb].append(producoes[inter])
                    marcadorSaidas[simb].append(marcador[inter] + 1)
                else:
                    saidas[simb] = [producoes[inter]]
                    marcadorSaidas[simb] = [marcador[inter] + 1]
            inter += 1

        # Para cada símbolo que saí do estado:
        for simb in saidas:
            naoExiste = True                                    # Flag para verificar se o novo estado já existe no autômato.
            novoNo = No(len(nos))                               # Cria um novo estado.
            
            # Adiciona as produções e os marcadores em um novo estado:
            for prod in saidas[simb]:
                novoNo.setProducoes(prod)
            for marcador in marcadorSaidas[simb]:
                novoNo.setMarcador(marcador)

            novoNo.construirProducoes(geradores, gramatica)     # Para construir as demais produções

            for no in nos:
                if novoNo == no:
                    self.setSimbSaindo(simb, no.getId())
                    naoExiste = False
            
            if naoExiste:
                self.setSimbSaindo(simb, novoNo.getId())
                nos.append(novoNo) 

        if len(self.getSimbsSaindo()) > 0 and self.isReducao():
            raise ValueError("A gramática não é LR(0)")

    def adicionarProducoes(self, gerador, prods):
        for prod in prods:
            prodModificada = prod.split(' ')
            prodModificada.insert(0, gerador)
            
            adicionar = True                                                                            # Pressupõe que a produção já não está adicionada no nó com o marcador no começo
            if prodModificada in self.getProducoes():                                                   # Se a produção já estiver no nó
               for indice in [i for i, x in enumerate(self.getProducoes()) if x == prodModificada]:     # Pega o indice dessa produção
                   if self.getMarcador()[indice] == 1:                                                  # Verifica se o marcador correspondente está no começo
                       adicionar = False                                                                # Se estiver, a produção não deve ser adicionada novamente
                       break
            if adicionar:
                self.setProducoes(prodModificada)
                self.setMarcador(1)

# Algoritmo que gera o autômato LR(0):
def automato(geradorInicial, geradores, gramatica):
    nos = []
    
    # Criando o nó raíz:
    nos.append(No(0, geradorInicial, gramatica[geradorInicial]))
    nos[0].construirProducoes(geradores, gramatica)
    nos[0].construirEstados(nos, geradores, gramatica)

    # Criando os demais nós:
    try:
        inter = 1
        while inter < len(nos):
            nos[inter].construirEstados(nos, geradores, gramatica) 
            inter += 1
    
    except ValueError as erro:
        print("[ERROR!]:",erro)
        exit(1)

    return nos

# Algoritmo que reconhece ou não a palavra na gramática que gerou o autômato:
def pilhaDeExecucao(automato, entrada):
    marcador = 0
    try:
        # Força a palavra a terminar com o marcador '$':
        if entrada[-1] != '$':
            entrada += '$'
        
        pilha = ['$', 0, entrada[marcador]]
        
        while True:
            # Busca o estado de destino:
            estado = automato[pilha[len(pilha) - 2]].simbsSaindo[pilha[len(pilha) - 1]]
            pilha.append(estado)

            # Verifica se o estado de destino é de redução:
            if automato[estado].isReducao():
                # Verifica se o estado de destino é de aceitação:
                if automato[estado].isAcc():
                    print('Sucesso')
                    break
                # Faz a redução e atualiza a pilha:
                simbReducao = automato[estado].producoes[0][0]
                n = (len(automato[estado].producoes[0]) - 1) * 2
                
                del pilha[-n:]
                pilha.append(simbReducao)
            else:
                marcador += 1
                pilha.append(entrada[marcador])
    except:
        print('Erro sintático')

    return 0

palavra = ''.join(input().split(' '))
geradores = gramatica.keys()

automatoSintatico = automato(str(list(geradores)[0]), geradores, gramatica)     # Gerando o autômato
pilhaDeExecucao(automatoSintatico, palavra)                                     # Reconhecimento sintático
# Printar autômato:
# for no in automatoSintatico:
#     print(no)