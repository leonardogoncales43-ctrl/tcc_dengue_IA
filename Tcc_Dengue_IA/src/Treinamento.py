import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


def treinar_modelo_dengue(codigo_ibge=3549904):
    pasta_src = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(pasta_src)

    caminho_processed = os.path.join(raiz_projeto, "data", "processed", f"dengue_clima_processado_{codigo_ibge}.csv")

    if not os.path.exists(caminho_processed):
        print(f"❌ Arquivo processado não encontrado em: {caminho_processed}")
        return

    print("🤖 Carregando dados e preparando o treinamento da IA...")
    df = pd.read_csv(caminho_processed)

    # 1. Definição das Features (Incluindo histórico de casos + clima)
    colunas_features = [
        'casos_lag1', 'casos_lag2',
        'tempmed', 'tempmed_lag2', 'tempmed_lag4',
        'umidmed', 'umidmed_lag2', 'umidmed_lag4'
    ]

    colunas_features = [col for col in colunas_features if col in df.columns]

    X = df[colunas_features]
    y = df['casos']

    # 2. Divisão dos dados em Treino (80%) e Teste (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    print(f"📊 Registros de Treino: {len(X_train)} semanas | Registros de Teste: {len(X_test)} semanas")

    # 3. Treinamento da Random Forest
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    # 4. Avaliação de Desempenho
    previsoes = modelo.predict(X_test)

    mae = mean_absolute_error(y_test, previsoes)
    r2 = r2_score(y_test, previsoes)

    print("\n📈 --- DESEMPENHO DA IA NO TESTE ---")
    print(f"🔹 Erro Médio Absoluto (MAE): ~{round(mae, 1)} casos")
    print(f"🔹 Precisão Geral (R² Score): {round(r2 * 100, 2)}%")

    # 5. Salvando o Modelo Treinado
    pasta_models = os.path.join(raiz_projeto, "models")
    os.makedirs(pasta_models, exist_ok=True)

    caminho_modelo = os.path.join(pasta_models, f"modelo_dengue_{codigo_ibge}.pkl")
    joblib.dump(modelo, caminho_modelo)

    print(f"\n💾 Modelo preditivo salvo com sucesso em: {caminho_modelo}")


if __name__ == "__main__":
    treinar_modelo_dengue(codigo_ibge=3549904)