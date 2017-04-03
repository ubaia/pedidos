from config import *
from modelo import *
from controlador import *
from interpretador import Interpretador

def barra():
	print('=================================================================================')
def sobre():
	print()
	barra()
	print('===          Rotina de interpretacao de pedidos Ubaia  -  Versao 0.3          ===')
	barra()
	print()

sobre()
controlador = Controlador()
interpretador = Interpretador(controlador)
print('Carregando csv...')
interpretador.interpretar_organicos()
print('Lendo mensagens baixadas...')
interpretador.interpretar_mensagens_pasta()
print('Atualizando datas de entrega...')
controlador.calcular_dias_entrega()

print('Atualizando listas csv...')

arq = open(pasta_pedidos + 'lista_pedidos.csv','w', encoding='utf8')
arq.write(controlador.pedidos.csv())
arq.close()

arq = open(pasta_pedidos + 'lista_cestas.csv','w', encoding='utf8')
arq.write(controlador.cestas.csv())
arq.close()

arq = open(pasta_pedidos + 'lista_organicos.csv','w', encoding='utf8')
arq.write(controlador.organicos_cesta.csv())
arq.close()

