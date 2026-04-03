import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, timedelta
from io import StringIO

st.set_page_config(page_title="Pontaj Allied Engineers", page_icon="🏗️", layout="wide")

# ============================================================
# STORAGE KEYS
# ============================================================
KEY_PONTAJ = "pontaj_data_v1"
KEY_CONFIG = "pontaj_config_v1"

# ============================================================
# SARBATORI LEGALE ROMANIA 2026
# ============================================================
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

COLS = ["timestamp", "coleg", "saptamana", "data_zi", "proiect", "faza", "subfaza", "ore", "comentarii"]

# ============================================================
# STORAGE FUNCTIONS
# ============================================================
def incarca_pontaj():
    try:
        result = st.connection("storage", type="sql")
    except:
        pass
    
    if KEY_PONTAJ not in st.session_state:
        st.session_state[KEY_PONTAJ] = []
    
    rows = st.session_state[KEY_PONTAJ]
    if not rows:
        return pd.DataFrame(columns=COLS)
    return pd.DataFrame(rows, columns=COLS)

def salveaza_inregistrare(inreg):
    if KEY_PONTAJ not in st.session_state:
        st.session_state[KEY_PONTAJ] = []
    st.session_state[KEY_PONTAJ].append([
        inreg.get(c, "") for c in COLS
    ])
    return True

def incarca_config():
    if KEY_CONFIG not in st.session_state:
        st.session_state[KEY_CONFIG] = CONFIG_DEFAULT.copy()
    return st.session_state[KEY_CONFIG]

def salveaza_config(config):
    st.session_state[KEY_CONFIG] = config
    return True

# ============================================================
# UTILITARE
# ============================================================
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
        nume_zi = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"][d.weekday()]
        label = f"{nume_zi} {d.strftime('%d.%m')}"
        if e_sarbatoare: label += " 🔴"
        elif e_weekend: label += " ⚫"
        zile.append((label, d, e_weekend or e_sarbatoare))
        d += timedelta(days=1)
    return zile

# ============================================================
# APP
# ============================================================
config = incarca_config()

