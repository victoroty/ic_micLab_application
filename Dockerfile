# Utilização da imagem base oficial de OrthanC
FROM jodogne/orthanc-python

# Copiando o arquivo de configuração .json, essencial para funcionamento do servidor PACs
COPY configuration.json /etc/configuration.json

# Expondo as portas necessárias (no padrão DICOM, as portas 8042 e 8043 são utilizadas)
EXPOSE 8042
EXPOSE 8043

# Comando para iniciar o servidor PACs OrthanC
CMD ["/etc/configuration.json"]