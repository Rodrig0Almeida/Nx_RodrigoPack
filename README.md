# Programa para Baixar Módulos de Forma Automática  

## Descrição  
Este repositório contém um programa para baixar módulos automaticamente e complementar pacotes do Atmosphere 1.8.0.
## as realeses em .zip inclui configurações de EOS (overclock para NS) otimizadas para meu NS OLED.  

Minha recomendação é que você baixe o código fonte e execute via linha de comando para criar seu próprio pacote de módulos. Edite o arquivo `links.json` para adicionar ou remover complementos conforme necessário.  

---

## Requisitos  
### Linux  
1. Instale o Python 3 e `pip`:  
   ```bash  
   sudo apt update && sudo apt install python3 python3-pip -y
   pip3 install requests tqdm
   
### Windows
1. Baixe e instale o Python 3.
2. Durante a instalação, habilite a opção "Add Python to PATH".
3. Instale as dependências via pip:
   ```bash
   pip install requests tqdm

### Termux

1. Atualize os pacotes e instale o Python:
   ```bash
   pkg update && pkg upgrade -y
   pkg install python -y
   pkg install python-pip -y
   pkg install python-pip -y
   pip install requests tqdm
   
### Mac

1. Certifique-se de ter o Python 3 instalado. No macOS moderno, ele geralmente já está disponível.

Caso precise instalar, use o Homebrew:
   ```bash
   brew install python
   pip3 install requests tqdm
```

## Como Usar

1. Clone este repositório:
   ```bash
   git clone https://github.com/Rodrig0Almeida/Nx_RodrigoPack.git
   cd Nx_RodrigoPack

2. Edite o arquivo links.json para incluir ou remover os complementos desejados.

3. Execute o script:
   ```bash
   python3 up_pack.py

No Windows ou Termux, pode ser necessário usar:
   ```bash
python up_pack.py
```
4. O pacote final será gerado na pasta RodrigoPack.

## Para fazer o sphaira baixar e extrair seu pacote diretamente do NS

1. Modifique o arquivo Sphaira.json e coloqueo na pasta do seu pacote gerado pelo programa: RodrigoPack/config/sphaira/github/Sphaira.json

## Para colocalo em seu próprio Github faça um fork do meu Github.

1. Baixe o código e vá no arquivo github.json e coloque o usuário/respositorio e o seu token

2. Instale módulos extras
   ```bash
   pip install requests tqdm requests-toolbelt

3. use o script upgithub.py
   ```bash
   pyhron3 upgithub.py
   
