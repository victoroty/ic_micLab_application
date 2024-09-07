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
- results: Pasta para armazenar os arquivos .json de resultados da função de análise da biblioteca TorchXRayVision. **Essencial** para o funcionamento do script Python, porém não é necessário ter nenhum arquivo dentro (o próprio container salvará arquivos lá).
- SR: Pasta para armazenar os arquivos *SR*s criados. **Essencial** para o funcionamento do script de Python, porém não é necessário ter nenhum arquivo dentro (o próprio container salvará arquivos nesta pasta).
- simplified_Docker: Pasta que contém uma versão simplificada dos arquivos *Dockerfile*, *configuration.json* e o script de Python *script.py*, além de outra pasta DICOM para os arquivos .dcm. Nesta versão, a aplicação faz o upload e delete normalmente, porém a análise XRayTorch dos arquivos .dcm não exporta um *json* com os resultados para uma pasta local (apenas realiza um *print* dos resultados), assim como a função de criar arquivos *SR*s baseados nestes arquivos .dcm, junto com os resultados das análises (os *SR*s são exportados automaticamente para o servidor, e não para uma pasta local).
## Avisos
- O *Dockerfile* para criação da imagem utiliza um *Virtual Environment* para o plugin de Python, garantindo seu funcionamento em computadores protegidos pela rede/organização.
- Para funcionamento do script de Python, é necessário um espaço consideravelmente alto disponível (para segurança, em torno de 6 GB), devido ao download de todas as bibliotecas e a criação dos *Structured Reports*.
- A imagem criada pelo *Dockerfile* utiliza a configuração proveniente do arquivo *configuration.json*, onde se faz a criação de um usuário para fazer login no servidor localizado na porta escolhida (O default é a porta 8042), e este usuário também é utilizado no script de Python para fazer o upload/delete dos arquivos enviados. O usuário default é (login:senha) `you:yourpassword` e se for feita a alteração no arquivo *.json*, deverá ser feita a alteração no script de Python (logo no início do script, essa informação está numa variável).
- O script da versão não simplificada possui 4 funções:
    -`upload()`: Faz o upload de todos os arquivos .dcm contidos na pasta DICOM.
    -`delete()`: Deleta todos os arquivos presentes no servidor local OrthanC.
    -`create_sr()`: Cria arquivos *SR*s baseados nos arquivos .dcm presentes na pasta DICOM em conjunto com o resultado das análises feito pela biblioteca XRayTorch, posteriormente fazendo o upload automático para o servidor, e exportando uma cópia desses *SR*s para a pasta *SR* local.
    -`analyze()`: Exporta um *.json* com o resultado das análises feito pela biblioteca XRayTorch para a pasta *results* local.
## Instruções
Para funcionamento e mais informações do funcionamento do servidor PACs OrthanC, assim como o script de Python, segue instruções e detalhes sobre a aplicação:
### 1°: Instalação do Docker e download ou `git clone` do repositório
Faça o download do [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/) e em seguida o download dos arquivos presentes neste repositório (`git clone` também é possível).
### 2°: Build da imagem
Através do seu terminal, ou pelo terminal presente no próprio *GUI* do Docker, primeiro localize o diretório onde está presente os arquivos deste repositório (ou onde foi clonado). Por exemplo:
  
    cd C:/Users/Voce/IC_MICLab
  
Em seguida, insira o seguinte comando: 

    docker build -t 'nomedaimagemescolhida' .

- `-t`: Abreviação para *tag*. Deve ser seguido pelo nome escolhido para imagem que o Docker irá criar

Não se esqueça do ` .` no final! A construção deve demorar cerca de 100 a 250segs. O terminal deve indicar a construção da imagem. 

### 3°: Run da imagem criada
Agora para o Docker iniciar o container com a imagem que criamos, devemos utilizar o seguinte comando:

    docker run -d -v X:\Users\caminho\para\pasta\SR:/etc/orthanc/SR -v X:\Users\caminho\para\pasta\results:/etc/orthanc/results --name 'nome' -p 8042:8042  --rm 'nomedaimagemescolhida'

Ou para versão simplificada, apenas:

    docker run -d --name 'nome' -p 8042:8042 --rm 'nomedaimagemescolhida'

- `-d`: Abreviação para *detached*. Permite rodar o container em segundo fundo, permitindo o uso do terminal.
- `-v`: Permite compartilhar arquivos gerados dentro do container para fora dele. Necessário para a função *analyze*, para salvar o arquivo *.json* que contém os resultados dos modelos pré-treinados. Sempre deve ser seguido pelo diretório que possui a pasta *results* seguido por */etc/orthanc/results* (definido pelo arquivo de configuração).
- `--name`: Nomeia o container, facilitando o uso posteriormente. Deve ser seguido por algum nome escolhido.
- `-p`: Mapeia ports entre o host e o container, permitindo acessar serviços do container fora dele. Deve ser seguido com a port do host:port do container.
- `--rm`: Remove a imagem e traços do container após utilizá-lo, liberando espaço (opcional).

