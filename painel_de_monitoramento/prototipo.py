import os
import requests
import json
import time
import matplotlib.pyplot as plt
from datetime import datetime
from selenium import webdriver

# Variável global para armazenar o ID da guia
id_guia_html = None

# Inicializar o driver do navegador
driver = webdriver.Chrome()  # Você pode precisar ajustar o caminho do driver para o seu ambiente


# Função para obter e salvar dados
def obter_e_salvar_dados():
    url = "http://192.168.1.113/"  # Substitua pela URL correta

    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()

            if dados:
                primeiro_nome_chave = next(iter(dados))
                nome_pasta = primeiro_nome_chave
                nome_arquivo = f"{nome_pasta}/{primeiro_nome_chave}.txt"

                if not os.path.exists(nome_pasta):
                    os.makedirs(nome_pasta)

                registros = dados[primeiro_nome_chave]
                registros_filtrados = [registro for registro in registros if
                                       registro.get("dataHora", "") != "1/1/1970" and all(registro.values())]

                if registros_filtrados:
                    with open(nome_arquivo, "a+", encoding="utf-8") as file:
                        file.seek(0)
                        content = file.read()

                        if content:
                            try:
                                content = json.loads(content)
                            except json.JSONDecodeError:
                                content = []

                        content = [dict(t) for t in {tuple(d.items()) for d in content}]
                        content.extend(registros_filtrados)

                        file.seek(0)
                        file.truncate(0)
                        file.write(json.dumps(content, ensure_ascii=False, indent=2))
                        file.write("\n")

                    print(f"Dados salvos com sucesso em {nome_arquivo}")
                    return nome_arquivo
        else:
            print("Falha ao obter os dados. Código de status:", response.status_code)
    except requests.RequestException as e:
        print("Erro na requisição:", e)


