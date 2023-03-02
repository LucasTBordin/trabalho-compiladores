import xmltodict
from copy import deepcopy
from tabulate import tabulate

actions_ref = ("err", "e", "r", "t", "a")


# adiciona linha na matriz
def addLinha():
    for x in range(len(matriz)):
        matriz[x].append(0)


def removeLinha(index):
    for x in range(len(matriz)):
        del matriz[x][index]


# retorna a letra do alfabeto correspondente ao número informado (exceto o S). Depois de acabarem as letras, começa a enumerar (A1, B1, C1...).
def alfabetoGet(alfabetoIndex):
    global alfabeto
    if alfabetoIndex > 24:
        return alfabeto[alfabetoIndex % 25] + str(round(alfabetoIndex / 25))
    else:
        return alfabeto[alfabetoIndex]


entrada = open("GR.txt")

simbolos = {}

alfabetoIndex = 0
alfabeto = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]

# guarda caracteres terminais
caracteres = []

# guarda numero de gramaticas
contGrams = 0

linhas = entrada.readlines()

# primeira iteração apenas para identificar os terminais e guardar em caracteres[]
for linha in linhas:
    # se estiver em formato de regra
    if linha[0] == "<":
        # separa a definição das regras
        splitDef = linha.split(" ::= ")

        resto = splitDef[1]
        # separa as regras
        regras = resto.split(" | ")

        for x in range(0, len(regras)):
            if regras[x][0] == "ε":
                simbolos["<gram" + str(contGrams) + ">"] = splitDef[1]
                contGrams += 1

            if regras[x][0] == "\n":
                continue
            if regras[x][0] not in caracteres and regras[x][0] != "ε":
                caracteres.append(regras[x][0])

    else:
        # se for uma palavra
        simbolos[linha[: len(linha) - 1]] = 0
        letras = list(linha)
        for letra in letras:
            if letra == "\n":
                continue
            if letra not in caracteres:
                caracteres.append(letra)

# declara matriz
matriz = [[]]

# forma primeira linha da matriz
for x in range(len(caracteres)):
    matriz.append([caracteres[x]])
matriz[0].append("δ")

# inicia linha S
addLinha()
matriz[0][1] = "S"

# inicia dicionario de não terminais
naoTerminais = {"<S>": "S"}

## geração do AFND ##

