import os
import pandas as pd
import joblib
from automacao_dados import coletar_clima_sjc #Importa a função do arquivo para realizae a consulta na internet
from coleta_dados import baixar_dados_dengue

#Apontando os caminhos para achar os modelos salvos

pasta_src = os.path.dirname(os.path.abspath(__file__))
raiz_projeto = os.path.dirname(pasta_src)
caminho_modelo = os.path.join(raiz_projeto, "models", "modelo_dengue_3549904.pkl")

def fazer_previsao_real():
    #Carregar a IA
    try:
        modelo = joblib.load(caminho_modelo)
    except FileNotFoundError:
        print("Erro, modelo de IA não encontrado")
        return

    # puxando dados da internet
    tabela_clima = coletar_clima_sjc()

    if tabela_clima is None:
        print("Erro ao puxar dados de clima")
        return
    #Convertendo dados diarios para modelos semanais
    temp_atual = tabela_clima['Temp_media_C'].tail(7).mean()
    umid_atual = tabela_clima['Umid_media_%'].tail(7).mean()

    temp_lag2 = tabela_clima['Temp_media_C'].iloc[7:14].mean()
    umid_lag2 = tabela_clima['Umid_media_%'].iloc[7:14].mean()

    temp_lag4 = tabela_clima['Temp_media_C'].head(7).mean()
    umid_lag4 = tabela_clima['Umid_media_%'].head(7).mean()

    # Dados Epidemiológicos (Puxando do InfoDengue)
    print(" Buscando casos reais no InfoDengue...")
    tabela_dengue = baixar_dados_dengue()

    if tabela_dengue is None or tabela_dengue.empty:
        print(" Erro ao puxar dados do InfoDengue. Abortando.")
        return

    # O InfoDengue normalmente entrega as semanas mais recentes no topo da tabela.
    # Pegamos a linha 0 (semana atual) e a linha 1 (semana passada).
    casos_lag1 = int(tabela_dengue['casos'].iloc[0])
    casos_lag2 = int(tabela_dengue['casos'].iloc[1])

    print(f" Casos reais confirmados: {casos_lag1} (última semana) e {casos_lag2} (semana anterior)")

    # Montando a Tabela Exata que a IA aprendeu a ler
    dados_para_prever = pd.DataFrame([{
        'casos_lag1': casos_lag1,
        'casos_lag2': casos_lag2,
        'tempmed': round(temp_atual, 2),
        'tempmed_lag2': round(temp_lag2, 2),
        'tempmed_lag4': round(temp_lag4, 2),
        'umidmed': round(umid_atual, 2),
        'umidmed_lag2': round(umid_lag2, 2),
        'umidmed_lag4': round(umid_lag4, 2)
    }])

    print("\n Variáveis montadas para análise da IA:")
    print(dados_para_prever.to_string(index=False))

    # A Mágica: IA, nos dê o futuro!
    previsao = modelo.predict(dados_para_prever)
    casos_previstos = max(0, round(previsao[0]))

    print("\n==================================================")
    print(" ALERTA EPIDEMIOLÓGICO PARA A PRÓXIMA SEMANA")
    print(f" Casos previstos pela Inteligência Artificial: {casos_previstos} casos")
    print("==================================================\n")


# "Botão de Ligar" do Script (Sem espaços no começo da linha!)
if __name__ == "__main__":
    fazer_previsao_real()