# Função para plotar gráficos de temperatura, batimentos e situação do paciente
def plotar_graficos(nome_arquivo):
    with open(nome_arquivo, "r", encoding="utf-8") as file:
        dados = file.read()

        if dados:
            dados = json.loads(dados)
        else:
            dados = []

    dados = [dict(t) for t in {tuple(d.items()) for d in dados}]

    dados_temperatura = sorted(dados, key=lambda x: datetime.strptime(x['dataHora'], '%d/%m/%Y %H:%M:%S'))
    dados_batimentos = sorted(dados, key=lambda x: datetime.strptime(x['dataHora'], '%d/%m/%Y %H:%M:%S'))
    dados_situacao = sorted(dados, key=lambda x: datetime.strptime(x['dataHora'], '%d/%m/%Y %H:%M:%S'))

    step = max(len(dados) // 20, 1)
    datas_temperatura = [registro['dataHora'] for registro in dados_temperatura[::step]]
    datas_batimentos = [registro['dataHora'] for registro in dados_batimentos[::step]]
    datas_situacao = [registro['dataHora'] for registro in dados_situacao[::step]]

    temperaturas = [float(registro['temperatura']) for registro in dados_temperatura[:len(datas_temperatura)]]
    batimentos = [float(registro['batimentos']) for registro in dados_batimentos[:len(datas_batimentos)]]
    situacoes = [registro['situacao'] for registro in dados_situacao[:len(datas_situacao)]]

    # Plotar gráfico de temperatura
    plt.figure(figsize=(25, 12))
    plt.plot(datas_temperatura, temperaturas, marker='o')
    plt.title('Variação da Temperatura ao Longo do Tempo')
    plt.xlabel('Data e Hora')
    plt.ylabel('Temperatura (°C)')
    plt.xticks(rotation=45, ha='right')

    nome_arquivo_grafico_temperatura = f"{nome_arquivo.replace('.txt', '_grafico_temperatura.png')}"
    plt.savefig(nome_arquivo_grafico_temperatura)

    plt.tight_layout()

    # Plotar gráfico de batimentos
    plt.figure(figsize=(25, 12))
    plt.plot(datas_batimentos, batimentos, marker='o', color='red')
    plt.title('Variação dos Batimentos ao Longo do Tempo')
    plt.xlabel('Data e Hora')
    plt.ylabel('Batimentos Cardíacos')
    plt.xticks(rotation=45, ha='right')

    nome_arquivo_grafico_batimentos = f"{nome_arquivo.replace('.txt', '_grafico_batimentos.png')}"
    plt.savefig(nome_arquivo_grafico_batimentos)

    plt.tight_layout()

    # Plotar gráfico de situação do paciente
    plt.figure(figsize=(25, 12))
    plt.plot(datas_situacao, situacoes, marker='o', color='green')
    plt.title('Variação da Situação do Paciente ao Longo do Tempo')
    plt.xlabel('Data e Hora')
    plt.ylabel('Situação do Paciente')
    plt.xticks(rotation=45, ha='right')

    nome_arquivo_grafico_situacao = f"{nome_arquivo.replace('.txt', '_grafico_situacao.png')}"
    plt.savefig(nome_arquivo_grafico_situacao)

    plt.tight_layout()


# Função para abrir a página HTML
def abrir_pagina_html():
    global id_guia_html  # Utiliza a variável global

    nome_pagina_html = "prototipo.html"

    # Verificar se a página HTML existe, senão, criar
    if not os.path.exists(nome_pagina_html):
        with open(nome_pagina_html, "w", encoding="utf-8") as html_file:
            html_file.write(
                """
                <html>
                    <head>
                        <title>Protótipo</title>
                        <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
                        <link rel="stylesheet" href="https://code.getmdl.io/1.3.0/material.indigo-pink.min.css">
                        <script defer src="https://code.getmdl.io/1.3.0/material.min.js"></script>
                        <style>
                            body {
                                margin: 0;
                                padding: 0;
                                overflow: hidden;
                            }
                            .mdl-layout__header {
                                position: fixed;
                                width: 100%;
                                z-index: 1000;
                            }
                            .mdl-layout__content {
                                margin-top: 64px;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                overflow: auto; /* Adicionado overflow para permitir rolar a tabela */
                            }
                            .mdl-data-table {
                                width: 100%;
                            }
                        </style>
                    </head>
                    <body class="mdl-color--grey-100">
                        <div class="mdl-layout mdl-js-layout">
                            <header class="mdl-layout__header mdl-layout__header--scroll mdl-color--primary">
                                <div class="mdl-layout-icon"></div>
                                <div class="mdl-layout__header-row">
                                    <span class="mdl-layout-title">Dados do Protótipo</span>
                                </div>
                            </header>
                            <main class="mdl-layout__content">
                                <h4 class="mdc-typography">Gráficos Disponíveis</h4>
                                <a href="#" id="linkGraficoTemperatura" class="mdc-typography">Temperatura (°C)   |   </a>
                                <a href="#" id="linkGraficoBatimentos" class="mdc-typography">Batimentos Cardíacos por Minuto (bpm)   |   </a>
                                <a href="#" id="linkGraficoSituacao" class="mdc-typography">Situação do Paciente/a><br><br>
                                <div class="page-content">
                                    <table class="mdl-data-table mdl-js-data-table mdl-shadow--2dp">
                                        <thead>
                                            <tr>
                                                <th class="mdl-data-table__cell--non-numeric">Paciente</th>
                                                <th class="mdl-data-table__cell--non-numeric">Data e Hora</th>
                                                <th class="mdl-data-table__cell--non-numeric">Temperatura (°C)</th>
                                                <th class="mdl-data-table__cell--non-numeric">Batimentos Cardíacos por Minuto (bpm)</th>
                                                <th class="mdl-data-table__cell--non-numeric">Situação do Paciente</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <!-- Linhas da tabela serão adicionadas dinamicamente aqui -->
                                        </tbody>
                                    </table>
                                </div>
                            </main>
                        </div>
                    </body>
                </html>
                """
            )
            print(f"Página HTML '{nome_pagina_html}' criada com sucesso.")

    # Abrir a página HTML no navegador padrão
    if id_guia_html is None:
        # Se a guia ainda não estiver aberta, abre e armazena o ID
        driver.get("file://" + os.path.abspath(nome_pagina_html))
        time.sleep(2)  # Espera um pouco para garantir que a guia esteja carregada
        id_guia_html = driver.current_window_handle
        print(f"ID da guia HTML armazenado: {id_guia_html}")
    else:
        # Se a guia já estiver aberta, recarrega a mesma guia
        driver.get("file://" + os.path.abspath(nome_pagina_html))
        driver.switch_to.window(id_guia_html)
        print("Guia HTML recarregada.")



# Função para atualizar a tabela HTML com dados do arquivo
def atualizar_tabela_html(nome_arquivo):
    nome_pagina_html = "prototipo.html"
    with open(nome_arquivo, "r", encoding="utf-8") as file:
        dados = file.read()

        if dados:
            dados = json.loads(dados)
        else:
            dados = []

    # Criar uma linha na tabela para cada registro nos dados
    linhas_tabela = ""
    for registro in dados:
        # Adicione a seguinte verificação para definir a cor da linha
        cor_linha = "background-color: #FFEBEE;" if registro['situacao'] != "De pé" else ""
        linhas_tabela += f"""
            <tr style="{cor_linha}">
                <td class="mdl-data-table__cell--non-numeric" style="text-align: center;">{registro['paciente']}</td>
                <td class="mdl-data-table__cell--non-numeric" style="text-align: center;">{registro['dataHora']}</td>
                <td class="mdl-data-table__cell--non-numeric" style="text-align: center;">{registro['temperatura']}</td>
                <td class="mdl-data-table__cell--non-numeric" style="text-align: center;">{registro['batimentos']}</td>
                <td class="mdl-data-table__cell--non-numeric" style="text-align: center;">{registro['situacao']}</td>
            </tr>
        """
    # Atualizar o conteúdo da página HTML
    conteudo_html = f"""
        <html>
            <head>
                <title>Protótipo</title>
                <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
                <link rel="stylesheet" href="https://code.getmdl.io/1.3.0/material.indigo-pink.min.css">
                <script defer src="https://code.getmdl.io/1.3.0/material.min.js"></script>
            </head>
            <body class="mdl-color--grey-100">
                <div class="mdl-layout mdl-js-layout">
                    <header class="mdl-layout__header mdl-layout__header--scroll mdl-color--primary">
                        <div class="mdl-layout-icon"></div>
                        <div class="mdl-layout__header-row">
                            <span class="mdl-layout-title">Dados do Protótipo</span>
                        </div>
                    </header>
                    <main class="mdl-layout__content">
                        <h4 class="mdc-typography">Gráficos Disponíveis</h4>
                        <a href="#" id="linkGraficoTemperatura" class="mdc-typography">Temperatura (°C)   |   </a>
                        <a href="#" id="linkGraficoBatimentos" class="mdc-typography">Batimentos Cardíacos por Minuto (bpm)   |   </a>
                        <a href="#" id="linkGraficoSituacao" class="mdc-typography">Situação do Paciente</a><br><br>
                        <div class="page-content">
                            <table class="mdl-data-table mdl-js-data-table mdl-shadow--2dp">
                                <thead>
                                    <tr>
                                        <th class="mdl-data-table__cell--non-numeric" style="text-align: center;">Paciente</th>
                                        <th class="mdl-data-table__cell--non-numeric" style="text-align: center;">Data e Hora</th>
                                        <th class="mdl-data-table__cell--non-numeric" style="text-align: center;">Temperatura (°C)</th>
                                        <th class="mdl-data-table__cell--non-numeric" style="text-align: center;">Batimentos Cardíacos por Minuto (bpm)</th>
                                        <th class="mdl-data-table__cell--non-numeric" style="text-align: center;">Situação do Paciente</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {linhas_tabela}
                                </tbody>
                            </table>
                        </div>
                    </main>
                </div>
            </body>
        </html>
    """
    
    # Atualizar o conteúdo da página HTML
    with open(nome_pagina_html, "w", encoding="utf-8") as html_file:
        html_file.write(conteudo_html)
        
    nome_paciente = nome_arquivo.split("/")[0]
     
    # Adicionar script JavaScript para abrir gráficos em novas abas
    script = """
        var links = document.querySelectorAll('.mdc-typography');
        links.forEach(function(link) {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                var nome_paciente = String.raw`""" + nome_paciente + """`;
                var tipoGrafico = event.target.textContent.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").split(' ')[0];
                var graphLink = nome_paciente + "/" + nome_paciente + "_grafico_" + tipoGrafico.toLowerCase().replace(/ /g, "_") + ".png";
                window.open(graphLink, '_blank');
            });
        });
    """
    driver.execute_script(script)

        

# Executar a função de obter e salvar dados a cada 20 segundos
while True:
    nome_arquivo = obter_e_salvar_dados()
    if nome_arquivo:
        plotar_graficos(nome_arquivo)
        abrir_pagina_html()
        atualizar_tabela_html(nome_arquivo)
    time.sleep(20)