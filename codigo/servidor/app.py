import streamlit as st
import sqlite3
import pandas as pd
import io

# 1. CONFIGURAÇÃO DA PÁGINA (Título que aparece na aba do navegador)
st.set_page_config(page_title="Controle de Estoque Fácil", page_icon="🛒")

# 2. FUNÇÃO PARA GERENCIAR O BANCO DE DADOS (Cria o arquivo localmente)
def conectar_banco():
    conn = sqlite3.connect('estoque_mercado.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS produtos 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nome TEXT NOT NULL, 
                  quantidade INTEGER NOT NULL, 
                  preco_custo REAL,
                  preco_venda REAL NOT NULL)''')
    conn.commit()
    return conn

# 3. LÓGICA PRINCIPAL DA APLICAÇÃO
def main():
    conn = conectar_banco()
    
    st.title("🛒 Gestão do Mercadinho")
    st.markdown("---")
    
    # Menu lateral com ícones e nomes claros
    menu = ["📊 Ver Estoque", "🆕 Cadastrar Produto", "🔄 Entrada/Saída"]
    escolha = st.sidebar.selectbox("O que deseja fazer?", menu)

    # --- ABA: VER ESTOQUE ---
    # --- ABA: VER ESTOQUE ---
    if escolha == "📊 Ver Estoque":
        st.subheader("Itens no Estoque")
        
        df = pd.read_sql_query("SELECT nome as 'Produto', quantidade as 'Qtd', preco_custo as 'Custo', preco_venda as 'Venda' FROM produtos", conn)
        
        if df.empty:
            st.info("O estoque está vazio.")
        else:
            # Formatação para exibir como dinheiro (R$ 0,00)
            df_formatado = df.copy()
            df_formatado['Custo'] = df_formatado['Custo'].map('R$ {:.2f}'.format)
            df_formatado['Venda'] = df_formatado['Venda'].map('R$ {:.2f}'.format)
            
            # Exibe a tabela com visual limpo
            st.table(df_formatado)

    # --- ABA: CADASTRAR PRODUTO ---
    elif escolha == "🆕 Cadastrar Produto":
        st.subheader("Cadastrar Novo Item")
        
        with st.form("form_cadastro", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            col1, col2 = st.columns(2)
            qtd = col1.number_input("Quantidade Inicial", min_value=0, step=1)
            p_custo = col2.number_input("Preço de Custo (R$)", min_value=0.0, format="%.2f")
            p_venda = st.number_input("Preço de Venda (R$)", min_value=0.0, format="%.2f")
            
            submit = st.form_submit_button("Salvar Produto")

            if submit:
                if nome:
                    c = conn.cursor()
                    c.execute("INSERT INTO produtos (nome, quantidade, preco_custo, preco_venda) VALUES (?,?,?,?)", 
                              (nome, qtd, p_custo, p_venda))
                    conn.commit()
                    st.success(f"✅ {nome} adicionado com sucesso!")
                else:
                    st.error("Erro: O nome do produto é obrigatório.")

    # --- ABA: ENTRADA/SAÍDA ---
    elif escolha == "🔄 Entrada/Saída":
        st.subheader("Atualizar Quantidades")
        
        # Busca lista de produtos para o dropdown
        produtos_cadastrados = pd.read_sql_query("SELECT nome FROM produtos", conn)
        
        if produtos_cadastrados.empty:
            st.warning("Cadastre um produto primeiro para poder movimentar o estoque.")
        else:
            item = st.selectbox("Selecione o produto:", produtos_cadastrados['nome'].tolist())
            tipo = st.radio("Tipo de movimento:", ["Venda (Saída)", "Compra (Entrada)"])
            quantidade = st.number_input("Quantidade", min_value=1, step=1)

            if st.button("Confirmar Movimentação"):
                ajuste = -quantidade if "Venda" in tipo else quantidade
                c = conn.cursor()
                c.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE nome = ?", (ajuste, item))
                conn.commit()
                st.success("✨ Estoque atualizado!")

if __name__ == '__main__':
    main()
