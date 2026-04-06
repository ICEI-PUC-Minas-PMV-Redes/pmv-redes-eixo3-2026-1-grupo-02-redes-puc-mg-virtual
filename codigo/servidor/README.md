# 📂 Pasta do Servidor (Back-end)

Esta pasta contém o núcleo da aplicação. **Não mova os arquivos desta pasta** sem atualizar os caminhos no arquivo `.bat` do cliente.

## 📄 Arquivos contidos:
* **`app.py`**: Código fonte desenvolvido em Python/Streamlit.
* **`estoque_mercado.db`**: Banco de dados SQLite (gerado automaticamente). **Este arquivo deve ter backup frequente.**

## ⚙️ Manutenção Técnica:
1.  **Dependências:**
2.  ```bash
    pip install streamlit pandas xlsxwriter
    ```
3.  **Modificações:** Sempre que alterar o `app.py`, o Streamlit atualizará a interface automaticamente no cliente.
4.  **Endereço de Rede:** Para que o cliente acesse de outros dispositivos, o servidor deve manter um IP fixo na rede local.

---
> **Atenção:** Se o arquivo `estoque_mercado.db` for deletado, todos os dados de estoque serão perdidos.
