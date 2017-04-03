import os
import smtplib
from email.mime.text import MIMEText

from modelo import *
from controlador import *
from interpretador import Interpretador
from config import *

sobre()

#selecionando pedidos
parte = 'CABECALHO'
nomes_campos=[]
numeros_pedido = []
pedidos_abertos = []
pedidos_entrega = []
proxima_entrega = None

for linha in open(pasta_pedidos + 'lista_pedidos.csv','r', encoding='utf8'):
	campos = linha.rstrip().split(';')
	linha_pedido = dict()
	if parte == 'CABECALHO':
		for campo in campos:
			nomes_campos.append(campo)
		qtde_campos = len(nomes_campos)
		parte = 'CORPO'
	else:
		for i in range(qtde_campos):
			linha_pedido[nomes_campos[i]] = campos[i]
		if linha_pedido['proxima entrega'] != '-':
			entrega_pedido = datetime.strptime(linha_pedido['proxima entrega'], '%d/%m/%Y')
			pedidos_abertos.append(linha_pedido)
			if not proxima_entrega or proxima_entrega > entrega_pedido:
				proxima_entrega = entrega_pedido
		numeros_pedido.append(linha_pedido['numero'])

for pedido in pedidos_abertos:
	if proxima_entrega == datetime.strptime(pedido['proxima entrega'], '%d/%m/%Y'):
		pedidos_entrega.append(pedido['numero'])



#montando conteudo
controlador = Controlador()
interpretador = Interpretador(controlador)
interpretador.interpretar_organicos()
interpretador.interpretar_pedidos_entrega(pedidos_entrega, proxima_entrega)

titulo = 'Entrega prevista para ' + proxima_entrega.strftime('%d/%m/%Y')
conteudo = '\n' + titulo.upper() + '\n------- -------- ---- ----------\n\n' + str(controlador.pedidos) +  '\n\n\n' + barras() + '\n\n' + str(controlador.cestas) + '\n\n' + barras() + '\n\n\n' + str(controlador.organicos_cesta)

#gravando em disco
nome_arq = pasta_pedidos + 'entregas/entrega-'+proxima_entrega.strftime('%Y-%m-%d')+'.txt'
print ('Salvando arquivo: ' + nome_arq)
arq = open(nome_arq,'w', encoding='utf8')
arq.write(conteudo)
arq.close()

#preparando mensagem
mensagem = MIMEText(conteudo)
mensagem['From'] = 'contato@portalubaia.com.br'
mensagem['To'] = 'leonardo3108@gmail.com,contato@portalubaia.com.br'
mensagem['Subject'] = titulo
mensagem.set_type('text/plain') 

#enviando mensagem
print ('Conectando ao gmail')
gmail = smtplib.SMTP('smtp.gmail.com:587')
gmail.starttls()
print ('Logando no gmail')
gmail.login(conta, senha)
print ('Enviando o e-mail')
gmail.send_message(mensagem)
gmail.quit()
			
			