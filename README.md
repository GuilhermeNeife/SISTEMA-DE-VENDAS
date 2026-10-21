# 📊 Sistema de Vendas - ERP Completo

Sistema de gestão comercial feito em **Python** com interface gráfica **Tkinter** e banco de dados **SQLite**. Roda direto no seu computador, sem precisar de internet, servidor ou instalar nada além do Python.

Ideal para pequenos negócios que vendem produtos e querem controlar clientes, estoque, compras, vendas, pagamentos e devoluções num só lugar.

---

## 🎯 O que o sistema faz

O sistema é dividido em **7 abas**, cada uma cuidando de uma parte do negócio:

### 📈 Dashboard
Tela inicial com os números do negócio em tempo real:
- Total faturado, recebido e a receber
- Lucro realizado e lucro esperado
- Ticket médio, quantidade de pedidos e total de vendas
- **Saldo em conta** (quanto entrou menos quanto saiu)
- Ranking dos produtos mais vendidos

Você pode filtrar tudo por **mês e ano**.

### 👥 Clientes
Cadastro de clientes com nome, telefone e observações. Cada cliente tem uma **Ficha Financeira** que mostra:
- Tudo que ele já comprou
- Quanto já pagou e quanto ainda deve
- Histórico completo de pedidos e pagamentos
- Possibilidade de excluir vendas ou pagamentos direto da ficha

### 📦 Produtos
Cadastro de produtos com nome, cor, preço padrão e categoria. O **estoque é atualizado automaticamente** conforme você registra compras, vendas e devoluções — não precisa mexer nele na mão.

### 🛒 Compras
Registro do que você compra dos fornecedores. O sistema:
- Calcula o **custo real de cada produto** (valor pago + parte do frete)
- Rateia o frete automaticamente entre os itens
- Soma tudo ao estoque
- Permite editar ou excluir uma compra (revertendo o estoque corretamente)

### 💵 Vendas
Registro do que você vende. O sistema:
- Avisa se o estoque é suficiente antes de fechar a venda
- Mostra o **último custo** do produto e o **preço sugerido**
- Calcula o **lucro de cada item** e da venda inteira
- Aceita desconto
- Dá baixa automática no estoque

### 💳 Pagamentos
Registro dos pagamentos recebidos. Aceita:
- Dinheiro, Pix, Cartão de Débito, Cartão de Crédito ou Transferência
- Pagamentos **parciais** (o cliente paga um pouco agora e o resto depois)
- O status da venda muda sozinho: **Aberto → Parcial → Pago**

### 🔄 Retiradas
Registro de movimentações que não são compra nem venda, como:
- Devolução de cliente
- Logística reversa
- Perda ou avaria
- Custo de envio
- Outros

Você escolhe se a operação **aumenta, diminui ou não mexe** no estoque.

---

## 🔧 Como funciona por dentro

### Cálculo de custo com frete
Quando você compra vários produtos de uma vez e paga um frete único, o sistema distribui o frete proporcionalmente ao valor de cada item:

```
frete do item = frete total × (valor do item ÷ valor total da compra)
custo unitário = (valor do item + frete do item) ÷ quantidade
```

### Cálculo de lucro
```
lucro do item = (preço de venda − custo unitário) × quantidade
```

### Saldo em conta (no dashboard)
```
saldo = tudo que foi pago pelos clientes
      − compras feitas
      − custos de frete das retiradas
      − reembolsos a clientes
```

---

## 🚀 Como rodar

### O que você precisa
- **Python 3.8 ou superior** instalado
- **Tkinter** (já vem com o Python na maioria dos sistemas)

### Passo a passo

**1. Baixe o projeto**
```bash
git clone https://github.com/SEU-USUARIO/sistema-vendas.git
cd sistema-vendas
```

**2. Confira se o Tkinter está disponível**
```bash
python -c "import tkinter; print('Tkinter OK')"
```

Se der erro:
| Sistema | Instalar com |
|---------|--------------|
| Ubuntu / Debian | `sudo apt-get install python3-tk` |
| Fedora | `sudo dnf install python3-tkinter` |
| macOS | `brew install python-tk` |
| Windows | Já vem instalado |

**3. Ajuste o caminho do banco de dados**

Abra `sistema_vendas.py` e procure esta linha perto do topo:

```python
pasta_sistema = r"C:\Users\gneife\Desktop\PROJETOS\SISTEMA DE VENDAS"
```

Troque por uma pasta qualquer no seu computador:

```python
# Windows
pasta_sistema = r"C:\MeusProjetos\SistemaVendas"

# Linux / Mac
pasta_sistema = os.path.join(os.path.expanduser("~"), "SistemaVendas")
```

**4. Execute**
```bash
python sistema_vendas.py
```

Na primeira execução o arquivo `erp_completo.db` é criado automaticamente nessa pasta. É ele que guarda todos os seus dados.

---

## 📖 Primeiros passos dentro do sistema

Siga esta ordem para começar:

1. **Cadastre seus clientes** → aba *Clientes*
2. **Cadastre seus produtos** → aba *Produtos*
3. **Registre uma compra** → aba *Compras* (o estoque sobe)
4. **Registre uma venda** → aba *Vendas* (o estoque desce)
5. **Registre o pagamento** → aba *Pagamentos*
6. **Acompanhe tudo no Dashboard**

---

## ⚠️ Coisas importantes de saber

- **Não tem login nem senha.** O sistema é feito para uso pessoal, num computador só seu.
- **O banco de dados não é criptografado.** É um arquivo `.db` normal — trate como documento confidencial.
- **Faça backup.** Copie o `erp_completo.db` de vez em quando para um pendrive ou nuvem. Se ele se perder, os dados vão junto.
- **Não apague o arquivo `.db`** pensando que é lixo. É ele que guarda tudo.

### Backup rápido
```bash
# Linux / Mac
cp erp_completo.db backup_$(date +%Y%m%d).db

# Windows (PowerShell)
Copy-Item erp_completo.db "backup_$(Get-Date -Format yyyyMMdd).db"
```

---

## 🎨 Personalização rápida

**Mudar a cor do tema** (no método `__init__`):
```python
self.root.configure(bg="#1e1e1e")  # fundo escuro
```

**Mudar o tamanho da janela:**
```python
largura = 1200
altura = 650
```

**Adicionar formas de pagamento** (na aba *Pagamentos*):
```python
self.pag_forma = ttk.Combobox(frame_add, values=[
    "Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito", "Transferência"
])
```

---

## 🗄️ Estrutura dos dados

O sistema guarda tudo em 8 tabelas:

| Tabela | O que guarda |
|--------|--------------|
| `clientes` | Cadastro de clientes |
| `produtos` | Catálogo com estoque e preço |
| `compras` / `compra_itens` | Compras e itens com frete rateado |
| `vendas` / `venda_itens` | Vendas e itens com custo e lucro |
| `pagamentos` | Cada pagamento recebido |
| `retiradas` | Devoluções, perdas e custos de envio |

---

## 🐛 Problemas comuns

| Problema | Solução |
|----------|---------|
| `No module named 'tkinter'` | Instale o Tkinter conforme a tabela acima |
| `unable to open database file` | Ajuste o caminho `pasta_sistema` no código |
| `database is locked` | Feche outras janelas do sistema abertas ao mesmo tempo |
| A janela não abre | O Python precisa de ambiente gráfico (não funciona em servidor sem tela) |

---

## 📄 Licença

Livre para uso pessoal e comercial. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

**Se este projeto te ajudou, deixa uma ⭐ no repositório!**
