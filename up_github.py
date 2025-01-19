# -*- coding: utf-8 -*-
import requests
import os
import zipfile
import json
import subprocess
from datetime import datetime

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

def upload_release(config_path, zip_path, release_name, release_description):
    """Faz upload do ZIP como um release no GitHub."""
    # Lê os dados do arquivo de configuração
    with open(config_path, 'r', encoding='utf-8-sig') as file:
        config = json.load(file)

    repository = config["repository"]
    token = config["token"]
    
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
        "body": release_description,
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
        upload_response = requests.post(upload_url, headers=upload_headers, params=params, data=zip_file)
        if upload_response.status_code == 201:
            print(f"Arquivo {file_name} enviado com sucesso para o release.")
        else:
            print(f"Erro ao enviar o arquivo: {upload_response.status_code} - {upload_response.text}")

def update_github_repo():
    """Faz commit e push do codigo atual para o repositorio GitHub."""
    try:
        # Adiciona e comita os arquivos
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Atualizando codigo e arquivos"], check=True)

        # Faz o push para o repositório remoto
        subprocess.run(["git", "push"], check=True)
        print("Repositorio Git atualizado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao atualizar o repositório Git: {e}")

def main():
    # Caminho da pasta onde o script está e a pasta RodrigoPack
    source_dir = "."  # Diretório atual onde o script está localizado
    output_zip = "RodrigoPack.zip"  # Nome do arquivo ZIP
    config_path = "github.json"  # Caminho do arquivo de configuração

    # 1. Atualiza o repositório Git com os arquivos locais
    update_github_repo()

    # 2. Cria o arquivo ZIP da pasta RodrigoPack
    create_zip("RodrigoPack", output_zip)

    # Nome e descrição do release
    release_name = f"Release-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    release_description = "Release gerado automaticamente com o codigo fonte e arquivos."

    # 3. Faz o upload do release com o arquivo ZIP
    upload_release(config_path, output_zip, release_name, release_description)

if __name__ == "__main__":
    main()