from datetime import datetime
import imaplib
import email
import os
from config import *
import locale
locale.setlocale(locale.LC_ALL, 'C')

def decodificar_gmail(texto):
	texto = texto.replace('=09', '\t').replace('=\r\n', '').replace('=20', ' ').replace('=3A', ':')
	texto = texto.replace('=A0', ' ').replace('=A1', '¡').replace('=A3', '£').replace('=A7', '§').replace('=A9', '©').replace('=AA', 'ª')
	texto = texto.replace('=B3', '³').replace('=B5', 'µ').replace('=BD', '½').replace('=BF', '¿').replace('=BA', '¿')
	texto = texto.replace('=C2', 'Â').replace('=C3', 'Ã').replace('=C7', 'Ç').replace('=CD', 'Í').replace('=D3', 'Ó').replace('=DA', 'Ú')
	texto = texto.replace('=E1', 'á').replace('=E2', 'â').replace('=E3', 'ã').replace('=E7', 'ç').replace('=E9', 'é').replace('=EA', 'ê').replace('=ED', 'í').replace('=EF', 'ï')
	texto = texto.replace('=FA', 'ú').replace('=F3', 'ó').replace('=F5', 'õ').replace('=3D', '=')#.replace('=', '!!!!!!!!!!!')
	return texto
def obter_textos_mensagem(mensagem):
	textos = []
	formato_mensagem = mensagem.get_content_maintype()
	if formato_mensagem == 'text':
		textos.append(decodificar_gmail(mensagem.get_payload()))
	elif formato_mensagem == 'multipart':
		for parte in mensagem.get_payload():
			for texto_parte in obter_textos_mensagem(parte):
				textos.append(texto_parte)
	elif formato_mensagem == 'image' or formato_mensagem == 'application':
		print('   Mensagem tipo ' + formato_mensagem)
	else:
		print('!!! Erro de leitura do e-mail: esperando mensagem tipo text, mas recebi ' + formato_mensagem + ' !!!')
	return textos
def registrar_mensagem(nome_arq, codificacao, mensagem):
	if not os.path.isfile(nome_arq):
		for texto in obter_textos_mensagem(mensagem):
			if '<html' in texto and pasta_pedidos + 'pedido-' in nome_arq:
				nome_arq = nome_arq.replace(pasta_pedidos, pasta_pedidos + 'html/')
				if os.path.isfile(nome_arq):
					return
				else:
					print ('      html: ' + nome_arq)
			arq = open(nome_arq,'w', encoding=codificacao)
			arq.write(texto.replace('\r\n', '\n'))
			arq.close()
		print ('   ...baixado')
def identificar_pedido(assunto):
	tipo = numero = ''
	if '(' in assunto:
		campos = assunto.replace('=?UTF-8?Q?','').replace('_', ' ').replace('[Ubaia] ','').split('(')
		tipo = campos[0].rstrip()
		numero = campos[1].split(')')[0]
	if 'Fwd: ' in assunto:
		tipo = tipo.lstrip('Fwd: ') + ' (encaminhado)'
	if 'Re: ' in assunto:
		tipo = tipo.lstrip('Re: ').rstrip(' (encaminhado)') + ' (encaminhado)'
	return tipo, numero
def registrar_pedido(tipo, numero, mensagem):
	if tipo == 'Novo pedido de cliente':
		nome_arq = pasta_pedidos + 'pedido-' + numero + '.txt'
	elif tipo == 'Pedido cancelado':
		nome_arq = pasta_pedidos + 'cancelados/pedido-' + numero + '.txt'
	else:
		print(tipo + ': ' + str(numero))# + '====' + mensagem[0:50])
		nome_arq = pasta_pedidos + 'encaminhados/pedido-' + numero + '.txt'
	print ('   pedido: ' + nome_arq)
	registrar_mensagem(nome_arq, 'utf8', mensagem)
