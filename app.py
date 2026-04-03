import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Pontaj Allied Engineers", page_icon="🏗️", layout="wide")

SHEET_ID = "1QXjwUep9mYj_eStxQUuHUo4juT2-YH3g2Mwmta-DMGg"
SHEET_PONTAJ = "Pontaj"
SHEET_CONFIG = "Config"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

SARBATORI_ROMANIA = [
    date(2026, 1, 1), date(2026, 1, 2), date(2026, 4, 10), date(2026, 4, 12),
    date(2026, 4, 13), date(2026, 5, 1), date(2026, 6, 1), date(2026, 6, 8),
    date(2026, 6, 9), date(2026, 8, 15), date(2026, 11, 30),
    date(2026, 12, 1), date(2026, 12, 25), date(2026, 12, 26),
]

CONFIG_DEFAULT = {
    "proiecte": [
        "907", "000.CO", "010.INVATARE", "020.DIVERSE", "03.PROIECTE LICITATIE",
        "111/112", "114.OCT-C1", "115.OCT-C2", "1305.ARENA NATIONALA",
        "132.SNM", "133.SNM", "136.BORZESTI", "137.COROD", "138.LEMACONS",
        "140.WNDPT", "141.PESTERA2", "142.POIANA", "145.TOPALU", "144.CNV",
        "143.MIRCEA", "191.CEF-BBD", "192.CEF-PTR", "193.CEF-GNS1",
        "194.CEF-GNS2", "195.CEF-PLC", "210.H4L", "227A.DECO BHB",
        "490.ELIADE", "575.TN2", "675.OLD", "678.OCP2", "680.PENINSULA",
        "691.OLC", "700.OHD", "705.OMN", "706.J8", "722.WNDGP", "723.WNDGC",
        "724.WNDIN", "726.WNDGV", "727.WNDPT", "747.SRUCJ IASI",
        "750.HALA FORD", "752.SPITAL CLUJ", "753.AZUGA", "756.PENNY",
        "768.BUC-3", "777.DOBROSLOVENI", "778.SP-PITESTI", "782.OCCIDENTULUI",
        "797.OST", "799.BCV", "800.AFI3", "803.CHTL", "817.GLOBE",
        "824.TANDAREI", "824.CEF Tandarei", "829.BUC-3", "830.OP17",
        "836.WNDGN", "840.SLT", "842.WNDGP", "853.RMW", "859.SATU MARE",
        "869.KFLBVT", "870.OPL", "872.BANEASA GIURGIU", "874.WNDAO",
        "875.HOLBAN", "878.BC SLT", "881.GHE", "885.AHC", "890.SINAIA",
        "891.DM-BRATIANU", "892.KFLOTP", "900.QDN", "905.01 KFLISD",
        "905.02 KFLSCL", "905.03 KFLIST", "905.04 KFLVLT", "905.KFLLGP",
        "915.SPITAL CONSTANTA", "920.JND", "921.CNV", "923.NOVO PARK",
        "929.BUCHAREST ONE", "936.MORA", "939.ORION DEBRECEN", "941.EDT",
        "943.ARENA NATIONALA", "947.HJLV", "950.KFLVLT", "952.CALIMANESTI",
        "953.Gura Ialomitei", "956.Brazi", "963.KFLJLV", "964.HOLBAN",
        "966.STC", "967.BUC4", "969.GALA", "972.BESS IS3", "AVALANSEI",
        "CASA - VALULUI", "DIVERSE", "FUNDENI", "GW Tower", "OME",
        "renovatio", "SPITAL BACAU", "EVERGENT", "CEE POIANA",
        "H4L.HOLBAN", "H4L.POMPEIU"
    ],
    "colegi": [
        "ADINA-MADALINA DOSPINA", "ADRIANA STEFAN", "ALEXANDRU SETREANU",
        "ALIN MIHAI MINDOIU", "ANAS ALISSA", "ANAMARIA LAZAROIU",
        "ANCA CERCEL", "ANDREI CATRINOIU", "ANDREI PAUN",
        "ANDREI-DANIEL MOROITA", "ARINA-LAURA MITU", "BIANCA ANDRONACHE",
        "BIANCA GABRIELA MANOLACHE", "CEZARINA FLORINA BRAN", "CRISTI ANDONE",
        "DIANA PANA", "DRAGOS GUBICS", "DRAGOS-NICOLAE SEITAN",
        "ELENA BURLACU", "ELENA VOLCINSCHI", "FLORIAN DANIEL TILIMPEA",
        "GABRIELA IONITA", "GABRIELA MARIN", "GEORGIANA ANA-MARIA BALUTA",
        "IOANA GAVRILA", "IONUT-FLORIN TOMA", "IRINA FARCAS",
        "IRINA-MIHAELA MATEI", "LEONARD IONUT TRAZNEA", "LIDIA DRAGANOVA",
        "LIDIA MIHAELA PANTIRU-MARIN", "MADALINA MUSAT", "MIHAI NEGRITORU",
        "OCTAVIAN DEACONU", "RADU SECATUREANU", "RADU STANCIU",
        "RICHARD MILOSAN", "RUXANDRA MARIA ANDRITOIU", "SAMUEL TOMA",
        "STEFAN GEORGESCU", "TIBERIU TUGURLAN", "TUDOR CIUCAN",
        "VIRGIL MICLIUC", "VLAD ANDREI WEBER"
    ],
    "faze": [
        "ASISTENTA TEHNICA", "PT", "DE", "CONCEPT", "CONCEPT PRELIMINAR",
        "CONCEPT FINAL", "DTAC", "EVALUARE OFERTA", "VERIFICARE PROIECT",
        "PTh", "LUCRARI SUPLIMENTARE"
    ],
    "subfaze": [
        "ESTIMARE LISTA DE CANTITATI", "întocmire documentație",
        "ACTUALIZARE MODEL", "Calcul piloti", "Coordonare echipa",
        "Editare memoriu", "EXPERTIZA TEHNICA", "PUNCT DE VEDERE", "REAUTORIZARE"
    ]
}

