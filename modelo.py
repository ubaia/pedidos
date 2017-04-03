from datetime import datetime
from config import *

class Pedido:
	def __init__(self, numero):
		self.numero = numero
		self.cestas = []
		self.nota = ''
		self.primeira_entrega = None
		self.proxima_entrega = None
		self.entregas = 1
		self.entregas_restantes = 1
		self.dia = None
	def str_cep(self):
		if self.cep:
			return 'CEP: ' + self.cep
		return '(sem cep)'
	def str_cidade_uf_cep(self):
		if self.cidade.lower() == 'brasilia' or self.cidade.lower() == 'brasília':
			return self.str_cep()
		if self.uf == 'Distrito Federal':
			return self.cidade + '   ' + self.str_cep()
		return self.cidade + ' - ' + self.uf + '   ' + self.str_cep()
	def str_data(self, data):
		if data:
			return data.strftime('%d/%m/%Y')
		print('Fail data: ' + str(self.numero))
		return '?'
	def str_dia(self):
		return self.str_data(self.dia)
	def str_dia_semana(self):
		return self.dia.strftime('%a')
	def str_primeira_entrega(self):
		if self.primeira_entrega:
			return self.str_data(self.primeira_entrega)
		return '?'
	def str_proxima_entrega(self):
		if self.proxima_entrega:
			return self.str_data(self.proxima_entrega)
		return '-'
	def __str__(self):
		texto = 'Pedido nr. ' + self.numero + ' de ' + self.str_dia()
		texto = texto + '\n   Valores: cestas ' + self.subtotal + ' frete ' + self.frete + ' total ' + self.total
		texto = texto + '\n   URL: ' + self.url + '\n'
		for cesta in self.cestas:
			texto = texto + '\n' + str(cesta)
		texto = texto + '\n   Cliente: ' + self.nome_cliente + '    e-mail ' + str(self.email) + '   tel ' + str(self.telefone)
		texto = texto + '\n      ' + self.endereco + ', ' + self.complemento
		texto = texto + '\n      ' + self.str_cidade_uf_cep()
		if self.nota:
			texto = texto + '\n   \n   Nota: ' + self.nota
		return texto
	def str_frequencia_cestas(self):
		frequencias = []
		for cesta in self.cestas:
			if not cesta.tipo.frequencia in frequencias:
				frequencias.append(cesta.tipo.frequencia)
		texto = ''
		for frequencia in frequencias:
			texto = texto + frequencia
		return texto
	def quantidade_entregas(self):
		frequencias = self.str_frequencia_cestas()
		if '4' in frequencias:
			return 4
		if '2' in frequencias:
			return 2
		return 1
	def csv_base(self):
		return self.numero + ';' + self.str_dia() + ';' + self.str_dia_semana() + ';' + self.nome_cliente;
	def csv(self):
		texto = self.csv_base() +  ';' + self.email + ';' + self.str_frequencia_cestas() + ';' + self.subtotal + ';' + self.frete + ';' + self.total
		return texto + ';' + str(self.entregas_restantes) + ';' + self.str_primeira_entrega() + ';' + self.str_proxima_entrega()
class TipoCesta:
	def __init__(self, nome, frequencia):
		self.nome = nome
		self.frequencia = frequencia
	def __str__(self):
		return self.nome