A imagem deve estar funcionando. Para testar, pode utilizar `docker ps` para indicar o container que está em uso, assim como entrar em um localhost (a imagem configura a port 8042 automaticamente, assim, ficaria como: `localhost:8042`). Como já dito, será necessário inserir um usuário e uma senha para entrar no servidor OrthanC. Como default, nós temos usuário:senha como: `you:yourpassword`.

Todas estas configurações estão presentes no arquivo `configuration.json` presente no repositório, e podem ser modificadas a qualquer momento. O [site de OrthanC](https://orthanc.uclouvain.be/book/users/configuration.html) pode auxiliar na criação do arquivo de configuração específico desejado.

### 4°: Utilização do script Python
Primeiro, verifique se o diretório com o Dockerfile possui a pasta /scripts com o script de Python `script.py`, assim como uma pasta DICOM onde você deverá armazenar os arquivos DICOM que serão enviados ao servidor. Assim, posteriormente, com o container sendo utilizado, deve-se inserir o comando:

    docker exec -it 'nome' python /usr/local/bin/script.py
  
- `-it`: Abreviação para *interactive*. Permite interagir com o próprio shell do container através do terminal.
- `python`: Inicia o plugin Python da imagem. Deve ser seguido com o diretório, especificado no configuration.json, onde estará o script Python após o início do container.

Logo após este comando, espere um tempo e deverá aparecer a seguinte frase:

    Selecione uma opção:
    1. Enviar arquivos DICOM
    2. Analisar arquivos DICOM
    3. Criar e enviar arquivos SR DICOM
    4. Deletar todos os arquivos DICOM do servidor Orthanc
    5. Sair
    Digite o número da sua escolha: 

Após qualquer comando utilizado, aparecerão informações relevantes ao que foi escolhido. Após uma escolha, o programa voltará para essa tela inicial até que escolha a opção 5.

### 5°: Finalização do container
Para finalização do container, é necessário a utilização do comando:

    docker stop 'nome'

E deverá aparecer no terminal o 'nome' escolhido para imagem. Também é recomendado a utilização do comando:

    docker system prune -a -f

Para remoção de quaisquers arquivos ainda presentes no computador após a utilização do script. O comando *system prune* lista os itens a serem removidos, e `-a` e `-f` garantem que serão removidas quaisquer imagens não utilizadas e pula o prompt de confirmação, respectivamente.

## Dificuldades/Considerações
### 1) Configurar e rodar um PACs OrthanC, utilizando Docker.
Como as noções de Docker, imagens e containeres eram relativamente novas para mim, o processo de criação do Dockerfile para a configuração do servidor OrthanC foi relativamente longa. Nesta etapa, o [livro oficial para imagens](https://orthanc.uclouvain.be/book/users/docker.html) e a [página de configuração para o arquivo .json](https://orthanc.uclouvain.be/book/users/configuration.html) foram essenciais. No começo, o servidor local nem iniciava, e após, não tinha como logar. A utilização do [forum oficial do Docker](https://forums.docker.com/) também foi muito importante, pois lá recebi o direcionamento de outros programadores mais experientes.
### 2) Utilizar um script Python para enviar arquivos DICOM
Esta etapa foi relativamente mais simples, devido estar mais acostumado com a programação em Python. Porém, a utilização do REST API era nova, então foi necessário mais um processo de aprendizado. Um detalhe importante foi o aperfeiçoamento das função de upload, pois devido à outras funções do script, ela rotinamente enviava mais arquivos do que o necessário.
### 3) Utilizando os mesmos arquivos DICOM, computar os resultados de classificação de achados utilizando o modelo pré-treinado e instruções encontradas na seção "Get Started"  do README do TorchXRayVision. 
Nesta etapa ocorreu o erro comentado pelo professor Diedre no e-mail, onde a aplicação não funcionava devido a falta de um terceiro eixo necessário para conversão de uma imagem colorida para grayscale. Foi implementado a função que extrai o array de pixeis e normaliza automaticamente, implementada um código para lidar com os casos de arrays 2D e feito a conversão do número np.float32() para o float padrão do Python.
### 4) EXTRA: Criar um DICOM SR (Structured Report) para cada arquivo DICOM com os resultados do modelo, e enviar os DICOM SR para o PACS local OrthanC. Note que o DICOM SR deve ser do paciente/estudo/série correta.
Extensivamente a etapa mais díficil, onde diversos problemas foram encontrados durante toda a etapa, principalmente relacionados à parâmetros não preenchidos necessários como 'SOPClassUID', 'Dataset.is_little_endian', 'Dataset.is_implicit_VR', etc. De longe o maior problema foi a aparição de '*instace:null*' após conseguir fazer o upload dos *SR*s, correlacionada à uma criação errada dos SRs. Para identificar os parâmetros errados ou não preenchidos, utilizei de bibliotecas e toolkits como *dicom-validator* ou *dcmtk* para verificar as *tags* dos *SR*s criados.
