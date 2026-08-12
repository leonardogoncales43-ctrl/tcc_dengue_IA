# 🦟 Sistema Preditivo de Dengue (TCC) - São José dos Campos / SP

Este repositório contém o código-fonte do Trabalho de Conclusão de Curso focado na criação de um pipeline automatizado (MLOps) para a **previsão de casos de Dengue** na cidade de São José dos Campos, SP.

O sistema utiliza técnicas de **Machine Learning** e integra dados climáticos e epidemiológicos em tempo real para gerar alertas precoces, auxiliando na tomada de decisão em saúde pública.

---

## ⚙️ Arquitetura do Sistema e Funcionalidades

O projeto foi construído para ser 100% autônomo, rodando em um ciclo completo de ponta a ponta:

* **Coleta de Dados Climáticos:** Integração com a API do *Open-Meteo* para capturar dados meteorológicos atuais (temperatura e umidade).
* **Coleta de Dados Epidemiológicos:** Conexão com a API do *InfoDengue* (Fiocruz/FGV) para extrair o boletim de casos notificados nas últimas semanas.
* **Engenharia de Recursos (Feature Engineering):** Cálculo automático de defasagens temporais (*lags* de 1, 2 e 4 semanas) que simulam o ciclo de vida do mosquito e o período de incubação do vírus.
* **Inteligência Artificial:** O vetor de dados é processado por um modelo preditivo treinado previamente que estima o número de casos para a próxima semana.
* **Dashboard Interativo:** Uma interface visual construída para que usuários e gestores possam consumir os dados e visualizar os alertas epidemiológicos de forma intuitiva.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Manipulação de Dados:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn, Joblib
* **Consumo de APIs:** `requests` (Open-Meteo e InfoDengue)
* **Interface Visual / Deploy:** Streamlit
* **Controle de Versão:** Git e GitHub

---

## 🚀 Como executar este projeto localmente

Caso queira clonar este repositório e rodar em sua própria máquina, abra o seu terminal e siga os passos abaixo:

**1. Clone o repositório:**
> git clone https://github.com/leonardogoncales43-ctrl/tcc_dengue_IA.git

**2. Acesse a pasta do projeto:**
> cd tcc_dengue_IA/Tcc_Dengue_IA

**3. Instale as dependências (requer Python instalado):**
> pip install pandas numpy scikit-learn requests streamlit joblib

**4. Execute o simulador em tempo real:**
> python src/previsao_real.py

**5. Inicie o Dashboard Web:**
> streamlit run app.py

---
*Projeto desenvolvido por Leonardo Gonçalves como requisito de Trabalho de Conclusão de Curso.*