class Cesta:
	def __init__(self, pedido, tipo):
		self.pedido = pedido
		self.tipo = tipo
		self.organicos = []
		self.custo_compra = 0
	def acrescentar_organico(self, organico):
		self.organicos.append(organico)
		self.custo_compra = self.custo_compra + organico.custo()
	def str_plural(self, separador):
		if len(self.pedido.cestas) > 1:
			return separador + str(self.ordem_pedido)
		return ''
	def str_custo(self):
		valor = round(self.custo_compra, 2)
		if self.tipo.frequencia != 'U':
			return str(valor * int(self.tipo.frequencia[-1])).replace('.',',')
		return str(valor).replace('.',',')
	def str_custo_expandido(self):
		valor = round(self.custo_compra, 2)
		if self.tipo.frequencia != 'U':
			qtde = self.tipo.frequencia[-1]
			return qtde + ' x ' + str(valor).replace('.',',') + ' = ' + str(valor * int(qtde)).replace('.',',')
		return str(valor).replace('.',',')
	def __str__(self):
		texto = '   Cesta' + self.str_plural(' ') + ': ' + self.tipo.nome + '  venda: ' + self.custo + '  compra: ' + self.str_custo_expandido()
		for organico in self.organicos:
			texto = texto + '\n      ' + str(organico)
		return texto + '\n'
	def str_pedido(self):
		return self.pedido.numero + self.str_plural('-')
	def str_resumo(self):
		return self.pedido.nome_cliente.lower() + ' (pedido ' + self.str_pedido()
	def csv_base(self):
		return self.pedido.csv_base() + ';' + self.tipo.nome
	def csv(self):
		return self.csv_base() + ';' + self.custo + ';' + self.str_custo()
class Organico:
	def __init__(self, nome, unidade, custo):
		self.nome = nome
		self.unidade = unidade
		self.custo = custo
		self.sinonimos = []
	def acrescentar_sinonimo(self, sinonimo):
		self.sinonimos.append(sinonimo)
	def str_unidade(self):
		if self.unidade:
			return self.unidade
		return ''
	def str_nome_unidade(self):
		if self.unidade:
			return self.nome + ' (' + self.unidade + ')'
		return self.nome
	def str_custo(self):
		if self.custo:
			return self.custo.replace('.',',')
		return '?'
	def __str__(self):
		return self.str_nome_unidade() + ' (custo: ' + self.str_custo() + ')'
class OrganicoCesta:
	def __init__(self, cesta, tipo, unidade, organico):
		self.cesta = cesta
		self.tipo = tipo
		self.unidade = unidade
		self.organico = organico
	def custo(self):
		if self.organico and self.organico.custo:
			return self.quantidade * float(self.organico.custo)
		return 0
	def str_custo(self):
		return str(round(self.custo(),2)).replace('.',',')
	def str_ordem_cesta(self):
		return str(self.ordem_cesta).rjust(2)
	def str_unidade(self):
		if self.unidade:
			return self.unidade
		return ''
	def str_tipo_unidade(self):
		if self.unidade:
			return self.tipo + ' (' + self.unidade + ')'
		return self.tipo
	def __str__(self):
		return (str(self.quantidade) + ' ' + self.str_tipo_unidade()).ljust(30) + (' (' + str(self.ordem_cesta) + ')').rjust(5)
	def str_pedido(self):
		return str(self.quantidade) + ' ' + self.cesta.str_resumo() + ', prioridade ' + str(self.ordem_cesta) + ')'
	def csv(self):
		return self.cesta.csv_base() + ';' + str(self.ordem_cesta) + ';' + str(self.tipo) + ';' + self.str_unidade() + ';' + str(self.quantidade) + ';' + self.str_custo()
class Pedidos:
	def __init__(self):
		self.lista_pedidos = []
	def acrescentar_pedido(self, pedido):
		self.lista_pedidos.append(pedido)
	def __str__(self):
		texto = ''
		for pedido in self.lista_pedidos:
			texto = texto + str(pedido) + '\n\n\n'
		return texto[:-3]
	def cabecalho(self):
		return 'numero;dia do pedido;dia da semana;nome do cliente;email;frequencia das cestas;subtotal;frete;total;entregas por fazer;primeira entrega;proxima entrega'
	def csv(self):
		texto = self.cabecalho()
		for pedido in self.lista_pedidos:
			texto = texto + '\n' + pedido.csv()
		return texto
class TiposCestas:
	def __init__(self):
		self.lista_tipos = []
	def acrescentar_tipo_cesta(self, tipo_cesta):
		self.lista_tipos.append(tipo_cesta)
	def encontrar_tipo(self, nome):
		for tipo in self.lista_tipos:
			if tipo.nome == nome:
				return tipo
		return None
	def __str__(self):
		texto = ''
		for tipo in self.lista_tipos:
			texto = texto + str(tipo) + ', '
		return texto[:-2]
