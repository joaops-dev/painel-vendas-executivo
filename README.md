# Painel de Vendas Executivo - Build 1.5.0

Este é um dashboard interativo desenvolvido para análise de faturamento, monitoramento de metas e gestão de performance de vendas em tempo real.

O projeto evoluiu de um simples visualizador de dados para um sistema **CRUD completo**, permitindo a gestão direta do banco de dados através de uma interface segura.

---

## Demonstração (Live App)
Você pode acessar o painel rodando ao vivo aqui: 
**(https://painel-venda-executivo.streamlit.app/)**

---

## Funcionalidades Principais

### Business Intelligence (BI)
* **Métricas em Tempo Real:** Faturamento total, quantidade de vendas e ticket médio com indicadores de variação (Deltas).
* **Análise Temporal:** Gráfico interativo de faturamento ao longo do tempo.
* **Visão por Vendedor:** Performance individual comparada com metas dinâmicas extraídas de arquivos CSV.
* **Filtros Inteligentes:** Segmentação por data, região, produto e vendedor.

### Gestão e Segurança (Modo Gestor)
* **Registro de Vendas (Create):** Formulário integrado para cadastro de novos registros no banco de dados.
* **Auditoria e Exclusão (Delete):** Painel de controle para cancelar registros incorretos via ID de venda.
* **Autenticação Segura:** As funcionalidades de edição são protegidas por um cofre de senhas (`st.secrets`), garantindo que apenas usuários autorizados alterem os dados.
* **Blindagem SQL:** Implementação de consultas parametrizadas para prevenir ataques de SQL Injection.

---

## Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Interface:** [Streamlit](https://streamlit.io/)
* **Análise de Dados:** Pandas
* **Banco de Dados:** SQLite (SQL Nativo)
* **Visualização:** Plotly Express
* **Deploy:** Streamlit Cloud

---

## Desenvolvedor
**João Pedro Freitas**
* GitHub: [@joaops-dev](https://github.com/joaops-dev)

---
*Este projeto foi desenvolvido como parte de um estudo prático de Engenharia de Software e Ciência da Computação.*