@st.cache_resource
def get_gsheet_client():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Eroare conectare Google Sheets: {e}")
        return None

def get_or_create_sheet(client, sheet_name, headers):
    try:
        spreadsheet = client.open_by_key(SHEET_ID)
        try:
            ws = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            ws.append_row(headers)
        return ws
    except Exception as e:
        st.error(f"Eroare sheet {sheet_name}: {e}")
        return None

@st.cache_data(ttl=30)
def incarca_pontaj():
    client = get_gsheet_client()
    headers = ["timestamp","coleg","saptamana","data_zi","proiect","faza","subfaza","ore","comentarii"]
    if not client:
        return pd.DataFrame(columns=headers)
    ws = get_or_create_sheet(client, SHEET_PONTAJ, headers)
    if not ws:
        return pd.DataFrame(columns=headers)
    try:
        data = ws.get_all_records()
        if not data:
            return pd.DataFrame(columns=headers)
        return pd.DataFrame(data)
    except:
        return pd.DataFrame(columns=headers)

def salveaza_inregistrare(inregistrare):
    client = get_gsheet_client()
    if not client:
        return False
    headers = ["timestamp","coleg","saptamana","data_zi","proiect","faza","subfaza","ore","comentarii"]
    ws = get_or_create_sheet(client, SHEET_PONTAJ, headers)
    if not ws:
        return False
    try:
        row = [str(inregistrare.get(h, "")) for h in headers]
        ws.append_row(row)
        return True
    except Exception as e:
        st.error(f"Eroare salvare: {e}")
        return False

@st.cache_data(ttl=60)
def incarca_config():
    client = get_gsheet_client()
    if not client:
        return CONFIG_DEFAULT.copy()
    try:
        spreadsheet = client.open_by_key(SHEET_ID)
        try:
            ws = spreadsheet.worksheet(SHEET_CONFIG)
            data = ws.get_all_records()
            if data:
                config = {}
                for row in data:
                    cheie = row.get("cheie", "")
                    valoare = row.get("valoare", "")
                    if cheie and valoare:
                        if cheie not in config:
                            config[cheie] = []
                        config[cheie].append(valoare)
                if all(k in config for k in ["proiecte","colegi","faze","subfaze"]):
                    return config
        except gspread.WorksheetNotFound:
            pass
    except:
        pass
    return CONFIG_DEFAULT.copy()

def salveaza_config(config):
    client = get_gsheet_client()
    if not client:
        return False
    try:
        spreadsheet = client.open_by_key(SHEET_ID)
        try:
            ws = spreadsheet.worksheet(SHEET_CONFIG)
            ws.clear()
        except gspread.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(title=SHEET_CONFIG, rows=500, cols=3)
        ws.append_row(["cheie", "valoare"])
        rows = []
        for cheie, lista in config.items():
            for valoare in lista:
                rows.append([cheie, valoare])
        if rows:
            ws.append_rows(rows)
        return True
    except Exception as e:
        st.error(f"Eroare salvare config: {e}")
        return False

def get_saptamani_2026():
    saptamani = []
    vazute = set()
    d = date(2026, 1, 1)
    while d.year == 2026:
        luni = d - timedelta(days=d.weekday())
        duminica = luni + timedelta(days=6)
        week_num = d.isocalendar()[1]
        label = f"W{week_num:02d} — {luni.strftime('%d.%m')} – {duminica.strftime('%d.%m.%Y')}"
        if label not in vazute:
            saptamani.append((label, f"w{week_num:02d}", luni, duminica))
            vazute.add(label)
        d += timedelta(days=7)
    return saptamani

