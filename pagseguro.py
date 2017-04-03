import os
import re
from datetime import datetime
from config import *

er_nome_arquivo_identificado = re.compile('(?P<data>\d\d\d\d-\d\d-\d\d)_(?P<id>.+).html')
er_nome_cliente = re.compile('.+ por (?P<nome_cliente>.+) (foi aprovado|está disponível|foi gerada|foi <strong>negado|não foi autorizado|não foi efetuado|está em análise).+')
er_valor = re.compile('.+<font face="arial" size="2">(?P<valor>.+)</font>')
er_cesta = re.compile('.*<tr align="left"><td><p><font face="arial" size="-1">(?P<nome>.+)</font></p></td><td align="center"><p><font face="arial" size="-1">(?P<qtde>.+)</font></p></td><td align="right"><p><font face="arial" size="-1">(?P<valor>.+)</font></p></td><td align="right"><p><font face="arial" size="-1">(?P<total>.+)</font></p></td>')
er_frete = re.compile('.+<td colspan="4">Frete: R[$]&nbsp;(?P<valor>.+)</td>')
er_total = re.compile('.+<td colspan="4"><b>Total geral: R[$]&nbsp;(?P<valor>.+)</b><hr size="1" color="#449c38"/></td>')

class InterpretadorPagSeguro:
	def interpretar_texto(self, texto):
		if self.parte == 'CABECALHO':
			m_nome_cliente = er_nome_cliente.match(texto)
			if m_nome_cliente:
				self.nome_cliente = m_nome_cliente.group('nome_cliente').strip()
				self.parte = 'DESCRICAO'
		elif self.parte == 'DESCRICAO' and '<font face="arial" size="2"><strong>Status:</strong></font>' in texto:
			self.parte = 'STATUS'
		elif self.parte == 'STATUS':
			m_valor = er_valor.match(texto)
			if m_valor:
				self.status_compra = m_valor.group('valor').strip()
				self.parte = 'ID'
		elif self.parte == 'ID':
			if '<font face="arial" size="2"><strong>E-mail do comprador:</strong></font>' in texto:
				self.parte = 'EMAIL'
			elif 'carrinho' in texto:
				self.parte = 'CARRINHO'	
		elif self.parte == 'EMAIL':
			m_valor = er_valor.match(texto)
			if m_valor:
				self.email = m_valor.group('valor').strip()
				self.parte = 'CARRINHO'
		elif self.parte == 'CARRINHO':
			for texto_cesta in texto.split('</tr>'):
				m_cesta = er_cesta.match(texto_cesta)
				if m_cesta:
					self.cestas.append((m_cesta.group('nome').strip(), m_cesta.group('qtde').strip(), m_cesta.group('valor').strip(), m_cesta.group('total').strip()))
			if '</tbody>' in texto:
				self.parte = 'FRETE'
		elif self.parte == 'FRETE' or self.parte == 'TOTAL':
			m_frete = er_frete.match(texto)
			m_total = er_total.match(texto)
			if m_frete:
				self.frete = m_frete.group('valor').strip()
				self.parte = 'TOTAL'
			elif m_total:
				self.total = m_total.group('valor').strip()
				self.parte = 'FIM'

	def interpretar_mensagem(self, pasta, arquivo, modo):
		self.parte = 'CABECALHO'
		self.cestas = []
		self.id = self.data = self.nome_cliente = self.status_compra = self.email = self.frete = self.total = ''
		m_nome_arquivo_identificado = er_nome_arquivo_identificado.match(arquivo)
		if m_nome_arquivo_identificado:
			self.data = datetime.strptime(m_nome_arquivo_identificado.group('data'), '%Y-%m-%d').strftime('%d/%m/%Y')
			self.id = m_nome_arquivo_identificado.group('id')
		for linha in open(pasta + arquivo,'r', encoding='iso-8859-1'):
			self.interpretar_texto(linha)
		if modo == 'completo':
			self.csv_pagamentos.write(self.id + ';' + self.data + ';' + self.nome_cliente + ';' + self.status_compra + ';' + self.email + ';' + self.frete + ';' + self.total + '\n')
		elif modo == 'normal':
			self.csv_pagamentos.write(self.id + ';' + self.data + ';' + self.nome_cliente + ';' + self.status_compra + ';' + self.frete + ';' + self.total + '\n')
		for cesta in self.cestas:
			self.csv_cestas.write(self.id + ';' + cesta[0] + ';' + cesta[1] + ';' + cesta[2] + ';' + cesta[3] + '\n')
	def vasculhar_pasta_pagseguro(self, pasta, modo):
		self.csv_pagamentos = open(pasta + 'pagamentos.csv','w', encoding='utf8')
		if modo == 'completo':
			self.csv_pagamentos.write('id;data;cliente;status da compra;email;frete;total\n')
		elif modo == 'normal':
			self.csv_pagamentos.write('id;data;cliente;status da compra;frete;total\n')
		self.csv_cestas = open(pasta + 'cestas.csv','w', encoding='utf8')
		self.csv_cestas.write('id;nome da cesta;quantidade;valor;total\n')
		for arquivo in os.listdir(pasta):
			if not '.csv' in arquivo:
				self.interpretar_mensagem(pasta, arquivo, modo)
		self.csv_pagamentos.close()
		self.csv_cestas.close()
	def localizar_saldo(self, pasta, arquivo):
		self.data = datetime.strptime(arquivo.rstrip('.html'), '%Y-%m-%d').strftime('%d/%m/%Y')
		for linha in open(pasta + arquivo,'r', encoding='iso-8859-1'):
			if 'Você tem R$ ' in linha:
				self.valor = linha.strip().lstrip('Você tem R$ ').rstrip(' disponíveis em sua conta.')
				self.csv_extrato.write(self.data + ';' + self.valor + '\n')
				return
	def vasculhar_pasta_saldo(self, pasta):
		self.csv_extrato = open(pasta + 'extrato.csv','w', encoding='utf8')
		self.csv_extrato.write('data;valor\n')
		for arquivo in os.listdir(pasta):
			if not '.csv' in arquivo:
				self.localizar_saldo(pasta, arquivo)
		self.csv_extrato.close()
	def interpretar_mensagem_compra(self, pasta, arquivo):
		self.parte = 'CABECALHO'
		self.data_pgto = self.valor = self.fornecedor = self.email = self.telefone = self.prazo = ''
		self.data_email = datetime.strptime(arquivo.rstrip('.html'), '%Y-%m-%d').strftime('%d/%m/%Y')
		for linha in open(pasta + arquivo,'r', encoding='iso-8859-1'):
			if self.parte == 'CABECALHO' and 'voc&ecirc; realizou um pagamento atrav&eacute;s do PagSeguro para <strong><font color="#71ba2f">' in linha:
				campos = linha.split('<strong>')
				self.data_pgto = campos[0].lstrip('				No dia ').rstrip(', voc&ecirc; realizou um pagamento atrav&eacute;s do PagSeguro para ')
				self.fornecedor = campos[1].strip().lstrip('<font color="#71ba2f">')[:-28]
				self.valor = campos[2].strip().lstrip('<font color="#71ba2f">R$ ').rstrip('</font></strong>.')
				self.parte = 'EMAIL'
			elif self.parte == 'EMAIL' and '<span><strong>' in linha:
				self.email = linha.strip().lstrip('<span><strong>').rstrip('</strong></span>')
				self.parte = 'TELEFONE'
			elif self.parte == 'TELEFONE' and '<span><strong>' in linha:
				self.telefone = linha.strip().lstrip('<span><strong>').rstrip('</strong></span>')
				self.parte = 'PRAZO'
			elif self.parte == 'PRAZO' and 'Você tem até <strong> ' in linha:
				self.prazo = linha.strip().lstrip('Você tem até <strong> >').rstrip(' </strong> para abrir uma disputa e solicitar a devolução do seu dinheiro se necessário. Após esta data, o dinheiro dessa transação será repassado ao vendedor.')
				self.parte = 'PRAZO'
		self.csv_lembrete_compra.write(self.data_email + ';' + self.data_pgto + ';' + self.valor + ';' + self.fornecedor + ';' + self.email + ';' + self.telefone + ';' + self.prazo + '\n')
	def vasculhar_pasta_compra(self, pasta):
		self.csv_lembrete_compra = open(pasta + 'lembrete_compra.csv','w', encoding='utf8')
		self.csv_lembrete_compra.write('data do email;data do pagamento;valor;fornecedor;email;telefone;prazo para disputa\n')
		for arquivo in os.listdir(pasta):
			if not '.csv' in arquivo:
				self.interpretar_mensagem_compra(pasta, arquivo)
		self.csv_lembrete_compra.close()
	def interpretar_mensagens_pagseguro(self):
		self.vasculhar_pasta_pagseguro(pasta_pedidos + 'pagseguro/pago/', 'completo')
		self.vasculhar_pasta_pagseguro(pasta_pedidos + 'pagseguro/disponivel/', 'normal')
		self.vasculhar_pasta_pagseguro(pasta_pedidos + 'pagseguro/pedido/', 'normal')
		self.vasculhar_pasta_pagseguro(pasta_pedidos + 'pagseguro/negado/', 'normal')
		self.vasculhar_pasta_pagseguro(pasta_pedidos + 'pagseguro/nao-autorizado/', 'normal')
		self.vasculhar_pasta_pagseguro(pasta_pedidos + 'pagseguro/cancelado/', 'normal')
		self.vasculhar_pasta_pagseguro(pasta_pedidos + 'pagseguro/analise/', 'normal')
		self.vasculhar_pasta_saldo(pasta_pedidos + 'pagseguro/saldo/')
		self.vasculhar_pasta_compra(pasta_pedidos + 'pagseguro/compra/')

InterpretadorPagSeguro().interpretar_mensagens_pagseguro()