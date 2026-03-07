# Imports dos pacotes externos
import requests
import json
import os
import config

class Verifai:
    # Carrega as configurações do arquivo Config.py
    var_dictConfig = config.dicConfig()

    var_strToken            = var_dictConfig['token']
    var_strUrlRetornoTarefa = var_dictConfig['UrlRetornoTarefa']
    var_strUrlCriarTarefa   = var_dictConfig['UrlCriarTarefa']
    var_strLayout           = var_dictConfig['numLayout']
    var_strEmpresaIA        = var_dictConfig['EmpresaIA']
    var_strModeloIA         = var_dictConfig['ModeloIA']

    @classmethod
    def criar_tarefa(cls, arg_strCaminhoArquivo: str, arg_intLayout: int, arg_strDescription: str):
        """
        Cria a tarefa para que o verifAI faça a extração dos dados

        Parâmetros:
            arg_strCaminhoArquivo (str): caminho do arquivo
            arg_intLayout (int): número do layout do verifai
            arg_strDescription (str): descrição do layout

        Retorna:
            (str): número da tarefa
        """
    
        var_strUrl = cls.var_strUrlCriarTarefa
        headers = {"Authorization": f"Bearer {cls.var_strToken}",
                   }
        with open(arg_strCaminhoArquivo, 'rb') as f:
            files = {'files': (os.path.basename(arg_strCaminhoArquivo), f)}
            var_strResponse = requests.post(var_strUrl, headers=headers, data={
                "ia_company": "claudeai",
                "ia_model": "claude-sonnet-4-20250514",
                # "ia_company": "openai",
                # "ia_model": "gpt-4-turbo-2024-04-09",
                "layout": arg_intLayout,
                "project": 231,
                "priority": "medium",
                "image_model": "true",
                "description": arg_strDescription
            }, files=files)
        
        if var_strResponse.status_code == 200: # Status 200 indica que a tarefa foi criada com sucesso
            var_JsonResponse = var_strResponse.text
            var_JsonResponse = json.loads(var_JsonResponse)
            #Maestro.write_log(f"Criação da tarefa realizada com sucesso.")
            return var_JsonResponse['tasks'][0]['task']
        else:
            #Maestro.write_log(f"Não foi possível criar a tarefa no VerifAI: {var_JsonResponse.text}")
            return
    
    

    @classmethod
    def captura_infos_tarefa(cls, arg_intIdTarefa: int):
        
        # Monta a URL
        var_strUrl = cls.var_strUrlRetornoTarefa
        var_strUrl = var_strUrl.replace('{{idTarefa}}', str(arg_intIdTarefa))
        headers = {"Authorization": f"Bearer {cls.var_strToken}",
                   }
        
        var_strResponse = requests.get(url=var_strUrl, headers=headers)
        
        if var_strResponse.status_code == 200:
            # converte a resposta em JSON
            var_JsonResponse = var_strResponse.json()
            #Maestro.write_log(f"Informações da tarefa capturadas com sucesso.")
            return var_JsonResponse
        else:
            #Maestro.write_log(f"Erro na requisição: {var_strResponse.status_code}: {var_strResponse.text} ")
            raise Exception (f'Erro na requisição:{var_strResponse.status_code}')