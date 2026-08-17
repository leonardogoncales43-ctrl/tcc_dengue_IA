# Sistema Preditivo de Dengue (TCC) – São José dos Campos/SP

Este repositório contém o código-fonte do Trabalho de Conclusão de Curso (TCC) voltado ao desenvolvimento de um Sistema Preditivo e de Monitoramento Epidemiológico da Dengue para o município de São José dos Campos/SP.

A solução utiliza uma arquitetura MLOps automatizada responsável por coletar dados climáticos e epidemiológicos atualizados, treinar modelos de Aprendizado de Máquina periodicamente e disponibilizar previsões em tempo real por meio de um painel interativo.

---

## Demonstração On-line

O dashboard interativo em produção pode ser acessado no seguinte endereço:  
https://tccdengueia-jps7kuph2rjlzfktkog9kc.streamlit.app

---

## Principais Funcionalidades

- Previsão Epidemiológica: Modelos de Machine Learning treinados com dados de temperatura, umidade e histórico de notificações.
- Mapeamento Georreferenciado: Mapas de calor e divisões de risco interativas desenvolvidas com Folium e Streamlit-Folium.
- Dashboards Interativos: Gráficos dinâmicos de tendência e análise de cenários climáticos desenvolvidos em Plotly.
- Pipeline MLOps Automatizado: Atualização semanal dos dados e re-treinamento do modelo sem intervenção humana via GitHub Actions.

---

## Tecnologias e Bibliotecas

- Linguagem: Python 3.10+
- Dashboard e Interface: Streamlit
- Visualização e Geoprocessamento: Folium, Streamlit-Folium, Plotly
- Machine Learning e Análise de Dados: Pandas, NumPy, Scikit-Learn, Joblib
- Automação e Deploy: GitHub Actions, Streamlit Cloud

---

## Estrutura do Repositório

```text
tcc_dengue_IA/
├── .github/
│   └── workflows/
│       └── automacao.yml       # Pipeline CI/CD MLOps semanal (GitHub Actions)
├── Tcc_Dengue_IA/
│   └── src/
│       ├── app.py              # Interface e Dashboard Streamlit
│       └── Treinamento.py      # Script de ingestão, tratamento e treinamento da IA
├── .gitignore                  # Arquivos ignorados pelo Git
├── README.md                   # Documentação do repositório
└── requirements.txt            # Dependências do projeto