def get_zile_saptamana(luni, duminica):
    zile = []
    d = luni
    while d <= duminica:
        e_sarbatoare = d in SARBATORI_ROMANIA
        e_weekend = d.weekday() >= 5
        nume_zi = ["Luni","Marți","Miercuri","Joi","Vineri","Sâmbătă","Duminică"][d.weekday()]
        label = f"{nume_zi} {d.strftime('%d.%m')}"
        if e_sarbatoare:
            label += " 🔴"
        elif e_weekend:
            label += " ⚫"
        zile.append((label, d, e_weekend or e_sarbatoare))
        d += timedelta(days=1)
    return zile

config = incarca_config()

with st.sidebar:
    st.markdown("### 🏗️ Allied Engineers")
    st.markdown("---")
    pagina = st.radio("Navigare", ["📝 Introducere ore", "📊 Rapoarte", "⚙️ Administrare"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Allied Engineers MEP © 2026")

if pagina == "📝 Introducere ore":
    st.title("📝 Pontaj ore")
    st.markdown("Completează orele lucrate pentru săptămâna selectată.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        coleg = st.selectbox("👤 Numele tău", options=["— selectează —"] + sorted(config["colegi"]))
        saptamani = get_saptamani_2026()
        azi = date.today()
        sapt_curenta = 0
        for i, (label, cod, luni, dum) in enumerate(saptamani):
            if luni <= azi <= dum:
                sapt_curenta = i
                break
        sapt_selectata_label = st.selectbox("📅 Săptămâna", options=[s[0] for s in saptamani], index=sapt_curenta)
        sapt_info = next(s for s in saptamani if s[0] == sapt_selectata_label)
        sapt_cod, sapt_luni, sapt_dum = sapt_info[1], sapt_info[2], sapt_info[3]

    with col2:
        st.markdown("**📆 Zilele săptămânii:**")
        zile = get_zile_saptamana(sapt_luni, sapt_dum)
        for label_zi, data_zi, e_liber in zile:
            if e_liber:
                st.caption(f"~~{label_zi}~~")
            else:
                st.caption(label_zi)

    st.markdown("---")

    if coleg == "— selectează —":
        st.info("👆 Selectează-ți numele pentru a continua.")
    else:
        st.subheader(f"Adaugă intrare pentru {coleg}")
        with st.form("form_pontaj", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                optiuni_zile = [(l, d) for l, d, e_liber in zile if not e_liber]
                zi_selectata_label = st.selectbox("📅 Ziua", [l for l, d in optiuni_zile])
                zi_selectata_data = next(d for l, d in optiuni_zile if l == zi_selectata_label)
                ore = st.number_input("⏱️ Ore lucrate", min_value=0.5, max_value=24.0, value=8.0, step=0.5)
            with col_b:
                proiect = st.selectbox("🏗️ Proiect", options=sorted(config["proiecte"]))
                faza = st.selectbox("📐 Faza", options=config["faze"])
            with col_c:
                subfaza_opt = ["— fără subfază —"] + config["subfaze"]
                subfaza = st.selectbox("🔍 Subfază", options=subfaza_opt)
                if subfaza == "— fără subfază —":
                    subfaza = ""
                comentarii = st.text_input("💬 Comentarii", placeholder="opțional...")

            submitted = st.form_submit_button("✅ Salvează înregistrarea", use_container_width=True)
            if submitted:
                inreg = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "coleg": coleg, "saptamana": sapt_cod,
                    "data_zi": zi_selectata_data.strftime("%Y-%m-%d"),
                    "proiect": proiect, "faza": faza, "subfaza": subfaza,
                    "ore": ore, "comentarii": comentarii
                }
                with st.spinner("Se salvează în Google Sheets..."):
                    ok = salveaza_inregistrare(inreg)
                if ok:
                    st.success(f"✅ Salvat! {ore}h pe {proiect} — {faza}")
                    incarca_pontaj.clear()

        st.markdown("---")
        st.subheader(f"Intrările tale din {sapt_selectata_label.split('—')[0].strip()}")
        df = incarca_pontaj()
        if len(df) > 0:
            df["ore"] = pd.to_numeric(df["ore"], errors="coerce")
            df_cs = df[(df["coleg"] == coleg) & (df["saptamana"] == sapt_cod)]
            if len(df_cs) == 0:
                st.info("Nu ai înregistrări pentru această săptămână încă.")
            else:
                st.metric("Total ore săptămână", f"{df_cs['ore'].sum():.1f}h")
                df_d = df_cs[["data_zi","proiect","faza","subfaza","ore","comentarii"]].copy()
                df_d.columns = ["Data","Proiect","Faza","Subfaza","Ore","Comentarii"]
                df_d["Data"] = pd.to_datetime(df_d["Data"]).dt.strftime("%d.%m")
                st.dataframe(df_d, use_container_width=True, hide_index=True)
        else:
            st.info("Nu ai înregistrări pentru această săptămână încă.")

elif pagina == "📊 Rapoarte":
    st.title("📊 Rapoarte pontaj")
    st.markdown("---")
    df = incarca_pontaj()
    if len(df) == 0:
        st.info("Nu există date de pontaj încă.")
    else:
        df["ore"] = pd.to_numeric(df["ore"], errors="coerce")
        col1, col2, col3 = st.columns(3)
        with col1:
            sapt_disp = sorted(df["saptamana"].dropna().unique().tolist())
            sapt_f = st.multiselect("Săptămâna", options=sapt_disp, default=sapt_disp[-1:] if sapt_disp else [])
        with col2:
            coleg_f = st.multiselect("Coleg", options=sorted(df["coleg"].dropna().unique().tolist()))
        with col3:
            proiect_f = st.multiselect("Proiect", options=sorted(df["proiect"].dropna().unique().tolist()))

        df_f = df.copy()
        if sapt_f: df_f = df_f[df_f["saptamana"].isin(sapt_f)]
        if coleg_f: df_f = df_f[df_f["coleg"].isin(coleg_f)]
        if proiect_f: df_f = df_f[df_f["proiect"].isin(proiect_f)]

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total ore", f"{df_f['ore'].sum():.0f}h")
        m2.metric("Colegi activi", df_f["coleg"].nunique())
        m3.metric("Proiecte active", df_f["proiect"].nunique())
        m4.metric("Înregistrări", len(df_f))
        st.markdown("---")

        t1, t2, t3 = st.tabs(["Per coleg", "Per proiect", "Per fază"])
        with t1:
            r = df_f.groupby("coleg")["ore"].sum().sort_values(ascending=False).reset_index()
            r.columns = ["Coleg","Ore"]; r["Ore"] = r["Ore"].round(1)
            st.dataframe(r, use_container_width=True, hide_index=True)
        with t2:
            r = df_f.groupby("proiect")["ore"].sum().sort_values(ascending=False).reset_index()
            r.columns = ["Proiect","Ore"]; r["Ore"] = r["Ore"].round(1)
            total = r["Ore"].sum()
            r["Procent"] = (r["Ore"] / total * 100).round(1).astype(str) + "%"
            st.dataframe(r, use_container_width=True, hide_index=True)
        with t3:
            r = df_f.groupby("faza")["ore"].sum().sort_values(ascending=False).reset_index()
            r.columns = ["Faza","Ore"]; r["Ore"] = r["Ore"].round(1)
            st.dataframe(r, use_container_width=True, hide_index=True)

        st.markdown("---")
        csv = df_f.to_csv(index=False, encoding="utf-8")
        st.download_button("⬇️ Descarcă CSV", data=csv,
            file_name=f"pontaj_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True)

elif pagina == "⚙️ Administrare":
    st.title("⚙️ Administrare liste")
    parola = st.text_input("🔒 Parolă admin", type="password")
    if parola != "allied2026":
        if parola: st.error("Parolă incorectă.")
        st.info("Introdu parola pentru a accesa administrarea.")
        st.stop()

    st.success("✅ Acces acordat.")
    st.markdown("---")
    tab_p, tab_c, tab_f, tab_sf = st.tabs(["Proiecte", "Colegi", "Faze", "Subfaze"])

    def editor_lista(tab, cheie, titlu):
        with tab:
            st.subheader(titlu)
            lista_noua = st.text_area("Un element pe linie:", value="\n".join(config[cheie]), height=400, key=f"ed_{cheie}")
            if st.button(f"💾 Salvează {titlu}", key=f"sv_{cheie}"):
                elemente = [x.strip() for x in lista_noua.split("\n") if x.strip()]
                config[cheie] = elemente
                with st.spinner("Se salvează..."):
                    ok = salveaza_config(config)
                if ok:
                    st.success(f"✅ {titlu} actualizate! ({len(elemente)} elemente)")
                    incarca_config.clear()
                    st.rerun()

    editor_lista(tab_p, "proiecte", "Proiecte")
    editor_lista(tab_c, "colegi", "Colegi")
    editor_lista(tab_f, "faze", "Faze")
    editor_lista(tab_sf, "subfaze", "Subfaze")

    st.markdown("---")
    st.subheader("🗃️ Date pontaj")
    df = incarca_pontaj()
    if len(df) > 0:
        st.write(f"Total înregistrări: **{len(df)}**")
        st.dataframe(df.tail(20), use_container_width=True)
    else:
        st.info("Nu există date salvate încă.")
