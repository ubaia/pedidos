import os
import re
from modelo import *
from config import *

er_numero_pedido = re.compile('NúMERO DO PEDIDO: (?P<numero>\d+)')
er_data_pedido = re.compile('(?P<dia>\d+ .+ \d\d\d\d)')
er_organico_unidade = re.compile('(?P<organico>.+) [(](?P<unidade>.+)[)]')
er_organico = re.compile('(?P<organico>.+)')
er_subtotal_pedido = re.compile('Subtotal:\s+[$](?P<valor>.+?)\s+')
er_frete_pedido = re.compile('Frete:\s+[$](?P<valor>.+?)\s+')
er_total_pedido = re.compile('Total:\s+[$](?P<valor>.+)')
er_arquivo_pedido = re.compile('pedido-(?P<numero>\d+).txt')

class Interpretador:
	def __init__(self, controlador):
		self.controlador = controlador
		self.arquivo = ''
	def log(self, texto):
		if self.arquivo == 'pedido-2691.txt':
			print(self.parte + '/' + self.subparte + ': ' + texto.rstrip())
	def interpretar_texto(self, linha):
		self.log(linha)
		if self.parte == 'CABECALHO':
			if '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-' in linha:
				self.parte = 'PEDIDO'
				self.subparte = 'GERAL'
		elif self.parte == 'PEDIDO':
			if '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-' in linha:
				self.parte = 'CLIENTE'
				self.subparte = 'DADOS'
			elif self.subparte == 'GERAL':
				m_numero_pedido = er_numero_pedido.match(linha)
				m_data_pedido = er_data_pedido.match(linha)
				if m_numero_pedido:
					#self.log('Achei o numero do pedido: ' + m_numero_pedido.group('numero'))
					self.pedido = self.controlador.acrescentar_pedido(m_numero_pedido.group('numero'))
				elif m_data_pedido:
					#self.log('Achei o dia: ' + m_data_pedido.group('dia'))
					self.pedido.dia = datetime.strptime(m_data_pedido.group('dia'), '%d %B %Y')
					self.subparte = 'CESTA'
			elif self.subparte == 'CESTA':
				if 'Quantidade: ' in linha:
					if linha[12:-1] != '1':
						print('!!! Erro de sintaxe: quantidade de cestas diferente de 1 !!!')
				elif 'Custo: $' in linha:
					self.cesta.custo = linha[8:-1].replace('.', ',')
					self.subparte = 'ORGANICOS'
				else:
					tipo_cesta = self.controlador.tipos_cestas.encontrar_tipo(linha.rstrip())
					if tipo_cesta:
						self.cesta = self.controlador.acrescentar_cesta(self.pedido, tipo_cesta)
			elif self.subparte == 'ORGANICOS':
				m_organico_unidade = er_organico_unidade.match(linha)
				m_organico = er_organico.match(linha)
				if '=========' in linha:
					self.subparte = 'SOMA'
				elif 'Quantidade: ' in linha:
					self.organico_cesta.quantidade = int(linha[12:-1])
					self.controlador.acrescentar_organico(self.cesta, self.organico_cesta)
				elif 'Custo: $' in linha or 'Na cesta: ' in linha:
					pass
				else:
					tipo_cesta = self.controlador.tipos_cestas.encontrar_tipo(linha.rstrip())
					if tipo_cesta:
						self.cesta = self.controlador.acrescentar_cesta(self.pedido, tipo_cesta)
						self.subparte = 'CESTA'
					elif m_organico_unidade:
						nome_organico = m_organico_unidade.group('organico')
						organico = self.controlador.organicos.encontrar_organico(nome_organico)
						if not organico:
#							print('!!! Erro: nao achei organico (' + nome_organico + ') na lista "organicos.txt"!!!')
							self.log('!!! Erro: nao achei organico (' + nome_organico + ') na lista "organicos.txt"!!!')
						self.organico_cesta = OrganicoCesta(self.cesta, nome_organico, m_organico_unidade.group('unidade'), organico)
					elif m_organico:
						nome_organico = m_organico.group('organico')
						organico = self.controlador.organicos.encontrar_organico(nome_organico)
						if not organico:
#							print('!!! Erro: nao achei organico (' + nome_organico + ') na lista "organicos.txt"!!!')
							self.log('!!! Erro: nao achei organico (' + nome_organico + ') na lista "organicos.txt"!!!')
						self.organico_cesta = OrganicoCesta(self.cesta, nome_organico, None, organico)
			elif self.subparte == 'SOMA':
				m_subtotal_pedido = er_subtotal_pedido.match(linha)
				m_frete_pedido = er_frete_pedido.match(linha)
				m_total_pedido = er_total_pedido.match(linha)
				if m_subtotal_pedido:
					self.pedido.subtotal = m_subtotal_pedido.group('valor').replace('.', ',')
				elif m_frete_pedido:
					self.pedido.frete = m_frete_pedido.group('valor').replace('.', ',')
				elif m_total_pedido:
					self.pedido.total = m_total_pedido.group('valor').replace('.', ',')
				elif 'http://portalubaia.com.br/wp-admin/post.php?post=' in linha:
					self.pedido.url = linha.rstrip()
		elif self.parte == 'CLIENTE':
			if '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=' in linha:
				self.parte = 'RODAPE'
			elif 'ENDEREçO DE COBRANçA' in linha:
				self.subparte = 'COBRANCA'
			elif 'ENDEREçO DE ENTREGA' in linha:
				self.subparte = 'NOME'
			elif 'Nota:' in linha:
				self.subparte = 'NOTA'
				self.pedido.nota = linha[6:-1]
			elif 'E-mail: ' in linha:
				self.subparte = 'CLIENTE'
				self.pedido.email = linha[8:-1]
			elif 'Tel: ' in linha:
				self.pedido.telefone = linha[5:-1]
			elif self.subparte == 'NOTA':
				self.pedido.nota = self.pedido.nota + ' ' + linha[:-1]
			elif self.subparte == 'NOME':
				if linha.rstrip() != '':
					self.pedido.nome_cliente = linha[:-1]
					self.subparte = 'ENDERECO'
			elif self.subparte == 'ENDERECO':
				self.pedido.endereco = linha[:-1]
				self.subparte = 'COMPLEMENTO'
			elif self.subparte == 'COMPLEMENTO':
				self.pedido.complemento = linha[:-1]
				self.subparte = 'CIDADE'
			elif self.subparte == 'CIDADE':
				self.pedido.cidade = linha[:-1]
				self.subparte = 'UF'
			elif self.subparte == 'UF':
				self.pedido.uf = linha[:-1]
				self.subparte = 'CEP'
			elif self.subparte == 'CEP':
				self.pedido.cep = linha[:-1]
		elif self.parte == 'RODAPE':
			pass
	def interpretar_mensagem(self, arquivo):
		self.parte = 'CABECALHO'
		self.subparte = ''
		for linha in open(pasta_pedidos + arquivo,'r', encoding='utf8'):
			self.interpretar_texto(linha)
	def interpretar_tipos_cesta(self):
		for linha in open('cestas.txt','r', encoding='utf8'):
			campo = linha.rstrip().split(',')
			tipo_cesta = TipoCesta(campo[0], campo[1])
			self.controlador.tipos_cestas.acrescentar_tipo_cesta(tipo_cesta)
		self.controlador.cestas.inicializar(self.controlador.tipos_cestas)
	def interpretar_dias_entrega(self):
		self.controlador.dias_entrega = []
		for linha in open('dias_entrega.txt','r', encoding='utf8'):
			self.controlador.dias_entrega.append(int(linha.rstrip().split(',')[1]))
	def interpretar_mensagens_pasta(self):
		self.interpretar_tipos_cesta()
		self.interpretar_dias_entrega()
		for arq in os.listdir(pasta_pedidos):
			self.arquivo = arq
			if ('pedido-' in str(arq) and '.txt' in str(arq)):
				self.interpretar_mensagem(str(arq))
				self.log('interpretando mensagem ' + arq)
	def interpretar_pedidos_entrega(self, pedidos, data_entrega):
		self.interpretar_tipos_cesta()
		self.interpretar_dias_entrega()
		for arq in os.listdir(pasta_pedidos):
			m_arquivo_pedido = er_arquivo_pedido.match(arq)
			if m_arquivo_pedido:
				pedido = m_arquivo_pedido.group('numero')
				if pedido in pedidos:
					self.interpretar_mensagem(arq)				
	def interpretar_organicos(self):
		cabecalho = 'sim'
		for linha in open('organicos.txt','r', encoding='utf8'):
			if cabecalho == 'sim':
				cabecalho = 'nao'
				continue
			campo = linha.rstrip().split(',')
			if '(' in campo[0]:
				subcampo = campo[0].split(' (')
				organico = Organico(subcampo[0], subcampo[1].rstrip(')'), campo[1])
			else:
				organico = Organico(campo[0], '', campo[1])
			if len(campo) == 3 and campo[2] != '':
				for sinonimo in campo[2].split('|'):
					organico.acrescentar_sinonimo(sinonimo)
			self.controlador.organicos.acrescentar_organico(organico)
		self.controlador.organicos_cesta.inicializar(self.controlador.organicos)
		