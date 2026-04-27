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

# ── ESTILO FRONT-END ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    color: #e0e0e0 !important;
}
.stApp { background: #0e1117; }

.header {
    background: linear-gradient(135deg, #0a2e1a, #1b4332);
    border-radius: 20px; padding: 1.5rem; display: flex;
    align-items: center; gap: 1rem; margin-bottom: 2rem;
    color: #ffffff; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    border: 1px solid #2d6a4f;
}
.card {
    background: #161b22; border-radius: 15px; padding: 1.2rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3); text-align: center;
    border: 1px solid #30363d; border-bottom: 4px solid #2d6a4f;
}
.card-value { font-size: 1.8rem; font-weight: 800; color: #52b788; }
.card-label { font-size: 0.8rem; color: #8b949e; font-weight: 600; }

.stButton > button {
    background: #21262d !important; color: #52b788 !important;
    border: 1px solid #30363d !important; border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 0.65rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #2d6a4f !important; color: white !important;
    border-color: #52b788 !important; transform: translateY(-2px) !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 10px !important; border: 1px solid #30363d !important;
    color: #ffffff !important; background: #0d1117 !important;
}
label, .stTextInput label, .stNumberInput label,
.stSelectbox label, .stRadio label {
    color: #c9d1d9 !important; font-weight: 700 !important;
}
.stRadio > div > label {
    background: #161b22 !important; border: 1px solid #30363d !important;
    border-radius: 10px !important; padding: 0.4rem 1rem !important;
    color: #8b949e !important;
}
.stRadio > div > label:has(input:checked) {
    border-color: #52b788 !important; background: #1b4332 !important;
    color: #ffffff !important;
}
.stSuccess { background: #0a2e1a !important; color: #b7e4c7 !important; border: 1px solid #2d6a4f !important; }
.stInfo    { background: #0d1b2a !important; color: #a9d6e5 !important; border: 1px solid #1b4965 !important; }
.stWarning { background: #332701 !important; color: #ffd60a !important; border: 1px solid #917100 !important; }
.stError   { background: #2d0a0a !important; color: #ffadad !important; border: 1px solid #8b0000 !important; }

[data-testid="stForm"] {
    background: #161b22 !important; border-radius: 16px !important;
    border: 1px solid #30363d !important;
}
h1, h2, h3, h4, .stSubheader { color: #52b788 !important; }
hr { border-color: #30363d !important; }
</style>
""", unsafe_allow_html=True)

# ── BANCO DE DADOS ──
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
                preco_venda REAL NOT NULL DEFAULT 0,
                imagem_url TEXT DEFAULT ''
            )
        """)
        # Migração: adiciona coluna se banco já existia sem ela
        try:
            conn.execute("ALTER TABLE produtos ADD COLUMN imagem_url TEXT DEFAULT ''")
        except Exception:
            pass

def carregar_produtos():
    with conectar() as conn:
        return pd.read_sql_query("SELECT * FROM produtos ORDER BY nome", conn)

def buscar_produto_por_codigo(codigo):
    with conectar() as conn:
        return pd.read_sql_query(
            "SELECT * FROM produtos WHERE codigo_barras = ?", conn, params=(codigo,)
        )

def salvar_produto(codigo, nome, quantidade, custo, venda, imagem_url=""):
    with conectar() as conn:
        conn.execute("""
            INSERT INTO produtos (codigo_barras, nome, quantidade, preco_custo, preco_venda, imagem_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (codigo, nome, quantidade, custo, venda, imagem_url))

def atualizar_estoque(produto_id, nova_quantidade):
    with conectar() as conn:
        conn.execute(
            "UPDATE produtos SET quantidade = ? WHERE id = ?",
            (nova_quantidade, produto_id)
        )

def atualizar_imagens_faltantes():
    """Busca e salva imagens para produtos sem imagem_url."""
    with conectar() as conn:
        df = pd.read_sql_query(
            "SELECT id, codigo_barras FROM produtos WHERE imagem_url IS NULL OR imagem_url = ''",
            conn
        )
    if df.empty:
        return 0
    atualizados = 0
    for _, row in df.iterrows():
        _, imagem_url = buscar_produto_api(row["codigo_barras"])
        if imagem_url:
            with conectar() as conn:
                conn.execute(
                    "UPDATE produtos SET imagem_url = ? WHERE id = ?",
                    (imagem_url, row["id"])
                )
            atualizados += 1
    return atualizados

# ── API ──
@st.cache_data(ttl=3600)
def buscar_produto_api(codigo):
    """Retorna (nome, imagem_url) da API OpenFoodFacts."""
    url = f"https://br.openfoodfacts.org/api/v0/product/{codigo}.json"
    try:
        r = requests.get(url, timeout=4, headers={"User-Agent": "MercadinhoApp/2.0"})
        data = r.json()
        if data.get("status") == 1:
            p = data.get("product", {})
            nome = (p.get("product_name_pt_BR") or p.get("product_name") or "").strip()
            imagem = (
                p.get("image_front_small_url")
                or p.get("image_front_url")
                or p.get("image_url")
                or ""
            )
            return nome, imagem
    except Exception:
        pass
    return "", ""

def ler_codigo_imagem(imagem):
    img = Image.open(imagem)
    codigos = decode(img)
    if codigos:
        return codigos[0].data.decode("utf-8")
    return ""

def trocar_tela(tela):
    st.session_state.tela = tela
    st.rerun()

# ── COMPONENTES ──
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
    if col1.button("📦  Estoque",    use_container_width=True): trocar_tela("estoque")
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

    # Botão de sincronização de imagens
    col_sync, _ = st.columns([1, 4])
    with col_sync:
        if st.button("🖼️ Sincronizar imagens", use_container_width=True):
            with st.spinner("Buscando imagens na API..."):
                n = atualizar_imagens_faltantes()
            if n > 0:
                st.success(f"{n} imagem(ns) atualizada(s)!")
                st.rerun()
            else:
                st.info("Nenhuma imagem nova encontrada.")

    df = carregar_produtos()
    if df.empty:
        st.info("Seu estoque está vazio. Cadastre o primeiro produto.")
        return

    # Cards de resumo
    c1, c2, c3 = st.columns(3)
    with c1: card(int(df["quantidade"].sum()), "Unidades totais")
    with c2: card(f"R$ {df['quantidade'].mul(df['preco_venda']).sum():.2f}", "Valor total")
    with c3:
        baixos = int((df["quantidade"] <= ESTOQUE_BAIXO).sum())
        card(baixos, "Baixo estoque", "#ff4b4b" if baixos > 0 else "#52b788")

    st.markdown("### Lista de Produtos")

    # Cabeçalho da tabela
    header_cols = st.columns([1, 3, 2, 2, 2, 2])
    for col, label in zip(header_cols, ["Imagem", "Nome", "Código", "Qtd", "Custo", "Venda"]):
        col.markdown(f"**{label}**")
    st.divider()

    # Linhas com imagem
    for _, row in df.iterrows():
        col_img, col_nome, col_cod, col_qtd, col_custo, col_venda = st.columns([1, 3, 2, 2, 2, 2])

        with col_img:
            imagem_url = row.get("imagem_url", "")
            if imagem_url:
                st.image(imagem_url, width=60)
            else:
                st.markdown("🏷️")

        col_nome.markdown(f"**{row['nome']}**")
        col_cod.markdown(f"`{row['codigo_barras']}`")

        qtd = row["quantidade"]
        cor_qtd = "🔴" if qtd <= ESTOQUE_BAIXO else "🟢"
        col_qtd.markdown(f"{cor_qtd} **{qtd}**")

        col_custo.markdown(f"R$ {row['preco_custo']:.2f}")
        col_venda.markdown(f"R$ {row['preco_venda']:.2f}")

        st.divider()

def tela_cadastro():
    st.subheader("➕ Cadastro de Produto")

    st.markdown("#### 📷 Ler código de barras")
    metodo = st.radio(
        "Como deseja informar o código?",
        ["📷 Câmera ao vivo", "🖼️ Upload de imagem", "⌨️ Digitar manualmente"],
        horizontal=True
    )

    # ── Câmera ao vivo ──
    if metodo == "📷 Câmera ao vivo":
        st.info("Aponte a câmera para o código de barras e clique em 'Tirar foto'.")
        foto = st.camera_input("Tirar foto do código de barras")
        if foto:
            codigo_lido = ler_codigo_imagem(foto)
            if codigo_lido:
                st.success(f"✅ Código detectado: `{codigo_lido}`")
                st.session_state.barcode_pendente = codigo_lido
            else:
                st.warning("⚠️ Nenhum código detectado. Tente centralizar e aproximar mais o código.")

    # ── Upload de imagem ──
    elif metodo == "🖼️ Upload de imagem":
        foto = st.file_uploader("Selecione a imagem do código", type=["jpg", "png", "jpeg"])
        if foto:
            codigo_lido = ler_codigo_imagem(foto)
            if codigo_lido:
                st.success(f"✅ Código detectado: `{codigo_lido}`")
                st.session_state.barcode_pendente = codigo_lido
            else:
                st.warning("⚠️ Nenhum código detectado na imagem.")

    # Campo de código (preenchido automaticamente ou manual)
    codigo = st.text_input(
        "Código de barras",
        value=st.session_state.get("barcode_pendente", ""),
        placeholder="Ex: 7891000065440"
    )

    if st.session_state.get("barcode_pendente"):
        if st.button("🗑️ Limpar código"):
            st.session_state.barcode_pendente = ""
            st.rerun()

    st.divider()

    # ── Formulário de cadastro ──
    if codigo:
        existente = buscar_produto_por_codigo(codigo)
        if not existente.empty:
            st.warning("⚠️ Produto já cadastrado.")
            st.dataframe(existente[["nome", "quantidade", "preco_venda"]], hide_index=True)
            return

        with st.spinner("Buscando produto na API..."):
            nome_api, imagem_api = buscar_produto_api(codigo)

        if imagem_api:
            col_img, col_info = st.columns([1, 3])
            with col_img:
                st.image(imagem_api, width=120, caption="Imagem da API")
            with col_info:
                st.markdown(f"**Produto encontrado:** {nome_api or 'Nome não encontrado'}")
                st.caption(f"Código: `{codigo}`")
        elif nome_api:
            st.info(f"Produto encontrado: **{nome_api}** (sem imagem na API)")

        with st.form("cadastro"):
            nome = st.text_input("Nome do produto", value=nome_api)
            c1, c2, c3 = st.columns(3)
            qtd   = c1.number_input("Quantidade", min_value=0)
            custo = c2.number_input("Custo (R$)", min_value=0.0, format="%.2f")
            venda = c3.number_input("Venda (R$)", min_value=0.0, format="%.2f")
            if st.form_submit_button("💾 Salvar produto", use_container_width=True):
                if not nome.strip():
                    st.error("Informe o nome do produto.")
                else:
                    salvar_produto(codigo, nome, qtd, custo, venda, imagem_api)
                    st.session_state.barcode_pendente = ""
                    st.success(f"✅ '{nome}' salvo com sucesso!")
                    st.rerun()

def tela_movimentar():
    st.subheader("🔄 Movimentação")
    df = carregar_produtos()
    if df.empty:
        st.info("Nenhum produto cadastrado.")
        return

    opcoes = {f"{r.nome} (Qtd: {r.quantidade})": r for r in df.itertuples()}
    with st.form("movimento"):
        escolhido = st.selectbox("Produto", list(opcoes.keys()))
        tipo = st.radio("Operação", ["Saída", "Entrada"], horizontal=True)
        qtd_mov = st.number_input("Quantidade", min_value=1)
        if st.form_submit_button("Confirmar", use_container_width=True):
            prod = opcoes[escolhido]
            nova_qtd = prod.quantidade + (qtd_mov if tipo == "Entrada" else -qtd_mov)
            if nova_qtd < 0:
                st.error("Estoque insuficiente!")
            else:
                atualizar_estoque(prod.id, nova_qtd)
                st.success("✅ Estoque atualizado!")
                st.rerun()

# ── MAIN ──
def main():
    init_db()
    if "tela" not in st.session_state:
        st.session_state.tela = "estoque"
    if "barcode_pendente" not in st.session_state:
        st.session_state.barcode_pendente = ""
    header()
    menu()
    if st.session_state.tela == "estoque":      tela_estoque()
    elif st.session_state.tela == "cadastro":   tela_cadastro()
    elif st.session_state.tela == "movimentar": tela_movimentar()

if __name__ == "__main__":
    main()
