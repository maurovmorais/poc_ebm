def dicConfig():
    # Configurações do processo
    return {
        'NomeProcesso': 'Piloto_EBM',
        'CaminhoPastaRelatorios':'C:\\Gemini_CLI\\poc_ebm\\arquivos\\processar',
        'UrlRetornoTarefa':'https://api.t2verification.com.br/api/v1/tasks/{{idTarefa}}',
        'UrlCriarTarefa':'https://api.t2verification.com.br/api/v1/tasks/layout/',
        'numLayout': "",
        'EmpresaIA': 'claudeai',
        'ModeloIA': 'claude-sonnet-4-20250514',
        'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg4NjI4NzUwLCJpYXQiOjE3NzI5MDM5NTAsImp0aSI6IjE5MTVjZDJlODZjODRiYWI5MzRkYTc5NTYwNDQ4Nzg5IiwidG9rZW4iOiJjb21wYW55X2FwaSIsImNvbXBhbnlfaWQiOiI0OCIsImNyZWF0ZWRfYnkiOjE3MH0.o3iHqxPLXYaK-bB8arQHo_hFSDG8LbH233_RkNezsiM'# Insira seu token do VerifAI aqui
    }