import os

def buscar_arquivos_pdf(arg_strCaminhoPasta: str) -> list:
    """
    Busca todos os arquivos com extensão .pdf no diretório especificado.

    Args:
        arg_strCaminhoPasta (str): O caminho completo da pasta onde os arquivos serão buscados.

    Returns:
        list: Uma lista contendo os caminhos completos de todos os arquivos .pdf encontrados.
    """
    var_listCaminhosCompletos = []

    # Verifica se o diretório existe antes de tentar listar
    if os.path.exists(arg_strCaminhoPasta):
        for var_strRaiz, var_listDiretorios, var_listArquivos in os.walk(arg_strCaminhoPasta):
            for var_strArquivo in var_listArquivos:
                if var_strArquivo.lower().endswith('.pdf'):
                    var_strCaminhoCompleto = os.path.abspath(os.path.join(var_strRaiz, var_strArquivo))
                    var_listCaminhosCompletos.append(var_strCaminhoCompleto)

    return var_listCaminhosCompletos