# percorre linhas
for linha in linhas:
    # se estiver em formato de regra
    if linha[0] == "<":
        # separa a definição
        splitDef = linha.split(" ::= ")
        define = splitDef[0]

        resto = splitDef[1]
        # separa cada regra
        regras = resto.replace("\n", "").split(" | ")

        # percorre regras
        for regra in regras:
            terminal = regra[0]

            # trata epsilon ou terminal sozinho
            if len(regra) < 2:
                if define not in naoTerminais:
                    naoTerminais[define] = alfabetoGet(alfabetoIndex)
                    addLinha()

                    # nomeia linha
                    matriz[0][len(matriz[0]) - 1] = alfabetoGet(alfabetoIndex)

                if terminal != "ε":
                    for x in range(1, len(matriz)):
                        if terminal == matriz[x][0]:
                            posColuna = x

                    alfabetoIndex += 1
                    addLinha()

                    matriz[0][len(matriz[0]) - 1] = "*" + alfabetoGet(alfabetoIndex)

                    aux = ["0"]
                    for y in range(1, len(matriz[0])):
                        aux.append(matriz[0][y].replace("*", ""))

                    matriz[posColuna][aux.index(naoTerminais[define])] = alfabetoGet(
                        alfabetoIndex
                    )

                matriz[0][matriz[0].index(naoTerminais[define])] = (
                    "*" + matriz[0][matriz[0].index(naoTerminais[define])]
                )

                alfabetoIndex += 1

                continue

            # guarda nao terminal
            # seleciona o que está entre <> na regra
            naoTerminal = regra[regra.index("<") : regra.index(">") + 1]

            # sinaliza se é recursivo
            if naoTerminal == define:
                flagRecursivo = 1
            else:
                flagRecursivo = 0

            # se o nao terminal ainda nao estiver no dicionario
            if naoTerminal not in naoTerminais:
                # adiciona no dicionario e atribui a uma letra de linha
                naoTerminais[naoTerminal] = alfabetoGet(alfabetoIndex)

                addLinha()
                # nomeia linha nova
                matriz[0][len(matriz[0]) - 1] = alfabetoGet(alfabetoIndex)

                # define a letra a ser impressa como a letra da nova linha
                letraImpressa = alfabetoGet(alfabetoIndex)
                alfabetoIndex += 1
            else:
                # se ja estiver na lista, a letra a ser impressa é a que já esta atribuida a ele
                letraImpressa = naoTerminais[naoTerminal]

            # passa pela linha dos terminais (S)
            for x in range(1, len(matriz)):
                if terminal == matriz[x][0]:
                    posColuna = x

            if define.startswith("<S"):
                # trata o S

                if flagRecursivo == 1:
                    # recursivo

                    # se a letra na tabela for 0
                    if matriz[posColuna][1] == 0:
                        # substitui por S
                        matriz[posColuna][1] = "S"
                    else:
                        # senão, concatena com S
                        matriz[posColuna][1] = matriz[posColuna][1] + ",S"

                else:
                    # nao recursivo

                    # se a letra na tabela for 0
                    if matriz[posColuna][1] == 0:
                        # substitui pela letra impressa
                        matriz[posColuna][1] = letraImpressa
                    else:
                        # senão, concatena com a letra impressa
                        matriz[posColuna][1] += "," + letraImpressa

            else:
                # trata as que nao sao o S
                if define not in naoTerminais:
                    naoTerminais[define] = alfabetoGet(alfabetoIndex)
                    addLinha()

                    matriz[0][len(matriz[0]) - 1] = alfabetoGet(alfabetoIndex)
                    alfabetoIndex += 1

                matriz[posColuna][matriz[0].index(naoTerminais[define])] = letraImpressa

    else:
        # se for uma palavra

        flagFirst = 0
        # passa por cada letra da linha
        for l in range(len(linha)):
            # trata a primeira letra
            if flagFirst == 0:
                # passa pela linha dos terminais (S)
                for x in range(1, len(matriz)):
                    # se a letra for igual a uma na tabela
                    if linha[l] == matriz[x][0]:
                        # se a letra na tabela for 0
                        if matriz[x][1] == 0:
                            # substitui pela próxima letra do alfabeto
                            matriz[x][1] = alfabetoGet(alfabetoIndex)
                        else:
                            # senão, concatena com a próxima letra do alfabeto
                            matriz[x][1] = (
                                matriz[x][1] + "," + alfabetoGet(alfabetoIndex)
                            )
                flagFirst = 1

            # trata as outras letras
            else:
                addLinha()
                matriz[0][len(matriz[0]) - 1] = alfabetoGet(alfabetoIndex)
                alfabetoIndex += 1

                for x in range(1, len(matriz)):
                    if linha[l] == matriz[x][0]:
                        matriz[x][len(matriz[0]) - 1] = alfabetoGet(alfabetoIndex)
                    if linha[l] == "\n":
                        if (
                            matriz[0][len(matriz[0]) - 1] == 0
                            or matriz[0][len(matriz[0]) - 1][0] == "*"
                        ):
                            continue
                        else:
                            matriz[0][len(matriz[0]) - 1] = (
                                "*" + matriz[0][len(matriz[0]) - 1]
                            )


# transpõe matriz antes de imprimir (troca linhas e colunas)
matrizPrint = list(zip(*matriz))

# imprime AFND
print("gerando AFND")
print(tabulate.tabulate(matrizPrint, headers="firstrow", tablefmt="fancy_grid"))

# guarda matriz para utilização na determinização
afnd = deepcopy(matriz)

## geração do AFD ##

# var de controle de necessidade de repetição
flagMudou = 0


