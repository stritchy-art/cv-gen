"""Styles CSS pour l'application"""

import streamlit as st
from components.translations import t


def apply_custom_styles():
    """Applique les styles CSS personnalisés"""
    st.markdown(
        """
    <style>
        /* ===== Couleurs  ===== */
        :root {
            --default-blue: #1D435B;
            --default-brown: #8D7034;
            --default-gold: #BC944A;
            --default-light-gold: #D4B068;
            --default-dark-blue: #142E3D;
            --background-light: #F8F9FA;
            --border-color: #E0E0E0;
        }
        
        /* ===== Style général de l'application ===== */
        .main {
            background-color: var(--background-light);
        }
        
        .stApp {
            background: linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%);
        }
        
        /* ===== Titres ===== */
        h1 {
            color: var(--default-blue) !important;
            font-weight: bold !important;
            font-size: 2.5rem !important;
            border-bottom: 3px solid var(--default-gold) !important;
            padding-bottom: 10px !important;
            margin-bottom: 30px !important;
        }
        
        h2 {
            color: var(--default-blue) !important;
            font-weight: 600 !important;
            font-size: 1.8rem !important;
            margin-top: 25px !important;
            margin-bottom: 15px !important;
        }
        
        h3 {
            color: var(--default-brown) !important;
            font-weight: 600 !important;
            font-size: 1.4rem !important;
        }
        
        /* ===== Boutons ===== */
        .stButton > button {
            background: linear-gradient(135deg, var(--default-gold) 0%, var(--default-brown) 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 12px 24px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(29, 67, 91, 0.2) !important;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, var(--default-brown) 0%, var(--default-dark-blue) 100%) !important;
            box-shadow: 0 6px 12px rgba(29, 67, 91, 0.3) !important;
            transform: translateY(-2px) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(29, 67, 91, 0.2) !important;
        }
        
        /* ===== Bouton de téléchargement ===== */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #4CAF50 0%, #45A049 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 12px 24px !important;
            box-shadow: 0 2px 4px rgba(76, 175, 80, 0.2) !important;
        }
        
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #45A049 0%, #388E3C 100%) !important;
            box-shadow: 0 6px 12px rgba(76, 175, 80, 0.3) !important;
            transform: translateY(-2px) !important;
        }
        
        /* ===== Inputs et TextArea ===== */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border: 2px solid var(--border-color) !important;
            border-radius: 6px !important;
            padding: 10px !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--default-gold) !important;
            box-shadow: 0 0 0 2px rgba(188, 148, 74, 0.2) !important;
        }
        
        /* ===== Radio buttons ===== */
        .stRadio > div {
            background-color: white !important;
            border-radius: 8px !important;
            padding: 15px !important;
            border: 1px solid var(--border-color) !important;
        }
        
        .stRadio > div > label > div[data-testid="stMarkdownContainer"] > p {
            color: var(--default-blue) !important;
            font-weight: 600 !important;
        }
        
        /* ===== Checkboxes ===== */
        .stCheckbox {
            background-color: white !important;
            border-radius: 6px !important;
            padding: 10px !important;
        }
        
        .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p {
            color: var(--default-blue) !important;
            font-weight: 500 !important;
        }
        
        /* ===== File Uploader ===== */
        .stFileUploader {
            background-color: white !important;
            border: 2px dashed var(--default-gold) !important;
            border-radius: 10px !important;
            padding: 20px !important;
            transition: all 0.3s ease !important;
        }
        
        .stFileUploader:hover {
            border-color: var(--default-brown) !important;
            background-color: #FFFEF8 !important;
        }
        
        .stFileUploader > div > button {
            background-color: var(--default-gold) !important;
            color: white !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
        }
        
        /* ===== Expanders ===== */
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, white 0%, #F8F9FA 100%) !important;
            border-left: 5px solid var(--default-gold) !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            color: var(--default-blue) !important;
            padding: 15px !important;
            transition: all 0.3s ease !important;
        }
        
        .streamlit-expanderHeader:hover {
            background: linear-gradient(90deg, #F8F9FA 0%, #F0F0F0 100%) !important;
            border-left-color: var(--default-brown) !important;
        }
        
        .streamlit-expanderContent {
            background-color: white !important;
            border: 1px solid var(--border-color) !important;
            border-top: none !important;
            border-radius: 0 0 6px 6px !important;
            padding: 20px !important;
        }
        
        /* ===== Messages d'alerte ===== */
        .stSuccess {
            background-color: #E8F5E9 !important;
            border-left: 5px solid #4CAF50 !important;
            border-radius: 6px !important;
            padding: 15px !important;
            color: #1B5E20 !important;
        }
        
        .stInfo {
            background-color: #E3F2FD !important;
            border-left: 5px solid var(--default-blue) !important;
            border-radius: 6px !important;
            padding: 15px !important;
            color: var(--default-dark-blue) !important;
        }
        
        .stWarning {
            background-color: #FFF3E0 !important;
            border-left: 5px solid var(--default-gold) !important;
            border-radius: 6px !important;
            padding: 15px !important;
            color: #E65100 !important;
        }
        
        .stError {
            background-color: #FFEBEE !important;
            border-left: 5px solid #F44336 !important;
            border-radius: 6px !important;
            padding: 15px !important;
            color: #B71C1C !important;
        }
        
        /* ===== Barre de progression ===== */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, var(--default-gold) 0%, var(--default-brown) 100%) !important;
            border-radius: 10px !important;
        }
        
        .stProgress > div > div {
            background-color: #E0E0E0 !important;
            border-radius: 10px !important;
            height: 12px !important;
        }
        
        /* ===== Spinner ===== */
        .stSpinner > div {
            border-top-color: var(--default-gold) !important;
        }
        
        /* ===== Sidebar ===== */
        .css-1d391kg, [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--default-blue) 0%, var(--default-dark-blue) 100%) !important;
        }
        
        .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3,
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: white !important;
        }
        
        .css-1d391kg p, [data-testid="stSidebar"] p {
            color: #E0E0E0 !important;
        }
        
        /* ===== Tabs ===== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: white;
            border-radius: 8px;
            padding: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 6px;
            color: var(--default-blue);
            font-weight: 600;
            padding: 10px 20px;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #F8F9FA;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--default-gold) 0%, var(--default-brown) 100%) !important;
            color: white !important;
        }
        
        /* ===== Dataframe / Tables ===== */
        .stDataFrame {
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        .stDataFrame thead tr th {
            background: linear-gradient(135deg, var(--default-blue) 0%, var(--default-dark-blue) 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px !important;
        }
        
        .stDataFrame tbody tr:nth-child(even) {
            background-color: #F8F9FA !important;
        }
        
        .stDataFrame tbody tr:hover {
            background-color: #FFF9E6 !important;
        }
        
        /* ===== Selectbox / Multiselect ===== */
        .stSelectbox > div > div,
        .stMultiSelect > div > div {
            border: 2px solid var(--border-color) !important;
            border-radius: 6px !important;
        }
        
        .stSelectbox > div > div:focus-within,
        .stMultiSelect > div > div:focus-within {
            border-color: var(--default-gold) !important;
            box-shadow: 0 0 0 2px rgba(188, 148, 74, 0.2) !important;
        }
        
        /* ===== Cartes / Containers ===== */
        .element-container {
            transition: all 0.3s ease !important;
        }
        
        /* ===== Scrollbar ===== */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #F1F1F1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, var(--default-gold) 0%, var(--default-brown) 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, var(--default-brown) 0%, var(--default-dark-blue) 100%);
        }
        
        /* ===== Animations ===== */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .element-container {
            animation: fadeIn 0.4s ease-out;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_footer():
    """Affiche le footer de l'application"""
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #1D435B; padding: 20px;'>
            <p style='margin: 0; font-weight: bold; font-size: 18px;'>{t('footer_company')}</p>
            <p style='margin: 0; font-size: 14px;'>{t('footer_copyright')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
