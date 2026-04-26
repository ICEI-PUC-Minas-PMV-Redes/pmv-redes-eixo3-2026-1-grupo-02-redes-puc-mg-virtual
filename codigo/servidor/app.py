import sqlite3
import pandas as pd
import requests
import streamlit as st
from PIL import Image
from pyzbar.pyzbar import decode

# Configurações Iniciais
DB = "estoque_mercado.db"
ESTOQUE_BAIXO = 3

st.set_page_config(
    page_title="Meu Mercadinho - Dark Mode",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── ESTILO FRONT-END (Cores Escuras) ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap');

html, body, [class*="css"] { 
    font-family: 'Nunito', sans-serif !important; 
    color: #e0e0e0 !important; 
}

/* Fundo da aplicação */
.stApp { 
    background: #0e1117; 
}

/* ── Cabeçalho ── */
.header {
    background: linear-gradient(135deg, #0a2e1a, #1b4332);
    border-radius: 20px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    color: #ffffff;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    border: 1px solid #2d6a4f;
}

/* ── Cards de resumo ── */
.card {
    background: #161b22;
    border-radius: 15px;
    padding: 1.2rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    text-align: center;
    border: 1px solid #30363d;
    border-bottom: 4px solid #2d6a4f;
}
.card-value { font-size: 1.8rem; font-weight: 800; color: #52b788; }
.card-label { font-size: 0.8rem; color: #8b949e; font-weight: 600; }

/* ── Botões ── */
.stButton > button {
    background: #21262d !important;
    color: #52b788 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #2d6a4f !important;
    color: white !important;
    border-color: #52b788 !important;
    transform: translateY(-2px) !important;
}

/* ── Inputs e Selectbox ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1px solid #30363d !important;
    color: #ffffff !important;
    background: #0d1117 !important;
}

/* Labels */
label, .stTextInput label, .stNumberInput label, .stSelectbox label, .stRadio label {
    color: #c9d1d9 !important;
    font-weight: 700 !important;
}

/* ── Radio ── */
.stRadio > div > label {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    padding: 0.4rem 1rem !important;
    color: #8b949e !important;
}
.stRadio > div > label:has(input:checked) {
    border-color: #52b788 !important;
    background: #1b4332 !important;
    color: #ffffff !important;
}

/* ── Alertas ── */
.stSuccess { background: #0a2e1a !important; color: #b7e4c7 !important; border: 1px solid #2d6a4f !important; }
.stInfo    { background: #0d1b2a !important; color: #a9d6e5 !important; border: 1px solid #1b4965 !important; }
.stWarning { background: #332701 !important; color: #ffd60a !important; border: 1px solid #917100 !important; }
.stError   { background: #2d0a0a !important; color: #ffadad !important; border: 1px solid #8b0000 !important; }

/* ── Containers ── */
[data-testid="stForm"] {
    background: #161b22 !important;
    border-radius: 16px !important;
    border: 1px solid #30363d !important;
}
h1, h2, h3, h4, .stSubheader { color: #52b788 !important; }
hr { border-color: #30363d !important; }
</style>
""", unsafe_allow_html=True)

# ── FUNÇÕES DE BANCO DE DADOS ──
def conectar():
    return sqlite3.connect(DB)

def init_db():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT UNIQUE,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 0,
                preco_custo REAL NOT NULL DEFAULT 0,
                preco_venda REAL NOT NULL DEFAULT 0
            )
        """)

def carregar_produtos():
    with conectar() as conn:
        return pd.read_sql_query("SELECT * FROM produtos ORDER BY nome", conn)

def buscar_produto_por_codigo(codigo):
    with conectar() as conn:
        return pd.read_sql_query("SELECT * FROM produtos WHERE codigo_barras = ?", conn, params=(codigo,))

def salvar_produto(codigo, nome, quantidade, custo, venda):
    with conectar() as conn:
        conn.execute("""
            INSERT INTO produtos (codigo_barras, nome, quantidade, preco_custo, preco_venda)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo, nome, quantidade, custo, venda))

def atualizar_estoque(produto_id, nova_quantidade):
    with conectar() as conn:
        conn.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, produto_id))

# ── LOGICA DE NEGÓCIO ──
@st.cache_data(ttl=3600)
def buscar_produto_api(codigo):
    url = f"https://br.openfoodfacts.org/api/v0/product/{codigo}.json"
    try:
        r = requests.get(url, timeout=4, headers={"User-Agent": "MercadinhoApp/2.0"})
        data = r.json()
        if data.get("status") == 1:
            p = data.get("product", {})
            return (p.get("product_name_pt_BR") or p.get("product_name") or "").strip()
    except: pass
    return ""

def ler_codigo_imagem(imagem):
    img = Image.open(imagem)
    codigos = decode(img)
    if codigos: return codigos[0].data.decode("utf-8")
    return ""

def trocar_tela(tela):
    st.session_state.tela = tela
    st.rerun()

# ── COMPONENTES DE INTERFACE ──
def header():
    st.markdown("""
    <div class="header">
        <div style="font-size:2.5rem">🏪</div>
        <div>
            <div style="font-size:1.6rem;font-weight:800;line-height:1">Meu Mercadinho</div>
            <div style="font-size:0.9rem;opacity:0.85;margin-top:4px">Gestão simples de estoque</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def menu():
    col1, col2, col3 = st.columns(3)
    if col1.button("📦  Estoque",   use_container_width=True): trocar_tela("estoque")
    if col2.button("➕  Cadastrar",  use_container_width=True): trocar_tela("cadastro")
    if col3.button("🔄  Movimentar", use_container_width=True): trocar_tela("movimentar")
    st.divider()

def card(valor, label, cor="#52b788"):
    st.markdown(f"""
    <div class="card" style="border-color:{cor}">
        <div class="card-value" style="color:{cor}">{valor}</div>
        <div class="card-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

# ── TELAS ──
def tela_estoque():
    st.subheader("📦 Estoque atual")
    df = carregar_produtos()
    if df.empty:
        st.info("Seu estoque está vazio. Cadastre o primeiro produto.")
        return

    c1, c2, c3 = st.columns(3)
    with c1: card(int(df["quantidade"].sum()), "Unidades totais")
    with c2: card(f"R$ {df['quantidade'].mul(df['preco_venda']).sum():.2f}", "Valor total")
    with c3: 
        baixos = int((df["quantidade"] <= ESTOQUE_BAIXO).sum())
        card(baixos, f"Baixo estoque", "#ff4b4b" if baixos > 0 else "#52b788")

    st.markdown("### Lista de Produtos")
    st.dataframe(df, use_container_width=True, hide_index=True)

def tela_cadastro():
    st.subheader("➕ Cadastro de Produto")
    foto = st.file_uploader("Scan do Código", type=["jpg", "png", "jpeg"])
    
    if foto:
        codigo_lido = ler_codigo_imagem(foto)
        if codigo_lido:
            st.success(f"Código lido: {codigo_lido}")
            st.session_state.barcode_pendente = codigo_lido

    codigo = st.text_input("Código de barras", value=st.session_state.get("barcode_pendente", ""))
    
    if codigo:
        existente = buscar_produto_por_codigo(codigo)
        if not existente.empty:
            st.warning("Produto já cadastrado.")
            return

        nome_api = buscar_produto_api(codigo)
        with st.form("cadastro"):
            nome = st.text_input("Nome", value=nome_api)
            c1, c2, c3 = st.columns(3)
            qtd = c1.number_input("Qtd", min_value=0)
            custo = c2.number_input("Custo", min_value=0.0)
            venda = c3.number_input("Venda", min_value=0.0)
            if st.form_submit_button("Salvar"):
                salvar_produto(codigo, nome, qtd, custo, venda)
                st.success("Salvo!")
                st.rerun()

def tela_movimentar():
    st.subheader("🔄 Movimentação")
    df = carregar_produtos()
    if df.empty: return
    
    opcoes = {f"{r.nome} (Qtd: {r.quantidade})": r for r in df.itertuples()}
    with st.form("movimento"):
        escolhido = st.selectbox("Produto", list(opcoes.keys()))
        tipo = st.radio("Operação", ["Saída", "Entrada"], horizontal=True)
        qtd_mov = st.number_input("Quantidade", min_value=1)
        if st.form_submit_button("Confirmar"):
            prod = opcoes[escolhido]
            nova_qtd = prod.quantidade + (qtd_mov if tipo == "Entrada" else -qtd_mov)
            if nova_qtd < 0:
                st.error("Estoque insuficiente!")
            else:
                atualizar_estoque(prod.id, nova_qtd)
                st.success("Atualizado!")
                st.rerun()

# ── MAIN ──
def main():
    init_db()
    if "tela" not in st.session_state: st.session_state.tela = "estoque"
    header()
    menu()
    if st.session_state.tela == "estoque": tela_estoque()
    elif st.session_state.tela == "cadastro": tela_cadastro()
    elif st.session_state.tela == "movimentar": tela_movimentar()

if __name__ == "__main__":
    main()
