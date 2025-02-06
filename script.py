import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import subprocess, time
# import tkinter as tk
# from tkinter import filedialog
from log import logger
from halo import Halo
from banner import Banner
import configparser

spinner = Halo(spinner='dots')

def get_config():
    global TYPE_FILE, TYPE_PHOTO, TYPE_VIDEO, IGNORE_FOLDERS
    config = configparser.ConfigParser()
    config.read("config.ini")
    IGNORE_FOLDERS = eval(config.get("order_photo", "IGNORE_FOLDERS"))
    TYPE_PHOTO = eval(config.get("order_photo", "TYPE_PHOTO"))
    TYPE_VIDEO = eval(config.get("order_photo", "TYPE_VIDEO"))
    TYPE_FILE = TYPE_PHOTO + TYPE_VIDEO

def get_date_obj(date_taken):
    formats = ["%Y-%m-%d %H:%M:%S", "%Y:%m:%d %H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.strptime(date_taken, fmt)
        except ValueError:
            continue
    raise ValueError


def get_exif_data(image_path):
    """Obtém os dados EXIF da imagem e retorna a data e hora de captura."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data is not None:
            for tag, value in exif_data.items():
                if TAGS.get(tag) == "DateTimeOriginal":  # Data e hora da foto
                    return value
    except Exception as e:
        print(f"Erro ao obter EXIF de {image_path}: {e}")
        logger.error(f"Erro ao obter EXIF de {image_path}: {e}")
    return get_file_modification_date(image_path)


def get_file_modification_date(file_path):
    """Obtém a data de modificação do arquivo se a data de captura não estiver disponível."""
    try:
        mod_time = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mod_time).strftime("%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"Erro ao obter data de modificação de {file_path}: {e}")
        logger.error(f"Erro ao obter data de modificação de {file_path}: {e}")
    return None


def get_video_creation_date(video_path):
    """Obtém a data de criação de um vídeo usando ffprobe (parte do ffmpeg)."""
    try:
        # Usando ffprobe para extrair a data de criação do vídeo
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format_tags=creation_time",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        creation_time = result.stdout.decode().strip()
        if creation_time:
            # Exemplo de data retornada: "2024-12-25T15:30:45.000000Z"
            return creation_time.replace("T", " ").split(".")[0]
        else:
            return get_file_modification_date(video_path)
    except Exception as e:
        print(f"Erro ao obter data de criação do vídeo {video_path}: {e}")
        logger.error(f"Erro ao obter data de criação do vídeo {video_path}: {e}")
    return None


def is_file_renamed_and_in_correct_folder(file_path, date_taken, destination_folder):
    """Verifica se o arquivo já foi renomeado e se está na pasta do ano correspondente."""
    # Converte a data para o formato desejado
    try:
        date_obj = get_date_obj(date_taken)
        date_str = date_obj.strftime("%Y-%m-%d_%H-%M-%S")
    except ValueError as e:
        print(f"Erro ao converter data para {file_path}: {e}")
        logger.error(f"Erro ao converter data para {file_path}: {e}")
        return False

    # Obtém o ano do arquivo
    year = date_obj.year
    # Obtém o nome do arquivo
    file_name = os.path.basename(file_path)

    # Verifica se o nome do arquivo já contém a data e se ele está na pasta do ano
    if date_str in file_name and os.path.dirname(file_path).endswith(str(year)):
        return True

    return False


def convert_video(origem, destino):
    try:
        comando = f'ffmpeg -i "{origem}" -c:v libx264 -c:a aac "{destino}"'
        subprocess.call(comando, shell=True)
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        logger.error(f"Erro: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Erro durante a conversão: {e}")
        logger.error(f"Erro durante a conversão: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        logger.error(f"Erro inesperado: {e}")


def copy_safe_or_convert(origem, destino):
    file_extension = origem.lower().split(".")[-1]
    if os.path.exists(destino):
        spinner.text = f"Arquivo {destino} já existe."
        logger.info(f"Arquivo {destino} já existe.")
    elif file_extension in TYPE_VIDEO and file_extension != "mp4":
        destino = destino.lower()
        destino_convert = destino.replace(file_extension, "mp4")
        if not os.path.exists(destino_convert):
            spinner.text = f"Arquivo {origem} é um vídeo, será convertido para mp4"
            logger.info(
                f"Arquivo {origem} é um vídeo, será convertido para mp4 e movido para {destino_convert}"
            )
            convert_video(origem=origem, destino=destino_convert)
        spinner.text = f"Video {destino_convert} já existe."

    else:
        #TODO - add config
        shutil.copy2(origem, destino)
        time.sleep(1)
        # shutil.move(origem, destino)
        spinner.text = f"Arquivo {origem} renomeado e copiado para {destino}"
        logger.info(f"Arquivo {origem} renomeado e copiado para {destino}")


def rename_and_move_file(file_path, destination_folder):
    """Renomeia a imagem ou vídeo com data e hora de captura ou de modificação e a move para a pasta do ano."""
    # Verifica se o arquivo já foi renomeado e movido para a pasta correta
    file_extension = file_path.lower().split(".")[-1]
    file_name = os.path.basename(file_path)

    # Para fotos, tenta obter a data EXIF
    if file_extension in TYPE_PHOTO:
        date_taken = get_exif_data(file_path)
    # Para vídeos, tenta obter a data de criação
    elif file_extension in TYPE_VIDEO:
        date_taken = get_video_creation_date(file_path)
    else:
        # Se não for foto nem vídeo, tenta usar a data de modificação do arquivo
        date_taken = get_file_modification_date(file_path)
    if date_taken is None:
        spinner.text = f"Data não encontrada para {file_path}. Colocando em pasta sem data..."
        logger.info(f"Data não encontrada para {file_path}. Colocando em pasta sem data...")
        other_folder = os.path.join(destination_folder, 'sem_data')
        if not os.path.exists(other_folder):
            os.makedirs(other_folder)
        copy_safe_or_convert(origem=file_path, destino=os.path.join(other_folder, file_name))
        return

    # Verifica se o arquivo já foi renomeado e movido corretamente
    if is_file_renamed_and_in_correct_folder(file_path, date_taken, destination_folder):
        spinner.text = f"Arquivo {file_path} já está renomeado e na pasta correta. Pulando..."
        logger.info(
            f"Arquivo {file_path} já está renomeado e na pasta correta. Pulando..."
        )
        return

    # Converte a data para o formato desejado
    try:
        date_obj = get_date_obj(date_taken)
        date_str = date_obj.strftime("%Y-%m-%d_%H-%M-%S")
    except ValueError as e:
        print(f"Erro ao converter data para {file_path}: {e}")
        logger.error(f"Erro ao converter data para {file_path}: {e}")
        return

    # Obtém o ano do arquivo (data de captura ou de modificação)
    year = date_obj.year
    # Cria a pasta para o ano, se não existir
    year_folder = os.path.join(destination_folder, str(year))
    if not os.path.exists(year_folder):
        os.makedirs(year_folder)

    # Renomeia o arquivo e cria o caminho de destino
    new_filename = f"{date_str}_{file_name}"
    new_filepath = os.path.join(year_folder, new_filename)

    # Move o arquivo para a pasta do ano com o novo nome
    try:
        copy_safe_or_convert(origem=file_path, destino=new_filepath)
    except PermissionError as e:
        print(f"Permissão negada ao copiar {file_path}: {e}")
        logger.error(f"Permissão negada ao copiar {file_path}: {e}")
    except Exception as e:
        print(f"Erro ao mover {file_path}: {e}")
        logger.error(f"Erro ao mover {file_path}: {e}")
        raise e


def is_ignore_path(root):
    for name in root.split(os.sep):
        if name.split(":")[-1] in IGNORE_FOLDERS:
            return True
    return False


def process_files_in_folder(root_folder, destination_folder):
    """Processa todos os arquivos de fotos e vídeos em uma pasta e suas subpastas."""
    for root, dirs, files in os.walk(root_folder):
        if is_ignore_path(root):
            continue
        for file in files:
            file_path = os.path.join(root, file)
            # Filtra arquivos de fotos e vídeos
            if file.lower().endswith(tuple(TYPE_FILE)):
                rename_and_move_file(file_path, destination_folder)


# def select_folder():
#     """Abre um diálogo para o usuário selecionar uma pasta de destino."""
#     root = tk.Tk()
#     root.withdraw()  # Esconde a janela principal
#     folder_selected = filedialog.askdirectory(title="Selecione a pasta de destino")
#     return folder_selected


if __name__ == "__main__":
    
    # Defina o diretório raiz onde as fotos e vídeos estão localizados
    os.system('clear')
    sep = "===================================================================="
    logger.info(sep)
    logger.error(sep)
    Banner("OrderPhoto").print_banner()
    get_config()
    
    # Solicitar que o usuário selecione a pasta de destino
    ROOT_FOLDER = input("Pasta de Origem:")
    destination_folder = input("Pasta de Destino:")

    # Se nenhuma pasta for selecionada, use o diretório atual
    if not destination_folder:
        destination_folder = os.getcwd()
        spinner.info(
            f"Nenhuma pasta de destino selecionada. Usando o diretório atual: {destination_folder}"
        ).start()
        logger.info(
            f"Nenhuma pasta de destino selecionada. Usando o diretório atual: {destination_folder}"
        )
    else:
        spinner.info(f"Pasta de destino selecionada: {destination_folder}").start()
        logger.info(f"Pasta de destino selecionada: {destination_folder}")
    spinner.start()
    process_files_in_folder(ROOT_FOLDER, destination_folder)
    spinner.succeed("Feito")
    spinner.stop()