# determinização
def determiniza():
    global flagMudou
    global afnd
    for i in range(1, len(matriz[0])):
        for j in range(1, len(matriz)):
            if matriz[j][i] != 0:
                # se houver virgula em qualquer lugar
                if "," in matriz[j][i]:
                    # trata indeterminismo

                    flagMudou = 1

                    regrasInd = matriz[j][i].split(",")
                    print("determinizando", regrasInd)

                    nomeNovo = "".join(regrasInd)
                    matriz[j][i] = nomeNovo

                    # checa se o mesmo indeterminismo ja foi tratado
                    check = ["0"]
                    for y in range(1, len(matriz[0])):
                        check.append(matriz[0][y].replace("*", ""))

                    if nomeNovo in check:
                        continue

                    # se não foi, trata

                    addLinha()
                    # atribui o nome à nova linha
                    matriz[0][len(matriz[0]) - 1] = nomeNovo

                    # para cada regra do indeterminismo
                    for regra in regrasInd:
                        # percorre a linha
                        for x in range(1, len(matriz)):
                            naoTermAtuais = ["0"]
                            for y in range(1, len(matriz[0])):
                                naoTermAtuais.append(matriz[0][y].replace("*", ""))

                            # altera o nome da linha pra adicionar * se qualquer uma das regras for estado final
                            if (
                                matriz[0][naoTermAtuais.index(regra)][0] == "*"
                                and matriz[0][len(matriz[0]) - 1][0] != "*"
                            ):
                                matriz[0][len(matriz[0]) - 1] = (
                                    "*" + matriz[0][len(matriz[0]) - 1]
                                )

                            # se x na linha nova for 0
                            if matriz[x][len(matriz[0]) - 1] == 0:
                                # se x na linha da regra não for 0
                                if afnd[x][naoTermAtuais.index(regra)] != 0:
                                    # substitui 0 pelo que estiver na linha da regra
                                    matriz[x][len(matriz[0]) - 1] = afnd[x][
                                        naoTermAtuais.index(regra)
                                    ]

                            # se x na linha nova não for 0
                            else:
                                # se x na linha da regra não for 0
                                if afnd[x][naoTermAtuais.index(regra)] != 0:
                                    # se o que queremos colocar ainda não estiver na string
                                    if (
                                        afnd[x][naoTermAtuais.index(regra)]
                                        not in matriz[x][len(matriz[0]) - 1]
                                    ):
                                        # concatenamos com o que está na string
                                        matriz[x][len(matriz[0]) - 1] += (
                                            "," + afnd[x][naoTermAtuais.index(regra)]
                                        )

    # transpõe matriz
    mPrint = list(zip(*matriz))

    # atualiza afnd auxiliar
    afnd = deepcopy(matriz)

    # recursão e impressão de estado
    if flagMudou == 1:
        print(tabulate.tabulate(mPrint, headers="firstrow", tablefmt="fancy_grid"))
        flagMudou = 0
        determiniza()


determiniza()

# reutiliza a flag de cima para a minimização
flagMudou = 0


## minimização ##
def minimiza():
    global flagMudou
    naoTermAtuais = ["0"]
    for y in range(1, len(matriz[0])):
        naoTermAtuais.append(matriz[0][y].replace("*", ""))

    for naoTerm in naoTermAtuais:
        if naoTerm == "0" or naoTerm == "S":
            continue
        encontrou = 0
        for i in range(1, len(matriz[0])):
            for j in range(1, len(matriz)):
                if naoTerm == matriz[j][i]:
                    encontrou = 1

        if encontrou == 0:
            flagMudou = 1
            coluna0 = []
            for y in range(0, len(matriz[0])):
                coluna0.append(matriz[0][y].replace("*", ""))
            print("removendo", naoTerm)
            removeLinha(coluna0.index(naoTerm))

    if flagMudou == 1:
        flagMudou = 0
        minimiza()


print("minimização:")
minimiza()

# add estado de erro e impressão final
print("adicionando estado de erro")
addLinha()
mPrint = list(zip(*matriz))
print(tabulate.tabulate(mPrint, headers="firstrow", tablefmt="fancy_grid"))

tabela = list(zip(*matriz))


# dicionario relacionando token ao estado final
token_estado = {}

for simbolo in simbolos:
    # se não é uma regra
    if simbolo[0] != "<":
        estado = "S"
        # pra cada letra
        for letra in simbolo:
            # procura em que coluna do afd está
            for x in range(1, len(matriz)):
                if letra == matriz[x][0]:
                    posColuna = x
            try:
                # percorre as transições na tabela e encontra o estado final de cada token
                estado = matriz[posColuna][matriz[0].index(estado)]
                token_estado[simbolo] = estado
            except:
                estado = matriz[posColuna][matriz[0].index("*" + estado)]
                token_estado[simbolo] = estado
    else:
        # separa as regras
        regras = simbolos[simbolo].split(" | ")

        for regra in regras:
            # se não tiver chave
            if regra.find("<") == -1:
                continue

            for x in range(1, len(matriz)):
                if regra[0] == matriz[x][0]:
                    posColuna = x

            try:
                # busca = o que está entre <> na regra
                busca = regra[regra.index("<") : regra.index(">") + 1]

                estado = matriz[posColuna][matriz[0].index(naoTerminais[busca])]
                token_estado[simbolo] = estado
            except:
                # busca = o que está entre <> na regra
                busca = regra[regra.index("<") : regra.index(">") + 1]
                estado = matriz[posColuna][matriz[0].index("*" + naoTerminais[busca])]
                token_estado[simbolo] = estado

