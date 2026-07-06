from aqt import mw, gui_hooks
from aqt.utils import showInfo
from aqt.qt import *
from datetime import datetime, date, timedelta
import math
import time
import os
import json

# ==========================================
# MOTOR DINÁMICO DE TRADUCCIÓN
# ==========================================
try:
    anki_lang = mw.pm.meta.get("defaultLang", "en")[:2]
except:
    anki_lang = "en"

addon_dir = os.path.dirname(__file__)
translations_dir = os.path.join(addon_dir, "translations")
CURRENT_STRINGS = {}

def cargar_idioma():
    global CURRENT_STRINGS
    en_path = os.path.join(translations_dir, "en.json")
    if os.path.exists(en_path):
        try:
            with open(en_path, "r", encoding="utf-8") as f:
                CURRENT_STRINGS = json.load(f)
        except: pass
    if anki_lang != "en":
        lang_path = os.path.join(translations_dir, f"{anki_lang}.json")
        if os.path.exists(lang_path):
            try:
                with open(lang_path, "r", encoding="utf-8") as f:
                    CURRENT_STRINGS.update(json.load(f))
            except: pass

cargar_idioma()

def tr(key):
    return CURRENT_STRINGS.get(key, key)

# ==========================================
# INTERFAZ Y LÓGICA PRINCIPAL
# ==========================================
class AnalisisEstudioDialog(QDialog):
    def __init__(self, parent=None, deck_id=None, deck_name=""):
        super().__init__(parent)
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.setWindowTitle(tr("title"))
        self.setMinimumWidth(550)
        self.setMinimumHeight(600)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel(f"<h3 style='margin-bottom: 5px; color: #333;'>{tr('deck')} {self.deck_name}</h3>"))

        self.tabs = QTabWidget()
        
        # PESTAÑA 1: PRONÓSTICO
        self.tab_pronostico = QWidget()
        layout_p = QVBoxLayout()
        layout_p.addWidget(QLabel(tr("tab1_desc")))
        btn_p = QPushButton(tr("btn_calc1"))
        btn_p.clicked.connect(self.calcular_pronostico)
        btn_p.setStyleSheet("padding: 8px; font-weight: bold; background-color: #4CAF50; color: white; border-radius: 4px;")
        layout_p.addWidget(btn_p)
        self.lbl_p = QLabel("")
        self.lbl_p.setWordWrap(True)
        layout_p.addWidget(self.lbl_p)
        layout_p.addStretch()
        self.tab_pronostico.setLayout(layout_p)

        # PESTAÑA 2: PLANIFICADOR
        self.tab_meta = QWidget()
        layout_m = QVBoxLayout()
        layout_m.addWidget(QLabel(tr("tab2_desc")))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate().addDays(14))
        layout_m.addWidget(self.date_edit)
        btn_m = QPushButton(tr("btn_calc2"))
        btn_m.clicked.connect(self.calcular_meta)
        btn_m.setStyleSheet("padding: 8px; font-weight: bold; background-color: #2196F3; color: white; border-radius: 4px;")
        layout_m.addWidget(btn_m)
        self.lbl_m = QLabel("")
        self.lbl_m.setWordWrap(True)
        layout_m.addWidget(self.lbl_m)
        layout_m.addStretch()
        self.tab_meta.setLayout(layout_m)

        # PESTAÑA 3: REPORTE AVANZADO
        self.tab_reporte = QWidget()
        layout_r = QVBoxLayout()
        btn_r = QPushButton("Generar Analítica Completa")
        btn_r.clicked.connect(self.generar_reporte)
        btn_r.setStyleSheet("padding: 10px; font-weight: bold; background-color: #673AB7; color: white; border-radius: 4px;")
        layout_r.addWidget(btn_r)
        
        # Cambiamos QLabel por QTextBrowser para permitir Scroll
        self.txt_r = QTextBrowser()
        self.txt_r.setOpenExternalLinks(False)
        self.txt_r.setStyleSheet("background-color: #1e1e1e; color: #f5f5f5; border-radius: 5px; padding: 10px;")
        layout_r.addWidget(self.txt_r)
        
        self.tab_reporte.setLayout(layout_r)

        self.tabs.addTab(self.tab_pronostico, tr("tab1_name"))
        self.tabs.addTab(self.tab_meta, tr("tab2_name"))
        self.tabs.addTab(self.tab_reporte, "📊 Analítica Pro")
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def obtener_ids_mazos(self):
        try:
            ids = mw.col.decks.deck_and_child_ids(self.deck_id)
            return ",".join(map(str, ids))
        except AttributeError:
            hijos = mw.col.decks.children(self.deck_id)
            ids = [str(self.deck_id)] + [str(hijo[1]) for hijo in hijos]
            return ",".join(ids)

    def generar_barra(self, porcentaje, color):
        """Genera una barra de progreso usando tablas para compatibilidad total con Qt Rich Text"""
        p = max(0, min(100, int(porcentaje))) # Asegura que el valor esté entre 0 y 100
        resto = 100 - p
        
        # Si el porcentaje es 0, dibujamos solo el fondo gris
        if p == 0:
            return """
            <table width="100%" height="8" cellspacing="0" cellpadding="0" style="margin-top: 2px; margin-bottom: 8px;">
                <tr><td style="background-color: #444;"></td></tr>
            </table>
            """
            
        # Si hay porcentaje, dividimos la tabla proporcionalmente
        return f"""
        <table width="100%" height="8" cellspacing="0" cellpadding="0" style="margin-top: 2px; margin-bottom: 8px;">
            <tr>
                <td width="{p}%" style="background-color: {color};"></td>
                <td width="{resto}%" style="background-color: #444;"></td>
            </tr>
        </table>
        """

    def calcular_pronostico(self):
        dids = self.obtener_ids_mazos()
        nuevas = mw.col.db.scalar(f"select count() from cards where did in ({dids}) and queue = 0")
        if nuevas == 0: 
            self.lbl_p.setText(tr("msg_done")); return
        hace_7d = (time.time() - (7 * 24 * 60 * 60)) * 1000
        ritmo = (mw.col.db.scalar(f"select count(distinct cid) from revlog where id > {hace_7d} and type = 0 and cid in (select id from cards where did in ({dids}))") or 0) / 7.0
        if ritmo > 0:
            dias = nuevas / ritmo
            fin = date.today() + timedelta(days=int(dias))
            self.lbl_p.setText(tr("result_date").format(fecha=fin.strftime('%d/%m/%Y'), dias=int(dias)))
        else: 
            self.lbl_p.setText(tr("msg_nodata"))

    def calcular_meta(self):
        target = self.date_edit.date().toPyDate()
        dias = (target - date.today()).days
        if dias <= 0: 
            self.lbl_m.setText(tr("msg_date_err")); return
        dids = self.obtener_ids_mazos()
        nuevas = mw.col.db.scalar(f"select count() from cards where did in ({dids}) and queue = 0")
        if nuevas == 0: 
            self.lbl_m.setText(tr("msg_done")); return
        req = nuevas / dias
        limite_30d = (time.time() - (30 * 24 * 60 * 60)) * 1000
        hist = (mw.col.db.scalar(f"select count(distinct cid) from revlog where id > {limite_30d} and type = 0") or 1) / 30.0
        prob = min(99, max(5, int((hist / req) * 100)))
        color = "#4CAF50" if prob > 80 else "#F44336"
        self.lbl_m.setText(tr("result_goal").format(meta=math.ceil(req), color=color, prob=prob))

    def generar_reporte(self):
        dids = self.obtener_ids_mazos()
        
        # 1. SALUD DEL MAZO Y DIFICULTAD
        total = mw.col.db.scalar(f"select count() from cards where did in ({dids})") or 1
        nuevas = mw.col.db.scalar(f"select count() from cards where did in ({dids}) and queue = 0")
        maduras = mw.col.db.scalar(f"select count() from cards where did in ({dids}) and ivl >= 21")
        jovenes = total - nuevas - maduras
        sanguijuelas = mw.col.db.scalar(f"select count() from cards where did in ({dids}) and lapses >= 8")
        facilidad_promedio = mw.col.db.scalar(f"select avg(factor) from cards where did in ({dids}) and queue in (1,2,3)") or 2500

        pct_maduras = (maduras / total) * 100
        pct_jovenes = (jovenes / total) * 100
        pct_nuevas = (nuevas / total) * 100

        # 2. HÁBITOS, TIEMPO Y BOTONES
        repasos = mw.col.db.all(f"select ease, time, id from revlog where cid in (select id from cards where did in ({dids}))")
        
        if not repasos:
            self.txt_r.setHtml(f"<h3 style='color:#F44336;'>Sin datos suficientes</h3><p>Estudia unas cuantas tarjetas para generar analíticas.</p>")
            return

        total_repasos = len(repasos)
        tiempo_total_min = sum([r[1] for r in repasos]) / 1000 / 60
        velocidad_promedio = sum([r[1] for r in repasos]) / total_repasos / 1000.0

        b_otravez = len([r for r in repasos if r[0] == 1])
        b_dificil = len([r for r in repasos if r[0] == 2])
        b_bien = len([r for r in repasos if r[0] == 3])
        b_facil = len([r for r in repasos if r[0] == 4])

        tasa_acierto = ((b_dificil + b_bien + b_facil) / total_repasos) * 100
        
        # 3. RACHAS Y CARGA FUTURA
        dias_unicos = len(set([datetime.fromtimestamp(r[2]/1000.0).date() for r in repasos]))
        manana = (date.today() + timedelta(days=1)).toordinal() - date(1970, 1, 1).toordinal()
        carga_futura = mw.col.db.scalar(f"select count() from cards where did in ({dids}) and due <= {manana} and queue in (2,3)")

        # CONSTRUCCIÓN HTML (Modo Oscuro Elegante con Gráficas CSS)
        html = f"""
        <div style="font-family: sans-serif; font-size: 13px;">
            <h2 style="color: #BB86FC; border-bottom: 1px solid #555; padding-bottom: 5px; margin-bottom: 10px;">🧠 Analítica de Maestría</h2>
            
            <p style="margin-bottom: 2px;"><b>Progreso Global del Mazo</b> ({total} tarjetas)</p>
            <table width="100%" cellspacing="0" cellpadding="2">
                <tr><td width="30%">Dominadas: {maduras}</td><td>{self.generar_barra(pct_maduras, '#4CAF50')}</td></tr>
                <tr><td>En Aprendizaje: {jovenes}</td><td>{self.generar_barra(pct_jovenes, '#FFC107')}</td></tr>
                <tr><td>Sin Ver: {nuevas}</td><td>{self.generar_barra(pct_nuevas, '#2196F3')}</td></tr>
            </table>

            <h3 style="color: #03DAC6; margin-top: 20px; border-bottom: 1px solid #555;">⚡ Rendimiento y Hábitos</h3>
            <ul style="list-style-type: none; padding-left: 0; margin-top: 5px;">
                <li style="margin-bottom: 5px;">🎯 <b>Tasa de Retención:</b> <span style="color:{'#4CAF50' if tasa_acierto > 85 else '#FF9800'}; font-weight:bold;">{tasa_acierto:.1f}%</span> (Ideal: 85-90%)</li>
                <li style="margin-bottom: 5px;">⏱️ <b>Velocidad de Respuesta:</b> {velocidad_promedio:.1f} segundos/tarjeta</li>
                <li style="margin-bottom: 5px;">🔥 <b>Días de Estudio Activo:</b> {dias_unicos} días</li>
                <li style="margin-bottom: 5px;">⏳ <b>Tiempo Total Invertido:</b> {int(tiempo_total_min)} minutos</li>
            </ul>

            <h3 style="color: #FF8A65; margin-top: 20px; border-bottom: 1px solid #555;">📊 Carga de Trabajo (Botones)</h3>
            <p style="font-size: 11px; color: #aaa; margin-top: 0;">Historial de {total_repasos} interacciones totales</p>
            <table width="100%" cellspacing="0" cellpadding="2">
                <tr><td width="25%" style="color:#F44336;">Otra vez ({b_otravez})</td><td>{self.generar_barra((b_otravez/total_repasos)*100, '#F44336')}</td></tr>
                <tr><td style="color:#795548;">Difícil ({b_dificil})</td><td>{self.generar_barra((b_dificil/total_repasos)*100, '#795548')}</td></tr>
                <tr><td style="color:#4CAF50;">Bien ({b_bien})</td><td>{self.generar_barra((b_bien/total_repasos)*100, '#4CAF50')}</td></tr>
                <tr><td style="color:#2196F3;">Fácil ({b_facil})</td><td>{self.generar_barra((b_facil/total_repasos)*100, '#2196F3')}</td></tr>
            </table>

            <h3 style="color: #E91E63; margin-top: 20px; border-bottom: 1px solid #555;">🏥 Salud del Mazo</h3>
            <ul style="list-style-type: none; padding-left: 0; margin-top: 5px;">
                <li style="margin-bottom: 5px;">⚖️ <b>Facilidad Promedio:</b> {facilidad_promedio/10:.0f}% <span style="font-size:11px; color:#aaa;">(>200% es saludable)</span></li>
                <li style="margin-bottom: 5px;">🩸 <b>Tarjetas Sanguijuela:</b> {sanguijuelas} tarjetas sobre-estudiadas <span style="font-size:11px; color:#aaa;">(Lapses > 8)</span></li>
                <li style="margin-bottom: 5px;">📅 <b>Proyección de Repasos:</b> ~{carga_futura} tarjetas para mañana</li>
            </ul>
        </div>
        """
        self.txt_r.setHtml(html)

def abrir_planificador(did=None):
    if not mw.col: return
    if did is None:
        try: did = mw.col.decks.get_current_id()
        except: did = mw.col.decks.all_ids()[0]
    deck = mw.col.decks.get(did)
    deck_name = deck['name'] if deck else "Deck"
    dlg = AnalisisEstudioDialog(mw, did, deck_name)
    dlg.exec()

def al_mostrar_menu_engranaje(menu, did):
    action = menu.addAction(tr("menu_gear"))
    action.triggered.connect(lambda: abrir_planificador(did))

def registrar_menu_herramientas():
    action = QAction(tr("menu_tools"), mw)
    action.triggered.connect(lambda: abrir_planificador())
    mw.form.menuTools.addAction(action)

gui_hooks.deck_browser_will_show_options_menu.append(al_mostrar_menu_engranaje)
registrar_menu_herramientas()