with st.sidebar:
    st.markdown("### 🏗️ Allied Engineers")
    st.markdown("---")
    pagina = st.radio("Navigare", ["📝 Introducere ore", "📊 Rapoarte", "⚙️ Administrare"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Allied Engineers MEP © 2026")

# ============================================================
# PAGINA 1 - INTRODUCERE ORE
# ============================================================
if pagina == "📝 Introducere ore":
    st.title("📝 Pontaj ore")
    st.markdown("Completează orele lucrate pentru săptămâna selectată.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        coleg = st.selectbox("👤 Numele tău", ["— selectează —"] + sorted(config["colegi"]))
        saptamani = get_saptamani_2026()
        azi = date.today()
        sapt_idx = 0
        for i, (label, cod, luni, dum) in enumerate(saptamani):
            if luni <= azi <= dum:
                sapt_idx = i
                break
        sapt_label = st.selectbox("📅 Săptămâna", [s[0] for s in saptamani], index=sapt_idx)
        sapt_info = next(s for s in saptamani if s[0] == sapt_label)
        sapt_cod, sapt_luni, sapt_dum = sapt_info[1], sapt_info[2], sapt_info[3]

    with col2:
        st.markdown("**📆 Zilele săptămânii:**")
        zile = get_zile_saptamana(sapt_luni, sapt_dum)
        for lz, dz, el in zile:
            st.caption(f"~~{lz}~~" if el else lz)

    st.markdown("---")

    if coleg == "— selectează —":
        st.info("👆 Selectează-ți numele pentru a continua.")
    else:
        st.subheader(f"Adaugă intrare pentru {coleg}")
        with st.form("form_pontaj", clear_on_submit=True):
            ca, cb, cc = st.columns(3)
            with ca:
                zile_lucr = [(l, d) for l, d, el in zile if not el]
                zi_label = st.selectbox("📅 Ziua", [l for l, d in zile_lucr])
                zi_data = next(d for l, d in zile_lucr if l == zi_label)
                ore = st.number_input("⏱️ Ore lucrate", min_value=0.5, max_value=24.0, value=8.0, step=0.5)
            with cb:
                proiect = st.selectbox("🏗️ Proiect", sorted(config["proiecte"]))
                faza = st.selectbox("📐 Faza", config["faze"])
            with cc:
                sf_opt = ["— fără subfază —"] + config["subfaze"]
                subfaza = st.selectbox("🔍 Subfază", sf_opt)
                if subfaza == "— fără subfază —": subfaza = ""
                comentarii = st.text_input("💬 Comentarii", placeholder="opțional...")

            if st.form_submit_button("✅ Salvează înregistrarea", use_container_width=True):
                inreg = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "coleg": coleg, "saptamana": sapt_cod,
                    "data_zi": zi_data.strftime("%Y-%m-%d"),
                    "proiect": proiect, "faza": faza, "subfaza": subfaza,
                    "ore": ore, "comentarii": comentarii
                }
                salveaza_inregistrare(inreg)
                st.success(f"✅ Salvat! {ore}h pe {proiect} — {faza}")

        st.markdown("---")
        st.subheader(f"Intrările tale din {sapt_label.split('—')[0].strip()}")
        df = incarca_pontaj()
        if len(df) > 0:
            df["ore"] = pd.to_numeric(df["ore"], errors="coerce")
            df_cs = df[(df["coleg"] == coleg) & (df["saptamana"] == sapt_cod)]
            if len(df_cs) == 0:
                st.info("Nu ai înregistrări pentru această săptămână.")
            else:
                st.metric("Total ore săptămână", f"{df_cs['ore'].sum():.1f}h")
                d2 = df_cs[["data_zi", "proiect", "faza", "subfaza", "ore", "comentarii"]].copy()
                d2.columns = ["Data", "Proiect", "Faza", "Subfaza", "Ore", "Comentarii"]
                d2["Data"] = pd.to_datetime(d2["Data"]).dt.strftime("%d.%m")
                st.dataframe(d2, use_container_width=True, hide_index=True)
        else:
            st.info("Nu ai înregistrări pentru această săptămână.")

# ============================================================
# PAGINA 2 - RAPOARTE
# ============================================================
elif pagina == "📊 Rapoarte":
    st.title("📊 Rapoarte pontaj")
    st.markdown("---")
    df = incarca_pontaj()
    if len(df) == 0:
        st.info("Nu există date de pontaj încă.")
    else:
        df["ore"] = pd.to_numeric(df["ore"], errors="coerce")
        c1, c2, c3 = st.columns(3)
        with c1:
            sd = sorted(df["saptamana"].dropna().unique().tolist())
            sf = st.multiselect("Săptămâna", sd, default=sd[-1:] if sd else [])
        with c2:
            cf = st.multiselect("Coleg", sorted(df["coleg"].dropna().unique().tolist()))
        with c3:
            pf = st.multiselect("Proiect", sorted(df["proiect"].dropna().unique().tolist()))

        df_f = df.copy()
        if sf: df_f = df_f[df_f["saptamana"].isin(sf)]
        if cf: df_f = df_f[df_f["coleg"].isin(cf)]
        if pf: df_f = df_f[df_f["proiect"].isin(pf)]

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
            r.columns = ["Coleg", "Ore"]; r["Ore"] = r["Ore"].round(1)
            st.dataframe(r, use_container_width=True, hide_index=True)
        with t2:
            r = df_f.groupby("proiect")["ore"].sum().sort_values(ascending=False).reset_index()
            r.columns = ["Proiect", "Ore"]; r["Ore"] = r["Ore"].round(1)
            t = r["Ore"].sum()
            r["Procent"] = (r["Ore"] / t * 100).round(1).astype(str) + "%"
            st.dataframe(r, use_container_width=True, hide_index=True)
        with t3:
            r = df_f.groupby("faza")["ore"].sum().sort_values(ascending=False).reset_index()
            r.columns = ["Faza", "Ore"]; r["Ore"] = r["Ore"].round(1)
            st.dataframe(r, use_container_width=True, hide_index=True)

        st.markdown("---")
        csv = df_f.to_csv(index=False, encoding="utf-8")
        st.download_button("⬇️ Descarcă CSV", data=csv,
            file_name=f"pontaj_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True)

# ============================================================
# PAGINA 3 - ADMINISTRARE
# ============================================================
elif pagina == "⚙️ Administrare":
    st.title("⚙️ Administrare liste")
    parola = st.text_input("🔒 Parolă admin", type="password")
    if parola != "allied2026":
        if parola: st.error("Parolă incorectă.")
        st.info("Introdu parola pentru a accesa administrarea.")
        st.stop()

    st.success("✅ Acces acordat.")
    st.markdown("---")
    t1, t2, t3, t4 = st.tabs(["Proiecte", "Colegi", "Faze", "Subfaze"])

    def editor(tab, cheie, titlu):
        with tab:
            st.subheader(titlu)
            nou = st.text_area("Un element pe linie:", value="\n".join(config[cheie]), height=400, key=f"ed_{cheie}")
            if st.button(f"💾 Salvează {titlu}", key=f"sv_{cheie}"):
                elemente = [x.strip() for x in nou.split("\n") if x.strip()]
                config[cheie] = elemente
                salveaza_config(config)
                st.success(f"✅ {titlu} actualizate! ({len(elemente)} elemente)")
                st.rerun()

    editor(t1, "proiecte", "Proiecte")
    editor(t2, "colegi", "Colegi")
    editor(t3, "faze", "Faze")
    editor(t4, "subfaze", "Subfaze")

    st.markdown("---")
    st.subheader("🗃️ Export date")
    df = incarca_pontaj()
    if len(df) > 0:
        st.write(f"Total înregistrări în sesiunea curentă: **{len(df)}**")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False, encoding="utf-8")
        st.download_button("⬇️ Descarcă toate datele CSV", data=csv,
            file_name=f"pontaj_complet_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True)
    else:
        st.info("Nu există date salvate încă.")
