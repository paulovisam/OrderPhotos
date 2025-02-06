import logging, os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not os.path.exists("./logs"):
    os.makedirs("./logs")

# Criando um handler para gravar em um arquivo de erros
error_handler = logging.FileHandler('./logs/erros.txt')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(error_handler)

# Criando um handler para gravar em um arquivo de informações gerais
info_handler = logging.FileHandler('./logs/info.txt')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(info_handler)

log = logging