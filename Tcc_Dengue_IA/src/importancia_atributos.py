import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt


def plotar_importancia_atributos(codigo_ibge=3549904):
    pasta_src = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(pasta_src)

    caminho_csv = os.path.join(raiz_projeto, "data", "processed", f"dengue_clima_processado_{codigo_ibge}.csv")
    caminho_modelo = os.path.join(raiz_projeto, "models", f"modelo_dengue_{codigo_ibge}.pkl")

    if not os.path.exists(caminho_csv) or not os.path.exists(caminho_modelo):
        print("❌ Arquivo CSV ou modelo .pkl não encontrado.")
        return

    df = pd.read_csv(caminho_csv)
    modelo = joblib.load(caminho_modelo)

    colunas_features = [
        'casos_lag1', 'casos_lag2',
        'tempmed', 'tempmed_lag2', 'tempmed_lag4',
        'umidmed', 'umidmed_lag2', 'umidmed_lag4'
    ]
    colunas_features = [col for col in colunas_features if col in df.columns]

    # Extrai o peso/relevância atribuído a cada variável pelo Random Forest
    importancias = modelo.feature_importances_
    df_imp = pd.DataFrame({
        'Atributo': colunas_features,
        'Importancia': importancias
    }).sort_values(by='Importancia', ascending=True)

    # Dicionário de tradução para rótulos legíveis no TCC
    nomes_amigaveis = {
        'casos_lag1': 'Casos (1 sem. atrás)',
        'casos_lag2': 'Casos (2 sem. atrás)',
        'tempmed': 'Temperatura Média Atual',
        'tempmed_lag2': 'Temperatura (2 sem. atrás)',
        'tempmed_lag4': 'Temperatura (4 sem. atrás)',
        'umidmed': 'Umidade Média Atual',
        'umidmed_lag2': 'Umidade (2 sem. atrás)',
        'umidmed_lag4': 'Umidade (4 sem. atrás)'
    }
    df_imp['Atributo_Rotulo'] = df_imp['Atributo'].map(lambda x: nomes_amigaveis.get(x, x))

    # Construção do gráfico de barras horizontais
    plt.figure(figsize=(10, 5), dpi=300)
    barras = plt.barh(df_imp['Atributo_Rotulo'], df_imp['Importancia'] * 100, color='#2ca02c')

    plt.title('Importância Relativa das Variáveis na Predição da Dengue', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Peso de Influência no Modelo (%)', fontsize=10, labelpad=10)

    # Adiciona a porcentagem exata ao lado de cada barra
    for barra in barras:
        largura = barra.get_width()
        plt.text(largura + 0.8, barra.get_y() + barra.get_height() / 2, f'{largura:.1f}%',
                 ha='left', va='center', fontsize=9, fontweight='bold')

    plt.xlim(0, max(df_imp['Importancia'] * 100) + 10)
    plt.grid(axis='x', linestyle=':', alpha=0.6)
    plt.tight_layout()

    pasta_reports = os.path.join(raiz_projeto, "reports")
    os.makedirs(pasta_reports, exist_ok=True)
    caminho_imagem = os.path.join(pasta_reports, "importancia_atributos.png")

    plt.savefig(caminho_imagem, dpi=300, bbox_inches='tight')
    print(f"📊 Gráfico de importância salvo em: {caminho_imagem}")
    plt.show()


if __name__ == "__main__":
    plotar_importancia_atributos(codigo_ibge=3549904)