# definindo características específicas da gramática adotada
token_estado["exp"] = token_estado["<gram0>"]
del token_estado["<gram0>"]

# gera dicionario inverso de token_estado
estado_token = {v: k for k, v in token_estado.items()}
estado_token["$"] = "EOF"

# carrega e lê código de entrada
codigo = open("codEntrada.txt")
linhasCod = codigo.readlines()

# inicializa estruturas
fitaSaida = ""
tabSimbolos = []

tabSimbolos.append(["Token", "Estado", "linha", "Tipo"])

contLinhas = 0


### análise léxica ###
# percorre as linhas do código de entrada
for linha in linhasCod:
    contLinhas += 1  # mantém enumeração das linhas

    tokens = linha.split()

    # percorre cada token da linha, fazendo a checagem léxica
    for token in tokens:
        # primeira letra
        letra = token[0]

        if letra not in tabela[0]:
            fitaSaida += (
                "err:L" + str(contLinhas) + ": " + token + "|"
            )  # adiciona estado de erro na fita de saída
            tabSimbolos.append(
                [token, proxEstado, contLinhas, "err"]
            )  # adiciona token do tipo err na tabela de símbolos
            continue

        coluna = tabela[0].index(letra)
        proxEstado = tabela[1][coluna]
        if proxEstado == 0:
            fitaSaida += "err:L" + str(contLinhas) + ": " + token + "|"
            tabSimbolos.append([token, proxEstado, contLinhas, "err"])
            continue

        nxt = False
        for letra in token[1 : len(token) - 1]:
            # segunda a penultima letra
            if letra not in tabela[0]:
                fitaSaida += "err:L" + str(contLinhas) + ": " + token + "|"
                tabSimbolos.append([token, proxEstado, contLinhas, "err"])
                nxt = True
                break

            # gera lista de nao terminais para indexar a linha em que está o prox estado
            naoTermAtuais = ["δ"]
            for y in range(1, len(matriz[0])):
                naoTermAtuais.append(str(matriz[0][y]).replace("*", ""))

            linha = naoTermAtuais.index(proxEstado)

            coluna = tabela[0].index(letra)
            proxEstado = tabela[linha][coluna]
            if proxEstado == 0:
                fitaSaida += "err:L" + str(contLinhas) + ": " + token + "|"
                tabSimbolos.append([token, proxEstado, contLinhas, "err"])
                nxt = True
                break

            # print(letra, proxEstado) #debug

        if nxt:
            continue

        # ultima letra

        letra = token[len(token) - 1]

        if letra not in tabela[0]:
            fitaSaida += "err:L" + str(contLinhas) + ": " + token + "|"
            tabSimbolos.append([token, proxEstado, contLinhas, "err"])
            continue

        # gera lista de nao terminais para indexar a linha em que está o prox estado
        naoTermAtuais = ["δ"]
        for y in range(1, len(matriz[0])):
            naoTermAtuais.append(str(matriz[0][y]).replace("*", ""))

        if proxEstado == 0:
            fitaSaida += "err:L" + str(contLinhas) + ": " + token + "|"
            tabSimbolos.append([token, proxEstado, contLinhas, "err"])
            continue

        linha = naoTermAtuais.index(proxEstado)

        coluna = tabela[0].index(letra)
        proxEstado = tabela[linha][coluna]
        if proxEstado == 0:
            fitaSaida += "err:L" + str(contLinhas) + ": " + token + "|"
            tabSimbolos.append([token, proxEstado, contLinhas, "err"])
            continue

        linhaFim = naoTermAtuais.index(proxEstado)

        if tabela[linhaFim][0].startswith("*"):
            fitaSaida += proxEstado + "|"  # adiciona estado na fita de saída
            tipo = ""
            if estado_token[proxEstado] == "exp":
                tipo = "exp"
            else:
                tipo = "word"

            tabSimbolos.append(
                [token, proxEstado, contLinhas, tipo]
            )  # adiciona token (tipo exp ou word) na tabela de símbolos

        else:
            # adiciona erro na fita de saída
            fitaSaida += "err:L" + str(contLinhas) + ": " + token + "|"
            tabSimbolos.append([token, proxEstado, contLinhas, "err"])


