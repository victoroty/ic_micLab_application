import os
import io
import shutil
import json
import time
import warnings
import requests
import torch
import torchvision
import torchxrayvision as xrv
from numpy import ndarray
from torchxrayvision.utils import normalize
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import generate_uid
from pydicom.uid import UID

# Configuração
ORTHANC_URL = 'http://localhost:8042'
DICOM_DIR = '/etc/orthanc/DICOM'  # Diretório onde os arquivos DICOM estão localizados no container
ORTHANC_USERNAME = 'you'           # Substitua pelo seu nome de usuário real
ORTHANC_PASSWORD = 'yourpassword'  # Substitua pela sua senha real

def read_xray_dcm(path: os.PathLike) -> ndarray:
    """Lê um arquivo DICOM e converte para um array numpy

    Args:
        path (PathLike): caminho para o arquivo DICOM

    Retorna:
        ndarray: imagem 2D em escala de cinza para uma imagem DICOM, escalada entre -1024 e 1024
    """

    # Obtém o array de pixels
    ds = pydicom.dcmread(path, force=True)

    # Verifica se a interpretação fotométrica é suportada
    if ds.PhotometricInterpretation not in ['MONOCHROME1', 'MONOCHROME2']:
        raise NotImplementedError(f'Interpretação fotométrica `{ds.PhotometricInterpretation}` ainda não é suportada.')

    data = ds.pixel_array
    
    # LUT para visualização amigável
    data = pydicom.pixel_data_handlers.util.apply_voi_lut(data, ds, index=0)

    # `MONOCHROME1` tem uma visão invertida; ossos são pretos; fundo é branco
    if ds.PhotometricInterpretation == "MONOCHROME1":
        warnings.warn(f"Convertendo MONOCHROME1 para MONOCHROME2 para o arquivo: {path}.")
        data = data.max() - data

    # Normaliza os dados para [-1024, 1024]
    data = normalize(data, data.max())
    return data

def upload_dicom_files():
    # Verifica se o diretório DICOM existe
    if not os.path.isdir(DICOM_DIR):
        print(f"O diretório {DICOM_DIR} não existe.")
        return

    dicom_files = []

    # Percorre todos os subdiretórios para encontrar arquivos DICOM
    for root, dirs, files in os.walk(DICOM_DIR):
        for file in files:
            if file.endswith(".dcm"):  # Garante que seja um arquivo DICOM
                file_path = os.path.join(root, file)

                try:
                    ds = pydicom.dcmread(file_path, force=True)
                    dicom_files.append(file_path)
                
                except Exception as e:
                    print(f"Falha ao ler o arquivo DICOM {file_path}: {e}")

    # Verifica se algum arquivo DICOM foi encontrado
    if not dicom_files:
        print(f"O diretório {DICOM_DIR} não contém arquivos DICOM para upload.")
        return

    # Faz o upload de cada arquivo DICOM válido
    for file_path in dicom_files:
        print(f"Enviando {file_path}...")

        with open(file_path, 'rb') as file_data:
            response = requests.post(
                f'{ORTHANC_URL}/instances',
                files={'file': file_data},
                auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD)  # Inclui autenticação
            )
            if response.status_code == 200:
                print(f"Upload bem-sucedido de {os.path.basename(file_path)}")
            else:
                print(f"Falha no upload de {os.path.basename(file_path)}: {response.status_code} {response.text}")

def delete_all_dicom_files():
    # Obtém uma lista de todas as instâncias (arquivos DICOM) no servidor
    response = requests.get(f'{ORTHANC_URL}/instances', auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
    
    if response.status_code != 200:
        print(f"Falha ao recuperar instâncias: {response.status_code} {response.text}")
        return
    
    instance_ids = response.json()
    
    if not instance_ids:
        print("Nenhum arquivo DICOM encontrado no servidor.")
        return

    # Deleta cada instância
    for instance_id in instance_ids:
        delete_response = requests.delete(f'{ORTHANC_URL}/instances/{instance_id}', auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD))
        if delete_response.status_code == 200:
            print(f"Instância {instance_id} deletada com sucesso")
        else:
            print(f"Falha ao deletar instância {instance_id}: {delete_response.status_code} {delete_response.text}")

