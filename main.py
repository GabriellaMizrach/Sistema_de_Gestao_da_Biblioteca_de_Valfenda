import streamlit as st
import sqlite3
import pandas as pd
from datetime import date


# estetica com css

st.set_page_config(page_title="Biblioteca de Valfenda", layout="wide")


custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap');
    
    /* Fundo e fonte principal */
    .stApp {
        background-color: #080c08;
        color: #d4af37;
        font-family: 'Cinzel', serif;
    }
    
    h1, h2, h3, h4, p, span, label {
        color: #d4af37 !important;
        font-family: 'Cinzel', serif !important;
    }

    /*  botões */
    .stButton > button {
        background-color: #3b2313;
        color: #d4af37;
        border: 1px solid #d4af37;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #52321b;
        border: 1px solid #ffdf73;
    }

    /* texto e seleção */
    .stTextInput > div > div > input, .stSelectbox > div > div > select, .stDateInput > div > div > input {
        background-color: #0d140d;
        color: #d4af37;
        border: 1px solid #d4af37;
        border-radius: 8px;
    }

    /*  Dashboard */
    .valfenda-card {
        background-color: #3b2313;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #24150b;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }
    .valfenda-card h2 { font-size: 36px; margin: 0; color: #ffdf73 !important; }
    .valfenda-card p { font-size: 18px; margin: 0; text-transform: uppercase; }

    /* mensagens */
    .dialog-success {
        background-color: #051405;
        border: 2px solid #28a745;
        color: #28a745;
        padding: 20px;
        text-align: center;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .dialog-error {
        background-color: #1a0505;
        border: 2px solid #dc3545;
        color: #dc3545;
        padding: 20px;
        text-align: center;
        border-radius: 5px;
        margin-bottom: 20px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

#banco de dados
DB_NAME = "valfenda.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tabela de Viajantes
    c.execute('''
        CREATE TABLE IF NOT EXISTS TB_VIAJANTE (
            id_viajante INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_viajante VARCHAR(100) NOT NULL,
            origem_comitiva VARCHAR(100),
            status_ativo BOOLEAN DEFAULT 1
        )
    ''')
    
    # Tabela de Tomos
    c.execute('''
        CREATE TABLE IF NOT EXISTS TB_TOMO (
            id_tomo INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo_obra VARCHAR(150) NOT NULL,
            era_autor VARCHAR(100),
            status_disponibilidade VARCHAR(20) DEFAULT 'Disponível'
        )
    ''')
    
    # Tabela de Empréstimos
    c.execute('''
        CREATE TABLE IF NOT EXISTS TB_EMPRESTIMO (
            id_emprestimo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_viajante INTEGER NOT NULL,
            id_tomo INTEGER NOT NULL,
            data_retirada DATE NOT NULL,
            data_devolucao_prevista DATE NOT NULL,
            status_devolucao BOOLEAN DEFAULT 0,
            FOREIGN KEY (id_viajante) REFERENCES TB_VIAJANTE(id_viajante),
            FOREIGN KEY (id_tomo) REFERENCES TB_TOMO(id_tomo)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=()):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def fetch_data(query, params=()):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

#mensagen
def show_success(msg):
    st.markdown(f'<div class="dialog-success"><h3>V</h3><b>{msg}</b></div>', unsafe_allow_html=True)

def show_error(msg):
    st.markdown(f'<div class="dialog-error"><h3>X</h3><b>AÇÃO BLOQUEADA:</b><br/>{msg}</div>', unsafe_allow_html=True)


#menu lateral
st.sidebar.title("Menu do Guardião")
menu_opcoes = {
    "Painel do Guardião": "dashboard",
    "Acervo: Adicionar Novo Tomo": "add_tomo",
    "Acervo: Consultar Catálogo": "cat_tomo",
    "Comitiva: Registrar Viajante": "add_viajante",
    "Comitiva: Lista de Acesso": "list_viajante",
    "Circulação: Novo Empréstimo": "add_emprestimo",
    "Circulação: Registrar Devolução": "ret_emprestimo",
    "Auditoria: Relatórios": "relatorios"
}
escolha = st.sidebar.radio("Navegue pelas seções:", list(menu_opcoes.keys()))
page = menu_opcoes[escolha]

#paginas

if page == "dashboard":
    st.title("SAUDAÇÕES, GUARDIÃO")
    st.subheader("VISÃO GERAL DO CONHECIMENTO — 2ª ERA, ANO 1697")
    st.write("Após a fundação de Valfenda por Elrond Meio-Elfo")
    st.write("---")
    
    total_tomos = fetch_data("SELECT COUNT(*) as qtd FROM TB_TOMO")['qtd'][0]
    em_jornada = fetch_data("SELECT COUNT(*) as qtd FROM TB_TOMO WHERE status_disponibilidade != 'Disponível'")['qtd'][0]
    pendencias = fetch_data("SELECT COUNT(*) as qtd FROM TB_EMPRESTIMO WHERE status_devolucao = 0 AND data_devolucao_prevista < date('now')")['qtd'][0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="valfenda-card"><h2>{total_tomos}</h2><p>Total de Tomos</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="valfenda-card"><h2>{em_jornada}</h2><p>Em Jornada</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="valfenda-card"><h2 style="color:#ff4b4b !important;">{pendencias}</h2><p>Pendências</p></div>', unsafe_allow_html=True)


elif page == "add_tomo":
    st.title("🕮 ADICIONAR NOVO TOMO")
    with st.form("form_tomo", clear_on_submit=True):
        titulo = st.text_input("TÍTULO DA OBRA:")
        era = st.text_input("ERA DO AUTOR:")
        submit = st.form_submit_button("GUARDAR CONHECIMENTO")
        
        if submit:
            if titulo and era:
                run_query("INSERT INTO TB_TOMO (titulo_obra, era_autor) VALUES (?, ?)", (titulo, era))
                show_success("TOMO ADICIONADO AO ACERVO. O CONHECIMENTO FOI GUARDADO COM SUCESSO.")
            else:
                show_error("Os campos Título e Era são obrigatórios.")


elif page == "cat_tomo":
    st.title("📚 CATÁLOGO DO ACERVO")
    df_tomos = fetch_data("SELECT id_tomo as ID, titulo_obra as Título, era_autor as Era, status_disponibilidade as Status FROM TB_TOMO")
    st.dataframe(df_tomos, use_container_width=True, hide_index=True)
    
    # CRUD
    st.write("---")
    st.subheader("⚙️ GERENCIAR REGISTRO DE TOMO")
    
    if not df_tomos.empty:
        tomo_dict = dict(zip(df_tomos['ID'], df_tomos['Título']))
        sel_tomo_id = st.selectbox("SELECIONE UM TOMO PARA MODIFICAR OU APAGAR:", options=tomo_dict.keys(), format_func=lambda x: f"ID {x} - {tomo_dict[x]}")
        
        
        tomo_atual = fetch_data("SELECT * FROM TB_TOMO WHERE id_tomo = ?", (sel_tomo_id,)).iloc[0]
        
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            st.markdown("### Alterar Propriedades")
            novo_titulo = st.text_input("EDITAR TÍTULO DA OBRA:", value=tomo_atual['titulo_obra'])
            nova_era = st.text_input("EDITAR ERA DO AUTOR:", value=tomo_atual['era_autor'])
            if st.button("SALVAR ALTERAÇÕES"):
                if novo_titulo and nova_era:
                    run_query("UPDATE TB_TOMO SET titulo_obra = ?, era_autor = ? WHERE id_tomo = ?", (novo_titulo, nova_era, sel_tomo_id))
                    show_success("As alterações da obra foram salvas nos pergaminhos.")
                    st.rerun()
                else:
                    show_error("Nenhum campo estrutural pode ficar em branco.")
                    
        with col_ed2:
            st.markdown("### Expurgar do Acervo")
            st.write("A exclusão removerá permanentemente o tomo dos registros de Valfenda.")
            if st.button("REMOVER TOMO DEFINITIVAMENTE"):
                
                if tomo_atual['status_disponibilidade'] != 'Disponível':
                    show_error("Este tomo já se encontra em uma jornada (Indisponível).")
                else:
                    run_query("DELETE FROM TB_TOMO WHERE id_tomo = ?", (sel_tomo_id,))
                    show_success("Tomo excluído do acervo com sucesso.")
                    st.rerun()
    else:
        st.info("Nenhum tomo catalogado para gerenciar.")


elif page == "add_viajante":
    st.title("🕯️ REGISTRO DOS VIAJANTES")
    with st.form("form_viajante", clear_on_submit=True):
        nome = st.text_input("NOME DO VIAJANTE:", placeholder='"Aragorn, filho de Arathorn..."')
        origem = st.text_input("ORIGEM/COMITIVA:", placeholder='"Val-de-Lórien..."')
        submit = st.form_submit_button("CADASTRAR VIAJANTE")
        
        if submit:
            if nome and origem:
                run_query("INSERT INTO TB_VIAJANTE (nome_viajante, origem_comitiva) VALUES (?, ?)", (nome, origem))
                show_success("VIAJANTE REGISTRADO COM SUCESSO NOS SALÕES DE ELROND.")
            else:
                show_error("Identifique o viajante e sua origem para prosseguir.")


elif page == "list_viajante":
    st.title("📜 LISTA DE ACESSO")
    df_viajantes = fetch_data("SELECT id_viajante as ID, nome_viajante as Nome, origem_comitiva as Origem, status_ativo as Ativo FROM TB_VIAJANTE")
    
    df_viajantes['Ativo'] = df_viajantes['Ativo'].apply(lambda x: 'Sim' if x==1 else 'Não')
    st.dataframe(df_viajantes, use_container_width=True, hide_index=True)
    
    
    st.write("---")
    st.subheader("⚙️ GERENCIAR REGISTRO DE VIAJANTE")
    
    if not df_viajantes.empty:
        viajante_dict = dict(zip(df_viajantes['ID'], df_viajantes['Nome']))
        sel_viaj_id = st.selectbox("SELECIONE UM VIAJANTE PARA MODIFICAR OU APAGAR:", options=viajante_dict.keys(), format_func=lambda x: f"ID {x} - {viajante_dict[x]}")
        
        
        viaj_atual = fetch_data("SELECT * FROM TB_VIAJANTE WHERE id_viajante = ?", (sel_viaj_id,)).iloc[0]
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("### Alterar Credenciais")
            novo_nome = st.text_input("EDITAR NOME DO VIAJANTE:", value=viaj_atual['nome_viajante'])
            nova_comitiva = st.text_input("EDITAR ORIGEM/COMITIVA:", value=viaj_atual['origem_comitiva'])
            status_ativo = st.checkbox("VIAJANTE COM ACESSO ATIVO", value=bool(viaj_atual['status_ativo']))
            
            if st.button("ATUALIZAR VIAJANTE"):
                if novo_nome and nova_comitiva:
                    run_query("UPDATE TB_VIAJANTE SET nome_viajante = ?, origem_comitiva = ?, status_ativo = ? WHERE id_viajante = ?", 
                              (novo_nome, nova_comitiva, 1 if status_ativo else 0, sel_viaj_id))
                    show_success("Os dados do integrante da comitiva foram atualizados.")
                    st.rerun()
                else:
                    show_error("Os campos de identificação não podem ficar vazios.")
                    
        with col_v2:
            st.markdown("### Banir/Remover dos Registros")
            st.write("Esta ação remove o histórico direto de acesso do viajante.")
            if st.button("REMOVER VIAJANTE DEFINITIVAMENTE"):
                
                pendencias = fetch_data("SELECT COUNT(*) as qtd FROM TB_EMPRESTIMO WHERE id_viajante = ? AND status_devolucao = 0", (sel_viaj_id,))['qtd'][0]
                if pendencias > 0:
                    show_error("Este viajante possui tomos em jornada pendentes de devolução.")
                else:
                    run_query("DELETE FROM TB_VIAJANTE WHERE id_viajante = ?", (sel_viaj_id,))
                    show_success("Viajante removido com sucesso das crônicas de acesso.")
                    st.rerun()
    else:
        st.info("Nenhum viajante registrado para gerenciar.")


elif page == "add_emprestimo":
    st.title("🌿 TOMOS EM CIRCULAÇÃO")
    
    viajantes = fetch_data("SELECT id_viajante, nome_viajante FROM TB_VIAJANTE WHERE status_ativo = 1")
    tomos = fetch_data("SELECT id_tomo, titulo_obra FROM TB_TOMO WHERE status_disponibilidade = 'Disponível'")
    
    with st.form("form_emprestimo"):
        if not viajantes.empty:
            v_dict = dict(zip(viajantes.id_viajante, viajantes.nome_viajante))
            sel_viajante = st.selectbox("SELECIONAL VIAJANTE:", options=v_dict.keys(), format_func=lambda x: v_dict[x])
        else:
            st.warning("Nenhum viajante ativo registrado.")
            sel_viajante = None
            
        if not tomos.empty:
            t_dict = dict(zip(tomos.id_tomo, tomos.titulo_obra))
            sel_tomo = st.selectbox("SELECIONAR TOMO:", options=t_dict.keys(), format_func=lambda x: t_dict[x])
        else:
            st.warning("Nenhum tomo disponível no momento.")
            sel_tomo = None
            
        dt_devolucao = st.date_input("DATA LIMITE DE RETORNO:")
        submit = st.form_submit_button("AUTORIZAR JORNADA")
        
        if submit:
            if sel_viajante and sel_tomo:
                run_query("INSERT INTO TB_EMPRESTIMO (id_viajante, id_tomo, data_retirada, data_devolucao_prevista) VALUES (?, ?, date('now'), ?)", 
                          (sel_viajante, sel_tomo, dt_devolucao))
                run_query("UPDATE TB_TOMO SET status_disponibilidade = 'Em Jornada' WHERE id_tomo = ?", (sel_tomo,))
                show_success("JORNADA AUTORIZADA. O TOMO FOI ENTREGUE AO VIAJANTE.")
                st.rerun()
            else:
                show_error("É necessário selecionar um viajante e um tomo válidos.")


elif page == "ret_emprestimo":
    st.title("🛡️ RECOLHER TOMO (DEVOLUÇÃO)")
    
    query = """
        SELECT e.id_emprestimo, t.titulo_obra, v.nome_viajante, e.data_devolucao_prevista, e.id_tomo
        FROM TB_EMPRESTIMO e
        JOIN TB_TOMO t ON e.id_tomo = t.id_tomo
        JOIN TB_VIAJANTE v ON e.id_viajante = v.id_viajante
        WHERE e.status_devolucao = 0
    """
    emprestimos = fetch_data(query)
    
    if not emprestimos.empty:
        emp_dict = {row['id_emprestimo']: f"Tomo: {row['titulo_obra']} | Viajante: {row['nome_viajante']}" for index, row in emprestimos.iterrows()}
        
        with st.form("form_devolucao"):
            sel_emp = st.selectbox("SELECIONE O TOMO RETORNANDO A VALFENDA:", options=emp_dict.keys(), format_func=lambda x: emp_dict[x])
            submit = st.form_submit_button("RECOLHER TOMO")
            
            if submit:
                id_tomo = emprestimos.loc[emprestimos['id_emprestimo'] == sel_emp, 'id_tomo'].values[0]
                run_query("UPDATE TB_EMPRESTIMO SET status_devolucao = 1 WHERE id_emprestimo = ?", (sel_emp,))
                run_query("UPDATE TB_TOMO SET status_disponibilidade = 'Disponível' WHERE id_tomo = ?", (int(id_tomo),))
                show_success("TOMO RECOLHIDO. O CONHECIMENTO RETORNOU AOS SALÕES SEGUROS.")
                st.rerun()
    else:
        st.info("Não há tomos em jornada no momento.")


elif page == "relatorios":
    st.title("👁️‍ RELATÓRIOS GERENCIAIS DA AUDITORIA")
    
    st.subheader("Histórico de Jornadas (Empréstimos)")
    query_relatorio = """
        SELECT 
            t.titulo_obra as 'Tomo',
            v.nome_viajante as 'Viajante',
            e.data_retirada as 'Data de Retirada',
            e.data_devolucao_prevista as 'Prazo Limite',
            CASE WHEN e.status_devolucao = 1 THEN 'Devolvido' ELSE 'Em Andamento' END as 'Status'
        FROM TB_EMPRESTIMO e
        JOIN TB_TOMO t ON e.id_tomo = t.id_tomo
        JOIN TB_VIAJANTE v ON e.id_viajante = v.id_viajante
        ORDER BY e.data_retirada DESC
    """
    df_relatorio = fetch_data(query_relatorio)
    st.dataframe(df_relatorio, use_container_width=True, hide_index=True)