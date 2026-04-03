import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta
import calendar

# ============================================================
# CONFIGURARE PAGINA
# ============================================================
st.set_page_config(
    page_title="Pontaj Allied Engineers",
    page_icon="🏗️",
    layout="wide"
)

# ============================================================
# FISIERE DE DATE
# Toate datele se salveaza in fisiere locale JSON si CSV
# ============================================================
FISIER_PONTAJ = "pontaj_date.csv"
FISIER_CONFIG = "config.json"

# ============================================================
# SARBATORI LEGALE ROMANIA 2026
# ============================================================
SARBATORI_ROMANIA = [
    date(2026, 1, 1),   # Anul Nou
    date(2026, 1, 2),   # Anul Nou
    date(2026, 4, 10),  # Vinerea Mare
    date(2026, 4, 12),  # Paste
    date(2026, 4, 13),  # Paste
    date(2026, 5, 1),   # Ziua Muncii
    date(2026, 6, 1),   # Ziua Copilului
    date(2026, 6, 8),   # Rusalii (Duminica)  
    date(2026, 6, 9),   # Rusalii (Luni)
    date(2026, 8, 15),  # Adormirea Maicii Domnului
    date(2026, 11, 30), # Sf. Andrei
    date(2026, 12, 1),  # Ziua Nationala
    date(2026, 12, 25), # Craciun
    date(2026, 12, 26), # Craciun
]

# ============================================================
# DATE IMPLICITE (prima rulare)
# ============================================================
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
        "Editare memoriu", "EXPERTIZA TEHNICA", "PUNCT DE VEDERE",
        "REAUTORIZARE"
    ]
}

# ============================================================
# FUNCTII UTILITARE
# ============================================================

def get_saptamani_2026():
    """Genereaza lista de saptamani pentru 2026"""
    saptamani = []
    d = date(2026, 1, 1)
    while d.year == 2026:
        # Gaseste lunea saptamanii
        luni = d - timedelta(days=d.weekday())
        duminica = luni + timedelta(days=6)
        week_num = d.isocalendar()[1]
        label = f"W{week_num:02d} — {luni.strftime('%d.%m')} – {duminica.strftime('%d.%m.%Y')}"
        if label not in [s[0] for s in saptamani]:
            saptamani.append((label, f"w{week_num:02d}", luni, duminica))
        d += timedelta(days=7)
    return saptamani

def get_zile_saptamana(luni, duminica):
    """Returneaza zilele dintr-o saptamana cu marcaj sarbatori"""
    zile = []
    d = luni
    while d <= duminica:
        e_sarbatoare = d in SARBATORI_ROMANIA
        e_weekend = d.weekday() >= 5
        nume_zi = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"][d.weekday()]
        label = f"{nume_zi} {d.strftime('%d.%m')}"
        if e_sarbatoare:
            label += " 🔴"
        elif e_weekend:
            label += " ⚫"
        zile.append((label, d, e_weekend or e_sarbatoare))
        d += timedelta(days=1)
    return zile

