import requests
import time
import yaml
import urllib3
import pandas as pd
import getpass
from bs4 import BeautifulSoup
from functions import *
import yfinance as yf

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

senha, cpf = get_login()

print_message('Buscando Carteiras')

login_url = "https://cei.b3.com.br/cei_responsivo/login.aspx"
home_url = "https://cei.b3.com.br/CEI_Responsivo/home.aspx"
negociacao_url = "https://cei.b3.com.br/CEI_Responsivo/negociacao-de-ativos.aspx"

session_requests = requests.session()

# Pega o código HTML e captura tokens
result = session_requests.get(login_url,verify=False)

soup = BeautifulSoup(result.text, "html.parser")

view_state = soup.find(id='__VIEWSTATE')['value']
viewstate_generator = soup.find(id='__VIEWSTATEGENERATOR')['value']
event_validation = soup.find(id='__EVENTVALIDATION')['value']

payload = {
	"__EVENTTARGET": "",
	"__EVENTARGUMENT": "",
	"ctl00$ContentPlaceHolder1$txtLogin": cpf, 
	"ctl00$ContentPlaceHolder1$txtSenha": senha, 
	"__VIEWSTATEGENERATOR": viewstate_generator,
	"__EVENTVALIDATION": event_validation,
	"__VIEWSTATE": view_state,
	"ctl00$ContentPlaceHolder1$btnLogar": "Entrar"
}

# Efetua o login
result = session_requests.post(
	login_url, 
	data = payload,
	headers = dict(referer=login_url)
)

# Abre a aba negociação de ativos
result = session_requests.get(
	negociacao_url,
	headers = dict(referer=home_url)
)

soup = BeautifulSoup(result.text, "html.parser")


data_inicio = soup.find(id='ctl00_ContentPlaceHolder1_txtDataDeBolsa')['value']
data_fim = soup.find(id='ctl00_ContentPlaceHolder1_txtDataAteBolsa')['value']
conta = "0"

# Itera sobre as corretoras disponíveis
agentes = soup.find(id='ctl00_ContentPlaceHolder1_ddlAgentes').find_all('option')

agentes_uteis = []

for agente_aux in agentes:
    view_state = soup.find(id='__VIEWSTATE')['value']
    viewstate_generator = soup.find(id='__VIEWSTATEGENERATOR')['value']
    event_validation = soup.find(id='__EVENTVALIDATION')['value']

    agente = agente_aux['value']

    print("Mudando Corretora => " + agente)

    payload = {
		"ctl00$ContentPlaceHolder1$ToolkitScriptManager1": "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1$ddlAgentes",
		"ctl00_ContentPlaceHolder1_ToolkitScriptManager1_HiddenField": "",
		"__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlAgentes",
		"__EVENTARGUMENT": "",
		"__LASTFOCUS": "",
		"ctl00$ContentPlaceHolder1$hdnPDF_EXCEL": "",
		"__VIEWSTATEGENERATOR": viewstate_generator,
		"__EVENTVALIDATION": event_validation,
		"__VIEWSTATE": view_state,
		"ctl00$ContentPlaceHolder1$txtDataDeBolsa": data_inicio,
		"ctl00$ContentPlaceHolder1$txtDataAteBolsa": data_fim,
		"ctl00$ContentPlaceHolder1$ddlContas": conta,
		"ctl00$ContentPlaceHolder1$ddlAgentes": agente
	}

    result = session_requests.post(
		negociacao_url,
		data = payload,
		headers = dict(referer=negociacao_url)
	)

    soup = BeautifulSoup(result.text, "html.parser")
    contas = soup.find(id='ctl00_ContentPlaceHolder1_ddlContas').find_all('option')

    for conta_aux in contas:

        view_state = soup.find(id='__VIEWSTATE')['value']
        viewstate_generator = soup.find(id='__VIEWSTATEGENERATOR')['value']
        event_validation = soup.find(id='__EVENTVALIDATION')['value']

        conta = conta_aux['value']

        payload = {
			"ctl00$ContentPlaceHolder1$ToolkitScriptManager1": "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1$ddlAgentes",
			"ctl00_ContentPlaceHolder1_ToolkitScriptManager1_HiddenField": "",
			"__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlAgentes",
			"__EVENTARGUMENT": "",
			"__LASTFOCUS": "",
			"ctl00$ContentPlaceHolder1$hdnPDF_EXCEL": "",
			"__VIEWSTATEGENERATOR": viewstate_generator,
			"__EVENTVALIDATION": event_validation,
			"__VIEWSTATE": view_state,
			"ctl00$ContentPlaceHolder1$txtDataDeBolsa": data_inicio,
			"ctl00$ContentPlaceHolder1$txtDataAteBolsa": data_fim,
			"ctl00$ContentPlaceHolder1$ddlContas": conta,
			"ctl00$ContentPlaceHolder1$ddlAgentes": agente,
			"ctl00$ContentPlaceHolder1$btnConsultar": "Consultar"
		}

        result = session_requests.post(
			negociacao_url,
			data = payload,
			headers = dict(referer=negociacao_url)
		)

        soup = BeautifulSoup(result.text, "html.parser")

        table = soup.find(id="ctl00_ContentPlaceHolder1_rptAgenteBolsa_ctl00_rptContaBolsa_ctl00_pnAtivosNegociados")

        if table != None:

            lista = []
            datas = []
            operacao = []
            mercado = []
            sticks = []
            esp_ativo = []
            quantidade = []
            preco_compra = []
            valor_total = []
            fator_cotacao = []

            table_body = table.find('tbody')

            rows = table_body.find_all('tr')

            for row in rows:
                cols = row.find_all('td')
                colsd = [ele.text.replace('.','').replace(',','.').strip() for ele in cols]
                colsd.append(agente)
                colsd.append(conta)
                lista.append(colsd)
            
            for i in lista:
                datas.append(i[0])
                operacao.append(i[1])
                mercado.append(i[2])
                sticks.append(i[4])
                esp_ativo.append(i[5])
                quantidade.append(i[6])
                preco_compra.append(i[7])
                valor_total.append(i[8])
                fator_cotacao.append(i[9])
            

            colunas = {'Data' : datas, 'Operação' : operacao, 'Mercado' : mercado, 'Código' : sticks, 'Ativo' : esp_ativo, 'Quantidade' : quantidade, 'Preço de Compra' : preco_compra, 'Valor Total' : valor_total, 'Fator de Cotação' : fator_cotacao}
            dataframe = pd.DataFrame(colunas)
            dataframe.to_excel('Histórico-Corretora={}.xlsx'.format(agente))
            agentes_uteis.append(agente)

        view_state = soup.find(id='__VIEWSTATE')['value']
        viewstate_generator = soup.find(id='__VIEWSTATEGENERATOR')['value']
        event_validation = soup.find(id='__EVENTVALIDATION')['value']

        payload = {
			"ctl00$ContentPlaceHolder1$ToolkitScriptManager1": "ctl00$ContentPlaceHolder1$updFiltro|ctl00$ContentPlaceHolder1$btnConsultar",
			"ctl00$ContentPlaceHolder1$btnConsultar": "Nova Consulta",
			"ctl00_ContentPlaceHolder1_ToolkitScriptManager1_HiddenField": "",
			"__EVENTTARGET": "",
			"__EVENTARGUMENT": "",
			"__LASTFOCUS": "",
			"ctl00$ContentPlaceHolder1$hdnPDF_EXCEL": "",
			"__VIEWSTATEGENERATOR": viewstate_generator,
			"__EVENTVALIDATION": event_validation,
			"__VIEWSTATE": view_state,
			"ctl00$ContentPlaceHolder1$txtDataDeBolsa": data_inicio,
			"ctl00$ContentPlaceHolder1$txtDataAteBolsa": data_fim,
			"ctl00$ContentPlaceHolder1$ddlContas": conta,
			"ctl00$ContentPlaceHolder1$ddlAgentes": agente,
			"ctl00$ContentPlaceHolder1$btnConsultar": "Nova Consulta"
		}

        result = session_requests.post(
			negociacao_url,
			data = payload,
			headers = dict(referer=negociacao_url)
		)

        soup = BeautifulSoup(result.text, "html.parser")

