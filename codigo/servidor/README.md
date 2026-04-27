# 🏪 Meu Mercadinho — Documentação do Servidor (Back-end)

> Pasta responsável pelo núcleo da aplicação. Não mova, renomeie ou exclua arquivos desta pasta sem antes atualizar os caminhos no arquivo `.bat` do cliente.

---

## 📁 Arquivos desta pasta

| Arquivo | Descrição |
|---|---|
| `app.py` | Código-fonte principal em Python/Streamlit. Contém toda a lógica de negócio, interface e integração com o banco de dados. |
| `estoque_mercado.db` | Banco de dados SQLite. **Gerado automaticamente** na primeira execução. Contém todos os registros de estoque e produtos. |
| `iniciar.bat` | Atalho para iniciar o servidor com duplo clique. Deve ser atualizado sempre que o IP ou a pasta forem alterados. |
| `SEU-IP-AQUI.pem` | Certificado SSL vinculado ao IP desta máquina na rede interna. O nome do arquivo corresponde ao IP. |
| `SEU-IP-AQUI-key.pem` | Chave privada do certificado SSL. **Nunca compartilhe este arquivo.** |

> ⚠️ **ATENÇÃO:** Se o arquivo `estoque_mercado.db` for deletado, **todos os dados de estoque serão perdidos permanentemente**. Faça backup com frequência.

---

## 🔍 Passo zero — Descubra o IP desta máquina

> ⚠️ **Este passo é obrigatório antes de qualquer instalação.** O IP da máquina servidora precisa estar correto no comando de inicialização, nos arquivos de certificado e no `iniciar.bat`. Se o IP estiver errado, o sistema não vai funcionar na rede.

Abra o **Prompt de Comando** (`cmd`) e digite:

```
ipconfig
```

Procure pela seção **"Adaptador de Rede sem Fio Wi-Fi"** ou **"Adaptador Ethernet"** e anote o valor de **"Endereço IPv4"**:

```
Endereço IPv4. . . . . . . . . . . . . : 192.168.15.9
                                          ^^^^^^^^^^^^^^
                                          Este é o seu IP — anote-o agora
```

> 📌 O IP começa sempre com `192.168.` seguido de dois números. **Ignore** qualquer endereço que comece com `127.` (esse é o loopback local, não serve para a rede).

Nos exemplos desta documentação usamos `192.168.15.9` como referência. **Substitua sempre pelo IP real que você anotou acima.**

---

## ⚙️ Pré-requisitos (instalar uma única vez)

### 1. Python 3.10 ou superior

Verifique se o Python já está instalado abrindo o **Prompt de Comando** e digitando:

```
python --version
```

Se não estiver instalado, baixe em: https://www.python.org/downloads/

> ✅ Durante a instalação, marque a opção **"Add Python to PATH"** antes de clicar em Install.

---

### 2. Dependências Python

Com o Python instalado, abra o **Prompt de Comando** na pasta do servidor e execute:

```
pip install streamlit pandas requests Pillow pyzbar xlsxwriter
```

| Biblioteca | Finalidade |
|---|---|
| `streamlit` | Interface web da aplicação (telas, botões, tabelas) |
| `pandas` | Manipulação e exibição de dados em tabelas |
| `requests` | Consulta à API OpenFoodFacts para buscar nome e imagem dos produtos |
| `Pillow` | Processamento de imagens (necessário para leitura de código de barras) |
| `pyzbar` | Decodificação de códigos de barras a partir de fotos |
| `xlsxwriter` | Exportação de relatórios em formato Excel (.xlsx) |

---

### 3. Dependência do sistema: `zbar` (necessária para leitura de código de barras)

O `pyzbar` depende de uma biblioteca do sistema chamada **zbar**. No Windows, ela não vem instalada automaticamente.

**Passos:**

1. Baixe o instalador em: https://sourceforge.net/projects/zbar/files/zbar/0.10/
2. Execute o instalador (`zbar-0.10-setup.exe`)
3. Reinicie o computador após a instalação

> Se a leitura de código de barras não funcionar mesmo após instalar o `pyzbar`, provavelmente esta etapa está faltando.

---

## ▶️ Como iniciar o servidor

O sistema usa **HTTPS com certificado SSL** e precisa ser iniciado com o **IP desta máquina na rede interna** (o mesmo que você anotou no Passo Zero). Os arquivos de certificado (`.pem`) já devem estar na pasta do servidor com o IP no nome.

### Opção A — Duplo clique (recomendado)

Dê um duplo clique no arquivo `iniciar.bat`.

O `iniciar.bat` deve conter o seguinte — **substituindo `192.168.15.9` pelo IP real desta máquina:**

```bat
@echo off
cd /d %~dp0
streamlit run app.py ^
  --server.address 0.0.0.0 ^
  --server.port 8501 ^
  --server.sslCertFile ./192.168.15.9.pem ^
  --server.sslKeyFile ./192.168.15.9-key.pem
pause
```

### Opção B — Manualmente pelo terminal

1. Abra o **Prompt de Comando** (`cmd`)
2. Navegue até a pasta do servidor:
   ```
   cd C:\caminho\para\pasta\servidor
   ```
