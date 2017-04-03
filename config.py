import locale
locale.setlocale(locale.LC_ALL, '')

pasta_pedidos = 'COLOQUE A PASTA PRINCIPAL AQUI'
conta = 'COLOQUE SEU EMAIL AQUI'
senha = 'COLOQUE SUA SENHA AQUI'

def barra():
	print('=================================================================================')
def barras():
	return '================================================================================='
def sobre():
	print()
	barra()
	print('===          Rotina de interpretacao de pedidos Ubaia  -  Versao 0.3          ===')
	barra()
	print()
def aviso():
	print()
	barra()
	print('===      ATENCAO: NAO ESTAO COMPUTADOS ORGANICOS DAS CESTAS FECHADAS !!!      ===')
	barra()
def historia():
	print('Versao 0.1 - Geração dos relatorios de entrega')
	print('Versao 0.2 - Geração das listas de pedidos, cestas e organicos')
	print('Versao 0.3 - Processamento dos custos de compra dos organicos')
	print('Todo: retirar das listas pedidos de teste e os não pagos')
	print('Todo: custo de compra - ajuste das unidades')
	print('Todo: processar lista de orgânicos nas cestas fechadas')
	print('Todo: manipular tags no Gmail')
	print('Todo: alterar cestas - veja email Andrea dia 27/02')
