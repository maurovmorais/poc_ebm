from streamlit import json

from Verifai import Verifai
import lerArquivo as extrairTexto
from config import dicConfig
import excel
import os
import shutil
from prompt import prompt
import time
import json

def main():
    """
    Função principal para execução do processo de extração e preenchimento de dados.
    """
    # Chamar a função config para carregar as variáveis de ambiente
    var_dictConfig = dicConfig()

    # Atribui o prompt de descrição da tarefa a ser criada no VerifAI
    var_strDescription = prompt()

    # 1. Copiar template
    if not excel.copiar_template_projeto():
        print("Falha ao preparar o arquivo de extração.")
        return

    # 2. Buscar arquivos PDF na pasta processar
    var_strCaminhoRaiz = os.path.dirname(os.path.abspath(__file__))
    var_strPastaProcessar = os.path.join(var_strCaminhoRaiz, "arquivos", "processar")
    var_strPastaProcessado = os.path.join(var_strCaminhoRaiz, "arquivos", "processado")
    
    # Garante que a pasta processado existe
    if not os.path.exists(var_strPastaProcessado):
        os.makedirs(var_strPastaProcessado)

    var_listCaminhosPdfs = extrairTexto.buscar_arquivos_pdf(var_strPastaProcessar)
    
    if not var_listCaminhosPdfs:
        print(f"Nenhum arquivo PDF encontrado em: {var_strPastaProcessar}")
        return

    # Agrupar arquivos por nome da pessoa (Chave)
    var_dictGrupos = {}
    for var_strCaminhoPdf in var_listCaminhosPdfs:
        var_strNomeArquivo = os.path.basename(var_strCaminhoPdf).upper()
        
        # Identifica se é CCV ou MINUTA e limpa o nome para obter a chave
        var_strTipo = ""
        var_strChave = var_strNomeArquivo.replace(".PDF", "")
        
        if "CCV" in var_strNomeArquivo:
            var_strTipo = "CCV"
            var_strChave = var_strChave.replace("CCV", "")
        elif "MINUTA" in var_strNomeArquivo:
            var_strTipo = "MINUTA"
            var_strChave = var_strChave.replace("MINUTA", "")
        elif "MIN" in var_strNomeArquivo:
            var_strTipo = "MINUTA"
            var_strChave = var_strChave.replace("MIN", "")
            
        if var_strTipo:
            # Limpa espaços e caracteres especiais do nome para facilitar o agrupamento
            var_strChave = var_strChave.strip(" _-")
            
            if var_strChave not in var_dictGrupos:
                var_dictGrupos[var_strChave] = {"CCV": None, "MINUTA": None}
            
            var_dictGrupos[var_strChave][var_strTipo] = var_strCaminhoPdf

    # 3. Processar cada grupo (par de arquivos)
    for var_strChave, var_dictArquivos in var_dictGrupos.items():
        var_strPdfCCV = var_dictArquivos["CCV"]
        var_strPdfMin = var_dictArquivos["MINUTA"]

        if not var_strPdfCCV or not var_strPdfMin:
            print(f"Aviso: Par incompleto para '{var_strChave}'.")
            if var_strPdfCCV: print(f"  Faltando MINUTA para {var_strPdfCCV}")
            if var_strPdfMin: print(f"  Faltando CCV para {var_strPdfMin}")
            continue

        print(f"Processando par: {var_strChave}")
        
        var_listDadosExtraidosCCV = []
        var_listDadosExtraidosMin = []

        try:
            # Extração do CCV
            print(f"  Enviando CCV: {os.path.basename(var_strPdfCCV)}")
            var_intIdTarefaCCV = Verifai.criar_tarefa(arg_strCaminhoArquivo=var_strPdfCCV, arg_intLayout=396, arg_strDescription=var_strDescription)
            
            # Extração da MINUTA
            print(f"  Enviando MINUTA: {os.path.basename(var_strPdfMin)}")
            var_intIdTarefaMin = Verifai.criar_tarefa(arg_strCaminhoArquivo=var_strPdfMin, arg_intLayout=395, arg_strDescription=var_strDescription)

            if var_intIdTarefaCCV and var_intIdTarefaMin:
                # Captura resultados CCV
                var_dictResultadoCCV = None
                var_strStatusCCV = "processing"
                while var_strStatusCCV == "processing":
                    var_dictRes = Verifai.captura_infos_tarefa(arg_intIdTarefa=var_intIdTarefaCCV)
                    var_strStatusCCV = var_dictRes['status']
                    if var_strStatusCCV == "completed":
                        var_dictResultadoCCV = json.loads(var_dictRes['verification'])
                    time.sleep(2)
                
                # Captura resultados MINUTA
                var_dictResultadoMin = None
                var_strStatusMin = "processing"
                while var_strStatusMin == "processing":
                    var_dictRes = Verifai.captura_infos_tarefa(arg_intIdTarefa=var_intIdTarefaMin)
                    var_strStatusMin = var_dictRes['status']
                    if var_strStatusMin == "completed":
                        var_dictResultadoMin = json.loads(var_dictRes['verification'])
                    time.sleep(2)

                if var_dictResultadoCCV and var_dictResultadoMin:
                    print(f"  Dados CCV extraídos (keys): {list(var_dictResultadoCCV.keys())}")
                    print(f"  Dados Minuta extraídos (keys): {list(var_dictResultadoMin.keys())}")
                    var_listDadosExtraidosCCV.append(var_dictResultadoCCV)
                    var_listDadosExtraidosMin.append(var_dictResultadoMin)
                    
                    # 4. Preencher o Excel com os dados do par (mesma linha)
                    excel.preencher_dados_extracao(var_listDadosExtraidosCCV, var_listDadosExtraidosMin)
                    
                    # Move os arquivos para processados
                    for var_strPdf in [var_strPdfCCV, var_strPdfMin]:
                        var_strNome = os.path.basename(var_strPdf)
                        shutil.move(var_strPdf, os.path.join(var_strPastaProcessado, var_strNome))
                    print(f"Par {var_strChave} processado e movido com sucesso.")
                else:
                    print(f"Erro: Não foi possível obter resultados completos para {var_strChave}")
            else:
                print(f"Erro ao criar tarefas para {var_strChave}")

        except Exception as var_objErro:
            print(f"Erro durante o processamento do par {var_strChave}: {var_objErro}")

    print("Processo concluído.")


if __name__ == "__main__":
    main()
