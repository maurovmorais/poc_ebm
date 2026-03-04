import shutil
import os
import openpyxl

def copiar_template_projeto() -> bool:
    """
    Copia o arquivo template.xlsx da raiz do projeto para um novo arquivo 
    chamado extraçao_dados.xlsx na mesma pasta.

    Returns:
        bool: Retorna True se a operação for bem-sucedida, False caso contrário.
    """
    var_strCaminhoRaiz = os.path.dirname(os.path.abspath(__file__))
    var_strArquivoTemplate = os.path.join(var_strCaminhoRaiz, "template.xlsx")
    var_strArquivoDestino = os.path.join(var_strCaminhoRaiz, "extraçao_dados.xlsx")

    var_boolSucesso = False

    try:
        # Verifica se o template existe antes de copiar
        if os.path.exists(var_strArquivoTemplate):
            shutil.copy2(var_strArquivoTemplate, var_strArquivoDestino)
            print(f"Arquivo copiado com sucesso para: {var_strArquivoDestino}")
            var_boolSucesso = True
        else:
            print(f"Erro: Arquivo template não encontrado em {var_strArquivoTemplate}")
            
    except Exception as var_objErro:
        print(f"Ocorreu um erro ao copiar o arquivo: {var_objErro}")

    return var_boolSucesso

def preencher_dados_extracao(arg_listDadosCCV: list, arg_listDadosMin: list) -> bool:
    """
    Preenche o arquivo extraçao_dados.xlsx com as informações extraídas.
    Mapeia as colunas baseadas nos sufixos _CCV e _Min para os respectivos dados.
    Também realiza a comparação automática para as colunas de Status.

    Args:
        arg_listDadosCCV (list): Lista de dicionários com dados do CCV.
        arg_listDadosMin (list): Lista de dicionários com dados do Min.

    Returns:
        bool: True se o preenchimento ocorrer sem erros, False caso contrário.
    """
    var_strCaminhoRaiz = os.path.dirname(os.path.abspath(__file__))
    var_strArquivoExcel = os.path.join(var_strCaminhoRaiz, "extraçao_dados.xlsx")
    var_boolSucesso = False

    if not os.path.exists(var_strArquivoExcel):
        print(f"Erro: Arquivo {var_strArquivoExcel} não encontrado.")
        return False

    try:
        var_objWorkbook = openpyxl.load_workbook(var_strArquivoExcel)
        
        for var_strNomeAba in var_objWorkbook.sheetnames:
            var_objSheet = var_objWorkbook[var_strNomeAba]
            
            # Identifica os cabeçalhos (primeira linha)
            var_listCabecalhos = [cell.value for cell in var_objSheet[1]]
            
            # Localiza a primeira linha vazia (depois do cabeçalho)
            var_intUltimaLinha = var_objSheet.max_row
            # Se a max_row for 1 (apenas cabeçalho), a próxima é a 2.
            # Se a planilha estiver totalmente limpa, o max_row também pode retornar 1.
            var_intPrimeiraLinhaVazia = var_intUltimaLinha + 1 if var_intUltimaLinha > 1 else 2

            # Assume que a quantidade de linhas a preencher é a maior entre as duas listas
            var_intTotalNovasLinhas = max(len(arg_listDadosCCV), len(arg_listDadosMin))
            
            for var_intIndex in range(var_intTotalNovasLinhas):
                var_intLinhaExcel = var_intPrimeiraLinhaVazia + var_intIndex
                var_dictDadosCCV = arg_listDadosCCV[var_intIndex] if var_intIndex < len(arg_listDadosCCV) else {}
                var_dictDadosMin = arg_listDadosMin[var_intIndex] if var_intIndex < len(arg_listDadosMin) else {}

                for var_intColIdx, var_strColuna in enumerate(var_listCabecalhos, 1):
                    if not var_strColuna:
                        continue
                    
                    # Preenchimento de dados CCV e Min
                    if var_strColuna.endswith("_CCV"):
                        var_strChave = var_strColuna.replace("_CCV", "")
                        var_objSheet.cell(row=var_intLinhaExcel, column=var_intColIdx).value = var_dictDadosCCV.get(var_strChave, "")
                    elif var_strColuna.endswith("_Min"):
                        var_strChave = var_strColuna.replace("_Min", "")
                        var_objSheet.cell(row=var_intLinhaExcel, column=var_intColIdx).value = var_dictDadosMin.get(var_strChave, "")
                    
                    # Lógica para as colunas de Status
                    elif "Status" in var_strColuna or "status" in var_strColuna:
                        # Identifica a coluna anterior para comparar
                        var_strColMin = var_listCabecalhos[var_intColIdx - 2] if var_intColIdx > 1 else ""
                        var_strColCCV = var_listCabecalhos[var_intColIdx - 3] if var_intColIdx > 2 else ""
                        
                        if var_strColMin.endswith("_Min") and var_strColCCV.endswith("_CCV"):
                            var_strValMin = str(var_objSheet.cell(row=var_intLinhaExcel, column=var_intColIdx - 1).value or "").strip().upper()
                            var_strValCCV = str(var_objSheet.cell(row=var_intLinhaExcel, column=var_intColIdx - 2).value or "").strip().upper()
                            
                            if var_strValMin == var_strValCCV and var_strValMin != "":
                                var_objSheet.cell(row=var_intLinhaExcel, column=var_intColIdx).value = "OK"
                            elif var_strValMin != var_strValCCV:
                                var_objSheet.cell(row=var_intLinhaExcel, column=var_intColIdx).value = "Divergente"

        var_objWorkbook.save(var_strArquivoExcel)
        print("Dados preenchidos com sucesso no Excel.")
        var_boolSucesso = True

    except Exception as var_objErro:
        print(f"Erro ao preencher o Excel: {var_objErro}")
    
    return var_boolSucesso