def montar_nome_arquivo(assunto, data):
	if 'Fwd: ' in assunto:
		assunto = assunto.replace('?','').replace('!','').replace(':','').replace('=','').replace('Ã','').replace('§','')
		assunto = assunto.replace('\t=UTF-8Q','').replace('=ISO-8859-1Q','').replace('=UTF-8Q','').replace('\tUTF-8Q','').replace('UTF-8Q','').replace('ISO-8859-1Q','')
		return pasta_pedidos + 'pagseguro/etc/', datetime.strptime((' ' + data[5:16].strip())[-11:], '%d %b %Y').strftime('%Y-%m-%d') + '-' + assunto, '.txt', 'iso-8859-1'
	if 'Saldo_disponível_em_sua_conta' in assunto:
		return pasta_pedidos + 'pagseguro/saldo/', datetime.strptime(data[5:16], '%d %b %Y').strftime('%Y-%m-%d'), '.html', 'iso-8859-1'
	if 'Deu_tudo_certo_com_o_produto' in assunto:
		return pasta_pedidos + 'pagseguro/compra/', datetime.strptime(data[5:16], '%d %b %Y').strftime('%Y-%m-%d'), '.html', 'iso-8859-1'
	if 'Pagamento concluído | Venda aprovada' in assunto or 'Pagamento_concluído_|_Venda_aprovada' in assunto:
		return pasta_pedidos + 'pagseguro/pago/', '', '.html', 'iso-8859-1'
	if 'Pagamento concluído | Valor recebido disponível' in assunto or 'Pagamento_concluído_|_Valor_recebido_disponível' in assunto:	
		return pasta_pedidos + 'pagseguro/disponivel/', '', '.html', 'iso-8859-1'
	if 'Pagamento aprovado' in assunto:
		return pasta_pedidos + 'pagseguro/aprovado/', '', '.html', 'iso-8859-1'
	if 'Pedido_concluído' in assunto:
		return pasta_pedidos + 'pagseguro/pedido/', '', '.html', 'iso-8859-1'
	elif 'Novo_pagamento_em_análise' in assunto:
		return pasta_pedidos + 'pagseguro/analise/', '', '.html', 'iso-8859-1'
	elif 'Pagamento_não_realizado' in assunto:
		return pasta_pedidos + 'pagseguro/cancelado/', '', '.html', 'iso-8859-1'
	elif 'Recebimento_não_autorizado' in assunto:
		return pasta_pedidos + 'pagseguro/nao-autorizado/', '', '.html', 'iso-8859-1'
	elif 'Pagamento negado' in assunto:
		return pasta_pedidos + 'pagseguro/negado/', '', '.html', 'iso-8859-1'
	else:
		assunto = assunto.replace('?','').replace('!','').replace(':','').replace('=','').replace('Ã','').replace('§','')
		assunto = assunto.replace('\t=UTF-8Q','').replace('=ISO-8859-1Q','').replace('=UTF-8Q','').replace('\tUTF-8Q','').replace('UTF-8Q','').replace('ISO-8859-1Q','')
		return pasta_pedidos + 'pagseguro/etc/', datetime.strptime((' ' + data[5:16].strip())[-11:], '%d %b %Y').strftime('%Y-%m-%d') + '-' + assunto, '.html', 'iso-8859-1'
def baixar_emails(gmail, pasta, criterio, limite):
	gmail.select(pasta)
	result, lista = gmail.search(None, criterio)
	ids = lista[0].decode().split()
	mensagens = []
	qtde = 0
	for id in ids:
		if limite and qtde == limite:
			break
		qtde = qtde + 1
		result2, email_bruto = gmail.fetch(id, '(RFC822)')
		mensagem = email.message_from_string(email_bruto[0][1].decode())
		assunto = mensagem.get('Subject', failobj='')
		data = mensagem.get('Date', failobj='')
		if pasta == 'Pedidos':
			tipo, numero = identificar_pedido(assunto)
			if numero:
				registrar_pedido(tipo, numero, mensagem)
			continue
		elif pasta == 'PagSeguro':
			pasta_arq, nome_arq, formato, codificacao = montar_nome_arquivo(decodificar_gmail(assunto), data)
			if nome_arq:
				print ('   pagseguro: ' + pasta_arq + nome_arq + formato)
				registrar_mensagem(pasta_arq + nome_arq + formato, codificacao, mensagem)
				continue
		print('   baixado email ' + str(id))
		mensagens.append((mensagem, assunto, data))
	return mensagens
def encontrar_codigo(texto):
	estado = 'antes'
	for linha in texto.split('\n'):
		if estado == 'antes' and 'Código' in linha:
			estado = 'código'
		elif estado == 'antes' and 'o da compra no PagSeguro:' in linha:
			estado = 'código2'
		elif estado == 'código' and  '<font face="arial" size="2">' in linha:
			return linha.replace('<font face="arial" size="2">','').replace('</font>','').strip()
		elif estado == 'código2' and  '<strong>' in linha:
			return linha.replace('<strong>','').replace('</strong>','').strip()
def registrar_mensagem_pagseguro(nome_arq, codificacao, texto):
	print('   pagseguro: ' + nome_arq)
	if not os.path.isfile(nome_arq):
		arq = open(nome_arq,'w', encoding=codificacao)
		arq.write(texto.replace('\r\n', '\n'))
		arq.close()
		print ('   ...baixado')
def mostrar_erro_texto(texto, data, assunto):
	print('!!! Erro: texto nao reconhecido !!!')
	print(texto)
	print('!!! Erro: texto nao reconhecido !!!')
	print(data)
	print(assunto)
	print()

print ('Conectando ao gmail')
gmail = imaplib.IMAP4_SSL('imap.gmail.com')
print ('Logando no gmail')
gmail.login(conta, senha)
print ('Acessando emails com os pedidos...')
mensagensPedido = baixar_emails(gmail, "Pedidos", "ALL", 0)

print ('Acessando emails com os pagamentos...')
mensagensPagamento = baixar_emails(gmail, "PagSeguro", "ALL", 0)
print ('Lendo emails com os pagamentos...')
for mensagem, assunto, data in mensagensPagamento:	
	textos = obter_textos_mensagem(mensagem)
	pasta_arq, nome_arq, formato, codificacao = montar_nome_arquivo(decodificar_gmail(assunto), data)
	for texto in textos:
		codigo = encontrar_codigo(texto)
		if codigo:
			dataf = datetime.strptime((' ' + data[5:16].strip())[-11:], '%d %b %Y').strftime('%Y-%m-%d') + '_' 
			registrar_mensagem_pagseguro(pasta_arq + dataf + codigo + formato, codificacao, texto)
		else:
			mostrar_erro_texto(texto, data, assunto)
print ('Encerrando conexao')
gmail.close()
gmail.logout()
