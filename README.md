# 📊 Sistema de Vendas - ERP Completo

Sistema de gestão comercial (ERP) desenvolvido em Python com interface gráfica Tkinter e banco de dados SQLite. Ideal para pequenos e médios negócios que precisam controlar clientes, produtos, compras, vendas, pagamentos e movimentações de estoque.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
- [Lógica de Negócio](#lógica-de-negócio)
- [Personalização](#personalização)
- [Solução de Problemas](#solução-de-problemas)
- [Licença](#licença)

---

## 🎯 Visão Geral

O **Sistema de Vendas** é uma aplicação desktop completa que oferece:

- **Dashboard analítico** com indicadores financeiros em tempo real
- **Gestão de clientes** com ficha financeira detalhada
- **Controle de produtos** com categorização e estoque
- **Registro de compras** com rateio automático de frete
- **Sistema de vendas** com cálculo de lucro por item
- **Controle de pagamentos** (parciais e totais)
- **Gestão de retiradas/devoluções** com impacto no estoque

---

## ✨ Funcionalidades

### 📈 Dashboard
- **9 indicadores principais:**
  - Total Faturado
  - Total Recebido
  - A Receber
  - Lucro Realizado
  - Lucro Esperado
  - Total de Vendas
  - Ticket Médio
  - Quantidade de Pedidos
  - 💰 Saldo em Conta
- Filtro por **mês/ano**
- Ranking dos **10 produtos mais vendidos** por quantidade e faturamento

### 👥 Clientes
- Cadastro completo (nome, telefone, observações)
- Pesquisa em tempo real
- Edição e exclusão com validação
- **Ficha Financeira** com:
  - Resumo de compras, pagamentos e pendências
  - Lista de pedidos com status (Aberto/Parcial/Pago)
  - Detalhamento de itens por pedido
  - Pagamentos por pedido
  - Histórico completo de pagamentos
  - Filtro por período
  - Exclusão de vendas e pagamentos diretamente da ficha

### 📦 Produtos
- Cadastro com nome, cor, preço padrão e categoria
- Controle de estoque automático
- Pesquisa e edição
- Categorização para organização

### 🛒 Compras
- Registro com fornecedor, data e frete
- **Rateio automático de frete** proporcional ao valor de cada item
- Cálculo de custo unitário real (produto + frete)
- Atualização automática de estoque
- Edição com reversão e reaplicação de estoque
- Exclusão com reversão de estoque

### 💵 Vendas
- Seleção de cliente e produtos
- Verificação de **estoque disponível** antes de vender
- Exibição de **último custo** e **preço padrão**
- Cálculo automático de lucro por item
- Desconto por venda
- Atualização automática de estoque
- Edição com reversão de estoque e pagamentos
- Status automático: Aberto → Parcial → Pago

### 💳 Pagamentos
- Registro de pagamentos por venda
- Múltiplas formas: Dinheiro, Pix, Débito, Crédito, Transferência
- Atualização automática do status da venda
- Suporte a pagamentos parciais

### 🔄 Retiradas
- **5 tipos de movimentação:**
  - Devolução de Cliente
  - Logística Reversa
  - Perda/Avaria
  - Custo de Envio
  - Outros
- Controle de impacto no estoque (aumenta/diminui/nenhum)
- Registro de valores de custo, reembolso e frete
- Edição com reversão automática de estoque
- Exclusão com reversão de estoque

---

## ⚙️ Requisitos

- **Python 3.8+**
- **Tkinter** (geralmente incluso no Python)
- **SQLite3** (nativo do Python)
- Sistema operacional: Windows, Linux ou macOS

### Dependências
Nenhuma dependência externa necessária! O sistema usa apenas bibliotecas padrão do Python:
- `sqlite3`
- `os`
- `tkinter`
- `datetime`
- `calendar`

---

## 🚀 Instalação

### 1. Verificar Python
```bash
python --version
```

### 2. Verificar Tkinter
```bash
python -c "import tkinter; print('Tkinter OK')"
```

Se não tiver Tkinter instalado:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

### 3. Baixar o projeto
Salve o arquivo `sistema_vendas.py` em uma pasta de sua preferência.

### 4. Configurar o caminho do banco de dados

**⚠️ IMPORTANTE:** No código, localize a linha:

```python
pasta_sistema = r"C:\Users\gneife\Desktop\PROJETOS\SISTEMA DE VENDAS"
```

E altere para um caminho válido no seu computador. Exemplos:

```python
# Windows
pasta_sistema = r"C:\MeusProjetos\SistemaVendas"

# Linux/Mac
pasta_sistema = os.path.join(os.path.expanduser("~"), "SistemaVendas")
```

### 5. Executar
```bash
python sistema_vendas.py
```

O banco de dados `erp_completo.db` será criado automaticamente na primeira execução.

---

## 📖 Como Usar

### Fluxo Recomendado

1. **Cadastre Clientes** → aba *Clientes*
2. **Cadastre Produtos** → aba *Produtos*
3. **Registre Compras** → aba *Compras* (atualiza estoque e custo)
4. **Registre Vendas** → aba *Vendas* (baixa estoque)
5. **Registre Pagamentos** → aba *Pagamentos*
6. **Acompanhe no Dashboard** → aba *Dashboard*

### Dicas de Uso

- 🔍 Use a **barra de pesquisa** nas abas de clientes e produtos para localizar rapidamente
- 🖱️ **Clique duas vezes** ou selecione um item para editar
- 💡 Na aba **Vendas**, ao selecionar um produto, o sistema mostra:
  - Estoque disponível
  - Último custo de compra
  - Preço padrão sugerido
- 💰 O **Saldo em Conta** no dashboard considera:
  - (+) Todos os pagamentos recebidos
  - (-) Todas as compras realizadas
  - (-) Custos de frete das retiradas
  - (-) Reembolsos a clientes

---

## 🗄️ Estrutura do Banco de Dados

| Tabela | Descrição |
|--------|-----------|
| `clientes` | Cadastro de clientes |
| `produtos` | Catálogo de produtos com estoque |
| `compras` | Cabeçalho das compras |
| `compra_itens` | Itens da compra com frete rateado |
| `vendas` | Cabeçalho das vendas |
| `venda_itens` | Itens vendidos com custo e lucro |
| `pagamentos` | Pagamentos vinculados a vendas |
| `retiradas` | Movimentações especiais (devoluções, perdas, etc.) |

### Relacionamentos
```
clientes ──┬── vendas ──┬── venda_itens ── produtos
           │            └── pagamentos
           └── retiradas
           
produtos ──┬── compra_itens ── compras
           ├── venda_itens
           └── retiradas
```

---

## 🧮 Lógica de Negócio

### Cálculo de Custo com Frete
```
frete_item = frete_total × (valor_total_item / valor_total_compra)
custo_unitario = (valor_total_item + frete_item) / quantidade
```

### Cálculo de Lucro
```
lucro_item = (preco_venda - custo_unitario) × quantidade
lucro_venda = total_final - soma_custos
```

### Lucro Realizado (Dashboard)
Considera apenas a **proporção paga** de cada venda:
```
proporcao_paga = total_pago / total_venda
lucro_realizado += lucro_venda × proporcao_paga
```

### Saldo em Conta
```
saldo = Σ pagamentos - (Σ compras + Σ custos_frete_retiradas + Σ reembolsos)
```

### Status de Venda
- **Aberto**: nenhum pagamento
- **Parcial**: pagamento > 0 mas < total
- **Pago**: pagamento ≥ total

---

## 🎨 Personalização

### Alterar cores do tema
No método `__init__` da classe `ERP`, modifique:
```python
self.root.configure(bg="#1e1e1e")  # Fundo escuro
```

### Alterar tamanho da janela
```python
largura = 1200
altura = 650
```

### Alterar caminho do banco de dados
```python
pasta_sistema = r"SEU_CAMINHO_AQUI"
```

### Adicionar novas formas de pagamento
Na aba *Pagamentos*, localize:
```python
self.pag_forma = ttk.Combobox(frame_add, values=[
    "Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito", "Transferência"
], width=15)
```

---

## 🐛 Solução de Problemas

### Erro: "No module named 'tkinter'"
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Mac (com Homebrew)
brew install python-tk
```

### Erro: "unable to open database file"
- Verifique se o caminho em `pasta_sistema` existe
- Verifique permissões de escrita na pasta
- Em Windows, evite caminhos com caracteres especiais

### Erro: "database is locked"
- Feche outras instâncias do sistema
- Verifique se não há outro programa acessando o `.db`

### Interface não abre
- Verifique se o Python tem suporte a GUI (ambiente gráfico disponível)
- Em servidores remotos, use VNC ou X11 forwarding

### Estoque incorreto
- Verifique se a compra foi registrada corretamente
- Use a ficha do produto para auditar movimentações
- Exclua e recadastre a operação problemática

---

## 📝 Notas Técnicas

### Performance
- O sistema usa **transações** (`BEGIN TRANSACTION`) para operações críticas
- **Rollback automático** em caso de erro
- Índices implícitos nas chaves primárias e estrangeiras

### Segurança
- ⚠️ **Não há autenticação de usuários** — recomendado apenas para uso pessoal ou em rede confiável
- ⚠️ O banco de dados **não é criptografado**
- ⚠️ Faça **backups regulares** do arquivo `erp_completo.db`

### Backup
Copie o arquivo `erp_completo.db` para um local seguro periodicamente:
```bash
# Exemplo de backup manual
cp erp_completo.db backup_$(date +%Y%m%d).db
```

---

## 🔮 Melhorias Futuras (Sugestões)

- [ ] Sistema de login e permissões
- [ ] Relatórios em PDF
- [ ] Exportação para Excel
- [ ] Backup automático
- [ ] Gráficos no dashboard (matplotlib)
- [ ] Cadastro de fornecedores
- [ ] Múltiplos usuários em rede (PostgreSQL/MySQL)
- [ ] Emissão de recibos e notas
- [ ] Código de barras

---

## 📄 Licença

Este projeto é fornecido **"como está"**, sem garantias. Uso livre para fins pessoais e comerciais.

---

## 👨‍💻 Autor

Desenvolvido como sistema de gestão completo para pequenos negócios.

**Contribuições são bem-vindas!** Sinta-se livre para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

---

## 📞 Suporte

Para dúvidas técnicas:
1. Verifique a seção [Solução de Problemas](#solução-de-problemas)
2. Revise a [Lógica de Negócio](#lógica-de-negócio)
3. Consulte o código-fonte (bem comentado)

---

**⭐ Se este projeto te ajudou, considere dar uma estrela!**