def analyze_dicom_files():
    # Prepara o modelo e a transformação
    model = xrv.models.DenseNet(weights="densenet121-res224-all")
    transform = torchvision.transforms.Compose([
        xrv.datasets.XRayCenterCrop(),
        xrv.datasets.XRayResizer(224)
    ])
    
    dicom_files = []

    # Percorre todos os subdiretórios para encontrar arquivos DICOM
    for root, dirs, files in os.walk(DICOM_DIR):
        for file in files:
            if file.endswith(".dcm"):
                file_path = os.path.join(root, file)
                dicom_files.append(file_path)

    # Verifica se algum arquivo DICOM foi encontrado
    if not dicom_files:
        print(f"O diretório {DICOM_DIR} não contém arquivos DICOM.")
        return

    results = {}

    for dicom_file in dicom_files:
        # Lê e converte DICOM diretamente usando read_xray_dcm
        img_array = read_xray_dcm(dicom_file)

        # Ajusta a normalização
        img = np.clip(img_array, -1024, 1024)  # Garante que os valores estejam dentro do intervalo
        img = ((img + 1024) / 2048) * 255  # Normaliza para a faixa de 0-255

        # Converte para canal único, se necessário
        if img.ndim == 2:
            img = img[None, ...]  # Adiciona uma dimensão de canal único
        else:
            img = img.mean(0, keepdims=True)  # Lida com imagem multi-canal, fazendo média sobre os canais

        # Prepara a imagem
        img = xrv.datasets.normalize(img, 255)
        img = transform(img)
        img = torch.from_numpy(img)
        
        # Processa a imagem
        outputs = model(img[None, ...])
        result = dict(zip(model.pathologies, outputs[0].detach().numpy()))

        # Converte os resultados np.float32 para float do Python para facilitar a leitura
        results[os.path.basename(dicom_file)] = {k: float(v) for k, v in result.items()}

    # Exibe os resultados no terminal
    for dicom_file, result in results.items():
        print(f"Arquivo: {dicom_file}")
        for pathology, score in result.items():
            print(f"  {pathology}: {score:.4f}")