fitaSaida += "$"  # add estado final na fita de saída

print("\nTabela de Símbolos:")
print(tabulate.tabulate(tabSimbolos, tablefmt="fancy_grid", headers="firstrow"))

print("\nFita de saída:", fitaSaida)
print()


# abre xml com a tabela de parsing gerada no GoldParser
xml_data = open("lalr_table.xml").read()

# converte a tabela xml para um dicionário do python
dict1 = xmltodict.parse(xml_data)


# função para encotrar o índice na tabela xml de um dado token
def getIndexByName(name):
    for s in dict1["Tables"]["m_Symbol"]["Symbol"]:
        if s["@Name"] == name:
            return s["@Index"]


# função para encontrar a ação na tabela de parsing dados o token e o estado
def findAction(symbol, state):
    # se tiver mais de uma ação
    if int(dict1["Tables"]["LALRTable"]["LALRState"][state]["@ActionCount"]) > 1:
        # percorre as açoes até achar a certa
        for action in dict1["Tables"]["LALRTable"]["LALRState"][state]["LALRAction"]:
            if action["@SymbolIndex"] == getIndexByName(symbol):
                return actions_ref[int(action["@Action"])], action["@Value"]
        return None, None
    # se tiver uma ação
    elif int(dict1["Tables"]["LALRTable"]["LALRState"][state]["@ActionCount"]) == 1:
        action = dict1["Tables"]["LALRTable"]["LALRState"][state]["LALRAction"]
        if action["@SymbolIndex"] == getIndexByName(symbol):
            return actions_ref[int(action["@Action"])], action["@Value"]
        return None, None

    else:
        return None, None


# declara pilha
stack = []
stack.append(0)

# lê arquivo com a GLC que gerou a tabela LALR
glc = open("GLC.txt").read()
glc = glc.split("\n")

for i in range(len(glc)):
    glc[i] = glc[i].split(" ")

# transforma a fita em um vetor para melhor utilização
fitaSplit = fitaSaida.split("|")

### análise sintática ###


# função responsável pela realização de cada ação da tabela
def parse(token):
    action, value = findAction(token, stack[-1])

    # formatação e impressão da iteração atual
    padding = " " * 100
    print(
        "{} {:.8s}| {} {:.3s}| {} {:.4s}| {} {:.64}| {} {}".format(
            "token:",
            token + padding,
            "estado:",
            str(stack[-1]) + padding,
            "ação:",
            str(action) + str(value) + padding,
            "fita:",
            str(fitaSplit) + padding,
            "pilha:",
            str(stack),
        )
    )

    # se ação for um empilhamento
    if action == "e":
        stack.append(token)
        stack.append(int(value))
        fitaSplit.pop(0)

    # se ação for uma redução
    if action == "r":
        # num de elementos a reduzir: tamanho da regra, - definição, * 2
        numReducoes = (len(glc[int(value)]) - 2) * 2

        for i in range(numReducoes):
            stack.pop()

        # simbolo que da nome a regra
        ruleName = glc[int(value)][0].strip("<>")
        action, value = findAction(ruleName, stack[-1])
        stack.append(ruleName)
        stack.append(int(value))
        # parse(ruleName)

    # se ação for uma transição
    if action == "a":
        return True

    if action == None:
        return (
            "erro sintático: '"
            + str(tabSimbolos[-(len(fitaSplit) - 1)][0])
            + "' inesperado na linha "
            + str(tabSimbolos[-(len(fitaSplit) - 1)][2])
        )


# flag de parada (e retorno de texto de erro)
end = False

# percorre a fita chamando a função de parse
while not end:
    # se houver erro léxico explícito na fita
    if (fitaSplit[0]).startswith("err:"):
        print("erro léxico na linha", fitaSplit[0][5:])
        break

    token = estado_token[fitaSplit[0]]
    end = parse(token)

    # se end não for exatamente True mas tiver valor, considera ele uma mensagem de erro
    if end and end != True:
        print(end)
        break

if end == True:
    print("Aceito")
