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
    page_title="Mini Mercado Arthur",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── ESTILO FRONT-END ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Open+Sans:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Open Sans', sans-serif !important;
    color: #1a1a1a !important;
}
.stApp { background: #f5f0eb; }

.header {
    background: linear-gradient(135deg, #e85d04, #f48c06);
    border-radius: 16px;
    padding: 1.4rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 2rem;
    color: #ffffff;
    box-shadow: 0 6px 20px rgba(232, 93, 4, 0.45);
    border: 3px solid #1a5c2a;
    position: relative;
    overflow: hidden;
}
.header::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 120px; height: 120px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}
.header::after {
    content: '';
    position: absolute;
    bottom: -40px; right: 80px;
    width: 90px; height: 90px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.header-title {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 1.8rem;
    font-weight: 900;
    line-height: 1;
    text-shadow: 1px 2px 4px rgba(0,0,0,0.2);
    letter-spacing: -0.5px;
}
.header-sub {
    font-size: 0.85rem;
    opacity: 0.92;
    margin-top: 4px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.header-name {
    color: #1a5c2a;
    font-style: italic;
    font-size: 2rem;
    text-shadow: 1px 2px 0px rgba(0,0,0,0.15);
}

.card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.2rem;
    box-shadow: 0 3px 12px rgba(0,0,0,0.1);
    text-align: center;
    border-top: 5px solid #e85d04;
}
.card-value {
    font-family: 'Montserrat', sans-serif;
    font-size: 1.9rem;
    font-weight: 900;
    color: #e85d04;
}
.card-label {
    font-size: 0.78rem;
    color: #444;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}

.stButton > button {
    background: #e85d04 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 3px 8px rgba(232, 93, 4, 0.35) !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    background: #1a5c2a !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 14px rgba(26, 92, 42, 0.4) !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 2px solid #e8c99a !important;
    color: #111111 !important;
    background: #ffffff !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #e85d04 !important;
    box-shadow: 0 0 0 3px rgba(232,93,4,0.15) !important;
}

/* Garante fundo branco e texto escuro dentro de forms */
[data-testid="stForm"] input,
[data-testid="stForm"] .stNumberInput > div > div > input,
[data-testid="stForm"] .stTextInput > div > div > input {
    background: #ffffff !important;
    color: #111111 !important;
}

/* Botão confirmar dentro do form */
[data-testid="stForm"] .stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background: #e85d04 !important;
    color: #ffffff !important;
    border: none !important;
}

label, .stTextInput label, .stNumberInput label,
.stSelectbox label, .stRadio label {
    color: #333333 !important;
    font-weight: 700 !important;
    font-family: 'Montserrat', sans-serif !important;
}
.stRadio > div > label {
    background: #ffffff !important;
    border: 2px solid #e8c99a !important;
    border-radius: 10px !important;
    padding: 0.4rem 1rem !important;
    color: #333 !important;
}
.stRadio > div > label:has(input:checked) {
    border-color: #e85d04 !important;
    background: #fff4ed !important;
    color: #e85d04 !important;
    font-weight: 700 !important;
}

.stSuccess { background: #eafbea !important; color: #1a5c2a !important; border: 1px solid #1a5c2a !important; border-radius: 10px !important; }
.stInfo    { background: #fff8f0 !important; color: #c04e00 !important; border: 1px solid #f48c06 !important; border-radius: 10px !important; }
.stWarning { background: #fff9e6 !important; color: #b07c00 !important; border: 1px solid #f4c542 !important; border-radius: 10px !important; }
.stError   { background: #fff0f0 !important; color: #c0392b !important; border: 1px solid #e74c3c !important; border-radius: 10px !important; }

[data-testid="stForm"] {
    background: #ffffff !important;
    border-radius: 16px !important;
    border: 2px solid #e8c99a !important;
    padding: 1rem !important;
}

h1, h2, h3, h4, .stSubheader {
    color: #e85d04 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 900 !important;
}

/* Textos gerais de parágrafos, spans e markdown */
p, span, div, li, td, th {
    color: #1a1a1a !important;
}

/* Inputs: texto digitado e placeholder */
input, textarea, select {
    color: #111111 !important;
}
input::placeholder, textarea::placeholder {
    color: #888888 !important;
}

/* Selectbox: opção selecionada e itens do dropdown */
.stSelectbox > div > div,
.stSelectbox > div > div > div,
[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #111111 !important;
}

/* Texto dentro do stRadio (opções não selecionadas) */
.stRadio > div > div > label > div {
    color: #222222 !important;
}

/* Markdown gerado pelo st.markdown e st.caption */
.stMarkdown p, .stMarkdown span, .stMarkdown div {
    color: #1a1a1a !important;
}
.stMarkdown small, .element-container small {
    color: #444444 !important;
}

/* Caption / st.caption */
[data-testid="stCaptionContainer"] p {
    color: #555555 !important;
}

/* st.info / st.warning / st.success / st.error — textos internos */
[data-testid="stNotification"] p,
[data-testid="stAlert"] p,
.stAlert p {
    color: inherit !important;
}

/* Número dentro do number_input */
.stNumberInput input {
    color: #111111 !important;
}

/* Spinner text */
.stSpinner > div > div {
    color: #333333 !important;
}

/* Texto dos file uploader e camera input */
[data-testid="stFileUploader"] label,
[data-testid="stCameraInput"] label {
    color: #222222 !important;
}

/* File uploader — fundo branco e textos legíveis */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 2px dashed #e8c99a !important;
    padding: 0.5rem !important;
}
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] section > div,
[data-testid="stFileUploader"] section > button,
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section p {
    background: #ffffff !important;
    color: #222222 !important;
}
[data-testid="stFileUploader"] section > button {
    border: 2px solid #e85d04 !important;
    color: #e85d04 !important;
    border-radius: 8px !important;
}
hr { border-color: #e8c99a !important; }

/* Zebra nas linhas da tabela */
.produto-row {
    background: #ffffff;
    border-radius: 10px;
    padding: 0.5rem;
    margin-bottom: 0.3rem;
    border-left: 4px solid #e85d04;
}
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
        <div style="font-size:2.8rem">🛒</div>
        <div>
            <div class="header-title">
                Mini Mercado <span class="header-name">Arthur</span>
            </div>
            <div class="header-sub">Gestão de Estoque</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def menu():
    col1, col2, col3 = st.columns(3)
    if col1.button("📦  Estoque",    use_container_width=True): trocar_tela("estoque")
    if col2.button("➕  Cadastrar",  use_container_width=True): trocar_tela("cadastro")
    if col3.button("🔄  Movimentar", use_container_width=True): trocar_tela("movimentar")
    st.divider()

def card(valor, label, cor="#e85d04"):
    st.markdown(f"""
    <div class="card" style="border-top-color:{cor}">
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
        card(baixos, "Baixo estoque", "#c0392b" if baixos > 0 else "#1a5c2a")

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

        col_nome.markdown(f"<span style='color:#111;font-weight:700'>{row['nome']}</span>", unsafe_allow_html=True)
        col_cod.markdown(f"<code style='color:#333;background:#f0ece6;padding:2px 6px;border-radius:5px'>{row['codigo_barras']}</code>", unsafe_allow_html=True)

        qtd = row["quantidade"]
        cor_qtd = "🔴" if qtd <= ESTOQUE_BAIXO else "🟢"
        col_qtd.markdown(f"<span style='color:#111;font-weight:700'>{cor_qtd} {qtd}</span>", unsafe_allow_html=True)

        col_custo.markdown(f"<span style='color:#222'>R$ {row['preco_custo']:.2f}</span>", unsafe_allow_html=True)
        col_venda.markdown(f"<span style='color:#222'>R$ {row['preco_venda']:.2f}</span>", unsafe_allow_html=True)

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