def create_dicom_sr_for_files():
    """Cria arquivos DICOM SR para imagens DICOM existentes no diretório DICOM e os envia diretamente para o servidor Orthanc."""

    # Prepara o modelo e a transformação
    model = xrv.models.DenseNet(weights="densenet121-res224-all")
    transform = torchvision.transforms.Compose([
        xrv.datasets.XRayCenterCrop(),
        xrv.datasets.XRayResizer(224)
    ])

    # Itera através dos arquivos DICOM
    for root, dirs, files in os.walk(DICOM_DIR):
        for file in files:
            if file.endswith(".dcm"):
                dicom_file_path = os.path.join(root, file)

                try:
                    # Lê o arquivo DICOM original
                    ds = pydicom.dcmread(dicom_file_path, force=True)

                    # Verifica se o arquivo já é um SR, caso contrário, procede
                    if ds.SOPClassUID.startswith("1.2.840.10008.5.1.4.1.1.88"):
                        continue  # Pula arquivos SR existentes

                    # Cria um novo dataset DICOM SR
                    sr_ds = Dataset()

                    # Meta Header
                    sr_ds.file_meta = Dataset()
                    sr_ds.file_meta.MediaStorageSOPClassUID = UID('1.2.840.10008.5.1.4.1.1.88')
                    sr_ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
                    sr_ds.file_meta.TransferSyntaxUID = UID('1.2.840.10008.1.2.1')
                    sr_ds.file_meta.ImplementationClassUID = UID('1.2.40.0.13.1.1.1')
                    sr_ds.file_meta.ImplementationVersionName = 'dcm4che-1.4.38'
                    sr_ds.file_meta.FileMetaInformationGroupLength = len(sr_ds.file_meta)

                    # Dataset
                    sr_ds.SOPClassUID = UID('1.2.840.10008.5.1.4.1.1.88')
                    sr_ds.SOPInstanceUID = sr_ds.file_meta.MediaStorageSOPInstanceUID
                    sr_ds.Modality = 'SR'
                    sr_ds.PatientName = ds.PatientName
                    sr_ds.PatientID = ds.PatientID
                    sr_ds.StudyInstanceUID = ds.StudyInstanceUID
                    sr_ds.SeriesInstanceUID = ds.SeriesInstanceUID
                    sr_ds.StudyDate = ds.get('StudyDate', '')
                    sr_ds.StudyTime = ds.get('StudyTime', '')
                    sr_ds.SeriesDate = ds.get('SeriesDate', '')
                    sr_ds.SeriesTime = ds.get('SeriesTime', '')
                    sr_ds.ContentDate = ds.get('ContentDate', '')
                    sr_ds.ContentTime = ds.get('ContentTime', '')
                    sr_ds.AccessionNumber = ds.get('AccessionNumber', '')
                    sr_ds.StudyDescription = ds.get('StudyDescription', '')
                    sr_ds.SeriesDescription = ds.get('SeriesDescription', '')
                    sr_ds.ProtocolName = ds.get('ProtocolName', '')
                    sr_ds.PerformingPhysicianName = ds.get('PerformingPhysicianName', '')
                    sr_ds.ReferringPhysicianName = ds.get('ReferringPhysicianName', '')

                    # Adiciona SeriesNumber e InstanceNumber do DICOM original
                    sr_ds.SeriesNumber = ds.get('SeriesNumber', '')
                    sr_ds.InstanceNumber = ds.get('InstanceNumber', '')

                    # Define a codificação VR como implícita, que é o padrão para muitos arquivos DICOM
                    sr_ds.is_implicit_VR = False
                    sr_ds.is_little_endian = True

                    # Realiza a análise para o arquivo DICOM atual
                    img_array = read_xray_dcm(dicom_file_path)
                    img = np.clip(img_array, -1024, 1024)
                    img = ((img + 1024) / 2048) * 255
                    img = img[None, ...] if img.ndim == 2 else img.mean(0, keepdims=True)
                    img = xrv.datasets.normalize(img, 255)
                    img = transform(img)
                    img = torch.from_numpy(img)
                    outputs = model(img[None, ...])
                    result = dict(zip(model.pathologies, outputs[0].detach().numpy()))

                    # Armazena o resultado no SR
                    sr_ds.ConceptNameCodeSequence = [Dataset()]
                    sr_ds.ConceptNameCodeSequence[0].CodeValue = '1111'
                    sr_ds.ConceptNameCodeSequence[0].CodingSchemeDesignator = 'DCM'
                    sr_ds.ConceptNameCodeSequence[0].CodeMeaning = 'Resultado da Análise'

                    sr_ds.ContentSequence = []
                    for pathology, value in result.items():
                        item = Dataset()
                        item.ConceptNameCodeSequence = [Dataset()]
                        item.ConceptNameCodeSequence[0].CodeValue = pathology
                        item.ConceptNameCodeSequence[0].CodingSchemeDesignator = 'DCM'
                        item.ConceptNameCodeSequence[0].CodeMeaning = pathology
                        item.NumericValue = float(value)
                        sr_ds.ContentSequence.append(item)

                    # Salva o SR em um buffer em memória
                    buffer = io.BytesIO()
                    sr_ds.save_as(buffer)
                    buffer.seek(0)

                    # Envia o SR para o servidor Orthanc
                    print(f"Enviando SR para Orthanc...")
                    response = requests.post(
                        f'{ORTHANC_URL}/instances',
                        files={'file': buffer},
                        auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD)  # Inclui autenticação
                    )

                    if response.status_code == 200:
                        print(f"Upload bem-sucedido de {os.path.basename(dicom_file_path)}")
                    else:
                        print(f"Falha no upload de {os.path.basename(dicom_file_path)}: {response.status_code} {response.text}")

                except Exception as e:
                    print(f"Falha ao criar e enviar DICOM SR para {dicom_file_path}: {e}")

def main():
    while True:
        print("\nSelecione uma opção:")
        print("1. Enviar arquivos DICOM")
        print("2. Analisar arquivos DICOM")
        print("3. Criar SR DICOM para arquivos existentes")
        print("4. Deletar todos os arquivos DICOM do servidor Orthanc")
        print("5. Sair")
        
        choice = input("Digite o número da sua escolha: ")
        
        if choice == '1':
            upload_dicom_files()
        elif choice == '2':
            analyze_dicom_files()
        elif choice == '3':
            create_dicom_sr_for_files()
        elif choice == '4':
            delete_all_dicom_files()
        elif choice == '5':
            print("Saindo...")
            break
        else:
            print("Escolha inválida. Tente novamente.")

if __name__ == '__main__':
    main()
