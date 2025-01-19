# -*- coding: utf-8 -*-
import requests
import os
import zipfile
import json
from datetime import datetime
from tqdm import tqdm

def create_zip(source_dir, output_zip):
    """Cria um arquivo ZIP da pasta especificada."""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Adiciona o arquivo ao ZIP mantendo a estrutura de diretórios
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
    print(f"Arquivo ZIP criado: {output_zip}")

def upload_release(config_path, zip_path, release_name):
    """Faz upload do ZIP como um release no GitHub."""
    # Lê os dados do arquivo de configuração
    with open(config_path, 'r', encoding='utf-8-sig') as file:
        config = json.load(file)

    repository = config["repository"]
    token = config["token"]
    
    # Lê o conteúdo do README.md
    readme_path = "README.md"  # Caminho para o README.md
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as readme_file:
            readme_content = readme_file.read()
    else:
        readme_content = "README.md não encontrado. Release gerado automaticamente com o código fonte e arquivos."  # Caso o README.md não exista
    
    # API para criar o release
    release_url = f"https://api.github.com/repos/{repository}/releases"
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }

    # Dados do release
    release_data = {
        "tag_name": release_name,
        "name": release_name,
        "body": readme_content,  # Agora o conteúdo do README.md é usado como descrição
        "draft": False,
        "prerelease": False
    }

    # Cria o release no GitHub
    response = requests.post(release_url, headers=headers, json=release_data)
    if response.status_code == 201:
        release_info = response.json()
        upload_url = release_info["upload_url"].split("{")[0]
        print(f"Release criado: {release_info['html_url']}")
    else:
        print(f"Erro ao criar o release: {response.status_code} - {response.text}")
        return

    # Faz o upload do arquivo ZIP para o release
    with open(zip_path, 'rb') as zip_file:
        file_name = os.path.basename(zip_path)
        params = {"name": file_name}
        upload_headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/zip"
        }

        # Obtemos o tamanho do arquivo para usar na barra de progresso
        total_size = os.path.getsize(zip_path)

        # Criar a barra de progresso
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Enviando {file_name}") as pbar:
            def progress_callback(chunk):
                pbar.update(len(chunk))
                return chunk
            
            # Enviar o arquivo com o callback de progresso
            upload_response = requests.post(upload_url, headers=upload_headers, params=params, data=iter(lambda: progress_callback(zip_file.read(1024 * 1024)), None))

            if upload_response.status_code == 201:
                print(f"Arquivo {file_name} enviado com sucesso para o release.")
            else:
                print(f"Erro ao enviar o arquivo: {upload_response.status_code} - {upload_response.text}")

def main():
    # Caminho da pasta onde o script está e a pasta RodrigoPack
    source_dir = "."  # Diretório atual onde o script está localizado
    output_zip = "RodrigoPack.zip"  # Nome do arquivo ZIP
    config_path = "github.json"  # Caminho do arquivo de configuração

    # 1. Cria o arquivo ZIP da pasta RodrigoPack
    create_zip("RodrigoPack", output_zip)

    # Nome do release
    release_name = f"Release-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # 2. Faz o upload do release com o arquivo ZIP
    upload_release(config_path, output_zip, release_name)

if __name__ == "__main__":
    main()