import requests
import json
import os
import zipfile
import tarfile
import shutil
from tqdm import tqdm

def get_latest_release(url, file_type):
    """Obtém o link do último lançamento na página de releases do GitHub usando a API."""
    headers = {"User-Agent": "Termux-Script"}
    
    # API para obter as últimas releases
    api_url = url.replace("https://github.com/", "https://api.github.com/repos/") + "/releases/latest"
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Erro ao acessar {url}: {response.status_code}")
        return None, None, None

    # Extrai os dados da última release
    release_data = response.json()
    
    # Procura pelo link de download com base no tipo de arquivo especificado
    for asset in release_data['assets']:
        if asset['name'].endswith(file_type):
            # Retorna o URL do arquivo e o nome do arquivo
            return asset['browser_download_url'], asset['name'], release_data['tag_name']
    
    print(f"Nenhum arquivo do tipo {file_type} encontrado na última release de {url}.")
    return None, None, None

def download_file(url, file_name, output_dir="downloads"):
    """Faz o download de um arquivo dado um URL com barra de progresso, verificando se já existe."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = os.path.join(output_dir, file_name)

    # Verifica se o arquivo já existe
    if os.path.exists(file_path):
        print(f"Arquivo {file_name} já existe. Não será feito o download novamente.")
        return file_path
    
    headers = {"User-Agent": "Termux-Script"}
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        # Obtém o tamanho do arquivo
        total_size = int(response.headers.get('content-length', 0))

        # Cria a barra de progresso com tqdm
        with open(file_path, 'wb') as file, tqdm(
            desc=file_name,
            total=total_size,
            unit='B',
            unit_scale=True
        ) as bar:
            # Baixa o arquivo em pedaços e atualiza a barra de progresso
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                bar.update(len(chunk))  # Atualiza a barra com o tamanho do pedaço

        print(f"Arquivo salvo em {file_path}")
        return file_path
    else:
        print(f"Erro ao baixar {url}: {response.status_code}")
        return None

def extract_file(file_path, extract_to="RodrigoPack", extract_folder=None, file_type="zip", copy_to=None):
    """Extrai ou copia um arquivo baseado no seu tipo (ZIP, TAR.GZ, ou outros tipos)."""
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    try:
        if file_type == "zip":
            # Extrai arquivos ZIP
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                if extract_folder:
                    for file_info in zip_ref.infolist():
                        if file_info.filename.startswith(extract_folder + os.sep):
                            file_info.filename = file_info.filename[len(extract_folder) + 1:]
                            if file_info.filename:
                                zip_ref.extract(file_info, extract_to)
                                print(f"Arquivo extraído: {file_info.filename}")
                else:
                    zip_ref.extractall(extract_to)
                    print(f"Arquivo ZIP extraído para {extract_to}")
        elif file_type in ["tar.gz", "tar.xz"]:
            # Extrai arquivos TAR (.tar.gz ou .tar.xz)
            with tarfile.open(file_path, 'r:*') as tar_ref:
                if extract_folder:
                    # Filtra arquivos da pasta específica
                    for member in tar_ref.getmembers():
                        if member.name.startswith(extract_folder + os.sep):
                            member.name = member.name[len(extract_folder) + 1:]
                            tar_ref.extract(member, extract_to)
                            print(f"Arquivo extraído: {member.name}")
                else:
                    tar_ref.extractall(extract_to)
                    print(f"Arquivo TAR extraído para {extract_to}")
        else:
            # Se o arquivo não for compactado, verifica se precisa copiar para uma pasta específica
            if copy_to:
                if not os.path.exists(copy_to):
                    os.makedirs(copy_to)
                shutil.copy(file_path, os.path.join(copy_to, os.path.basename(file_path)))
                print(f"Arquivo {file_path} copiado diretamente para {copy_to}")
            else:
                shutil.copy(file_path, os.path.join(extract_to, os.path.basename(file_path)))
                print(f"Arquivo {file_path} copiado diretamente para {extract_to}")
    except (zipfile.BadZipFile, tarfile.TarError) as e:
        print(f"Erro: O arquivo {file_path} não é um arquivo válido ou está corrompido. ({e})")

def generate_readme(repos, versions, output_file="README.md"):
    """Gera um README.md com a lista de programas baixados, suas versões e URLs."""
    with open(output_file, 'w') as readme:
        readme.write("# Programas Baixados\n\n")
        readme.write("Este repositório contém os seguintes programas baixados automaticamente:\n\n")
        for name, data in repos.items():
            version = versions.get(name, "Desconhecida")
            readme.write(f"- **{name}**\n")
            readme.write(f"  - Repositório: {data['url']}\n")
            readme.write(f"  - Tipo de arquivo: {data.get('file_type', 'Desconhecido')}\n")
            readme.write(f"  - Versão: {version}\n\n")
    print(f"README.md gerado em {output_file}")

def main():
    # Carrega o arquivo JSON (links.json)
    with open("links.json", "r") as file:
        repos = json.load(file)

    versions = {}
    for name, data in repos.items():
        print(f"Verificando {name}...")
        file_type = data.get("file_type", "zip")  # Default to "zip" if not provided
        release_url, file_name, version = get_latest_release(data['url'], file_type)
        if release_url and file_name:
            print(f"Último lançamento encontrado: {release_url} (Arquivo: {file_name}, Versão: {version})")
            versions[name] = version
            file_path = download_file(release_url, file_name)
            if file_path:
                # Extrai ou copia o conteúdo da pasta 'Copy_to_SD' (se presente) para RodrigoPack
                extract_folder = data.get('extract_folder', None)
                copy_to = data.get("copy_to", None)

                # Chama a função de extração ou cópia, incluindo o suporte ao campo 'copy_to'
                extract_file(file_path, extract_to="RodrigoPack", extract_folder=extract_folder, file_type=file_type, copy_to=copy_to)
        else:
            print(f"Não foi possível obter o último lançamento de {name}.")
            versions[name] = "Não encontrado"
    
    # Gera o README.md com versões
    generate_readme(repos, versions)

if __name__ == "__main__":
    main()