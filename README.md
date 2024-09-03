# Introdução
Olá, seja bem-vindo! Sou o Victor, estudante de Engenharia de Controle e Automação na Unicamp, e este 
é o meu gitHub para projetos e aplicações relacionados aos meus estudos na Universidade. 
Quaisquer dúvidas, favor me chamar!
# Projeto Atual
## IC - MICLab
Como uma das fases de avaliação do processo seletivo para oportunidade de Iniciação Científica com
a MICLab, fomos requeridos estudar, compreender e configurar um servidor PACs (*Picture Archiving and Communication System*)
para, posteriormente, envio e análise de arquivos DICOM (*Digital Imaging and Communications in Medicine*).
### Arquivos
- Dockerfile: Arquivo para construção de uma imagem.
- configuration.json: Arquivo essencial para configuração do servidor OrthanC. Nele estão denomeadas informações como as ports que serão utilizadas assim como os usuários registrados.
- scripts: Pasta que contém o script em Python3 para envio de arquivos DICOM, assim como análise por XRayTorchVision e a criação de DICOM SR (*Structured Reports*).
- DICOM: Pasta para armazenar os arquivos DICOM. Necessária para funcionamento do script Python.
## Instruções
Para funcionamento e mais informações do funcionamento do servidor PACs OrthanC, assim como o script de Python, segue instruções e detalhes sobre a aplicação:
### 1°: Instalação do Docker e download ou `git clone` do repositório
  Faça o download do [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/) e em seguida o download dos arquivos presentes neste repositório (`git clone` também é possível)
### 2°: Build da imagem
  Através do seu terminal, ou pelo terminal presente no próprio *GUI* do Docker, primeiro localize o diretório onde está presente os arquivos deste repositório (ou onde foi clonado). Por exemplo:
  
    cd C:/Users/Voce/IC_MICLab
  
  Não se esqueceça que se estiver usando o Windows, é necessário utilizar a barra `/` em vez de `\`.
  
  Em seguida, insira o seguinte comando: 

    docker build -t 'nomedaimagemescolhida' .

  - `t`: abreviação para *tag*. Deve ser seguido pelo nome escolhido para imagem que o Docker irá criar

  Não se esqueça do ` .` no final! O terminal deve indicar a construção da imagem. 

### 3°: Run da imagem criada
  Agora para o Docker iniciar o container com a imagem que criamos, devemos utilizar o seguinte comando:

    docker run -it --name 'nome' -p 8042:8042 -p 8043:8043 --rm 'nomedaimagemescolhida'

  - `it`: Permite interagir com o próprio shell do container através do terminal
  - `--name`: Nomeia o container, facilitando o uso posteriormente. Deve ser seguido por algum nome escolhido
  - `-p`: Mapeia ports entre o host e o container, permitindo acessar serviços do container fora dele. Deve ser seguido com a port do host:port do container
  - `--rm`: Remove a imagem e traços do container após utilizá-lo, liberando espaço (opcional)

A imagem deve estar funcionando. Para testar, pode utilizar `docker ps` para indicar o container que está em uso, assim como entrar em um localhost (a imagem configura a port 8042 automaticamente, assim, ficaria como: `localhost:8042`). Será necessário inserir um usuário e uma senha para entrar no servidor OrthanC. Como default, nós temos usuário:senha como: `you:yourpassword`.

Todas estas configurações estão presentes no arquivo `configuration.json` presente no repositório, e podem ser modificadas a qualquer momento. O [site de OrthanC](https://orthanc.uclouvain.be/book/users/configuration.html) pode auxiliar na criação do arquivo de configuração específico desejado.

### 4°: Utilização do script Python
  Primeiro, verifique se o diretório com o Dockerfile possui a pasta /scripts com o script de Python `script.py`, assim como uma pasta DICOM onde você deverá armazenar os arquivos DICOM que serão enviados ao servidor. Assim, posteriormente
