# **OrderPhotos**

Este script organiza automaticamente fotos e vídeos em pastas baseadas no ano de criação/captura. Ele lê os metadados EXIF de fotos, extrai datas de criação de vídeos usando `ffprobe` (parte do `ffmpeg`) e renomeia os arquivos com a data e hora correspondentes. Arquivos duplicados ou já organizados são ignorados.

## **Funcionalidades**

- Organiza fotos e vídeos em pastas por ano.
- Renomeia arquivos com base na data de captura (para fotos) ou data de criação (para vídeos).
- Converte vídeos para o formato MP4, se necessário.
- Mantém um log detalhado das operações realizadas.
- Ignora pastas e arquivos configuráveis através do `config.ini`.

---

## **Pré-requisitos**

Antes de executar o script, certifique-se de ter o seguinte instalado:

1. **Python 3.x**  
2. **Bibliotecas Python necessárias:**  
   - `Pillow` (para manipulação de imagens e metadados EXIF)  
   - `halo` (para animações de carregamento no terminal)  
   - `configparser` (para leitura do arquivo de configuração)

   Instale as dependências com:

   ```bash
   pip install Pillow halo configparser
   ```

3. **FFmpeg**  
   O `ffprobe` (parte do pacote `ffmpeg`) é usado para extrair metadados de vídeos. Instale com:

   - **Linux:**  
     ```bash
     sudo apt install ffmpeg
     ```

   - **MacOS (Homebrew):**  
     ```bash
     brew install ffmpeg
     ```

   - **Windows:**  
     Baixe e instale o FFmpeg do site oficial: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

---

## **Configuração**

O script utiliza um arquivo `config.ini` para configurar tipos de arquivos suportados e pastas a serem ignoradas. Um exemplo de `config.ini` pode ser assim:

```ini
[order_photo]
IGNORE_FOLDERS = ["System Volume Information", "node_modules", "__pycache__"]
TYPE_PHOTO = [".jpg", ".jpeg", ".png", ".heic"]
TYPE_VIDEO = [".mp4", ".mov", ".avi", ".mkv"]
```

- **IGNORE_FOLDERS**: Lista de pastas que o script deve ignorar.
- **TYPE_PHOTO**: Extensões de arquivos de imagem suportadas.
- **TYPE_VIDEO**: Extensões de arquivos de vídeo suportadas.

---

## **Como Usar**

1. **Clone ou baixe o script** para o seu computador.

2. **Prepare o arquivo `config.ini`** com as configurações adequadas.

3. **Execute o script:**

   ```bash
   python nome_do_script.py
   ```

4. **Digite os diretórios conforme solicitado:**

   - **Pasta de Origem:** Diretório onde estão localizadas suas fotos e vídeos.
   - **Pasta de Destino:** Diretório onde os arquivos organizados serão salvos. Caso não informe, o diretório atual será usado.

---

## **Exemplo de Execução**

```bash
$ python order_photos.py
====================================================================
ORDER PHOTO
====================================================================
Pasta de Origem: /home/usuario/fotos
Pasta de Destino: /home/usuario/fotos_organizadas

✔ Organizando arquivos...
✔ Feito
```

Após a execução, os arquivos estarão organizados assim:

```
/home/usuario/fotos_organizadas/
├── 2020/
│   ├── 2020-05-15_14-23-01_IMG001.jpg
│   └── 2020-07-10_18-45-12_VIDEO001.mp4
├── 2021/
│   └── 2021-09-22_09-10-33_IMG002.png
└── sem_data/
    └── arquivo_desconhecido.mov
```

---

## **Funcionalidades Adicionais**

- **Conversão de Vídeos:**  
  Vídeos que não estão no formato `.mp4` serão automaticamente convertidos usando `ffmpeg` para garantir compatibilidade.

- **Arquivos Sem Data:**  
  Arquivos que não contêm informações de data nos metadados serão movidos para a pasta `sem_data`.

- **Logs:**  
  O script gera logs detalhados das operações realizadas, incluindo erros encontrados. Verifique o arquivo `log.txt` (ou o arquivo configurado no `logger`).

---

## **Problemas Comuns**

- **Permissão negada ao acessar arquivos:**  
  Execute o script com permissões adequadas ou verifique as permissões dos arquivos.

- **`ffprobe` não encontrado:**  
  Certifique-se de que o `ffmpeg` está instalado e que o caminho está configurado corretamente no seu sistema.

---

## **Contribuições**

Contribuições são bem-vindas! Sinta-se à vontade para abrir um *pull request* ou relatar problemas na seção de *issues*.

---

## **Licença**

Este projeto está licenciado sob a [MIT License](https://opensource.org/licenses/MIT).

---

Se precisar de mais ajustes ou ajuda com outra parte do script, só avisar! 🚀