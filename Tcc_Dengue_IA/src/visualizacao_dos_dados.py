import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split


def gerar_grafico_previsoes(codigo_ibge=3549904):
    # 1. Mapeia os caminhos dinâmicos das pastas
    pasta_src = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(pasta_src)

    caminho_csv = os.path.join(raiz_projeto, "data", "processed", f"dengue_clima_processado_{codigo_ibge}.csv")
    caminho_modelo = os.path.join(raiz_projeto, "models", f"modelo_dengue_{codigo_ibge}.pkl")

    if not os.path.exists(caminho_csv) or not os.path.exists(caminho_modelo):
        print("❌ Arquivo CSV ou modelo .pkl não encontrado. Execute o processamento e o treinamento primeiro.")
        return

    # 2. Carrega o dataset e o cérebro da IA (.pkl)
    df = pd.read_csv(caminho_csv)
    modelo = joblib.load(caminho_modelo)

    # 3. Prepara as variáveis explicativas (Features)
    colunas_features = [
        'casos_lag1', 'casos_lag2',
        'tempmed', 'tempmed_lag2', 'tempmed_lag4',
        'umidmed', 'umidmed_lag2', 'umidmed_lag4'
    ]
    colunas_features = [col for col in colunas_features if col in df.columns]

    X = df[colunas_features]
    y = df['casos']

    # 4. Separação idêntica de Teste (20% finais)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Extrai o rótulo da Semana Epidemiológica (SE) para o eixo X
    se_teste = df.loc[y_test.index, 'SE'].astype(str)

    # 5. Executa as predições no conjunto de teste
    previsoes = modelo.predict(X_test)

    # 6. Construção da Figura no Matplotlib
    plt.figure(figsize=(12, 6), dpi=300)

    # Linha dos Casos Reais
    plt.plot(range(len(se_teste)), y_test.values, label='Casos Reais (Notificados)',
             color='#1f77b4', linewidth=2.2, marker='o', markersize=4)

    # Linha das Previsões da IA
    plt.plot(range(len(se_teste)), previsoes, label='Previsão da IA (Random Forest)',
             color='#d62728', linestyle='--', linewidth=2.2, marker='s', markersize=4)

    # Estilização para Padrão de Publicação / TCC
    plt.title(f'Validação Preditiva: Casos Reais vs. Previsão da IA (Código IBGE: {codigo_ibge})',
              fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Semana Epidemiológica (SE)', fontsize=11, labelpad=10)
    plt.ylabel('Número de Casos de Dengue', fontsize=11, labelpad=10)

    # Formata rótulos do eixo X com espaçamento dinâmico
    intervalo_ticks = max(1, len(se_teste) // 12)
    indices_ticks = list(range(0, len(se_teste), intervalo_ticks))
    rotulos_ticks = [se_teste.iloc[i] for i in indices_ticks]

    plt.xticks(indices_ticks, rotulos_ticks, rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=10, loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()

    # 7. Salva a imagem em alta qualidade
    pasta_reports = os.path.join(raiz_projeto, "reports")
    os.makedirs(pasta_reports, exist_ok=True)
    caminho_imagem = os.path.join(pasta_reports, "grafico_comparativo_dengue.png")

    plt.savefig(caminho_imagem, dpi=300, bbox_inches='tight')

    print("✅ Gráfico gerado com sucesso!")
    print(f"🖼️ Imagem salva em: {caminho_imagem}")

    # Exibe a janela gráfica do PyCharm
    plt.show()


if __name__ == "__main__":
    gerar_grafico_previsoes(codigo_ibge=3549904)