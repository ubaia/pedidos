from modelo import *
from datetime import datetime, timedelta, date

class Controlador:
	tipos_cestas = TiposCestas();
	cestas = Cestas();
	organicos = Organicos()
	organicos_cesta = OrganicosCesta();
	pedidos = Pedidos();

	def acrescentar_pedido(self, numero):
		pedido = Pedido(numero)
		self.pedidos.acrescentar_pedido(pedido)
		return pedido
	def acrescentar_cesta(self, pedido, tipo):
		cesta = Cesta(pedido, tipo)
		cesta.ordem_pedido = len(pedido.cestas) + 1
		pedido.cestas.append(cesta)
		self.cestas.acrescentar_cesta(cesta)
		return cesta
	def acrescentar_organico(self, cesta, organico):
		if (cesta.organicos):
			organico.ordem_cesta = cesta.organicos[len(cesta.organicos)-1].ordem_cesta + cesta.organicos[len(cesta.organicos)-1].quantidade
		else:
			organico.ordem_cesta = 1
		cesta.acrescentar_organico(organico)
		self.organicos_cesta.acrescentar_organico(organico)
	def calcular_prazo_entrega(self, pedido):
		dia_semana_pedido = int(pedido.dia.strftime('%w'))
		for dia_entrega in self.dias_entrega:
			if dia_entrega > dia_semana_pedido:
				return dia_entrega - dia_semana_pedido
		return 7 - dia_semana_pedido + self.dias_entrega[0]
	def calcular_dia_entrega(self, pedido):
		if not pedido.dia:
			print('Fail: ' + str(pedido))
		return pedido.dia + timedelta(days=self.calcular_prazo_entrega(pedido))
	def calcular_dias_entrega(self):
		hoje = datetime.strptime(date.today().strftime('%d/%m/%Y'), '%d/%m/%Y')
		for pedido in self.pedidos.lista_pedidos:
			dia_entrega = self.calcular_dia_entrega(pedido)
			pedido.primeira_entrega = dia_entrega
			entregas_restantes = pedido.quantidade_entregas()
			while dia_entrega < hoje and entregas_restantes > 1:
				dia_entrega = dia_entrega + timedelta(days=7)
				entregas_restantes = entregas_restantes - 1
			if dia_entrega < hoje:
				pedido.entregas_restantes = 0
				pedido.proxima_entrega = None
			else:
				pedido.entregas_restantes = entregas_restantes
				pedido.proxima_entrega = dia_entrega

