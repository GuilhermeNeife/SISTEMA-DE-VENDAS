import sqlite3
import os
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
import calendar

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
pasta_sistema = r"C:\Users\gneife\Desktop\PROJETOS\SISTEMA DE VENDAS"
os.makedirs(pasta_sistema, exist_ok=True)
db_path = os.path.join(pasta_sistema, "erp_completo.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# TABELAS
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    obs TEXT,
    data_cadastro TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cor TEXT,
    preco_padrao REAL,
    estoque REAL DEFAULT 0,
    categoria TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor TEXT,
    frete_total REAL,
    total_produtos REAL,
    total_compra REAL,
    data TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS compra_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compra_id INTEGER,
    produto_id INTEGER,
    quantidade REAL,
    valor_total REAL,
    frete_rateado REAL,
    custo_unitario REAL,
    FOREIGN KEY(compra_id) REFERENCES compras(id),
    FOREIGN KEY(produto_id) REFERENCES produtos(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    total REAL,
    desconto REAL,
    lucro_total REAL,
    status TEXT,
    data TEXT,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS venda_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER,
    produto_id INTEGER,
    quantidade REAL,
    preco_venda REAL,
    custo_unitario REAL,
    lucro REAL,
    FOREIGN KEY(venda_id) REFERENCES vendas(id),
    FOREIGN KEY(produto_id) REFERENCES produtos(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS pagamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER,
    valor REAL,
    forma_pagamento TEXT,
    data TEXT,
    FOREIGN KEY(venda_id) REFERENCES vendas(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS retiradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    tipo TEXT,
    cliente_id INTEGER,
    produto_id INTEGER,
    quantidade REAL,
    valor_custo REAL,
    valor_reembolso REAL,
    custo_frete REAL,
    observacao TEXT,
    impacta_estoque TEXT,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id),
    FOREIGN KEY(produto_id) REFERENCES produtos(id)
)
""")
try:
    cursor.execute("ALTER TABLE retiradas ADD COLUMN custo_frete REAL DEFAULT 0")
except:
    pass
conn.commit()

# =========================================================
# CLASSE PRINCIPAL
# =========================================================
class ERP:
    def __init__(self, root):
        self.root = root

        largura = 1200
        altura = 650

        self.root.minsize(largura, altura)
        self.root.geometry(f"{largura}x{altura}")
        self.root.title("SISTEMA DE VENDAS")
        self.root.configure(bg="#1e1e1e")

        self.root.update_idletasks()

        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()

        altura_util = self.root.winfo_screenheight() - 80

        x = (largura_tela - largura) // 2
        y = (altura_util - altura) // 2

        self.root.geometry(f"{largura}x{altura}+{x}+{y}")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white",
                        fieldbackground="#2b2b2b", rowheight=28, font=("Arial", 9))
        style.configure("Treeview.Heading", background="#111111", foreground="white",
                        font=("Arial", 9, "bold"))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=BOTH, expand=True)

        self.tab_dashboard = Frame(self.notebook, bg="#1e1e1e")
        self.tab_clientes = Frame(self.notebook, bg="#1e1e1e")
        self.tab_produtos = Frame(self.notebook, bg="#1e1e1e")
        self.tab_compras = Frame(self.notebook, bg="#1e1e1e")
        self.tab_vendas = Frame(self.notebook, bg="#1e1e1e")
        self.tab_pagamentos = Frame(self.notebook, bg="#1e1e1e")
        self.tab_retiradas = Frame(self.notebook, bg="#1e1e1e")

        self.notebook.add(self.tab_dashboard, text="Dashboard")
        self.notebook.add(self.tab_clientes, text="Clientes")
        self.notebook.add(self.tab_produtos, text="Produtos")
        self.notebook.add(self.tab_compras, text="Compras")
        self.notebook.add(self.tab_vendas, text="Vendas")
        self.notebook.add(self.tab_pagamentos, text="Pagamentos")
        self.notebook.add(self.tab_retiradas, text="Retiradas")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.dashboard_ui()
        self.clientes_ui()
        self.produtos_ui()
        self.compras_ui()
        self.vendas_ui()
        self.pagamentos_ui()
        self.retiradas_ui()

        self.atualizar_todos_combos()
        self.atualizar_opcoes_mes_ano()
        self.atualizar_dashboard_filtrado()

    # ---------------------------------------------------------
    # UTILITÁRIOS
    # ---------------------------------------------------------
    def on_tab_changed(self, event):
        tab = self.notebook.select()
        if tab == self.tab_compras:
            self.atualizar_combo_produtos()
            self.carregar_lista_compras()
        elif tab == self.tab_vendas:
            self.atualizar_combo_clientes_venda()
            self.atualizar_combo_produtos_venda()
            self.carregar_lista_vendas()
        elif tab == self.tab_pagamentos:
            self.atualizar_combo_clientes_pagamento()
        elif tab == self.tab_retiradas:
            self.atualizar_combo_clientes_retirada()
            self.atualizar_combo_produtos_retirada()
            self.carregar_lista_retiradas()

    def atualizar_todos_combos(self):
        self.atualizar_combo_produtos()
        self.atualizar_combo_produtos_venda()
        self.atualizar_combo_clientes_venda()
        self.atualizar_combo_clientes_pagamento()
        self.atualizar_combo_clientes_retirada()
        self.atualizar_combo_produtos_retirada()
        self.atualizar_lista_categorias()

    # ---------------------------------------------------------
    # DASHBOARD (com Saldo em Conta)
    # ---------------------------------------------------------
    def dashboard_ui(self):
        main_frame = Frame(self.tab_dashboard, bg="#1e1e1e")
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Filtro de data
        filter_frame = Frame(main_frame, bg="#1e1e1e")
        filter_frame.pack(fill=X, pady=5)

        Label(filter_frame, text="Mês/Ano:", bg="#1e1e1e", fg="white", font=("Arial", 10)).pack(side=LEFT, padx=5)
        self.mes_ano_var = StringVar()
        self.cmb_mes_ano = ttk.Combobox(filter_frame, textvariable=self.mes_ano_var, width=12, state="readonly")
        self.cmb_mes_ano.pack(side=LEFT, padx=5)
        self.cmb_mes_ano.bind("<<ComboboxSelected>>", self.atualizar_dashboard_filtrado)

        Button(filter_frame, text="Atualizar", bg="#2980b9", fg="white", command=self.atualizar_dashboard_filtrado).pack(side=LEFT, padx=10)

        # Cards de indicadores (9 cards)
        card_frame = Frame(main_frame, bg="#1e1e1e")
        card_frame.pack(fill=X, pady=10)

        self.cards = {}
        indicadores = [
            ("total_faturado", "TOTAL FATURADO", "#27ae60"),
            ("total_recebido", "TOTAL RECEBIDO", "#2980b9"),
            ("a_receber", "A RECEBER", "#c0392b"),
            ("lucro_realizado", "LUCRO REALIZADO", "#8e44ad"),
            ("lucro_esperado", "LUCRO ESPERADO", "#f39c12"),
            ("total_vendas", "TOTAL VENDAS", "#1abc9c"),
            ("ticket_medio", "TICKET MÉDIO", "#3498db"),
            ("qtd_pedidos", "QTD. PEDIDOS", "#e67e22"),
            ("saldo_conta", "💰 SALDO EM CONTA", "#2ecc71"),
        ]

        row, col = 0, 0
        for key, label, cor in indicadores:
            frame = LabelFrame(card_frame, text=label, bg="#2c2c2c", fg="white", font=("Arial", 9, "bold"), relief=FLAT)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            lbl_valor = Label(frame, text="R$ 0,00", bg="#2c2c2c", fg=cor, font=("Arial", 14, "bold"), width=14)
            lbl_valor.pack(padx=10, pady=10)
            self.cards[key] = lbl_valor
            col += 1
            if col == 4:
                col = 0
                row += 1

        # Tabela de produtos mais vendidos
        top_frame = LabelFrame(main_frame, text="🏆 Produtos Mais Vendidos (por quantidade)", bg="#2c2c2c", fg="white", font=("Arial", 10, "bold"))
        top_frame.pack(fill=BOTH, expand=True, pady=10)

        self.tree_top_produtos = ttk.Treeview(top_frame, columns=("produto", "qtd", "faturamento"), show="headings", height=6)
        self.tree_top_produtos.heading("produto", text="Produto")
        self.tree_top_produtos.heading("qtd", text="Quantidade")
        self.tree_top_produtos.heading("faturamento", text="Faturamento (R$)")
        self.tree_top_produtos.column("produto", width=250)
        self.tree_top_produtos.column("qtd", width=100, anchor="center")
        self.tree_top_produtos.column("faturamento", width=120, anchor="center")
        self.tree_top_produtos.pack(fill=BOTH, expand=True, padx=5, pady=5)

    def atualizar_opcoes_mes_ano(self):
        from datetime import datetime, timedelta
        hoje = datetime.now()
        opcoes = []
        for i in range(12):
            data = hoje - timedelta(days=30*i)
            opcoes.append(data.strftime("%m/%Y"))
        opcoes = sorted(set(opcoes), key=lambda x: (x.split('/')[1], x.split('/')[0]))
        self.cmb_mes_ano['values'] = opcoes
        if opcoes:
            self.mes_ano_var.set(opcoes[-1])

    def obter_filtro_data(self):
        mes_ano = self.mes_ano_var.get()
        if not mes_ano:
            from datetime import datetime
            mes_ano = datetime.now().strftime("%m/%Y")
        mes, ano = mes_ano.split('/')
        data_ini = f"{ano}-{mes}-01"
        ultimo_dia = calendar.monthrange(int(ano), int(mes))[1]
        data_fim = f"{ano}-{mes}-{ultimo_dia}"
        return data_ini, data_fim

    def atualizar_dashboard_filtrado(self, event=None):
        data_ini, data_fim = self.obter_filtro_data()

        # Vendas no período
        cursor.execute("""
            SELECT id, total, desconto, lucro_total, status
            FROM vendas
            WHERE substr(data, 7, 4) || '-' || substr(data, 4, 2) || '-' || substr(data, 1, 2)
                BETWEEN ? AND ?
        """, (data_ini, data_fim))
        vendas = cursor.fetchall()
        ids_vendas = [v[0] for v in vendas]

        total_faturado = sum(v[1] for v in vendas)
        lucro_esperado = sum(v[3] for v in vendas)
        qtd_pedidos = len(vendas)

        if ids_vendas:
            placeholders = ','.join(['?']*len(ids_vendas))
            cursor.execute(f"""
                SELECT SUM(valor) FROM pagamentos
                WHERE venda_id IN ({placeholders})
            """, ids_vendas)
            total_recebido = cursor.fetchone()[0] or 0
        else:
            total_recebido = 0

        a_receber = total_faturado - total_recebido

        lucro_realizado = 0.0
        for v in vendas:
            venda_id, total, desc, lucro_total, status = v
            if total > 0:
                cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM pagamentos WHERE venda_id=?", (venda_id,))
                pago = cursor.fetchone()[0]
                proporcao = pago / total
                lucro_realizado += lucro_total * proporcao

        ticket_medio = total_faturado / qtd_pedidos if qtd_pedidos > 0 else 0

        # ----- SALDO EM CONTA (TOTAL, SEM FILTRO) -----
        cursor.execute("SELECT SUM(valor) FROM pagamentos")
        total_recebido_geral = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(total_compra) FROM compras")
        total_gasto_compras = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(custo_frete) FROM retiradas")
        total_custos_retiradas = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(valor_reembolso) FROM retiradas")
        total_reembolsos = cursor.fetchone()[0] or 0

        saldo_conta = total_recebido_geral - (total_gasto_compras + total_custos_retiradas + total_reembolsos)

        def fmt(valor):
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        self.cards["total_faturado"].config(text=fmt(total_faturado))
        self.cards["total_recebido"].config(text=fmt(total_recebido))
        self.cards["a_receber"].config(text=fmt(a_receber))
        self.cards["lucro_realizado"].config(text=fmt(lucro_realizado))
        self.cards["lucro_esperado"].config(text=fmt(lucro_esperado))
        self.cards["total_vendas"].config(text=fmt(total_faturado))
        self.cards["ticket_medio"].config(text=fmt(ticket_medio))
        self.cards["qtd_pedidos"].config(text=str(qtd_pedidos))
        self.cards["saldo_conta"].config(text=fmt(saldo_conta))

        # Top produtos
        for item in self.tree_top_produtos.get_children():
            self.tree_top_produtos.delete(item)

        if ids_vendas:
            placeholders = ','.join(['?']*len(ids_vendas))
            cursor.execute(f"""
                SELECT p.nome,
                       SUM(vi.quantidade) as qtd_total,
                       SUM(vi.preco_venda * vi.quantidade) as faturamento
                FROM venda_itens vi
                JOIN produtos p ON vi.produto_id = p.id
                WHERE vi.venda_id IN ({placeholders})
                GROUP BY vi.produto_id
                ORDER BY qtd_total DESC
                LIMIT 10
            """, ids_vendas)
            for row in cursor.fetchall():
                qtd = row[1]
                qtd_str = f"{qtd:.2f}" if qtd % 1 != 0 else str(int(qtd))
                self.tree_top_produtos.insert("", END, values=(
                    row[0],
                    qtd_str,
                    fmt(row[2])
                ))

    # ---------------------------------------------------------
    # CLIENTES
    # ---------------------------------------------------------
    def clientes_ui(self):
        frame_form = Frame(self.tab_clientes, bg="#1e1e1e")
        frame_form.pack(fill=X, pady=10, padx=10)
        self.entry_cliente = {}
        campos = ["Nome:", "Telefone:", "Observações:"]
        for i, lbl in enumerate(campos):
            Label(frame_form, text=lbl, bg="#1e1e1e", fg="white").grid(row=i, column=0, sticky=W, padx=5, pady=2)
            entry = Entry(frame_form, width=30)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entry_cliente[lbl[:-1].lower()] = entry
        self.data_cadastro = datetime.now().strftime("%d/%m/%Y")
        Label(frame_form, text="Data Cadastro:", bg="#1e1e1e", fg="white").grid(row=3, column=0, sticky=W, padx=5)
        Label(frame_form, text=self.data_cadastro, bg="#1e1e1e", fg="white").grid(row=3, column=1, sticky=W)

        btn_frame = Frame(frame_form, bg="#1e1e1e")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        Button(btn_frame, text="Salvar Cliente", bg="#27ae60", fg="white", command=self.salvar_cliente).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Editar Cliente", bg="#f39c12", fg="white", command=self.editar_cliente).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Excluir Cliente", bg="#e74c3c", fg="white", command=self.excluir_cliente).pack(side=LEFT, padx=5)

        frame_pesq = Frame(self.tab_clientes, bg="#1e1e1e")
        frame_pesq.pack(fill=X, padx=10)
        Label(frame_pesq, text="Pesquisar:", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.pesq_cliente = Entry(frame_pesq, width=40)
        self.pesq_cliente.pack(side=LEFT, padx=5)
        self.pesq_cliente.bind("<KeyRelease>", lambda e: self.carregar_clientes())

        self.tree_clientes = ttk.Treeview(self.tab_clientes, columns=("id", "nome", "telefone", "saldo"), show="headings")
        self.tree_clientes.heading("id", text="ID")
        self.tree_clientes.heading("nome", text="NOME")
        self.tree_clientes.heading("telefone", text="TELEFONE")
        self.tree_clientes.heading("saldo", text="SALDO DEVEDOR (R$)")
        self.tree_clientes.column("saldo", width=120)
        self.tree_clientes.pack(fill=BOTH, expand=True, padx=10, pady=10)

        Button(self.tab_clientes, text="Abrir Ficha Financeira", bg="#2980b9", fg="white",
               command=self.ficha_cliente).pack(pady=5)
        self.carregar_clientes()

    def salvar_cliente(self):
        nome = self.entry_cliente["nome"].get().strip()
        if not nome:
            messagebox.showerror("Erro", "Nome é obrigatório")
            return
        cursor.execute("INSERT INTO clientes (nome, telefone, obs, data_cadastro) VALUES (?,?,?,?)",
                       (nome, self.entry_cliente["telefone"].get(), self.entry_cliente["observações"].get(), self.data_cadastro))
        conn.commit()
        for entry in self.entry_cliente.values():
            entry.delete(0, END)
        self.carregar_clientes()
        self.atualizar_todos_combos()
        messagebox.showinfo("Sucesso", "Cliente cadastrado")

    def carregar_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        busca = self.pesq_cliente.get()
        cursor.execute("SELECT id, nome, telefone FROM clientes WHERE nome LIKE ?", (f"%{busca}%",))
        for row in cursor.fetchall():
            cliente_id = row[0]
            cursor.execute("SELECT SUM(total) FROM vendas WHERE cliente_id=?", (cliente_id,))
            total_comprado = cursor.fetchone()[0] or 0
            cursor.execute("SELECT SUM(valor) FROM pagamentos WHERE venda_id IN (SELECT id FROM vendas WHERE cliente_id=?)", (cliente_id,))
            total_pago = cursor.fetchone()[0] or 0
            saldo = total_comprado - total_pago
            self.tree_clientes.insert("", END, values=(row[0], row[1], row[2], f"{saldo:.2f}" if saldo > 0 else "0.00"))

    def editar_cliente(self):
        selecionado = self.tree_clientes.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return
        cliente_id = self.tree_clientes.item(selecionado[0])['values'][0]
        cursor.execute("SELECT nome, telefone, obs FROM clientes WHERE id=?", (cliente_id,))
        dados = cursor.fetchone()
        if not dados:
            return
        janela = Toplevel(self.root)
        janela.title("Editar Cliente")
        janela.geometry("400x250")
        janela.configure(bg="#1e1e1e")
        entries = {}
        for i, campo in enumerate(["Nome", "Telefone", "Observações"]):
            Label(janela, text=campo, bg="#1e1e1e", fg="white").grid(row=i, column=0, padx=10, pady=5)
            entry = Entry(janela, width=30)
            entry.insert(0, dados[i])
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[campo] = entry

        def salvar_edicao():
            novo_nome = entries["Nome"].get().strip()
            if not novo_nome:
                messagebox.showerror("Erro", "Nome obrigatório")
                return
            cursor.execute("UPDATE clientes SET nome=?, telefone=?, obs=? WHERE id=?",
                           (novo_nome, entries["Telefone"].get(), entries["Observações"].get(), cliente_id))
            conn.commit()
            janela.destroy()
            self.carregar_clientes()
            self.atualizar_todos_combos()
            messagebox.showinfo("Sucesso", "Cliente atualizado")

        Button(janela, text="Salvar", bg="#27ae60", fg="white", command=salvar_edicao).grid(row=3, column=0, columnspan=2, pady=20)

    def excluir_cliente(self):
        selecionado = self.tree_clientes.selection()
        if not selecionado:
            return
        cliente_id = self.tree_clientes.item(selecionado[0])['values'][0]
        cursor.execute("SELECT COUNT(*) FROM vendas WHERE cliente_id=?", (cliente_id,))
        qtd = cursor.fetchone()[0]
        if qtd > 0:
            if not messagebox.askyesno("Atenção", f"Cliente possui {qtd} venda(s). Excluir mesmo assim? (Vendas serão mantidas sem cliente)"):
                return
        if messagebox.askyesno("Confirmar", "Excluir cliente?"):
            cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
            conn.commit()
            self.carregar_clientes()
            self.atualizar_todos_combos()
            messagebox.showinfo("Sucesso", "Cliente excluído")

    # ---------------------------------------------------------
    # FICHA FINANCEIRA (mantida)
    # ---------------------------------------------------------
    def ficha_cliente(self):
        selecionado = self.tree_clientes.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return

        cliente_id = self.tree_clientes.item(selecionado[0])['values'][0]
        cursor.execute("SELECT nome FROM clientes WHERE id=?", (cliente_id,))
        nome = cursor.fetchone()[0]

        janela = Toplevel(self.root)
        janela.title(f"Ficha Financeira - {nome}")

        largura, altura = 1100, 600

        janela.minsize(largura, altura)
        janela.geometry(f"{largura}x{altura}")
        janela.configure(bg="#1e1e1e")

        def centralizar():
            janela.update_idletasks()
            screen_w = janela.winfo_screenwidth()
            screen_h = janela.winfo_screenheight()
            x = (screen_w - largura) // 2
            y = (screen_h - altura) // 2
            janela.geometry(f"{largura}x{altura}+{x}+{y}")

        janela.after(0, centralizar)

        frame_resumo = Frame(janela, bg="#2c2c2c")
        frame_resumo.pack(fill=X, padx=10, pady=10)
        lbl_resumo = Label(frame_resumo, text="", bg="#2c2c2c", fg="white",
                           font=("Arial", 11, "bold"), justify=LEFT)
        lbl_resumo.pack(anchor="w", padx=10, pady=10)

        frame_filtro = Frame(janela, bg="#1e1e1e")
        frame_filtro.pack(fill=X, padx=10, pady=5)
        Label(frame_filtro, text="Filtrar Pedidos por Data:", bg="#1e1e1e", fg="white").pack(side=LEFT, padx=5)
        self.filtro_data_ini = Entry(frame_filtro, width=12)
        self.filtro_data_ini.insert(0, "01/01/2000")
        self.filtro_data_ini.pack(side=LEFT, padx=5)
        Label(frame_filtro, text="até", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.filtro_data_fim = Entry(frame_filtro, width=12)
        self.filtro_data_fim.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.filtro_data_fim.pack(side=LEFT, padx=5)
        Button(frame_filtro, text="Aplicar Filtro", bg="#2980b9", fg="white",
               command=lambda: carregar_pedidos()).pack(side=LEFT, padx=10)

        interno_notebook = ttk.Notebook(janela)
        interno_notebook.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Aba 1: Lista de Pedidos
        tab_pedidos = Frame(interno_notebook, bg="#1e1e1e")
        interno_notebook.add(tab_pedidos, text="📋 Pedidos do Cliente")

        tree_vendas = ttk.Treeview(tab_pedidos, columns=(
            "id", "data", "total", "desconto", "pago", "faltante", "qtd_pag", "status"
        ), show="headings", height=12)
        for col in tree_vendas["columns"]:
            tree_vendas.heading(col, text=col.upper())
        tree_vendas.column("id", width=50, anchor="center")
        tree_vendas.column("data", width=100, anchor="center")
        tree_vendas.column("total", width=100, anchor="center")
        tree_vendas.column("desconto", width=90, anchor="center")
        tree_vendas.column("pago", width=100, anchor="center")
        tree_vendas.column("faltante", width=100, anchor="center")
        tree_vendas.column("qtd_pag", width=80, anchor="center")
        tree_vendas.column("status", width=100, anchor="center")

        scroll_vendas = ttk.Scrollbar(tab_pedidos, orient="vertical", command=tree_vendas.yview)
        tree_vendas.configure(yscrollcommand=scroll_vendas.set)
        tree_vendas.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_vendas.pack(side=RIGHT, fill=Y)

        # Aba 2: Itens
        tab_itens = Frame(interno_notebook, bg="#1e1e1e")
        interno_notebook.add(tab_itens, text="📦 Itens do Pedido")

        tree_itens = ttk.Treeview(tab_itens, columns=(
            "produto", "qtd", "preco_unit", "subtotal", "custo_unit", "lucro_unit", "lucro_total"
        ), show="headings", height=12)
        tree_itens.heading("produto", text="PRODUTO")
        tree_itens.heading("qtd", text="QTD")
        tree_itens.heading("preco_unit", text="PREÇO UNIT.")
        tree_itens.heading("subtotal", text="SUBTOTAL")
        tree_itens.heading("custo_unit", text="CUSTO UNIT.")
        tree_itens.heading("lucro_unit", text="LUCRO UNIT.")
        tree_itens.heading("lucro_total", text="LUCRO TOTAL")
        for col in tree_itens["columns"]:
            tree_itens.column(col, width=120, anchor="center")
        tree_itens.column("produto", width=200, anchor="w")

        scroll_itens = ttk.Scrollbar(tab_itens, orient="vertical", command=tree_itens.yview)
        tree_itens.configure(yscrollcommand=scroll_itens.set)
        tree_itens.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_itens.pack(side=RIGHT, fill=Y)

        # Aba 3: Pagamentos do Pedido
        tab_pag_pedido = Frame(interno_notebook, bg="#1e1e1e")
        interno_notebook.add(tab_pag_pedido, text="💰 Pagamentos do Pedido")

        tree_pag_pedido = ttk.Treeview(tab_pag_pedido, columns=("id", "valor", "forma", "data"), show="headings", height=12)
        tree_pag_pedido.heading("id", text="ID")
        tree_pag_pedido.heading("valor", text="VALOR (R$)")
        tree_pag_pedido.heading("forma", text="FORMA")
        tree_pag_pedido.heading("data", text="DATA")
        for col in tree_pag_pedido["columns"]:
            tree_pag_pedido.column(col, width=150, anchor="center")

        scroll_pag_ped = ttk.Scrollbar(tab_pag_pedido, orient="vertical", command=tree_pag_pedido.yview)
        tree_pag_pedido.configure(yscrollcommand=scroll_pag_ped.set)
        tree_pag_pedido.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_pag_ped.pack(side=RIGHT, fill=Y)

        # Aba 4: Histórico completo
        tab_hist_pag = Frame(interno_notebook, bg="#1e1e1e")
        interno_notebook.add(tab_hist_pag, text="📜 Todos os Pagamentos")

        tree_hist_pag = ttk.Treeview(tab_hist_pag, columns=(
            "id", "data_pag", "venda_id", "venda_data", "valor", "forma"
        ), show="headings", height=12)
        tree_hist_pag.heading("id", text="ID PAG.")
        tree_hist_pag.heading("data_pag", text="DATA PAG.")
        tree_hist_pag.heading("venda_id", text="VENDA #")
        tree_hist_pag.heading("venda_data", text="DATA VENDA")
        tree_hist_pag.heading("valor", text="VALOR (R$)")
        tree_hist_pag.heading("forma", text="FORMA")
        for col in tree_hist_pag["columns"]:
            tree_hist_pag.column(col, width=120, anchor="center")
        tree_hist_pag.column("venda_id", width=80)
        tree_hist_pag.column("venda_data", width=100)

        scroll_hist = ttk.Scrollbar(tab_hist_pag, orient="vertical", command=tree_hist_pag.yview)
        tree_hist_pag.configure(yscrollcommand=scroll_hist.set)
        tree_hist_pag.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_hist.pack(side=RIGHT, fill=Y)

        frame_acoes = Frame(janela, bg="#1e1e1e")
        frame_acoes.pack(fill=X, padx=10, pady=10)
        Button(frame_acoes, text="🗑️ Excluir Venda Selecionada", bg="#e74c3c", fg="white", padx=10,
               command=lambda: excluir_venda()).pack(side=LEFT, padx=5)
        Button(frame_acoes, text="🗑️ Excluir Pagamento Selecionado", bg="#e74c3c", fg="white", padx=10,
               command=lambda: excluir_pagamento()).pack(side=LEFT, padx=5)
        Button(frame_acoes, text="🔄 Atualizar Tudo", bg="#2980b9", fg="white", padx=10,
               command=lambda: [carregar_pedidos(), carregar_historico_pagamentos()]).pack(side=LEFT, padx=5)

        venda_selecionada_id = None

        def carregar_pedidos():
            for item in tree_vendas.get_children():
                tree_vendas.delete(item)

            data_ini = self.filtro_data_ini.get().strip()
            data_fim = self.filtro_data_fim.get().strip()

            def para_iso(data_br):
                try:
                    d, m, a = data_br.split('/')
                    return f"{a}-{m}-{d}"
                except:
                    return "0000-00-00"

            data_ini_iso = para_iso(data_ini)
            data_fim_iso = para_iso(data_fim)

            cursor.execute("""
                SELECT id, data, total, desconto, status
                FROM vendas
                WHERE cliente_id = ?
                AND substr(data, 7, 4) || '-' || substr(data, 4, 2) || '-' || substr(data, 1, 2)
                    BETWEEN ? AND ?
                ORDER BY id DESC
            """, (cliente_id, data_ini_iso, data_fim_iso))

            vendas = cursor.fetchall()
            if not vendas:
                lbl_resumo.config(text=f"CLIENTE: {nome} – Nenhuma venda no período.")
                return

            total_comprado = 0
            total_pago_geral = 0
            pedidos_abertos = 0

            for v in vendas:
                venda_id = v[0]
                data_venda = v[1]
                total = float(v[2])
                desconto = float(v[3]) if v[3] else 0.0

                cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM pagamentos WHERE venda_id=?", (venda_id,))
                total_pago = float(cursor.fetchone()[0])
                faltante = total - total_pago

                cursor.execute("SELECT COUNT(*) FROM pagamentos WHERE venda_id=?", (venda_id,))
                qtd_pag = cursor.fetchone()[0]

                if total_pago <= 0:
                    status = "ABERTO"
                    pedidos_abertos += 1
                elif faltante > 0.01:
                    status = "PARCIAL"
                    pedidos_abertos += 1
                else:
                    status = "PAGO"

                total_comprado += total
                total_pago_geral += total_pago

                tree_vendas.insert("", END, values=(
                    venda_id, data_venda, f"{total:.2f}", f"{desconto:.2f}",
                    f"{total_pago:.2f}", f"{faltante:.2f}", qtd_pag, status
                ))

            pendente = total_comprado - total_pago_geral
            lbl_resumo.config(text=(
                f"CLIENTE: {nome}     |     "
                f"TOTAL COMPRADO: R$ {total_comprado:.2f}     |     "
                f"TOTAL PAGO: R$ {total_pago_geral:.2f}     |     "
                f"PENDENTE: R$ {pendente:.2f}     |     "
                f"PEDIDOS EM ABERTO: {pedidos_abertos}"
            ))

        def carregar_itens_e_pagamentos(event=None):
            nonlocal venda_selecionada_id
            selec = tree_vendas.selection()
            if not selec:
                return
            venda_id = tree_vendas.item(selec[0])['values'][0]
            venda_selecionada_id = venda_id
            for item in tree_itens.get_children():
                tree_itens.delete(item)
            for item in tree_pag_pedido.get_children():
                tree_pag_pedido.delete(item)
            cursor.execute("""
                SELECT p.nome, vi.quantidade, vi.preco_venda, vi.custo_unitario,
                       (vi.preco_venda - vi.custo_unitario) as lucro_unit
                FROM venda_itens vi
                JOIN produtos p ON vi.produto_id = p.id
                WHERE vi.venda_id = ?
            """, (venda_id,))
            for row in cursor.fetchall():
                nome_prod = row[0]
                qtd = row[1]
                preco_unit = row[2]
                subtotal = preco_unit * qtd
                custo_unit = row[3] if row[3] else 0
                lucro_unit = row[4] if row[4] else (preco_unit - custo_unit)
                lucro_total = lucro_unit * qtd
                tree_itens.insert("", END, values=(
                    nome_prod, qtd, f"{preco_unit:.2f}", f"{subtotal:.2f}",
                    f"{custo_unit:.2f}", f"{lucro_unit:.2f}", f"{lucro_total:.2f}"
                ))
            cursor.execute("SELECT id, valor, forma_pagamento, data FROM pagamentos WHERE venda_id=? ORDER BY data", (venda_id,))
            for pag in cursor.fetchall():
                tree_pag_pedido.insert("", END, values=(pag[0], f"{pag[1]:.2f}", pag[2], pag[3]))

        def carregar_historico_pagamentos():
            for item in tree_hist_pag.get_children():
                tree_hist_pag.delete(item)
            cursor.execute("""
                SELECT p.id, p.data, p.venda_id, v.data, p.valor, p.forma_pagamento
                FROM pagamentos p
                JOIN vendas v ON p.venda_id = v.id
                WHERE v.cliente_id = ?
                ORDER BY p.data DESC
            """, (cliente_id,))
            for pag in cursor.fetchall():
                tree_hist_pag.insert("", END, values=(
                    pag[0], pag[1], pag[2], pag[3], f"{pag[4]:.2f}", pag[5]
                ))

        def excluir_venda():
            if not venda_selecionada_id:
                messagebox.showwarning("Aviso", "Selecione uma venda na lista")
                return
            if messagebox.askyesno("Confirmar", f"Excluir venda #{venda_selecionada_id}?"):
                cursor.execute("BEGIN TRANSACTION")
                try:
                    cursor.execute("SELECT produto_id, quantidade FROM venda_itens WHERE venda_id=?", (venda_selecionada_id,))
                    for prod_id, qtd in cursor.fetchall():
                        cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id=?", (qtd, prod_id))
                    cursor.execute("DELETE FROM pagamentos WHERE venda_id=?", (venda_selecionada_id,))
                    cursor.execute("DELETE FROM venda_itens WHERE venda_id=?", (venda_selecionada_id,))
                    cursor.execute("DELETE FROM vendas WHERE id=?", (venda_selecionada_id,))
                    conn.commit()
                    messagebox.showinfo("Sucesso", "Venda excluída")
                    carregar_pedidos()
                    carregar_historico_pagamentos()
                    for item in tree_itens.get_children():
                        tree_itens.delete(item)
                    for item in tree_pag_pedido.get_children():
                        tree_pag_pedido.delete(item)
                    self.atualizar_todos_combos()
                    self.atualizar_dashboard_filtrado()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Erro", f"Erro ao excluir: {e}")

        def excluir_pagamento():
            selec = tree_hist_pag.selection()
            if not selec:
                messagebox.showwarning("Aviso", "Selecione um pagamento no histórico")
                return
            pag_id = tree_hist_pag.item(selec[0])['values'][0]
            if messagebox.askyesno("Confirmar", f"Excluir pagamento #{pag_id}?"):
                cursor.execute("BEGIN TRANSACTION")
                try:
                    cursor.execute("SELECT venda_id, valor FROM pagamentos WHERE id=?", (pag_id,))
                    venda_id, valor = cursor.fetchone()
                    cursor.execute("DELETE FROM pagamentos WHERE id=?", (pag_id,))
                    cursor.execute("SELECT SUM(valor) FROM pagamentos WHERE venda_id=?", (venda_id,))
                    total_pago = cursor.fetchone()[0] or 0
                    cursor.execute("SELECT total FROM vendas WHERE id=?", (venda_id,))
                    total_venda = cursor.fetchone()[0]
                    status = "Pago" if total_pago >= total_venda else ("Parcial" if total_pago > 0 else "Aberto")
                    cursor.execute("UPDATE vendas SET status=? WHERE id=?", (status, venda_id))
                    conn.commit()
                    messagebox.showinfo("Sucesso", "Pagamento excluído")
                    carregar_pedidos()
                    carregar_historico_pagamentos()
                    if venda_selecionada_id == venda_id:
                        carregar_itens_e_pagamentos()
                    self.atualizar_todos_combos()
                    self.atualizar_dashboard_filtrado()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Erro", f"Erro ao excluir: {e}")

        tree_vendas.bind("<<TreeviewSelect>>", carregar_itens_e_pagamentos)
        carregar_pedidos()
        carregar_historico_pagamentos()
        janela.bind("<Destroy>", lambda e: self.atualizar_todos_combos())

    # ---------------------------------------------------------
    # PRODUTOS
    # ---------------------------------------------------------
    def produtos_ui(self):
        frame_form = Frame(self.tab_produtos, bg="#1e1e1e")
        frame_form.pack(fill=X, pady=10, padx=10)
        self.entry_produto = {}
        Label(frame_form, text="Nome:", bg="#1e1e1e", fg="white").grid(row=0, column=0, sticky=W, padx=5, pady=2)
        self.entry_produto['nome'] = Entry(frame_form, width=30)
        self.entry_produto['nome'].grid(row=0, column=1, padx=5, pady=2)
        Label(frame_form, text="Cor:", bg="#1e1e1e", fg="white").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.entry_produto['cor'] = Entry(frame_form, width=30)
        self.entry_produto['cor'].grid(row=1, column=1, padx=5, pady=2)
        Label(frame_form, text="Preço Padrão (R$):", bg="#1e1e1e", fg="white").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.entry_produto['preco'] = Entry(frame_form, width=30)
        self.entry_produto['preco'].grid(row=2, column=1, padx=5, pady=2)
        Label(frame_form, text="Categoria:", bg="#1e1e1e", fg="white").grid(row=3, column=0, sticky=W, padx=5, pady=2)
        self.categoria_var = StringVar()
        self.combo_categoria = ttk.Combobox(frame_form, textvariable=self.categoria_var, width=27)
        self.combo_categoria.grid(row=3, column=1, padx=5, pady=2)
        self.atualizar_lista_categorias()
        Label(frame_form, text="Estoque inicial: 0 (atualizado via compras)", bg="#1e1e1e", fg="#aaa").grid(row=4, column=0, columnspan=2, pady=5)

        btn_frame = Frame(frame_form, bg="#1e1e1e")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        Button(btn_frame, text="Salvar Produto", bg="#27ae60", fg="white", command=self.salvar_produto).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Editar Produto", bg="#f39c12", fg="white", command=self.editar_produto).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Excluir Produto", bg="#e74c3c", fg="white", command=self.excluir_produto).pack(side=LEFT, padx=5)

        frame_pesq = Frame(self.tab_produtos, bg="#1e1e1e")
        frame_pesq.pack(fill=X, padx=10)
        Label(frame_pesq, text="Pesquisar:", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.pesq_produto = Entry(frame_pesq, width=40)
        self.pesq_produto.pack(side=LEFT, padx=5)
        self.pesq_produto.bind("<KeyRelease>", lambda e: self.carregar_produtos())

        self.tree_produtos = ttk.Treeview(self.tab_produtos, columns=("id", "nome", "cor", "preco", "estoque", "categoria"), show="headings")
        for col in ("id", "nome", "cor", "preco", "estoque", "categoria"):
            self.tree_produtos.heading(col, text=col.upper())
        self.tree_produtos.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.carregar_produtos()

    def atualizar_lista_categorias(self):
        cursor.execute("SELECT DISTINCT categoria FROM produtos WHERE categoria IS NOT NULL AND categoria != ''")
        categorias = [row[0] for row in cursor.fetchall()]
        self.combo_categoria['values'] = categorias

    def salvar_produto(self):
        nome = self.entry_produto['nome'].get().strip()
        if not nome:
            messagebox.showerror("Erro", "Nome obrigatório")
            return
        cor = self.entry_produto['cor'].get().strip()
        preco_str = self.entry_produto['preco'].get().strip().replace(",", ".")
        try:
            preco = float(preco_str) if preco_str else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Preço inválido")
            return
        categoria = self.categoria_var.get().strip()
        cursor.execute("INSERT INTO produtos (nome, cor, preco_padrao, estoque, categoria) VALUES (?,?,?,0,?)",
                       (nome, cor, preco, categoria))
        conn.commit()
        for entry in self.entry_produto.values():
            entry.delete(0, END)
        self.categoria_var.set("")
        self.carregar_produtos()
        self.atualizar_todos_combos()
        messagebox.showinfo("Sucesso", "Produto cadastrado")

    def carregar_produtos(self):
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        busca = self.pesq_produto.get()
        cursor.execute("SELECT id, nome, cor, preco_padrao, estoque, categoria FROM produtos WHERE nome LIKE ?", (f"%{busca}%",))
        for row in cursor.fetchall():
            self.tree_produtos.insert("", END, values=row)

    def editar_produto(self):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto")
            return
        prod_id = self.tree_produtos.item(selecionado[0])['values'][0]
        cursor.execute("SELECT nome, cor, preco_padrao, categoria FROM produtos WHERE id=?", (prod_id,))
        dados = cursor.fetchone()
        if not dados:
            return
        janela = Toplevel(self.root)
        janela.title("Editar Produto")
        janela.geometry("400x350")
        janela.configure(bg="#1e1e1e")
        entries = {}
        Label(janela, text="Nome:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=10, pady=5)
        entry_nome = Entry(janela, width=30)
        entry_nome.insert(0, dados[0])
        entry_nome.grid(row=0, column=1, padx=10, pady=5)
        entries['nome'] = entry_nome
        Label(janela, text="Cor:", bg="#1e1e1e", fg="white").grid(row=1, column=0, padx=10, pady=5)
        entry_cor = Entry(janela, width=30)
        entry_cor.insert(0, dados[1] if dados[1] else "")
        entry_cor.grid(row=1, column=1, padx=10, pady=5)
        entries['cor'] = entry_cor
        Label(janela, text="Preço Padrão (R$):", bg="#1e1e1e", fg="white").grid(row=2, column=0, padx=10, pady=5)
        entry_preco = Entry(janela, width=30)
        entry_preco.insert(0, str(dados[2]))
        entry_preco.grid(row=2, column=1, padx=10, pady=5)
        entries['preco'] = entry_preco
        Label(janela, text="Categoria:", bg="#1e1e1e", fg="white").grid(row=3, column=0, padx=10, pady=5)
        combo_cat = ttk.Combobox(janela, width=27)
        cursor.execute("SELECT DISTINCT categoria FROM produtos WHERE categoria IS NOT NULL AND categoria != ''")
        combo_cat['values'] = [row[0] for row in cursor.fetchall()]
        combo_cat.set(dados[3] if dados[3] else "")
        combo_cat.grid(row=3, column=1, padx=10, pady=5)
        entries['categoria'] = combo_cat

        def salvar_edicao():
            novo_nome = entries['nome'].get().strip()
            if not novo_nome:
                messagebox.showerror("Erro", "Nome obrigatório")
                return
            novo_preco_str = entries['preco'].get().strip().replace(",", ".")
            try:
                novo_preco = float(novo_preco_str) if novo_preco_str else 0.0
            except:
                messagebox.showerror("Erro", "Preço inválido")
                return
            cursor.execute("UPDATE produtos SET nome=?, cor=?, preco_padrao=?, categoria=? WHERE id=?",
                           (novo_nome, entries['cor'].get(), novo_preco, entries['categoria'].get(), prod_id))
            conn.commit()
            janela.destroy()
            self.carregar_produtos()
            self.atualizar_todos_combos()
            messagebox.showinfo("Sucesso", "Produto atualizado")

        Button(janela, text="Salvar", bg="#27ae60", fg="white", command=salvar_edicao).grid(row=4, column=0, columnspan=2, pady=20)

    def excluir_produto(self):
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            return
        prod_id = self.tree_produtos.item(selecionado[0])['values'][0]
        cursor.execute("SELECT COUNT(*) FROM compra_itens WHERE produto_id=?", (prod_id,))
        compras = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM venda_itens WHERE produto_id=?", (prod_id,))
        vendas = cursor.fetchone()[0]
        if compras > 0 or vendas > 0:
            if not messagebox.askyesno("Atenção", f"Produto possui {compras} compra(s) e {vendas} venda(s). Excluir mesmo assim?"):
                return
        if messagebox.askyesno("Confirmar", "Excluir produto?"):
            cursor.execute("DELETE FROM produtos WHERE id=?", (prod_id,))
            conn.commit()
            self.carregar_produtos()
            self.atualizar_todos_combos()
            messagebox.showinfo("Sucesso", "Produto excluído")

    # ---------------------------------------------------------
    # COMPRAS (com edição)
    # ---------------------------------------------------------
    def compras_ui(self):
        frame_cab = LabelFrame(self.tab_compras, text="Dados da Compra", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold"))
        frame_cab.pack(fill=X, padx=10, pady=5)
        Label(frame_cab, text="Fornecedor:", bg="#2b2b2b", fg="white").grid(row=0, column=0, padx=5, pady=5)
        self.comp_fornecedor = Entry(frame_cab, width=30)
        self.comp_fornecedor.grid(row=0, column=1)
        Label(frame_cab, text="Data (dd/mm/aaaa):", bg="#2b2b2b", fg="white").grid(row=0, column=2, padx=5)
        self.comp_data = Entry(frame_cab, width=12)
        self.comp_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.comp_data.grid(row=0, column=3)
        Label(frame_cab, text="Frete Total (R$):", bg="#2b2b2b", fg="white").grid(row=0, column=4, padx=5)
        self.comp_frete = Entry(frame_cab, width=10)
        self.comp_frete.grid(row=0, column=5)

        frame_itens = LabelFrame(self.tab_compras, text="Itens da Compra", bg="#2b2b2b", fg="white")
        frame_itens.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.tree_itens_compra = ttk.Treeview(frame_itens, columns=("produto", "qtd", "valor_total", "custo_unit"), show="headings")
        self.tree_itens_compra.heading("produto", text="Produto")
        self.tree_itens_compra.heading("qtd", text="Quantidade")
        self.tree_itens_compra.heading("valor_total", text="Valor Total (R$)")
        self.tree_itens_compra.heading("custo_unit", text="Custo Unit. (com frete)")
        self.tree_itens_compra.pack(fill=BOTH, expand=True)

        frame_add = Frame(frame_itens, bg="#2b2b2b")
        frame_add.pack(fill=X, pady=5)
        Label(frame_add, text="Produto:", bg="#2b2b2b", fg="white").pack(side=LEFT, padx=5)
        self.combo_prod_compra = ttk.Combobox(frame_add, width=30)
        self.combo_prod_compra.pack(side=LEFT, padx=5)
        self.atualizar_combo_produtos()
        Label(frame_add, text="Qtd:", bg="#2b2b2b", fg="white").pack(side=LEFT, padx=5)
        self.item_qtd = Entry(frame_add, width=8)
        self.item_qtd.pack(side=LEFT, padx=5)
        Label(frame_add, text="Valor Total (R$):", bg="#2b2b2b", fg="white").pack(side=LEFT, padx=5)
        self.item_valor_total = Entry(frame_add, width=10)
        self.item_valor_total.pack(side=LEFT, padx=5)
        Button(frame_add, text="Adicionar Item", bg="#27ae60", fg="white", command=self.adicionar_item_compra).pack(side=LEFT, padx=10)

        frame_btn = Frame(self.tab_compras, bg="#1e1e1e")
        frame_btn.pack(fill=X, padx=10, pady=5)
        Button(frame_btn, text="Remover Item", bg="#e67e22", fg="white", command=self.remover_item_compra).pack(side=LEFT, padx=5)
        Button(frame_btn, text="Finalizar Compra", bg="#27ae60", fg="white", command=self.finalizar_compra).pack(side=LEFT, padx=5)
        Button(frame_btn, text="Editar Compra", bg="#f39c12", fg="white", command=self.editar_compra).pack(side=LEFT, padx=5)
        Button(frame_btn, text="Excluir Compra", bg="#e74c3c", fg="white", command=self.excluir_compra).pack(side=LEFT, padx=5)

        self.tree_compras = ttk.Treeview(self.tab_compras, columns=("id", "data", "fornecedor", "total", "frete"), show="headings")
        for col in ("id", "data", "fornecedor", "total", "frete"):
            self.tree_compras.heading(col, text=col.upper())
        self.tree_compras.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.carregar_lista_compras()
        self.itens_temp = []

    def atualizar_combo_produtos(self):
        cursor.execute("SELECT id, nome, cor FROM produtos")
        produtos = [f"{row[1]} ({row[2]})" if row[2] else row[1] for row in cursor.fetchall()]
        self.combo_prod_compra['values'] = produtos

    def adicionar_item_compra(self):
        prod_str = self.combo_prod_compra.get()
        if not prod_str:
            messagebox.showwarning("Aviso", "Selecione um produto")
            return
        if " (" in prod_str and prod_str.endswith(")"):
            nome = prod_str.split(" (")[0]
            cor = prod_str.split("(")[1].replace(")", "")
        else:
            nome = prod_str
            cor = ""
        try:
            qtd = float(self.item_qtd.get().replace(",", "."))
            valor_total = float(self.item_valor_total.get().replace(",", "."))
        except:
            messagebox.showerror("Erro", "Quantidade e valor total devem ser números")
            return
        cursor.execute("SELECT id FROM produtos WHERE nome=? AND (cor=? OR (cor IS NULL AND ?=''))", (nome, cor, cor))
        prod = cursor.fetchone()
        if not prod:
            messagebox.showerror("Erro", "Produto não encontrado")
            return
        prod_id = prod[0]
        self.itens_temp.append((prod_id, nome, cor, qtd, valor_total))
        self.tree_itens_compra.insert("", END, values=(f"{nome} ({cor})" if cor else nome, qtd, f"{valor_total:.2f}", "A calcular"))
        self.item_qtd.delete(0, END)
        self.item_valor_total.delete(0, END)
        self.combo_prod_compra.set("")

    def remover_item_compra(self):
        selec = self.tree_itens_compra.selection()
        if not selec:
            return
        idx = self.tree_itens_compra.index(selec[0])
        self.tree_itens_compra.delete(selec[0])
        del self.itens_temp[idx]

    def finalizar_compra(self):
        if not self.itens_temp:
            messagebox.showwarning("Aviso", "Adicione pelo menos um item")
            return
        try:
            frete = float(self.comp_frete.get().replace(",", "."))
        except:
            frete = 0
        fornecedor = self.comp_fornecedor.get().strip()
        data = self.comp_data.get().strip()
        soma_valores = sum(item[4] for item in self.itens_temp)
        cursor.execute("BEGIN TRANSACTION")
        try:
            cursor.execute("INSERT INTO compras (fornecedor, frete_total, total_produtos, total_compra, data) VALUES (?,?,?,?,?)",
                           (fornecedor, frete, soma_valores, soma_valores + frete, data))
            compra_id = cursor.lastrowid
            for prod_id, nome, cor, qtd, valor_total in self.itens_temp:
                proporcao = valor_total / soma_valores if soma_valores > 0 else 0
                frete_item = frete * proporcao
                custo_unit = (valor_total + frete_item) / qtd
                cursor.execute("INSERT INTO compra_itens (compra_id, produto_id, quantidade, valor_total, frete_rateado, custo_unitario) VALUES (?,?,?,?,?,?)",
                               (compra_id, prod_id, qtd, valor_total, frete_item, custo_unit))
                cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id=?", (qtd, prod_id))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Compra #{compra_id} registrada")
            self.limpar_compra()
            self.carregar_lista_compras()
            self.atualizar_todos_combos()
            self.atualizar_dashboard_filtrado()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao salvar compra: {e}")

    def limpar_compra(self):
        self.itens_temp.clear()
        for row in self.tree_itens_compra.get_children():
            self.tree_itens_compra.delete(row)
        self.comp_fornecedor.delete(0, END)
        self.comp_frete.delete(0, END)
        self.comp_data.delete(0, END)
        self.comp_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

    def carregar_lista_compras(self):
        for row in self.tree_compras.get_children():
            self.tree_compras.delete(row)
        cursor.execute("SELECT id, data, fornecedor, total_compra, frete_total FROM compras ORDER BY id DESC")
        for row in cursor.fetchall():
            self.tree_compras.insert("", END, values=row)

    def editar_compra(self):
        selec = self.tree_compras.selection()
        if not selec:
            messagebox.showwarning("Aviso", "Selecione uma compra para editar")
            return
        compra_id = self.tree_compras.item(selec[0])['values'][0]

        cursor.execute("SELECT fornecedor, data, frete_total FROM compras WHERE id=?", (compra_id,))
        dados = cursor.fetchone()
        if not dados:
            return
        fornecedor, data, frete = dados

        cursor.execute("""
            SELECT ci.id, p.nome, p.cor, ci.quantidade, ci.valor_total
            FROM compra_itens ci
            JOIN produtos p ON ci.produto_id = p.id
            WHERE ci.compra_id = ?
        """, (compra_id,))
        itens = cursor.fetchall()

        janela = Toplevel(self.root)
        janela.title(f"Editar Compra #{compra_id}")
        janela.geometry("700x500")
        janela.configure(bg="#1e1e1e")

        Label(janela, text="Fornecedor:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        entry_forn = Entry(janela, width=40)
        entry_forn.insert(0, fornecedor)
        entry_forn.grid(row=0, column=1, padx=10, pady=5)

        Label(janela, text="Data (dd/mm/aaaa):", bg="#1e1e1e", fg="white").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        entry_data = Entry(janela, width=12)
        entry_data.insert(0, data)
        entry_data.grid(row=1, column=1, padx=10, pady=5, sticky=W)

        Label(janela, text="Frete Total (R$):", bg="#1e1e1e", fg="white").grid(row=2, column=0, padx=10, pady=5, sticky=W)
        entry_frete = Entry(janela, width=12)
        entry_frete.insert(0, str(frete))
        entry_frete.grid(row=2, column=1, padx=10, pady=5, sticky=W)

        Label(janela, text="Itens atuais:", bg="#1e1e1e", fg="white", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, pady=10)
        tree_itens = ttk.Treeview(janela, columns=("produto", "qtd", "valor"), show="headings", height=6)
        tree_itens.heading("produto", text="Produto")
        tree_itens.heading("qtd", text="Quantidade")
        tree_itens.heading("valor", text="Valor Total")
        tree_itens.column("produto", width=250)
        tree_itens.column("qtd", width=100, anchor="center")
        tree_itens.column("valor", width=120, anchor="center")
        tree_itens.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        for item in itens:
            nome = f"{item[1]} ({item[2]})" if item[2] else item[1]
            tree_itens.insert("", END, values=(nome, item[3], f"{item[4]:.2f}"))

        def salvar_edicao():
            novo_forn = entry_forn.get().strip()
            nova_data = entry_data.get().strip()
            try:
                novo_frete = float(entry_frete.get().replace(",", "."))
            except:
                novo_frete = 0

            if not novo_forn:
                messagebox.showerror("Erro", "Fornecedor obrigatório")
                return

            # Reverter estoque da compra antiga
            cursor.execute("SELECT produto_id, quantidade FROM compra_itens WHERE compra_id=?", (compra_id,))
            for prod_id, qtd in cursor.fetchall():
                cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id=?", (qtd, prod_id))

            cursor.execute("DELETE FROM compra_itens WHERE compra_id=?", (compra_id,))
            cursor.execute("DELETE FROM compras WHERE id=?", (compra_id,))

            if not itens:
                messagebox.showerror("Erro", "Nenhum item para salvar")
                return

            soma_valores = sum(item[4] for item in itens)
            cursor.execute("BEGIN TRANSACTION")
            try:
                cursor.execute("INSERT INTO compras (fornecedor, frete_total, total_produtos, total_compra, data) VALUES (?,?,?,?,?)",
                               (novo_forn, novo_frete, soma_valores, soma_valores + novo_frete, nova_data))
                nova_compra_id = cursor.lastrowid
                for item in itens:
                    nome_prod = item[1]
                    cor_prod = item[2]
                    cursor.execute("SELECT id FROM produtos WHERE nome=? AND (cor=? OR (cor IS NULL AND ?=''))", (nome_prod, cor_prod, cor_prod))
                    prod_id = cursor.fetchone()[0]
                    qtd = item[3]
                    valor_total = item[4]
                    proporcao = valor_total / soma_valores if soma_valores > 0 else 0
                    frete_item = novo_frete * proporcao
                    custo_unit = (valor_total + frete_item) / qtd
                    cursor.execute("INSERT INTO compra_itens (compra_id, produto_id, quantidade, valor_total, frete_rateado, custo_unitario) VALUES (?,?,?,?,?,?)",
                                   (nova_compra_id, prod_id, qtd, valor_total, frete_item, custo_unit))
                    cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id=?", (qtd, prod_id))
                conn.commit()
                messagebox.showinfo("Sucesso", f"Compra #{nova_compra_id} atualizada")
                janela.destroy()
                self.carregar_lista_compras()
                self.atualizar_todos_combos()
                self.atualizar_dashboard_filtrado()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Erro ao editar: {e}")

        Button(janela, text="Salvar Alterações", bg="#27ae60", fg="white", command=salvar_edicao).grid(row=5, column=0, columnspan=2, pady=20)

    def excluir_compra(self):
        selec = self.tree_compras.selection()
        if not selec:
            return
        compra_id = self.tree_compras.item(selec[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"Excluir compra #{compra_id}? Reverterá o estoque."):
            cursor.execute("BEGIN TRANSACTION")
            try:
                cursor.execute("SELECT produto_id, quantidade FROM compra_itens WHERE compra_id=?", (compra_id,))
                for prod_id, qtd in cursor.fetchall():
                    cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id=?", (qtd, prod_id))
                cursor.execute("DELETE FROM compra_itens WHERE compra_id=?", (compra_id,))
                cursor.execute("DELETE FROM compras WHERE id=?", (compra_id,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Compra excluída")
                self.carregar_lista_compras()
                self.atualizar_todos_combos()
                self.atualizar_dashboard_filtrado()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")

    # ---------------------------------------------------------
    # VENDAS (com edição)
    # ---------------------------------------------------------
    def vendas_ui(self):
        frame_cli = Frame(self.tab_vendas, bg="#1e1e1e")
        frame_cli.pack(fill=X, padx=10, pady=5)
        Label(frame_cli, text="Cliente:", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.v_cliente = ttk.Combobox(frame_cli, width=50)
        self.v_cliente.pack(side=LEFT, padx=5)
        self.v_cliente.bind("<Button-1>", lambda e: self.atualizar_combo_clientes_venda())

        frame_itens = LabelFrame(self.tab_vendas, text="Itens da Venda", bg="#2b2b2b", fg="white")
        frame_itens.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.tree_itens_venda = ttk.Treeview(frame_itens, columns=("produto", "qtd", "preco_venda", "subtotal", "lucro"), show="headings")
        for col in ("produto", "qtd", "preco_venda", "subtotal", "lucro"):
            self.tree_itens_venda.heading(col, text=col.upper())
        self.tree_itens_venda.pack(fill=BOTH, expand=True)

        frame_add = Frame(frame_itens, bg="#2b2b2b")
        frame_add.pack(fill=X, pady=5)
        Label(frame_add, text="Produto:", bg="#2b2b2b", fg="white").pack(side=LEFT, padx=5)
        self.v_produto = ttk.Combobox(frame_add, width=40)
        self.v_produto.pack(side=LEFT, padx=5)
        self.v_produto.bind("<Button-1>", lambda e: self.atualizar_combo_produtos_venda())
        self.v_produto.bind("<<ComboboxSelected>>", self.mostrar_custo_estoque)

        Label(frame_add, text="Quantidade:", bg="#2b2b2b", fg="white").pack(side=LEFT, padx=5)
        self.v_qtd = Entry(frame_add, width=8)
        self.v_qtd.pack(side=LEFT, padx=5)
        Label(frame_add, text="Preço Venda (R$):", bg="#2b2b2b", fg="white").pack(side=LEFT, padx=5)
        self.v_preco = Entry(frame_add, width=10)
        self.v_preco.pack(side=LEFT, padx=5)
        Button(frame_add, text="Adicionar Item", bg="#27ae60", fg="white", command=self.adicionar_item_venda).pack(side=LEFT, padx=10)

        self.lbl_info = Label(self.tab_vendas, text="", bg="#1e1e1e", fg="#aaa", font=("Arial", 9))
        self.lbl_info.pack(anchor=W, padx=10)

        frame_tot = Frame(self.tab_vendas, bg="#1e1e1e")
        frame_tot.pack(fill=X, padx=10, pady=5)
        Label(frame_tot, text="Desconto (R$):", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.v_desconto = Entry(frame_tot, width=10)
        self.v_desconto.pack(side=LEFT, padx=5)
        self.v_desconto.bind("<KeyRelease>", self.calcular_totais_venda)
        self.lbl_total = Label(frame_tot, text="TOTAL: R$ 0.00", bg="#1e1e1e", fg="white", font=("Arial", 10, "bold"))
        self.lbl_total.pack(side=LEFT, padx=20)
        self.lbl_lucro_total = Label(frame_tot, text="Lucro total: R$ 0.00", bg="#1e1e1e", fg="#27ae60")
        self.lbl_lucro_total.pack(side=LEFT, padx=20)

        frame_btn = Frame(self.tab_vendas, bg="#1e1e1e")
        frame_btn.pack(fill=X, padx=10, pady=5)
        Button(frame_btn, text="Remover Item", bg="#e67e22", fg="white", command=self.remover_item_venda).pack(side=LEFT, padx=5)
        Button(frame_btn, text="Registrar Venda", bg="#27ae60", fg="white", command=self.registrar_venda).pack(side=LEFT, padx=5)
        Button(frame_btn, text="Editar Venda", bg="#f39c12", fg="white", command=self.editar_venda).pack(side=LEFT, padx=5)
        Button(frame_btn, text="Excluir Venda", bg="#e74c3c", fg="white", command=self.excluir_venda).pack(side=LEFT, padx=5)

        self.tree_vendas = ttk.Treeview(self.tab_vendas, columns=("id", "cliente", "data", "total", "status"), show="headings")
        for col in ("id", "cliente", "data", "total", "status"):
            self.tree_vendas.heading(col, text=col.upper())
        self.tree_vendas.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.carregar_lista_vendas()
        self.itens_venda_temp = []

    def atualizar_combo_clientes_venda(self):
        cursor.execute("SELECT id, nome FROM clientes")
        self.v_cliente['values'] = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]

    def atualizar_combo_produtos_venda(self):
        cursor.execute("SELECT id, nome, cor, preco_padrao FROM produtos")
        produtos = [f"{row[1]} ({row[2]})" if row[2] else row[1] for row in cursor.fetchall()]
        self.v_produto['values'] = produtos

    def mostrar_custo_estoque(self, event=None):
        prod_str = self.v_produto.get()
        if not prod_str:
            return
        if " (" in prod_str and prod_str.endswith(")"):
            nome = prod_str.split(" (")[0]
            cor = prod_str.split("(")[1].replace(")", "")
        else:
            nome = prod_str
            cor = ""
        cursor.execute("SELECT id, estoque, preco_padrao FROM produtos WHERE nome=? AND (cor=? OR (cor IS NULL AND ?=''))", (nome, cor, cor))
        prod = cursor.fetchone()
        if prod:
            cursor.execute("SELECT custo_unitario FROM compra_itens WHERE produto_id=? ORDER BY compra_id DESC LIMIT 1", (prod[0],))
            custo = cursor.fetchone()
            custo_atual = custo[0] if custo else 0
            self.lbl_info.config(text=f"Estoque: {prod[1]} | Último custo: R$ {custo_atual:.2f} | Preço padrão: R$ {prod[2]:.2f}")
            self.v_preco.delete(0, END)
            self.v_preco.insert(0, str(prod[2]))

    def adicionar_item_venda(self):
        prod_str = self.v_produto.get()
        if not prod_str:
            return
        if " (" in prod_str and prod_str.endswith(")"):
            nome = prod_str.split(" (")[0]
            cor = prod_str.split("(")[1].replace(")", "")
        else:
            nome = prod_str
            cor = ""
        cursor.execute("SELECT id, estoque FROM produtos WHERE nome=? AND (cor=? OR (cor IS NULL AND ?=''))", (nome, cor, cor))
        prod = cursor.fetchone()
        if not prod:
            return
        prod_id, estoque = prod
        try:
            qtd = float(self.v_qtd.get().replace(",", "."))
            preco = float(self.v_preco.get().replace(",", "."))
            if qtd <= 0 or preco <= 0:
                raise ValueError
        except:
            messagebox.showerror("Erro", "Quantidade e preço válidos")
            return
        if qtd > estoque:
            messagebox.showerror("Erro", f"Estoque insuficiente. Disponível: {estoque}")
            return
        cursor.execute("SELECT custo_unitario FROM compra_itens WHERE produto_id=? ORDER BY compra_id DESC LIMIT 1", (prod_id,))
        custo_row = cursor.fetchone()
        custo = custo_row[0] if custo_row else 0
        lucro_item = (preco - custo) * qtd
        subtotal = preco * qtd
        self.itens_venda_temp.append((prod_id, nome, cor, qtd, preco, custo, lucro_item))
        self.tree_itens_venda.insert("", END, values=(f"{nome} ({cor})" if cor else nome, qtd, f"{preco:.2f}", f"{subtotal:.2f}", f"{lucro_item:.2f}"))
        self.calcular_totais_venda()
        self.v_qtd.delete(0, END)
        self.v_preco.delete(0, END)
        self.v_produto.set("")
        self.lbl_info.config(text="")

    def remover_item_venda(self):
        selec = self.tree_itens_venda.selection()
        if not selec:
            return
        idx = self.tree_itens_venda.index(selec[0])
        self.tree_itens_venda.delete(selec[0])
        del self.itens_venda_temp[idx]
        self.calcular_totais_venda()

    def calcular_totais_venda(self, event=None):
        total = sum(item[4] * item[3] for item in self.itens_venda_temp)
        try:
            desconto = float(self.v_desconto.get().replace(",", "."))
        except:
            desconto = 0
        total_final = total - desconto
        custo_total = sum(item[5] * item[3] for item in self.itens_venda_temp)
        lucro = total_final - custo_total
        self.lbl_total.config(text=f"TOTAL: R$ {total_final:.2f}")
        self.lbl_lucro_total.config(text=f"Lucro total: R$ {lucro:.2f}")

    def registrar_venda(self):
        if not self.itens_venda_temp:
            messagebox.showwarning("Aviso", "Adicione itens à venda")
            return
        cliente_str = self.v_cliente.get()
        if not cliente_str:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return
        cliente_id = int(cliente_str.split(" - ")[0])
        total = sum(item[4] * item[3] for item in self.itens_venda_temp)
        try:
            desconto = float(self.v_desconto.get().replace(",", "."))
        except:
            desconto = 0
        total_final = total - desconto
        custo_total = sum(item[5] * item[3] for item in self.itens_venda_temp)
        lucro = total_final - custo_total
        data = datetime.now().strftime("%d/%m/%Y")
        status = "Aberto"
        cursor.execute("BEGIN TRANSACTION")
        try:
            cursor.execute("INSERT INTO vendas (cliente_id, total, desconto, lucro_total, status, data) VALUES (?,?,?,?,?,?)",
                           (cliente_id, total_final, desconto, lucro, status, data))
            venda_id = cursor.lastrowid
            for prod_id, nome, cor, qtd, preco, custo, _ in self.itens_venda_temp:
                lucro_item = (preco - custo) * qtd
                cursor.execute("INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_venda, custo_unitario, lucro) VALUES (?,?,?,?,?,?)",
                               (venda_id, prod_id, qtd, preco, custo, lucro_item))
                cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id=?", (qtd, prod_id))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Venda #{venda_id} registrada. Total: R$ {total_final:.2f}")
            self.limpar_venda()
            self.carregar_lista_vendas()
            self.atualizar_todos_combos()
            self.atualizar_dashboard_filtrado()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Erro ao registrar venda: {e}")

    def limpar_venda(self):
        self.itens_venda_temp.clear()
        for row in self.tree_itens_venda.get_children():
            self.tree_itens_venda.delete(row)
        self.v_desconto.delete(0, END)
        self.v_cliente.set("")
        self.lbl_total.config(text="TOTAL: R$ 0.00")
        self.lbl_lucro_total.config(text="Lucro total: R$ 0.00")

    def carregar_lista_vendas(self):
        for row in self.tree_vendas.get_children():
            self.tree_vendas.delete(row)
        cursor.execute("SELECT v.id, c.nome, v.data, v.total, v.status FROM vendas v JOIN clientes c ON v.cliente_id = c.id ORDER BY v.id DESC")
        for row in cursor.fetchall():
            self.tree_vendas.insert("", END, values=row)

    def editar_venda(self):
        selec = self.tree_vendas.selection()
        if not selec:
            messagebox.showwarning("Aviso", "Selecione uma venda para editar")
            return
        venda_id = self.tree_vendas.item(selec[0])['values'][0]

        cursor.execute("SELECT cliente_id, data, total, desconto FROM vendas WHERE id=?", (venda_id,))
        dados = cursor.fetchone()
        if not dados:
            return
        cliente_id, data, total, desconto = dados

        cursor.execute("""
            SELECT vi.id, p.nome, p.cor, vi.quantidade, vi.preco_venda, vi.custo_unitario
            FROM venda_itens vi
            JOIN produtos p ON vi.produto_id = p.id
            WHERE vi.venda_id = ?
        """, (venda_id,))
        itens = cursor.fetchall()

        janela = Toplevel(self.root)
        janela.title(f"Editar Venda #{venda_id}")
        janela.geometry("700x550")
        janela.configure(bg="#1e1e1e")

        Label(janela, text="Cliente:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        combo_cli = ttk.Combobox(janela, width=50)
        cursor.execute("SELECT id, nome FROM clientes")
        clientes = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        combo_cli['values'] = clientes
        cursor.execute("SELECT nome FROM clientes WHERE id=?", (cliente_id,))
        nome_cli = cursor.fetchone()[0]
        combo_cli.set(f"{cliente_id} - {nome_cli}")
        combo_cli.grid(row=0, column=1, padx=10, pady=5)

        Label(janela, text="Data (dd/mm/aaaa):", bg="#1e1e1e", fg="white").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        entry_data = Entry(janela, width=12)
        entry_data.insert(0, data)
        entry_data.grid(row=1, column=1, padx=10, pady=5, sticky=W)

        Label(janela, text="Desconto (R$):", bg="#1e1e1e", fg="white").grid(row=2, column=0, padx=10, pady=5, sticky=W)
        entry_desconto = Entry(janela, width=12)
        entry_desconto.insert(0, str(desconto))
        entry_desconto.grid(row=2, column=1, padx=10, pady=5, sticky=W)

        Label(janela, text="Itens atuais:", bg="#1e1e1e", fg="white", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, pady=10)
        tree_itens = ttk.Treeview(janela, columns=("produto", "qtd", "preco", "custo"), show="headings", height=6)
        tree_itens.heading("produto", text="Produto")
        tree_itens.heading("qtd", text="Quantidade")
        tree_itens.heading("preco", text="Preço Venda")
        tree_itens.heading("custo", text="Custo Unit.")
        tree_itens.column("produto", width=200)
        tree_itens.column("qtd", width=80, anchor="center")
        tree_itens.column("preco", width=100, anchor="center")
        tree_itens.column("custo", width=100, anchor="center")
        tree_itens.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        for item in itens:
            nome = f"{item[1]} ({item[2]})" if item[2] else item[1]
            tree_itens.insert("", END, values=(nome, item[3], f"{item[4]:.2f}", f"{item[5]:.2f}"))

        def salvar_edicao():
            # Reverter estoque da venda antiga
            cursor.execute("SELECT produto_id, quantidade FROM venda_itens WHERE venda_id=?", (venda_id,))
            for prod_id, qtd in cursor.fetchall():
                cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id=?", (qtd, prod_id))

            cursor.execute("DELETE FROM pagamentos WHERE venda_id=?", (venda_id,))
            cursor.execute("DELETE FROM venda_itens WHERE venda_id=?", (venda_id,))
            cursor.execute("DELETE FROM vendas WHERE id=?", (venda_id,))

            if not itens:
                messagebox.showerror("Erro", "Nenhum item para salvar")
                return

            cliente_str = combo_cli.get()
            if not cliente_str:
                messagebox.showerror("Erro", "Selecione um cliente")
                return
            novo_cliente_id = int(cliente_str.split(" - ")[0])
            nova_data = entry_data.get().strip()
            try:
                novo_desconto = float(entry_desconto.get().replace(",", "."))
            except:
                novo_desconto = 0

            total_novo = sum(item[4] * item[3] for item in itens)
            total_final = total_novo - novo_desconto
            custo_total = sum(item[5] * item[3] for item in itens)
            lucro = total_final - custo_total

            cursor.execute("BEGIN TRANSACTION")
            try:
                status = "Aberto"
                cursor.execute("INSERT INTO vendas (cliente_id, total, desconto, lucro_total, status, data) VALUES (?,?,?,?,?,?)",
                               (novo_cliente_id, total_final, novo_desconto, lucro, status, nova_data))
                nova_venda_id = cursor.lastrowid

                for item in itens:
                    nome_prod = item[1]
                    cor_prod = item[2]
                    cursor.execute("SELECT id FROM produtos WHERE nome=? AND (cor=? OR (cor IS NULL AND ?=''))", (nome_prod, cor_prod, cor_prod))
                    prod_id = cursor.fetchone()[0]
                    qtd = item[3]
                    preco = item[4]
                    custo = item[5]
                    lucro_item = (preco - custo) * qtd
                    cursor.execute("INSERT INTO venda_itens (venda_id, produto_id, quantidade, preco_venda, custo_unitario, lucro) VALUES (?,?,?,?,?,?)",
                                   (nova_venda_id, prod_id, qtd, preco, custo, lucro_item))
                    cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id=?", (qtd, prod_id))

                conn.commit()
                messagebox.showinfo("Sucesso", f"Venda #{nova_venda_id} atualizada")
                janela.destroy()
                self.carregar_lista_vendas()
                self.atualizar_todos_combos()
                self.atualizar_dashboard_filtrado()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Erro ao editar: {e}")

        Button(janela, text="Salvar Alterações", bg="#27ae60", fg="white", command=salvar_edicao).grid(row=5, column=0, columnspan=2, pady=20)

    def excluir_venda(self):
        selec = self.tree_vendas.selection()
        if not selec:
            return
        venda_id = self.tree_vendas.item(selec[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"Excluir venda #{venda_id}? Reverterá o estoque e pagamentos."):
            cursor.execute("BEGIN TRANSACTION")
            try:
                cursor.execute("SELECT produto_id, quantidade FROM venda_itens WHERE venda_id=?", (venda_id,))
                for prod_id, qtd in cursor.fetchall():
                    cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id=?", (qtd, prod_id))
                cursor.execute("DELETE FROM pagamentos WHERE venda_id=?", (venda_id,))
                cursor.execute("DELETE FROM venda_itens WHERE venda_id=?", (venda_id,))
                cursor.execute("DELETE FROM vendas WHERE id=?", (venda_id,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Venda excluída")
                self.carregar_lista_vendas()
                self.atualizar_todos_combos()
                self.atualizar_dashboard_filtrado()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")

    # ---------------------------------------------------------
    # PAGAMENTOS
    # ---------------------------------------------------------
    def pagamentos_ui(self):
        frame_cliente = Frame(self.tab_pagamentos, bg="#1e1e1e")
        frame_cliente.pack(fill=X, padx=10, pady=5)
        Label(frame_cliente, text="Cliente:", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.combo_cliente_pag = ttk.Combobox(frame_cliente, width=60)
        self.combo_cliente_pag.pack(side=LEFT, padx=5)
        self.combo_cliente_pag.bind("<Button-1>", lambda e: self.atualizar_combo_clientes_pagamento())
        self.combo_cliente_pag.bind("<<ComboboxSelected>>", self.carregar_vendas_do_cliente_pagamento)

        frame_venda = Frame(self.tab_pagamentos, bg="#1e1e1e")
        frame_venda.pack(fill=X, padx=10, pady=5)
        Label(frame_venda, text="Venda:", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.combo_venda_pag = ttk.Combobox(frame_venda, width=80)
        self.combo_venda_pag.pack(side=LEFT, padx=5)
        self.combo_venda_pag.bind("<<ComboboxSelected>>", self.mostrar_pagamentos)

        frame_add = Frame(self.tab_pagamentos, bg="#1e1e1e")
        frame_add.pack(fill=X, padx=10, pady=5)
        Label(frame_add, text="Valor (R$):", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.pag_valor = Entry(frame_add, width=10)
        self.pag_valor.pack(side=LEFT, padx=5)
        Label(frame_add, text="Forma:", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.pag_forma = ttk.Combobox(frame_add, values=["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito", "Transferência"], width=15)
        self.pag_forma.pack(side=LEFT, padx=5)
        Label(frame_add, text="Data (dd/mm/aaaa):", bg="#1e1e1e", fg="white").pack(side=LEFT)
        self.pag_data = Entry(frame_add, width=12)
        self.pag_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.pag_data.pack(side=LEFT, padx=5)
        Button(frame_add, text="Registrar Pagamento", bg="#27ae60", fg="white", command=self.registrar_pagamento).pack(side=LEFT, padx=10)

        self.tree_pagamentos = ttk.Treeview(self.tab_pagamentos, columns=("id", "valor", "forma", "data"), show="headings")
        for col in ("id", "valor", "forma", "data"):
            self.tree_pagamentos.heading(col, text=col.upper())
        self.tree_pagamentos.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.vendas_dict = {}
        self.atualizar_combo_clientes_pagamento()

    def atualizar_combo_clientes_pagamento(self):
        cursor.execute("""
            SELECT DISTINCT c.id, c.nome
            FROM clientes c
            JOIN vendas v ON c.id = v.cliente_id
            WHERE v.status != 'Pago'
            ORDER BY c.nome
        """)
        clientes = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        self.combo_cliente_pag['values'] = clientes
        if clientes:
            self.combo_cliente_pag.current(0)
            self.carregar_vendas_do_cliente_pagamento()
        else:
            self.combo_venda_pag['values'] = []
            for row in self.tree_pagamentos.get_children():
                self.tree_pagamentos.delete(row)

    def carregar_vendas_do_cliente_pagamento(self, event=None):
        selec_cliente = self.combo_cliente_pag.get()
        if not selec_cliente:
            return
        cliente_id = int(selec_cliente.split(" - ")[0])
        cursor.execute("SELECT id, data, total, status FROM vendas WHERE cliente_id=? AND status != 'Pago' ORDER BY id DESC", (cliente_id,))
        vendas = cursor.fetchall()
        lista_vendas = []
        self.vendas_dict = {}
        for v in vendas:
            texto = f"Venda #{v[0]} - Data: {v[1]} - Total: R$ {v[2]:.2f} - Status: {v[3]}"
            lista_vendas.append(texto)
            self.vendas_dict[texto] = v[0]
        self.combo_venda_pag['values'] = lista_vendas
        if lista_vendas:
            self.combo_venda_pag.current(0)
            self.mostrar_pagamentos()
        else:
            for row in self.tree_pagamentos.get_children():
                self.tree_pagamentos.delete(row)

    def mostrar_pagamentos(self, event=None):
        selec = self.combo_venda_pag.get()
        if not selec:
            return
        venda_id = self.vendas_dict[selec]
        for row in self.tree_pagamentos.get_children():
            self.tree_pagamentos.delete(row)
        cursor.execute("SELECT id, valor, forma_pagamento, data FROM pagamentos WHERE venda_id=? ORDER BY data", (venda_id,))
        for p in cursor.fetchall():
            self.tree_pagamentos.insert("", END, values=p)

    def registrar_pagamento(self):
        selec_venda = self.combo_venda_pag.get()
        if not selec_venda:
            messagebox.showwarning("Aviso", "Selecione uma venda")
            return
        venda_id = self.vendas_dict[selec_venda]
        try:
            valor = float(self.pag_valor.get().replace(",", "."))
        except:
            messagebox.showerror("Erro", "Valor inválido")
            return
        forma = self.pag_forma.get()
        if not forma:
            forma = "Dinheiro"
        data_pag = self.pag_data.get().strip()
        cursor.execute("BEGIN TRANSACTION")
        try:
            cursor.execute("INSERT INTO pagamentos (venda_id, valor, forma_pagamento, data) VALUES (?,?,?,?)",
                           (venda_id, valor, forma, data_pag))
            cursor.execute("SELECT SUM(valor) FROM pagamentos WHERE venda_id=?", (venda_id,))
            total_pago = cursor.fetchone()[0] or 0
            cursor.execute("SELECT total FROM vendas WHERE id=?", (venda_id,))
            total_venda = cursor.fetchone()[0]
            if total_pago >= total_venda:
                status = "Pago"
            elif total_pago > 0:
                status = "Parcial"
            else:
                status = "Aberto"
            cursor.execute("UPDATE vendas SET status=? WHERE id=?", (status, venda_id))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Pagamento de R$ {valor:.2f} registrado")
            self.pag_valor.delete(0, END)
            self.carregar_vendas_do_cliente_pagamento()
            self.atualizar_todos_combos()
            self.atualizar_dashboard_filtrado()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Erro: {e}")

    # ---------------------------------------------------------
    # RETIRADAS
    # ---------------------------------------------------------
    def retiradas_ui(self):
        frame_registro = LabelFrame(self.tab_retiradas, text="Registrar Retirada/Devolução/Custo de Envio", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold"))
        frame_registro.pack(fill=X, padx=10, pady=5)

        Label(frame_registro, text="Data:", bg="#2b2b2b", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.ret_data = Entry(frame_registro, width=12)
        self.ret_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ret_data.grid(row=0, column=1, padx=5, pady=5)

        Label(frame_registro, text="Tipo:", bg="#2b2b2b", fg="white").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.ret_tipo = ttk.Combobox(frame_registro, values=["Devolução de Cliente", "Logística Reversa", "Perda/Avaria", "Custo de Envio", "Outros"], width=20)
        self.ret_tipo.grid(row=0, column=3, padx=5, pady=5)

        Label(frame_registro, text="Cliente (opcional):", bg="#2b2b2b", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.ret_cliente = ttk.Combobox(frame_registro, width=30)
        self.ret_cliente.grid(row=1, column=1, padx=5, pady=5)
        self.atualizar_combo_clientes_retirada()

        Label(frame_registro, text="Produto:", bg="#2b2b2b", fg="white").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        self.ret_produto = ttk.Combobox(frame_registro, width=30)
        self.ret_produto.grid(row=1, column=3, padx=5, pady=5)
        self.atualizar_combo_produtos_retirada()

        Label(frame_registro, text="Quantidade:", bg="#2b2b2b", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.ret_qtd = Entry(frame_registro, width=10)
        self.ret_qtd.grid(row=2, column=1, padx=5, pady=5)

        Label(frame_registro, text="Valor Custo (R$):", bg="#2b2b2b", fg="white").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        self.ret_valor_custo = Entry(frame_registro, width=12)
        self.ret_valor_custo.grid(row=2, column=3, padx=5, pady=5)

        Label(frame_registro, text="Valor Reembolso (R$):", bg="#2b2b2b", fg="white").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.ret_valor_reembolso = Entry(frame_registro, width=12)
        self.ret_valor_reembolso.grid(row=3, column=1, padx=5, pady=5)

        Label(frame_registro, text="Custo de Frete (R$):", bg="#2b2b2b", fg="white").grid(row=3, column=2, padx=5, pady=5, sticky=W)
        self.ret_custo_frete = Entry(frame_registro, width=12)
        self.ret_custo_frete.grid(row=3, column=3, padx=5, pady=5)

        Label(frame_registro, text="Impacto no Estoque:", bg="#2b2b2b", fg="white").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.ret_impacto = ttk.Combobox(frame_registro, values=["aumenta", "diminui", "nenhum"], width=10)
        self.ret_impacto.current(0)
        self.ret_impacto.grid(row=4, column=1, padx=5, pady=5)

        Label(frame_registro, text="Observação:", bg="#2b2b2b", fg="white").grid(row=4, column=2, padx=5, pady=5, sticky=W)
        self.ret_obs = Entry(frame_registro, width=40)
        self.ret_obs.grid(row=4, column=3, padx=5, pady=5)

        Button(frame_registro, text="Registrar Retirada", bg="#27ae60", fg="white", command=self.salvar_retirada).grid(row=5, column=0, columnspan=4, pady=10)

        frame_lista = LabelFrame(self.tab_retiradas, text="Histórico de Retiradas", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold"))
        frame_lista.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.tree_retiradas = ttk.Treeview(frame_lista, columns=("id", "data", "tipo", "cliente", "produto", "qtd", "custo", "reembolso", "frete", "impacto", "obs"), show="headings")
        self.tree_retiradas.heading("id", text="ID")
        self.tree_retiradas.heading("data", text="Data")
        self.tree_retiradas.heading("tipo", text="Tipo")
        self.tree_retiradas.heading("cliente", text="Cliente")
        self.tree_retiradas.heading("produto", text="Produto")
        self.tree_retiradas.heading("qtd", text="Qtd")
        self.tree_retiradas.heading("custo", text="Custo (R$)")
        self.tree_retiradas.heading("reembolso", text="Reemb. (R$)")
        self.tree_retiradas.heading("frete", text="Frete (R$)")
        self.tree_retiradas.heading("impacto", text="Estoque")
        self.tree_retiradas.heading("obs", text="Observação")
        self.tree_retiradas.column("id", width=40)
        self.tree_retiradas.column("data", width=80)
        self.tree_retiradas.column("tipo", width=120)
        self.tree_retiradas.column("cliente", width=120)
        self.tree_retiradas.column("produto", width=120)
        self.tree_retiradas.column("qtd", width=60)
        self.tree_retiradas.column("custo", width=80)
        self.tree_retiradas.column("reembolso", width=80)
        self.tree_retiradas.column("frete", width=80)
        self.tree_retiradas.column("impacto", width=60)
        self.tree_retiradas.column("obs", width=200)
        self.tree_retiradas.pack(fill=BOTH, expand=True)

        frame_btn = Frame(self.tab_retiradas, bg="#1e1e1e")
        frame_btn.pack(fill=X, padx=10, pady=5)
        Button(frame_btn, text="Editar Retirada", bg="#f39c12", fg="white", command=self.editar_retirada).pack(side=LEFT, padx=5)
        Button(frame_btn, text="Excluir Retirada", bg="#e74c3c", fg="white", command=self.excluir_retirada).pack(side=LEFT, padx=5)

        self.carregar_lista_retiradas()

    def atualizar_combo_clientes_retirada(self):
        cursor.execute("SELECT id, nome FROM clientes")
        clientes = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        self.ret_cliente['values'] = clientes

    def atualizar_combo_produtos_retirada(self):
        cursor.execute("SELECT id, nome, cor FROM produtos")
        produtos = [f"{row[1]} ({row[2]})" if row[2] else row[1] for row in cursor.fetchall()]
        self.ret_produto['values'] = produtos

    def salvar_retirada(self):
        data = self.ret_data.get().strip() or datetime.now().strftime("%d/%m/%Y")
        tipo = self.ret_tipo.get()
        if not tipo:
            messagebox.showerror("Erro", "Selecione o tipo de retirada")
            return
        cliente_str = self.ret_cliente.get()
        cliente_id = int(cliente_str.split(" - ")[0]) if cliente_str else None
        prod_str = self.ret_produto.get()
        if not prod_str:
            messagebox.showerror("Erro", "Selecione um produto")
            return
        if " (" in prod_str and prod_str.endswith(")"):
            nome = prod_str.split(" (")[0]
            cor = prod_str.split("(")[1].replace(")", "")
        else:
            nome = prod_str
            cor = ""
        cursor.execute("SELECT id FROM produtos WHERE nome=? AND (cor=? OR (cor IS NULL AND ?=''))", (nome, cor, cor))
        prod = cursor.fetchone()
        if not prod:
            messagebox.showerror("Erro", "Produto não encontrado")
            return
        produto_id = prod[0]
        try:
            qtd = float(self.ret_qtd.get().replace(",", ".")) if self.ret_qtd.get() else 0
        except:
            qtd = 0
        try:
            valor_custo = float(self.ret_valor_custo.get().replace(",", ".")) if self.ret_valor_custo.get() else 0.0
        except:
            valor_custo = 0.0
        try:
            valor_reembolso = float(self.ret_valor_reembolso.get().replace(",", ".")) if self.ret_valor_reembolso.get() else 0.0
        except:
            valor_reembolso = 0.0
        try:
            custo_frete = float(self.ret_custo_frete.get().replace(",", ".")) if self.ret_custo_frete.get() else 0.0
        except:
            custo_frete = 0.0
        impacto = self.ret_impacto.get()
        observacao = self.ret_obs.get().strip()

        cursor.execute("BEGIN TRANSACTION")
        try:
            cursor.execute("""
                INSERT INTO retiradas (data, tipo, cliente_id, produto_id, quantidade, valor_custo, valor_reembolso, custo_frete, observacao, impacta_estoque)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data, tipo, cliente_id, produto_id, qtd, valor_custo, valor_reembolso, custo_frete, observacao, impacto))
            if impacto == "aumenta":
                cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id=?", (qtd, produto_id))
            elif impacto == "diminui":
                cursor.execute("SELECT estoque FROM produtos WHERE id=?", (produto_id,))
                estoque_atual = cursor.fetchone()[0]
                if estoque_atual < qtd:
                    raise Exception(f"Estoque insuficiente. Disponível: {estoque_atual}")
                cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id=?", (qtd, produto_id))
            conn.commit()
            messagebox.showinfo("Sucesso", "Registro salvo e estoque atualizado")
            self.limpar_form_retirada()
            self.carregar_lista_retiradas()
            self.atualizar_todos_combos()
            self.atualizar_dashboard_filtrado()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    def limpar_form_retirada(self):
        self.ret_data.delete(0, END)
        self.ret_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.ret_tipo.set("")
        self.ret_cliente.set("")
        self.ret_produto.set("")
        self.ret_qtd.delete(0, END)
        self.ret_valor_custo.delete(0, END)
        self.ret_valor_reembolso.delete(0, END)
        self.ret_custo_frete.delete(0, END)
        self.ret_impacto.current(0)
        self.ret_obs.delete(0, END)

    def carregar_lista_retiradas(self):
        for item in self.tree_retiradas.get_children():
            self.tree_retiradas.delete(item)
        cursor.execute("""
            SELECT r.id, r.data, r.tipo, c.nome, 
                   p.nome || ' (' || p.cor || ')' AS produto, 
                   r.quantidade, r.valor_custo, r.valor_reembolso, r.custo_frete, 
                   r.impacta_estoque, r.observacao
            FROM retiradas r
            LEFT JOIN clientes c ON r.cliente_id = c.id
            LEFT JOIN produtos p ON r.produto_id = p.id
            ORDER BY r.id DESC
        """)
        for row in cursor.fetchall():
            cliente = row[3] if row[3] else "-"
            produto = row[4] if row[4] else "-"
            self.tree_retiradas.insert("", END, values=(row[0], row[1], row[2], cliente, produto,
                                                        row[5], f"{row[6]:.2f}" if row[6] else "0.00",
                                                        f"{row[7]:.2f}" if row[7] else "0.00",
                                                        f"{row[8]:.2f}" if row[8] else "0.00",
                                                        row[9], row[10] if row[10] else ""))

    def editar_retirada(self):
        selec = self.tree_retiradas.selection()
        if not selec:
            messagebox.showwarning("Aviso", "Selecione uma retirada")
            return
        retirada_id = self.tree_retiradas.item(selec[0])['values'][0]
        cursor.execute("SELECT data, tipo, cliente_id, produto_id, quantidade, valor_custo, valor_reembolso, custo_frete, observacao, impacta_estoque FROM retiradas WHERE id=?", (retirada_id,))
        dados = cursor.fetchone()
        if not dados:
            return
        janela = Toplevel(self.root)
        janela.title(f"Editar Retirada #{retirada_id}")
        janela.geometry("550x500")
        janela.configure(bg="#1e1e1e")

        Label(janela, text="Data:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=10, pady=5)
        entry_data = Entry(janela, width=12)
        entry_data.insert(0, dados[0])
        entry_data.grid(row=0, column=1, padx=10, pady=5)

        Label(janela, text="Tipo:", bg="#1e1e1e", fg="white").grid(row=1, column=0, padx=10, pady=5)
        combo_tipo = ttk.Combobox(janela, values=["Devolução de Cliente", "Logística Reversa", "Perda/Avaria", "Custo de Envio", "Outros"], width=25)
        combo_tipo.set(dados[1])
        combo_tipo.grid(row=1, column=1, padx=10, pady=5)

        Label(janela, text="Cliente:", bg="#1e1e1e", fg="white").grid(row=2, column=0, padx=10, pady=5)
        combo_cliente = ttk.Combobox(janela, width=30)
        cursor.execute("SELECT id, nome FROM clientes")
        clientes = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        combo_cliente['values'] = clientes
        if dados[2]:
            cursor.execute("SELECT nome FROM clientes WHERE id=?", (dados[2],))
            nome_cli = cursor.fetchone()[0]
            combo_cliente.set(f"{dados[2]} - {nome_cli}")
        combo_cliente.grid(row=2, column=1, padx=10, pady=5)

        Label(janela, text="Produto:", bg="#1e1e1e", fg="white").grid(row=3, column=0, padx=10, pady=5)
        combo_prod = ttk.Combobox(janela, width=30)
        cursor.execute("SELECT id, nome, cor FROM produtos")
        prods = [f"{row[1]} ({row[2]})" if row[2] else row[1] for row in cursor.fetchall()]
        combo_prod['values'] = prods
        cursor.execute("SELECT nome, cor FROM produtos WHERE id=?", (dados[3],))
        prod_nome, prod_cor = cursor.fetchone()
        combo_prod.set(f"{prod_nome} ({prod_cor})" if prod_cor else prod_nome)
        combo_prod.grid(row=3, column=1, padx=10, pady=5)

        Label(janela, text="Quantidade:", bg="#1e1e1e", fg="white").grid(row=4, column=0, padx=10, pady=5)
        entry_qtd = Entry(janela, width=10)
        entry_qtd.insert(0, str(dados[4]))
        entry_qtd.grid(row=4, column=1, padx=10, pady=5)

        Label(janela, text="Valor Custo (R$):", bg="#1e1e1e", fg="white").grid(row=5, column=0, padx=10, pady=5)
        entry_custo = Entry(janela, width=12)
        entry_custo.insert(0, str(dados[5]))
        entry_custo.grid(row=5, column=1, padx=10, pady=5)

        Label(janela, text="Valor Reembolso (R$):", bg="#1e1e1e", fg="white").grid(row=6, column=0, padx=10, pady=5)
        entry_reembolso = Entry(janela, width=12)
        entry_reembolso.insert(0, str(dados[6]))
        entry_reembolso.grid(row=6, column=1, padx=10, pady=5)

        Label(janela, text="Custo de Frete (R$):", bg="#1e1e1e", fg="white").grid(row=7, column=0, padx=10, pady=5)
        entry_frete = Entry(janela, width=12)
        entry_frete.insert(0, str(dados[7]))
        entry_frete.grid(row=7, column=1, padx=10, pady=5)

        Label(janela, text="Impacto Estoque:", bg="#1e1e1e", fg="white").grid(row=8, column=0, padx=10, pady=5)
        combo_impacto = ttk.Combobox(janela, values=["aumenta", "diminui", "nenhum"], width=10)
        combo_impacto.set(dados[9])
        combo_impacto.grid(row=8, column=1, padx=10, pady=5)

        Label(janela, text="Observação:", bg="#1e1e1e", fg="white").grid(row=9, column=0, padx=10, pady=5)
        entry_obs = Entry(janela, width=50)
        entry_obs.insert(0, dados[8] if dados[8] else "")
        entry_obs.grid(row=9, column=1, padx=10, pady=5)

        def salvar_edicao():
            impacto_antigo = dados[9]
            qtd_antiga = dados[4]
            produto_id_antigo = dados[3]
            cursor.execute("BEGIN TRANSACTION")
            try:
                if impacto_antigo == "aumenta":
                    cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id=?", (qtd_antiga, produto_id_antigo))
                elif impacto_antigo == "diminui":
                    cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id=?", (qtd_antiga, produto_id_antigo))

                nova_data = entry_data.get().strip()
                novo_tipo = combo_tipo.get()
                cliente_str = combo_cliente.get()
                novo_cliente_id = int(cliente_str.split(" - ")[0]) if cliente_str else None
                prod_str = combo_prod.get()
                if " (" in prod_str:
                    nome = prod_str.split(" (")[0]
                    cor = prod_str.split("(")[1].replace(")", "")
                else:
                    nome = prod_str
                    cor = ""
                cursor.execute("SELECT id FROM produtos WHERE nome=? AND (cor=? OR (cor IS NULL AND ?=''))", (nome, cor, cor))
                novo_produto_id = cursor.fetchone()[0]
                nova_qtd = float(entry_qtd.get().replace(",", ".")) if entry_qtd.get() else 0
                novo_custo = float(entry_custo.get().replace(",", ".")) if entry_custo.get() else 0.0
                novo_reembolso = float(entry_reembolso.get().replace(",", ".")) if entry_reembolso.get() else 0.0
                novo_frete = float(entry_frete.get().replace(",", ".")) if entry_frete.get() else 0.0
                novo_impacto = combo_impacto.get()
                nova_obs = entry_obs.get().strip()

                if novo_impacto == "aumenta":
                    cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id=?", (nova_qtd, novo_produto_id))
                elif novo_impacto == "diminui":
                    cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id=?", (nova_qtd, novo_produto_id))

                cursor.execute("""
                    UPDATE retiradas SET data=?, tipo=?, cliente_id=?, produto_id=?, quantidade=?, 
                    valor_custo=?, valor_reembolso=?, custo_frete=?, observacao=?, impacta_estoque=?
                    WHERE id=?
                """, (nova_data, novo_tipo, novo_cliente_id, novo_produto_id, nova_qtd, novo_custo, novo_reembolso, novo_frete, nova_obs, novo_impacto, retirada_id))
                conn.commit()
                messagebox.showinfo("Sucesso", "Retirada editada")
                janela.destroy()
                self.carregar_lista_retiradas()
                self.atualizar_todos_combos()
                self.atualizar_dashboard_filtrado()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Erro ao editar: {e}")

        Button(janela, text="Salvar Alterações", bg="#27ae60", fg="white", command=salvar_edicao).grid(row=10, column=0, columnspan=2, pady=20)

    def excluir_retirada(self):
        selec = self.tree_retiradas.selection()
        if not selec:
            messagebox.showwarning("Aviso", "Selecione uma retirada")
            return
        retirada_id = self.tree_retiradas.item(selec[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"Excluir retirada #{retirada_id}? Isso reverterá o impacto no estoque."):
            cursor.execute("SELECT produto_id, quantidade, impacta_estoque FROM retiradas WHERE id=?", (retirada_id,))
            prod_id, qtd, impacto = cursor.fetchone()
            cursor.execute("BEGIN TRANSACTION")
            try:
                if impacto == "aumenta":
                    cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id=?", (qtd, prod_id))
                elif impacto == "diminui":
                    cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id=?", (qtd, prod_id))
                cursor.execute("DELETE FROM retiradas WHERE id=?", (retirada_id,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Retirada excluída e estoque revertido")
                self.carregar_lista_retiradas()
                self.atualizar_todos_combos()
                self.atualizar_dashboard_filtrado()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")

if __name__ == "__main__":
    root = Tk()
    app = ERP(root)
    root.mainloop()