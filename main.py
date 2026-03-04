from Verifai import Verifai
import lerArquivo as extrairTexto
import excel
import os
import shutil

def main():
    """
    Função principal para execução do processo de extração e preenchimento de dados.
    """
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

    # 3. Processar arquivos extraindo dados via Verifai
    for var_strCaminhoPdf in var_listCaminhosPdfs:
        var_strNomeArquivo = os.path.basename(var_strCaminhoPdf)
        var_strNomeArquivoUpper = var_strNomeArquivo.upper()
        print(f"Processando arquivo: {var_strNomeArquivoUpper}")

        # Listas temporárias para o arquivo atual
        var_listDadosExtraidosCCV = []
        var_listDadosExtraidosMin = []

        # Identifica o tipo do arquivo (CCV ou MINUTA)
        var_boolEhCCV = "CCV" in var_strNomeArquivoUpper
        var_boolEhMinuta = "MINUTA" in var_strNomeArquivoUpper or "MIN" in var_strNomeArquivoUpper

        if not var_boolEhCCV and not var_boolEhMinuta:
            print(f"Aviso: O arquivo {var_strNomeArquivoUpper} não possui 'CCV' ou 'MINUTA' no nome. Pulando...")
            continue

        try:  
            # Chama a criação da tarefa no Verifai
            var_intIdTarefa = Verifai.create_task(var_strCaminhoPdf)
            
            if var_intIdTarefa:
                # Aguarda e obtém o resultado da extração
                var_dictResultadoExtracao = Verifai.try_get_result(var_intIdTarefa)
                
                if var_dictResultadoExtracao:
                    if var_boolEhCCV:
                        var_listDadosExtraidosCCV.append(var_dictResultadoExtracao)
                    else:
                        var_listDadosExtraidosMin.append(var_dictResultadoExtracao)
                    
                    # 4. Preencher o Excel com os dados do arquivo atual (anexando)
                    excel.preencher_dados_extracao(var_listDadosExtraidosCCV, var_listDadosExtraidosMin)
                else:
                    print(f"Erro: Não foi possível obter o resultado para a tarefa {var_intIdTarefa}")
            else:
                print(f"Erro ao criar tarefa para o arquivo: {var_strNomeArquivoUpper}")

        except Exception as var_objErro:
            print(f"Erro durante o processamento do arquivo {var_strNomeArquivoUpper}: {var_objErro}")
        
        finally:
            # Move o arquivo para a pasta processado após a tentativa de processamento
            try:
                var_strCaminhoDestino = os.path.join(var_strPastaProcessado, var_strNomeArquivo)
                # Se o arquivo já existir no destino, removemos para evitar erro no move
                #if os.path.exists(var_strCaminhoDestino):
                #   os.remove(var_strCaminhoDestino)
                #shutil.move(var_strCaminhoPdf, var_strPastaProcessado)
                print(f"Arquivo movido para: {var_strPastaProcessado}")
            except Exception as var_objErroMove:
                print(f"Erro ao mover o arquivo {var_strNomeArquivo}: {var_objErroMove}")

    print("Processo concluído.")

if __name__ == "__main__":
    main()