def incarca_config():
    """Incarca configuratia din fisier sau foloseste default"""
    if os.path.exists(FISIER_CONFIG):
        with open(FISIER_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return CONFIG_DEFAULT.copy()

def salveaza_config(config):
    """Salveaza configuratia in fisier"""
    with open(FISIER_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def incarca_pontaj():
    """Incarca datele de pontaj din CSV"""
    if os.path.exists(FISIER_PONTAJ):
        return pd.read_csv(FISIER_PONTAJ, encoding="utf-8")
    else:
        return pd.DataFrame(columns=[
            "timestamp", "coleg", "saptamana", "data_zi",
            "proiect", "faza", "subfaza", "ore", "comentarii"
        ])

def salveaza_inregistrare(inregistrare):
    """Adauga o inregistrare noua in CSV"""
    df = incarca_pontaj()
    rand_nou = pd.DataFrame([inregistrare])
    df = pd.concat([df, rand_nou], ignore_index=True)
    df.to_csv(FISIER_PONTAJ, index=False, encoding="utf-8")

def sterge_inregistrare(index):
    """Sterge o inregistrare dupa index"""
    df = incarca_pontaj()
    df = df.drop(index=index).reset_index(drop=True)
    df.to_csv(FISIER_PONTAJ, index=False, encoding="utf-8")

# ============================================================
# INTERFATA PRINCIPALA
# ============================================================

config = incarca_config()

# Sidebar — navigare
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/1a1a2e/ffffff?text=Allied+Engineers", width=200)
    st.markdown("---")
    pagina = st.radio(
        "Navigare",
        ["📝 Introducere ore", "📊 Rapoarte", "⚙️ Administrare"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Allied Engineers MEP © 2026")

# ============================================================
# PAGINA 1 — INTRODUCERE ORE
# ============================================================
if pagina == "📝 Introducere ore":
    st.title("📝 Pontaj ore")
    st.markdown("Completează orele lucrate pentru săptămâna selectată.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # Selectie coleg
        coleg = st.selectbox(
            "👤 Numele tău",
            options=["— selectează —"] + sorted(config["colegi"]),
            key="coleg"
        )

        # Selectie saptamana
        saptamani = get_saptamani_2026()
        optiuni_sapt = [s[0] for s in saptamani]

        # Gaseste saptamana curenta
        azi = date.today()
        sapt_curenta = 0
        for i, (label, cod, luni, dum) in enumerate(saptamani):
            if luni <= azi <= dum:
                sapt_curenta = i
                break

        sapt_selectata_label = st.selectbox(
            "📅 Săptămâna",
            options=optiuni_sapt,
            index=sapt_curenta,
            key="saptamana"
        )

        # Gaseste datele saptamanii selectate
        sapt_info = next(s for s in saptamani if s[0] == sapt_selectata_label)
        sapt_cod = sapt_info[1]
        sapt_luni = sapt_info[2]
        sapt_dum = sapt_info[3]

    with col2:
        # Afiseaza zilele saptamanii
        st.markdown("**📆 Zilele săptămânii:**")
        zile = get_zile_saptamana(sapt_luni, sapt_dum)
        for label_zi, data_zi, e_liber in zile:
            if e_liber:
                st.caption(f"~~{label_zi}~~")
            else:
                st.caption(label_zi)

    st.markdown("---")

    # ---- FORMULAR INREGISTRARE ----
    if coleg == "— selectează —":
        st.info("👆 Selectează-ți numele pentru a continua.")
    else:
        st.subheader(f"Adaugă intrare pentru {coleg}")

        with st.form("form_pontaj", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                # Ziua
                optiuni_zile = [(l, d) for l, d, e_liber in zile if not e_liber]
                optiuni_zile_labels = [l for l, d in optiuni_zile]
                zi_selectata_label = st.selectbox("📅 Ziua", optiuni_zile_labels)
                zi_selectata_data = next(d for l, d in optiuni_zile if l == zi_selectata_label)

                # Ore
                ore = st.number_input(
                    "⏱️ Ore lucrate",
                    min_value=0.5, max_value=24.0,
                    value=8.0, step=0.5
                )

            with col_b:
                # Proiect
                proiect = st.selectbox(
                    "🏗️ Proiect",
                    options=sorted(config["proiecte"])
                )

                # Faza
                faza = st.selectbox(
                    "📐 Faza",
                    options=config["faze"]
                )

            with col_c:
                # Subfaza
                optiuni_subfaza = ["— fără subfază —"] + config["subfaze"]
                subfaza = st.selectbox(
                    "🔍 Subfază",
                    options=optiuni_subfaza
                )
                if subfaza == "— fără subfază —":
                    subfaza = ""

                # Comentarii
                comentarii = st.text_input(
                    "💬 Comentarii",
                    placeholder="opțional..."
                )

            submitted = st.form_submit_button("✅ Salvează înregistrarea", use_container_width=True)

            if submitted:
                inregistrare = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "coleg": coleg,
                    "saptamana": sapt_cod,
                    "data_zi": zi_selectata_data.strftime("%Y-%m-%d"),
                    "proiect": proiect,
                    "faza": faza,
                    "subfaza": subfaza,
                    "ore": ore,
                    "comentarii": comentarii
                }
                salveaza_inregistrare(inregistrare)
                st.success(f"✅ Salvat! {ore}h pe {proiect} — {faza}")

        # ---- INTRARI EXISTENTE ALE COLEGULUI ----
        st.markdown("---")
        st.subheader(f"Intrările tale din {sapt_selectata_label.split('—')[0].strip()}")

        df = incarca_pontaj()
        df_coleg_sapt = df[(df["coleg"] == coleg) & (df["saptamana"] == sapt_cod)]

        if len(df_coleg_sapt) == 0:
            st.info("Nu ai înregistrări pentru această săptămână încă.")
        else:
            total_ore = df_coleg_sapt["ore"].sum()
            st.metric("Total ore săptămână", f"{total_ore:.1f}h")

            # Afiseaza tabelul
            df_display = df_coleg_sapt[["data_zi", "proiect", "faza", "subfaza", "ore", "comentarii"]].copy()
            df_display.columns = ["Data", "Proiect", "Faza", "Subfaza", "Ore", "Comentarii"]
            df_display["Data"] = pd.to_datetime(df_display["Data"]).dt.strftime("%d.%m")
            st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================================
# PAGINA 2 — RAPOARTE
# ============================================================
elif pagina == "📊 Rapoarte":
    st.title("📊 Rapoarte pontaj")
    st.markdown("---")

    df = incarca_pontaj()

    if len(df) == 0:
        st.info("Nu există date de pontaj încă.")
    else:
        df["ore"] = pd.to_numeric(df["ore"], errors="coerce")

        col1, col2, col3 = st.columns(3)

        # Filtre
        with col1:
            saptamani_disponibile = sorted(df["saptamana"].dropna().unique().tolist())
            sapt_filtru = st.multiselect(
                "Săptămâna",
                options=saptamani_disponibile,
                default=saptamani_disponibile[-1:] if saptamani_disponibile else []
            )

        with col2:
            colegi_disponibili = sorted(df["coleg"].dropna().unique().tolist())
            coleg_filtru = st.multiselect(
                "Coleg",
                options=colegi_disponibili
            )

        with col3:
            proiecte_disponibile = sorted(df["proiect"].dropna().unique().tolist())
            proiect_filtru = st.multiselect(
                "Proiect",
                options=proiecte_disponibile
            )

        # Aplicare filtre
        df_filtrat = df.copy()
        if sapt_filtru:
            df_filtrat = df_filtrat[df_filtrat["saptamana"].isin(sapt_filtru)]
        if coleg_filtru:
            df_filtrat = df_filtrat[df_filtrat["coleg"].isin(coleg_filtru)]
        if proiect_filtru:
            df_filtrat = df_filtrat[df_filtrat["proiect"].isin(proiect_filtru)]

        st.markdown("---")

        # Metrici sumar
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total ore", f"{df_filtrat['ore'].sum():.0f}h")
        m2.metric("Colegi activi", df_filtrat["coleg"].nunique())
        m3.metric("Proiecte active", df_filtrat["proiect"].nunique())
        m4.metric("Înregistrări", len(df_filtrat))

        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(["Per coleg", "Per proiect", "Per fază"])

        with tab1:
            ore_coleg = df_filtrat.groupby("coleg")["ore"].sum().sort_values(ascending=False).reset_index()
            ore_coleg.columns = ["Coleg", "Ore"]
            ore_coleg["Ore"] = ore_coleg["Ore"].round(1)
            st.dataframe(ore_coleg, use_container_width=True, hide_index=True)

        with tab2:
            ore_proiect = df_filtrat.groupby("proiect")["ore"].sum().sort_values(ascending=False).reset_index()
            ore_proiect.columns = ["Proiect", "Ore"]
            ore_proiect["Ore"] = ore_proiect["Ore"].round(1)
            total = ore_proiect["Ore"].sum()
            ore_proiect["Procent"] = (ore_proiect["Ore"] / total * 100).round(1).astype(str) + "%"
            st.dataframe(ore_proiect, use_container_width=True, hide_index=True)

        with tab3:
            ore_faza = df_filtrat.groupby("faza")["ore"].sum().sort_values(ascending=False).reset_index()
            ore_faza.columns = ["Faza", "Ore"]
            ore_faza["Ore"] = ore_faza["Ore"].round(1)
            st.dataframe(ore_faza, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Export
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv = df_filtrat.to_csv(index=False, encoding="utf-8")
            st.download_button(
                "⬇️ Descarcă CSV",
                data=csv,
                file_name=f"pontaj_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ============================================================
# PAGINA 3 — ADMINISTRARE
# ============================================================
elif pagina == "⚙️ Administrare":
    st.title("⚙️ Administrare liste")
    st.markdown("Modifică listele de proiecte, colegi, faze și subfaze.")

    # Parola simpla de protectie
    parola = st.text_input("🔒 Parolă admin", type="password")
    if parola != "allied2026":
        if parola:
            st.error("Parolă incorectă.")
        st.info("Introdu parola pentru a accesa administrarea.")
        st.stop()

    st.success("✅ Acces acordat.")
    st.markdown("---")

    tab_p, tab_c, tab_f, tab_sf = st.tabs(["Proiecte", "Colegi", "Faze", "Subfaze"])

    def editor_lista(tab, cheie, titlu):
        with tab:
            st.subheader(titlu)
            lista_curenta = "\n".join(config[cheie])
            lista_noua = st.text_area(
                "Un element pe linie:",
                value=lista_curenta,
                height=400,
                key=f"editor_{cheie}"
            )
            if st.button(f"💾 Salvează {titlu}", key=f"save_{cheie}"):
                elemente = [x.strip() for x in lista_noua.split("\n") if x.strip()]
                config[cheie] = elemente
                salveaza_config(config)
                st.success(f"✅ {titlu} actualizate! ({len(elemente)} elemente)")
                st.rerun()

    editor_lista(tab_p, "proiecte", "Proiecte")
    editor_lista(tab_c, "colegi", "Colegi")
    editor_lista(tab_f, "faze", "Faze")
    editor_lista(tab_sf, "subfaze", "Subfaze")

    st.markdown("---")
    st.subheader("🗃️ Date pontaj")

    df = incarca_pontaj()
    if len(df) > 0:
        st.write(f"Total înregistrări salvate: **{len(df)}**")
        st.dataframe(df.tail(20), use_container_width=True)

        # Sterge ultima inregistrare
        if st.button("🗑️ Șterge ultima înregistrare", type="secondary"):
            sterge_inregistrare(df.index[-1])
            st.success("Ultima înregistrare ștearsă.")
            st.rerun()
    else:
        st.info("Nu există date salvate încă.")
