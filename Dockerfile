# Puxando a imagem oficial OrthanC com suporte ao Python
FROM jodogne/orthanc-python

# Instalando pacotes necessários (como venv, pip)
USER root
RUN apt-get update && \
    apt-get install -y python3-venv python3-pip

# Criando o venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalando pacotes Python necessários
RUN pip install --upgrade pip && \
    pip install --no-cache-dir requests torchxrayvision torch torchvision pydicom==2.0 numpy

# Copia a configuração e as pastas necessárias para funcionamento
COPY configuration.json /etc/orthanc/configuration.json
COPY scripts/script.py /usr/local/bin/script.py
COPY DICOM /etc/orthanc/DICOM

# Expondo as portas necessárias
EXPOSE 8042

# Comando para iniciar o servidor PACs OrthanC
CMD ["/etc/orthanc/configuration.json"]