3. Execute o comando abaixo, **substituindo `192.168.15.9` pelo IP real desta máquina:**
   ```
   streamlit run app.py ^
     --server.address 0.0.0.0 ^
     --server.port 8501 ^
     --server.sslCertFile ./192.168.15.9.pem ^
     --server.sslKeyFile ./192.168.15.9-key.pem
   ```

> ℹ️ O `^` é o caractere de continuação de linha no `cmd`. Se estiver usando **PowerShell**, substitua `^` por `` ` `` (acento grave).

Após iniciar, o sistema estará disponível em — **substituindo pelo seu IP:**

```
https://192.168.15.9:8501
```

Se o navegador exibir um aviso de "conexão não segura" ou "sua conexão não é particular", clique em **Avançado → Continuar para o site**. Isso ocorre porque o certificado é local, não emitido por uma autoridade pública — é seguro prosseguir dentro da rede interna.

> 🔴 **Mantenha o terminal aberto** enquanto o sistema estiver em uso. Fechá-lo encerrará o servidor.

---

## 🌐 Acesso pela rede local (outros dispositivos)

Para acessar de outros computadores, celulares ou tablets na mesma rede Wi-Fi, use:

```
https://SEU-IP-DA-REDE:8501
```

**Exemplo** (se o IP desta máquina for `192.168.15.9`):

```
https://192.168.15.9:8501
```

> 📌 **IP Fixo Obrigatório:** O IP está gravado no comando de inicialização, nos arquivos `.pem` e no `iniciar.bat`. Se o IP mudar (por exemplo após reiniciar o roteador), o sistema parará de funcionar. Configure o roteador para **reservar sempre o mesmo IP para esta máquina** (reserva de DHCP) ou configure um IP estático no Windows.

---

## 💾 Backup do banco de dados

O arquivo `estoque_mercado.db` é o único arquivo que precisa de backup. Basta **copiar este arquivo** para outro local (pendrive, Google Drive, etc.).

**Boas práticas:**

- Faça backup ao fim de cada dia de trabalho
- Nomeie o arquivo com a data: `estoque_2025-06-15.db`
- Mantenha ao menos 7 cópias (uma por dia da semana)
- Guarde uma cópia fora do computador servidor (nuvem ou dispositivo externo)

### Como restaurar um backup

1. **Pare o servidor** (feche o terminal)
2. Substitua o arquivo `estoque_mercado.db` pelo arquivo de backup
3. Renomeie o arquivo de backup para `estoque_mercado.db`
4. Reinicie o servidor normalmente

---

## 🔄 Atualizações do sistema

Sempre que o arquivo `app2.py` for alterado, o Streamlit detecta a mudança automaticamente e exibe um botão **"Rerun"** no navegador. Clique nele para aplicar as atualizações sem reiniciar o servidor.

Se o botão não aparecer, feche e reabra o terminal e execute o servidor novamente.

---

## 🛠️ Solução de problemas

| Problema | Solução |
|---|---|
| Não sei qual é o IP desta máquina | Abra o `cmd`, digite `ipconfig` e procure "Endereço IPv4" (começa com `192.168.`) |
| Aviso de "conexão não segura" no navegador | Clique em **Avançado → Continuar para o site**. É seguro na rede interna. |
| Erro `Module not found` ao iniciar | Execute: `pip install streamlit pandas requests Pillow pyzbar xlsxwriter` |
| Cliente não acessa pela rede | Confirme o IP atual com `ipconfig` e verifique se está igual ao do `iniciar.bat` |
| IP da máquina mudou | Gere novos certificados `.pem` para o novo IP, renomeie os arquivos e atualize o `iniciar.bat` |
| Navegador não abre automaticamente | Acesse manualmente: `https://SEU-IP:8501` |
| Imagens dos produtos não aparecem | Clique em **"Sincronizar imagens"** na tela de Estoque. Requer conexão com a internet. |
| Câmera não funciona para ler código | Acesse pelo IP da rede (`https://SEU-IP:8501`), nunca por `localhost` |
| Código de barras não é detectado | Verifique se o `zbar` está instalado no sistema (ver seção de pré-requisitos) |
| Banco de dados corrompido | Pare o servidor e restaure o backup mais recente do arquivo `.db` |
| Porta 8501 já em uso | Encerre outros processos Streamlit ou reinicie o computador |

---

## 📋 Resumo rápido

```
# 1. Descobrir o IP desta máquina (obrigatório)
ipconfig
→ anote o "Endereço IPv4" (ex: 192.168.15.9)

# 2. Instalar dependências (apenas uma vez)
pip install streamlit pandas requests Pillow pyzbar xlsxwriter

# 3. Iniciar o servidor — substitua o IP pelo seu
streamlit run app.py ^
  --server.address 0.0.0.0 ^
  --server.port 8501 ^
  --server.sslCertFile ./SEU-IP.pem ^
  --server.sslKeyFile ./SEU-IP-key.pem

# 4. Endereço de acesso — substitua o IP pelo seu
https://SEU-IP:8501
```

---

*Meu Mercadinho — Documentação Interna do Servidor*
