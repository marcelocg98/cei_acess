import getpass
from time import sleep
import yfinance as yf

def get_cpf():
    cpf_l = input('\nCPF: ')

    while len(cpf_l) > 12:
        print('\nInsira um cpf válido: ')
        cpf_l = get_cpf()

    cpf = []

    for i in cpf_l:
        cpf.append(i)

    for i in cpf_l:
        if i == '-':
            cpf.remove(i)

    for i in range(len(cpf)):
        cpf[i] = int(cpf[i])

    cpf_validation(cpf)

    return cpf

def cpf_validation(cpf):
    var = 0
    for i in range(len(cpf)-2):
        var += cpf[i] * (10 - i)

    var = str((var * 10) % 11)

    if len(var) == 2 and var[0] == 1 and var[1] == 0:
        var = '1'

    if str(cpf[9]) == var[0]:
        val = True
    else:
        val = False

    if val == True:
        pass
    else:
        print('\nInsira um cpf válido: ')
        cpf = get_cpf()

def get_login():

    print('\nInsira o seu CPF: ')
    cpf = get_cpf()
    print('\nInsira sua senha: ')
    senha = getpass.getpass('\nSenha: ')

    return senha, cpf

def get_info_stocks(stock, lista, operacao, quantidade, valor_total):

    precofcompra = 0
    precofvenda = 0
    quantfcompra = 0
    quantfvenda = 0
    index = []

    for id, acao in enumerate(lista):
        if acao == stock:
            preco_tot = valor_total[id]
            op = operacao[id]
            quant = quantidade[id]
            index.append(id)

            if op=='C':
                precofcompra+=float(preco_tot)
                quantfcompra+=int(quant)
            elif op =='V':
                precofvenda+=float(preco_tot)
                quantfvenda+=int(quant)

    for i in index:
        lista = lista.drop(i)
        quantidade = quantidade.drop(i)
        operacao = operacao.drop(i)
        valor_total = valor_total.drop(i)

    return precofvenda, precofcompra, quantfcompra, quantfvenda, lista, quantidade, operacao, valor_total

def print_message(msg):
    print('\n{}.'.format(msg), end='')
    sleep(0.5)
    print('.', end='')
    sleep(0.5)
    print('.', end='')
    sleep(0.5)
    print('.', end='')
    sleep(0.5)
    print('.\n')

def get_stocks_price(data):
    
    atual_price = []

    for i in data['Ativo']:
      if i[-1] == 'F':
        i = i[:-1]
      atual_price.append(yf.download(i+'.SA', period='1y')['Adj Close'][-1])
    
    return atual_price