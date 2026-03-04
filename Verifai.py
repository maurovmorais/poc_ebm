from datetime import datetime
from time import sleep
import requests
import json
import os

class Verifai:
    """
    Classe contendo os métodos para manipulação do Verifai
    
    Parâmetros:
 
    Retorna:
    """
    '''
    var_strUrlCreateTask = InitAllSettings.var_dictConfig['ONEINNOVATION_ENDPOINT_CREATE_TASK']
    var_strUrlGetTask = InitAllSettings.var_dictConfig['ONEINNOVATION_ENDPOINT_GET_TASK']
    var_strIaCompany = InitAllSettings.var_dictConfig['ONEINNOVATION_IACOMPANY_VERIFAI_GEMINI']
    var_strProject = InitAllSettings.var_dictConfig['ONEINNOVATION_PROJECT_VERIFAI']
    var_strLayout = InitAllSettings.var_dictConfig['ONEINNOVATION_LAYOUT_VERIFAI']
    '''
    VAR_STRTOKEN = ""

    @classmethod
    def create_task(cls, arg_strPathFile: str):
        """
        Cria a tarefa para que o verifAI faça a extração dos dados

        Parâmetros:
            - arg_strPathFile (str): caminho do arquivo

        Retorna:
            (str): Número da tarefa
        """

        # 790      Criar task verifAi
        #if(InitAllSettings.var_dictConfig["AtivarT2CTracker"].upper() == "SIM"):
        #   T2CTracker.next_step(arg_intStep=790)
     
        var_strIaModel = InitAllSettings.var_dictConfig['ONEINNOVATION_IAMODEL_VERIFAI_GEMINI']
        
        headers = {"Authorization": f"Bearer {cls.VAR_STRTOKEN}"}

        # Realiza a requisição para processar o arquivo de acordo com o layout
        try:
            with open(arg_strPathFile, 'rb') as f:
                files = {'files': (os.path.basename(arg_strPathFile), f)}
                var_strResponse = requests.post(cls.var_strUrlCreateTask, headers=headers, data={
                    "ia_company": cls.var_strIaCompany,
                    "ia_model": var_strIaModel,
                    "layout": cls.var_strLayout,
                    "project": cls.var_strProject,
                    "priority": "medium",
                    "image_model": "true"
                }, files=files, timeout=60)
        except requests.exceptions.Timeout:
            print(f"Não foi possível criar a tarefa no VerifAI: Timeout na requisição")
            return
        
        if var_strResponse.status_code == 200: # Status 200 indica que a tarefa foi criada com sucesso
            var_JsonResponse = var_strResponse.text
            var_JsonResponse = json.loads(var_JsonResponse)
            print(f"Criação da tarefa realizada com sucesso.")
            return var_JsonResponse['tasks'][0]['task']
        else:
            print(f"Não foi possível criar a tarefa no VerifAI: {var_JsonResponse.text}")
            return
        
    
    @classmethod
    def get_task_info(cls, arg_intIdTask: int):
        """
        Pega as informações atuais da tarefa
        
        Parâmetros:
           - arg_intIdTask (int): Id da tarefa para resgate da informação
        
        Retorna:
           - json: Retorna um Json contendo as informações da tarefa
        """
        
        var_strUrlGetTask = cls.var_strUrlGetTask.replace('id', str(arg_intIdTask))
        headers = {"Authorization": f"Bearer {cls.VAR_STRTOKEN}"}
        var_strResponse = requests.get(url=var_strUrlGetTask, headers=headers)
        
        if var_strResponse.status_code == 200:
            var_JsonResponse = var_strResponse.json()
            print(f"Informações da tarefa capturadas com sucesso.")
            return var_JsonResponse
        else:
            print(f"Erro na requisição: {var_strResponse.status_code}: {var_strResponse.text} ")
            raise Exception (f'Erro na requisição:{var_strResponse.status_code}')
        

    @classmethod
    def verify_status(cls, arg_intIdTarefa: int):
        """
        Função para verificar o status da tarefa do verifAI

        Args:
           - arg_intIdTarefa (int): id da tarefa

        Retorna:
            - dict: Dicionário com o resultado
        """        
        timeout = 120
        var_dtmInicio = datetime.now()
        var_intDiferencaTempo = 0
        var_dictDadosTarefa = Verifai.get_task_info(arg_intIdTarefa)
        
        print(f'Iniciando verificação de status da tarefa: {arg_intIdTarefa}')
            
        while var_dictDadosTarefa['status'] == 'processing' and var_intDiferencaTempo < timeout:
            var_dtmAgora = datetime.now()
            var_intDiferencaTempo = abs((var_dtmAgora - var_dtmInicio).total_seconds())
            sleep(15)
            var_dictDadosTarefa = Verifai.get_task_info(arg_intIdTarefa)
        
        if var_dictDadosTarefa['status'] == 'processing':
            print(f'Demora de resposta do VerifAI. Não foi possível extrair as informações do documento: {arg_intIdTarefa}')
            raise Exception('RPA _ FALHA SISTEMA - demora de resposta do VerifAI. Não foi possível extrair as informações do documento.')
        
        return var_dictDadosTarefa
    

    def get_task_result(arg_intIdTarefa: int):
        """
        Função para capturar o resultado da tarefa conforme status

        Args:
           - arg_intIdTarefa (int): id da tarefa

        Retorna:
           - str: Dicionário ou None
        """      

        # 646      CAPTURA RETORNO VERIFAI
        #if(InitAllSettings.var_dictConfig["AtivarT2CTracker"].upper() == "SIM"):
        #   T2CTracker.next_step(arg_intStep=646)

        print(f'Verificando status da tarefa {arg_intIdTarefa}.')

        # Captura o status da tarefa
        var_dictTarefa = Verifai.verify_status(arg_intIdTarefa)
        
        # Verifica o status da tarefa e retorna os dados ou erro
        if var_dictTarefa['status'] == 'completed':
            return json.loads(var_dictTarefa['verification'])
        
        elif var_dictTarefa['errors']:
            print(f'RPA _ FALHA SISTEMA _ Não foi possível extrair as informações do documento: {var_dictTarefa["errors"]}')
            raise Exception (f'RPA _ FALHA SISTEMA _ Não foi possível extrair as informações do documento: {var_dictTarefa['errors']}')
        
        else:

            # 750      Falha na leitura VerifAI
            #if(InitAllSettings.var_dictConfig["AtivarT2CTracker"].upper() == "SIM"):
            #   T2CTracker.next_step(arg_intStep=750)
            
            return None
        
    @classmethod
    def try_get_result(cls, arg_intIdTarefa: int,arg_intMaxTentativas:int = 3):

        """
        Função para tentar capturar o resultado da tarefa até 3 vezes

        Args:
           - arg_intIdTarefa (int): Id da tarefa
           - arg_intTentativa (int): Número máximo de tentativas (default=3)
           - arg_strToken: Token de autenticação

        Retorna:
           - dict: Dicionário com o resultado
        """      

        print(f'Tentando capturar o resultado da tarefa {arg_intIdTarefa}.')
        
        for var_intTentativa in range(1, arg_intMaxTentativas + 1):
            try:
                # Tenta obter o resultado da tarefa
                return cls.get_task_result(arg_intIdTarefa)
            except Exception as err:
                # Última tentativa falhou, lança a exceção
                if var_intTentativa == arg_intMaxTentativas:

                    # 750      Falha na leitura VerifAI
                    #if(InitAllSettings.var_dictConfig["AtivarT2CTracker"].upper() == "SIM"):
                    #   T2CTracker.next_step(arg_intStep=750)

                    raise Exception(f'Falha ao obter retorno do VerifAI após {arg_intMaxTentativas} tentativas. Motivo: {str(err)}')
            
                # Aguarda antes de tentar novamente
                sleep(5)


    def obter_company_model(arg_strNomeAmigavel: str, arg_strToken: str):
        """
        Consulta o endpoint do Verifai e retorna IACompany e IAModel
        filtrando pelo nome amigável (label).

        Parâmetros:
            - nome_amigavel (str): Nome amigável do modelo IA.
            - arg_strToken (str): Token de autenticação
        
        Retorna:
            dict ou None: Dicionário com IACompany, IAModel e ImageModel ou None se não encontrar.

        """
        
        url = "https://api.t2verification.com.br/api/v1/ais/"

        headers = {
        "Authorization": f"Bearer {arg_strToken}",
        "Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            lista_modelos = response.json()

            for item in lista_modelos:
                if item.get("label") == arg_strNomeAmigavel:
                    company = item["value"].get("company")
                    model = item["value"].get("model")
                    image_model = item["value"].get("image_model")

                    return {
                        "IACompany": company,
                        "IAModel": model,
                        "ImageModel": image_model
                    }

            return None  # Não encontrou o modelo

        except Exception as e:
            print(f"Erro ao consultar modelos IA: {e}")
            return None


    
    