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
- Dockerfile: Arquivo para construção de uma imagem. Deve ser utilizada em um terminal com a sintaxe `docker build -t "nomedaimagemescolhida" .`
- configuration.json: Arquivo essencial para configuração do servidor OrthanC. Nele estão denomeadas informações como as portas expostas assim como os usuários registrados (O default é `"you";"yourpassword"`)
