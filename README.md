# Introdução
Olá, seja bem-vindo! Sou o Victor, estudante de Engenharia de Controle e Automação na Unicamp, e este 
é o meu gitHub para projetos e aplicações relacionados aos meus estudos na Universidade. 
Quaisquer dúvidas, favor me chamar em v248206@dac.unicamp.br!
# Projeto Atual
## IC - MICLab
Como uma das fases de avaliação do processo seletivo para oportunidade de Iniciação Científica com
a MICLab, fomos requeridos estudar, compreender e configurar um servidor PACs (*Picture Archiving and Communication System*)
para, posteriormente, envio e análise de arquivos DICOM (*Digital Imaging and Communications in Medicine*) e SR (*Structured Report*).
### Arquivos
- Dockerfile: Arquivo para construção de uma imagem, instalação das bibliotecas utilizadas no script Python e mais.
- configuration.json: Arquivo essencial para configuração do servidor OrthanC. Nele estão denomeadas informações como as ports que serão utilizadas assim como os usuários registrados.
- scripts: Pasta que contém o script em Python (denomeado script.py) para envio de arquivos DICOM, assim como análise por XRayTorchVision e a criação de DICOM SR (*Structured Reports*). Ambas a pasta e o script são **essenciais** para funcionamento do container.
- DICOM: Pasta para armazenar os arquivos DICOM. **Essencial** para funcionamento do script Python, e portanto os arquivos deverão estar localizados aqui.
## Avisos
- O *Dockerfile* para criação da imagem utiliza um *Virtual Environment* para o plugin de Python, garantindo seu funcionamento em computadores protegidos pela rede/organização.
- Para funcionamento do script de Python, é necessário um espaço consideravelmente alto disponível (para segurança, em torno de 8-10 GB), devido ao download de todas as bibliotecas e a criação dos *Structured Reports*.
- A imagem criada pelo *Dockerfile* utiliza a configuração proveniente do arquivo *configuration.json*, onde se faz a criação de um usuário para fazer login no servidor localizado na porta escolhida (O default é a porta 8042), e este usuário também é utilizado no script de Python para fazer o upload/delete dos arquivos enviados. O usuário default é (login:senha) `you:yourpassword` e se for feita a alteração no arquivo *.json*, deverá ser feita a alteração no script de Python (logo no início do script, essa informação está numa variável).
## Instruções
Para funcionamento e mais informações do funcionamento do servidor PACs OrthanC, assim como o script de Python, segue instruções e detalhes sobre a aplicação:
### 1°: Instalação do Docker e download ou `git clone` do repositório
Faça o download do [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/) e em seguida o download dos arquivos presentes neste repositório (`git clone` também é possível).
### 2°: Build da imagem
Através do seu terminal, ou pelo terminal presente no próprio *GUI* do Docker, primeiro localize o diretório onde está presente os arquivos deste repositório (ou onde foi clonado). Por exemplo:
  
    cd C:/Users/Voce/IC_MICLab
  
Em seguida, insira o seguinte comando: 

    docker build -t 'nomedaimagemescolhida' .

- `t`: Abreviação para *tag*. Deve ser seguido pelo nome escolhido para imagem que o Docker irá criar

Não se esqueça do ` .` no final! A construção deve demorar cerca de 100 à 200segs. O terminal deve indicar a construção da imagem. 

### 3°: Run da imagem criada
Agora para o Docker iniciar o container com a imagem que criamos, devemos utilizar o seguinte comando:

    docker run -d --name 'nome' -p 8042:8042 -p 8043:8043 --rm 'nomedaimagemescolhida'

- `-d`: Abreviação para *detached*. Permite rodar o container em segundo fundo, permitindo o uso do terminal.
- `--name`: Nomeia o container, facilitando o uso posteriormente. Deve ser seguido por algum nome escolhido.
- `-p`: Mapeia ports entre o host e o container, permitindo acessar serviços do container fora dele. Deve ser seguido com a port do host:port do container.
- `--rm`: Remove a imagem e traços do container após utilizá-lo, liberando espaço (opcional).

A imagem deve estar funcionando. Para testar, pode utilizar `docker ps` para indicar o container que está em uso, assim como entrar em um localhost (a imagem configura a port 8042 automaticamente, assim, ficaria como: `localhost:8042`). Como já dito, será necessário inserir um usuário e uma senha para entrar no servidor OrthanC. Como default, nós temos usuário:senha como: `you:yourpassword`.

Todas estas configurações estão presentes no arquivo `configuration.json` presente no repositório, e podem ser modificadas a qualquer momento. O [site de OrthanC](https://orthanc.uclouvain.be/book/users/configuration.html) pode auxiliar na criação do arquivo de configuração específico desejado.

### 4°: Utilização do script Python
Primeiro, verifique se o diretório com o Dockerfile possui a pasta /scripts com o script de Python `script.py`, assim como uma pasta DICOM onde você deverá armazenar os arquivos DICOM que serão enviados ao servidor. Assim, posteriormente, com o container sendo utilizado, deve-se inserir o comando:

    `docker exec -it 'nome' python /usr/local/bin/script.py`
  
- `it`: Abreviação para *interactive*. Permite interagir com o próprio shell do container através do terminal.
- `python`: Inicia o plugin Python da imagem. Deve ser seguido com o diretório, especificado no configuration.json, onde estará o script Python após o início do container.

Logo após este comando, espere um tempo e deverá aparecer a seguinte frase:

    Digite:
    -'upload' para enviar os arquivos .dcm localizados na pasta DICOM
    -'delete' para deletar os arquivos .dcm localizados no servidor OrthanC
    -'analise' para fazer a análise dos arquivos .dcm localizados na pasta DICOM
    -'sr' para fazer a criação dos SRs dos arquivos.dcm localizados na pasta DICOM e enviá-los para o servidor OrthanC

Após qualquer comando utilizado, aparecerão informações relevantes ao que foi escolhido. Se for desejado realizar qualquer outra operação, será sempre **necessário** utilizar o comando:

    `docker exec -it 'nome' python /usr/local/bin/script.py`

### 5°: Finalização do container
Para finalização do container, é necessário a utilização do comando:

    docker stop 'nome'

E deverá aparecer no terminal o 'nome' escolhido para imagem. Também é recomendado a utilização do comando:

    docker system prune -a -f

Para remoção de quaisquers arquivos ainda presentes no computador após a utilização do script. O comando `system` garante que `prune` (o operador de remoção) será de todos os arquivos, não apenas de uma imagem por exemplo, e `-a` e `-f` garantem que será feito no sistema inteiro e para qualquer 'tipo' de arquivo (inoperante ou não), respectivamente.

## Dificuldades/Considerações