print_message('Finalizando')

print_message('Calculando Carteira Atual')
s = 0
for agente in agentes_uteis:

    s += 1
    print('\n---------- CARTEIRA {} ----------\n'.format(s))
    df = pd.read_excel('Histórico-Corretora={}.xlsx'.format(agente))

    lista_p = df['Código']
    operacao = df['Operação']
    quantidade = df['Quantidade']
    valor_total = df['Valor Total']

    preco_compra = []
    preco_venda = []
    quantidadecompra = []
    quantidadevenda = []
    quantidadefinal = []
    ativo = []
    saldo = []
    passados = []

    for i in lista_p:

        precofvenda, precofcompra, quantidadefcompra, quantidadefvenda, lista_p, quantidade, operacao, valor_total = get_info_stocks(i, lista_p, operacao, quantidade, valor_total)

        if i in passados:
            pass
        else:
            preco_compra.append(precofcompra)
            preco_venda.append(precofvenda)
            quantidadevenda.append(quantidadefvenda)
            quantidadecompra.append(quantidadefcompra)
            quantidadefinal.append(quantidadefcompra - quantidadefvenda)
            ativo.append(i)
            saldo.append(precofvenda - precofcompra)
        
        passados.append(i)
        lista_p = lista_p.reset_index(drop=True)
        quantidade = quantidade.reset_index(drop=True)
        operacao = operacao.reset_index(drop=True)
        valor_total = valor_total.reset_index(drop=True)

    
    dic = {'Ativo': ativo, 'Q.C': quantidadecompra, 'Q.V': quantidadevenda, 'Q.T': quantidadefinal, 'P.C (R$)': preco_compra, 'P.V (R$)': preco_venda, 'Saldo(R$)': saldo}
    data = pd.DataFrame(dic)
    data.to_excel('Resumo Transações={}.xlsx'.format(agente))

    filtro = data['Q.T'] != 0
    data = data[filtro]

    data['P.M (R$)'] = abs(data['Saldo(R$)'] / data['Q.T'])

    if len(data['Ativo']) > 0: 
      atual_price = get_stocks_price(data)
      data['P.A (R$)'] = atual_price

      data['Retorno(%)'] = round((data['P.A (R$)']-data['P.M (R$)'])/data['P.M (R$)'] * 100, 2)

      data.to_excel('Carteira Atual={}.xlsx'.format(agente))
    else:
      print('Carteira Nula')

print_message('Finalizando')