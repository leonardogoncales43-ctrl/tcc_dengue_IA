import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# ---------------------------------------------------------
# Localização dos Arquivos
# ---------------------------------------------------------
pasta_src = os.path.dirname(os.path.abspath(__file__))
raiz_projeto = os.path.dirname(pasta_src)

caminho_dados = os.path.join(raiz_projeto, "data", "processed", "dengue_clima_processado_3549904.csv")
pasta_reports = os.path.join(raiz_projeto, "reports")
os.makedirs(pasta_reports, exist_ok=True)

# ---------------------------------------------------------
# 1. Carregamento e Preparação dos Dados
# ---------------------------------------------------------
df = pd.read_csv(caminho_dados)

features = [
    'casos_lag1', 'casos_lag2',
    'tempmed', 'tempmed_lag2', 'tempmed_lag4',
    'umidmed', 'umidmed_lag2', 'umidmed_lag4'
]
features_existentes = [c for c in features if c in df.columns]
target = 'casos'

df_clean = df.dropna(subset=features_existentes + [target]).copy()

# Divisão Temporal (80% treino temporal, 20% teste temporal)
tamanho_treino = int(len(df_clean) * 0.8)
train_df = df_clean.iloc[:tamanho_treino]
test_df = df_clean.iloc[tamanho_treino:].copy()

X_train, y_train = train_df[features_existentes], train_df[target]
X_test, y_test = test_df[features_existentes], test_df[target]

# ---------------------------------------------------------
# 2. Treinamento dos Algoritmos
# ---------------------------------------------------------
print("⏳ Treinando Random Forest Regressor...")
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

print("⏳ Treinando XGBoost Regressor...")
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)
xgb_model.fit(X_train, y_train)

# ---------------------------------------------------------
# 3. Predições e Cálculo de Métricas Estatísticas
# ---------------------------------------------------------
pred_rf = np.maximum(0, rf_model.predict(X_test))
pred_xgb = np.maximum(0, xgb_model.predict(X_test))

def calcular_metricas(y_real, y_pred):
    r2 = r2_score(y_real, y_pred)
    rmse = np.sqrt(mean_squared_error(y_real, y_pred))
    mae = mean_absolute_error(y_real, y_pred)
    return r2, rmse, mae

r2_rf, rmse_rf, mae_rf = calcular_metricas(y_test, pred_rf)
r2_xgb, rmse_xgb, mae_xgb = calcular_metricas(y_test, pred_xgb)

df_metricas = pd.DataFrame({
    'Modelo': ['Random Forest', 'XGBoost'],
    'R² Score': [r2_rf, r2_xgb],
    'RMSE': [rmse_rf, rmse_xgb],
    'MAE': [mae_rf, mae_xgb]
})

print("\n=================== TABELA COMPARATIVA DE DESEMPENHO ===================")
print(df_metricas.to_string(index=False))

# Save table as CSV for paper inclusion
caminho_csv = os.path.join(pasta_reports, "tabela_benchmark.csv")
df_metricas.to_csv(caminho_csv, index=False)
print(f"\n✅ Tabela de métricas salva em: {caminho_csv}")

# ---------------------------------------------------------
# 4. Geração do Gráfico Científico Comparativo
# ---------------------------------------------------------
plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")

semanas = test_df['SE'].astype(str) if 'SE' in test_df.columns else range(len(y_test))

plt.plot(semanas, y_test.values, label='Casos Reais Notificados', color='black', linewidth=2.5, marker='o', markersize=4)
plt.plot(semanas, pred_rf, label=f'Random Forest ($R^2 = {r2_rf:.2f}$)', color='#2ca02c', linestyle='--', linewidth=2)
plt.plot(semanas, pred_xgb, label=f'XGBoost ($R^2 = {r2_xgb:.2f}$)', color='#d62728', linestyle=':', linewidth=2)

plt.title('Benchmark de Modelos Preditivos: Casos Reais vs. RF vs. XGBoost', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Semana Epidemiológica (SE)', fontsize=12)
plt.ylabel('Número de Casos de Dengue', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.legend(fontsize=11, loc='upper left')
plt.tight_layout()

caminho_fig = os.path.join(pasta_reports, "comparacao_modelos.png")
plt.savefig(caminho_fig, dpi=300)
print(f"✅ Gráfico comparativo de alta resolução salvo em: {caminho_fig}\n")