class Cestas:
	def __init__(self):
		self.cestas = []
		self.lista = dict()
		self.quantidades = dict()
	def inicializar(self, tipos_cestas):
		for tipo_cesta in tipos_cestas.lista_tipos:
			self.lista[tipo_cesta.nome] = list()
			self.quantidades[tipo_cesta.nome] = 0
	def acrescentar_cesta(self, cesta):
		self.cestas.append(cesta)
		if cesta.tipo.nome in self.lista:
			self.lista[cesta.tipo.nome].append(cesta)
			self.quantidades[cesta.tipo.nome] = self.quantidades[cesta.tipo.nome] + 1
		else:
			print('!!! Erro de sintaxe: nome de cesta nao previsto (' + cesta.tipo.nome + '). Acrescentar no arquivo cestas.txt !!!')
	def __str__(self):
		texto = 'Cestas:'
		zero = '' 
		for tipo in sorted(self.lista.keys()):
			if self.quantidades[tipo]:
				texto = texto + '\n   ' + (str(self.quantidades[tipo]) + ' ' + str(tipo) + ': ').ljust(30)
				for cesta in self.lista[tipo]:
					texto = texto + cesta.str_pedido() + ', '
				texto = texto[:-2]
			else:
				zero = zero + str(tipo) + ', '
		if zero:
			return texto + '\n   \n   0 ' + zero[:-2]
		return texto
	def cabecalho(self):
		return 'numero;dia do pedido;dia da semana;nome do cliente;nome da cesta;preco da cesta;custo da cesta'
	def csv(self):
		texto = self.cabecalho()
		for cesta in self.cestas:
			texto = texto + '\n' + cesta.csv()
		return texto
class Organicos:
	def __init__(self):
		self.lista_organicos = []
	def acrescentar_organico(self, organico):
		self.lista_organicos.append(organico)
	def tratar_nome(self, nome):
		return nome.lower().replace('ó', 'o').replace('ê', 'e').replace('â', 'a')
	def encontrar_organico(self, nome):
		nome = self.tratar_nome(nome)
		for organico in self.lista_organicos:
			if self.tratar_nome(organico.nome) == nome:
				return organico
			for sinonimo in organico.sinonimos:
				if self.tratar_nome(sinonimo) == nome:
					return organico
		return None
	def __str__(self):
		texto = ''
		for organico in self.lista_organicos:
			texto = texto + str(organico) + ', '
		return texto[:-2]
class OrganicosCesta:
	def __init__(self):
		self.organicos = []
		self.lista = dict()
		self.quantidades = dict()
		self.preco = dict()
	def inicializar(self, organicos):
		for organico in organicos.lista_organicos:
			self.lista[organico.str_nome_unidade()] = list()
			self.quantidades[organico.str_nome_unidade()] = 0
			self.preco[organico.str_nome_unidade()] = 0.0
	def acrescentar_organico(self, organico):
		self.organicos.append(organico)
		tipo = organico.str_tipo_unidade()
		if tipo not in self.lista:
			self.lista[tipo] = list()
			self.quantidades[tipo] = 0
			self.preco[tipo] = 0.0
		self.lista[tipo].append(organico)
		self.quantidades[tipo] = self.quantidades[tipo] + organico.quantidade
		self.preco[tipo] = organico.organico.custo
	def __str__(self):
		texto = 'Organicos:'
		for tipo in sorted(self.lista.keys()):
			if (self.quantidades[tipo]):
				texto = texto + '\n   ' + str(self.quantidades[tipo]) + ' ' + str(tipo) + ' - preco ' + self.preco[tipo].replace('.',',') + ':'
				for organico in self.lista[tipo]:
					texto = texto + '\n      ' + organico.str_pedido()
				texto = texto + '\n'
		return texto
	def cabecalho(self):
		return 'numero;dia do pedido;dia da semana;nome do cliente;nome da cesta;ordem na cesta;organico;unidade;quantidade;custo'
	def csv(self):
		texto = self.cabecalho()
		for organico in self.organicos:
			texto = texto + '\n' + organico.csv()
		return texto
		