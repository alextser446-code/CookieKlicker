import math
import random
import pygame
from array import array

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Einen kurzen, weichen Klickton im speicher erzeugen
klick_sound = None
sound_lautstaerke = 1.0
mixer_info = pygame.mixer.get_init()

if mixer_info is not None:
    sample_rate, _, kanaele = mixer_info
    dauer = 0.09
    anzahl_samples = int(sample_rate * dauer)
    sound_daten = array("h")

    for i in range(anzahl_samples):
        fortschritt = i / anzahl_samples
        zeit = i / sample_rate

        # Der Ton wird etwas tiefer und leiser, damit er wie ein sanfter Klick klingt.
        frequenz = 1050 - 400 * fortschritt
        lautstaerke = 9000 * (1 - fortschritt) ** 2
        wert = int(
            lautstaerke
            * (
                math.sin(2 * math.pi * frequenz * zeit)
                + 0.2 * math.sin(4 * math.pi *frequenz * zeit)
            )
        )

        # Samples fÃ¼r alle AudiokanÃ¤le hinzufÃ¼gen.
        for _ in range(kanaele):
            sound_daten.append(wert)

    klick_sound = pygame.mixer.Sound(buffer=sound_daten.tobytes())

    if klick_sound is not None:
        klick_sound.set_volume(sound_lautstaerke)

    

def mache_sammel_sound(start_frequenz, end_frequenz, dauer):
    """Erzeugt einen kurzen Sound ohne externe Datei."""
    if mixer_info is None:
        return None

    sample_rate, _, kanaele = mixer_info
    anzahl_samples = max(1, int(sample_rate * dauer))
    sound_daten = array("h")

    for index in range(anzahl_samples):
        fortschritt = index / anzahl_samples
        zeit = index / sample_rate
        frequenz = start_frequenz + (end_frequenz - start_frequenz) * fortschritt
        huellkurve = (1.0 - fortschritt) ** 2
        wert = int(
            7000
            * huellkurve
            * math.sin(2 * math.pi * frequenz * zeit)
        )

        for _ in range(kanaele):
            sound_daten.append(wert)

    sound = pygame.mixer.Sound(buffer=sound_daten.tobytes())
    sound.set_volume(sound_lautstaerke)
    return sound


def mache_goldenen_erscheinungssound():
    """Erzeugt eine kurze, aufsteigende GlÃ¶ckchenmelodie fÃ¼r den Golden Cookie."""
    if mixer_info is None:
        return None

    sample_rate, _, kanaele = mixer_info
    dauer = 1.15
    anzahl_samples = int(sample_rate * dauer)
    noten = (
        (880.00, 0.00),
        (1108.73, 0.10),
        (1318.51, 0.20),
        (1760.00, 0.31),
        (2093.00, 0.43),
    )
    sound_daten = array("h")

    for index in range(anzahl_samples):
        zeit = index / sample_rate
        wert = 0.0

        for frequenz, startzeit in noten:
            lokalzeit = zeit - startzeit
            if lokalzeit < 0:
                continue

            huellkurve = (1.0 - math.exp(-lokalzeit * 70)) * math.exp(-lokalzeit * 4.2)
            leichte_schwankung = 1.0 + 0.002 * math.sin(2 * math.pi * 5 * lokalzeit)
            ton = 2 * math.pi * frequenz * leichte_schwankung * lokalzeit

            # Grundton mit zwei leisen ObertÃ¶nen gibt dem Ton einen hellen Glockenklang.
            wert += 2600 * huellkurve * (
                math.sin(ton)
                + 0.32 * math.sin(ton * 2.76)
                + 0.12 * math.sin(ton * 4.08)
            )

        wert = max(-32767, min(32767, int(wert)))
        for _ in range(kanaele):
            sound_daten.append(wert)

    sound = pygame.mixer.Sound(buffer=sound_daten.tobytes())
    sound.set_volume(sound_lautstaerke)
    return sound


goldener_cookie_erscheint_sound = mache_goldenen_erscheinungssound()
goldener_cookie_einsammel_sound = mache_sammel_sound(950, 1700, 0.20)
kiste_erscheint_sound = mache_sammel_sound(360, 700, 0.32)
kiste_einsammel_sound = mache_sammel_sound(520, 980, 0.24)

wheel_start_sound = mache_sammel_sound(420, 950, 0.22)
wheel_stop_sound = mache_sammel_sound(950, 420, 0.18)
wheel_win_sound = mache_sammel_sound(700, 1500, 0.35)
wheel_lose_sound = mache_sammel_sound(300, 170, 0.32)
wheel_spin_loop_sound = mache_sammel_sound(620, 380, 0.30)
wheel_spin_channel = None

def sammelsounds_lautstaerke_setzen():
    for sound in (
        goldener_cookie_erscheint_sound,
        goldener_cookie_einsammel_sound,
        kiste_erscheint_sound,
        kiste_einsammel_sound,
        wheel_start_sound,
        wheel_stop_sound,
        wheel_win_sound,
        wheel_lose_sound,
    ):
        if sound is not None:
            sound.set_volume(sound_lautstaerke)
    if wheel_spin_loop_sound is not None:
        wheel_spin_loop_sound.set_volume(sound_lautstaerke * 0.28)

# Fenster und Farben: Vollbild in der aktuellen Bildschirmaufloesung
FENSTER = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
BREITE, HOEHE = FENSTER.get_size()
ist_vollbild = True
pygame.display.set_caption("Cookie Clicker")

HINTERGRUND = (247, 239, 220)
BRAUN = (112, 66, 42)
DUNKELBRAUN = (74, 43, 30)
TEXTFARBE = (58, 43, 33)

schrift = pygame.font.SysFont("arial", 32, bold=True)
kleine_schrift = pygame.font.SysFont("arial", 20)
inventar_detail_schrift = pygame.font.SysFont("arial", 13)
inventar_kopf_schrift = pygame.font.SysFont("arial", 16, bold=True)

clock = pygame.time.Clock()

cookie_anzahl = 0
goldene_cookies = 100
truhe_belohnung_text = ""
truhe_belohnung_timer = 0.0
# Zustand für das Spinning Wheel
spinning_wheel_menu_feld = pygame.Rect(0, 0, 1, 1)

wheel_bet = 1
wheel_current_bet = 0
wheel_spinning = False
wheel_result_index = None
wheel_result = None
wheel_angle = 0.0
wheel_start_angle = 0.0
wheel_final_angle = 0.0
wheel_spin_elapsed = 0.0
wheel_spin_duration = 4.5
wheel_result_timer = 0.0
wheel_zeit = 0.0

cookies_pro_klick = 1
cookies_pro_sekunde = 0.0
auto_cursor_rate = 0.0
auto_cursor_timer = 0.0

upgrades = [
    {
        "name": "More Cookies per Click",
        "preis": 300,
        "level": 0,
        "art": "click",
        "menge": 1,
        "effekt": "+1 Cookie per click"
    },
    {
        "name": "Auto Cursor",
        "preis": 1000,
        "level": 0,
        "art": "cursor",
        "menge": 0,
        "effekt": "1 CPS first, then +3 CPS",
    },
    {
        "name": "Cookie Grandma",
        "preis": 5000,
        "level": 0,
        "art": "production",
        "menge": 5,
        "effekt": "+5 Cookies per second",
    },
    {
        "name": "Cookie Oven",
        "preis": 10000,
        "level": 0,
        "art": "production",
        "menge": 10,
        "effekt": "+10 Cookies per second",
    },
    {
        "name": "Magic Fingers",
        "preis": 20000,
        "level": 0,
        "art": "click",
        "menge": 5,
        "effekt": "+5 Cookies per click",
    },
]

upgrade_kauf_felder = []
cookie_mitte = (BREITE // 2, HOEHE // 2 + 35)
cookie_radius = 135

# Zustaende fuer die zeitbasierten Animationen
hover_skalierung = 1.0
cookie_skalierung = 1.0
skalierung_tempo = 0.0
dreh_winkel = 0.0
dreh_tempo = 0.0
kruemel = []
klick_texte = []

# Zustand und Bereiche des Shops
shop_offen = False
shop_breite = 360
shop_x = float(BREITE)
shop_panel = pygame.Rect(BREITE, 100, shop_breite, HOEHE - 130)
shop_schliessen = pygame.Rect(BREITE + shop_breite - 48, 112, 34, 34)
shop_button = pygame.Rect(BREITE - 125, 18, 105, 46)

# Welche Shop Seite gerade angezeigt wird
shop_seite = "upgrades"

# Positionen der Shop Tabs und kaufbuttons 
shop_upgrades_tab = pygame.Rect(0, 0, 1, 1)
shop_cookie_tab = pygame.Rect(0, 0, 1, 1)
cookie_shop_kauf_felder = []

# Cookie-Designs: nur das Aussehen und der Preis werden hier gespeichert.
COOKIE_DESIGNS = (
    {"name": "Classic Cookie", "preis": 0, "farbe": (205, 137, 65),
     "schoko": (78, 39, 27)},
    {"name": "Chocolate Cookie", "preis": 5, "farbe": (112, 65, 43),
     "schoko": (48, 28, 22)},
    {"name": "Strawberry Cookie", "preis": 10, "farbe": (224, 145, 135),
     "schoko": (112, 53, 55)},
    {"name": "Rainbow Cookie", "preis": 20, "farbe": (225, 183, 86),
     "schoko": (89, 74, 172)},
    {"name": "Ice Cookie", "preis": 30, "farbe": (164, 218, 224),
     "schoko": (82, 145, 169)},
    {"name": "Galaxy Cookie", "preis": 50, "farbe": (91, 70, 143),
     "schoko": (224, 160, 242)},
    {"name": "Golden Cookie", "preis": 100, "farbe": (246, 190, 48),
     "schoko": (132, 78, 25)},
)

# Classic ist von Anfang an corhanden. Käufe gelten für diese Spielsitzung.
COOKIE_DESIGNS_OWNED = {"Classic Cookie"}
selected_cookie_design = "Classic Cookie"
cookie_design_grid_rect = pygame.Rect(0, 0, 1, 1)
cookie_design_select_felder = []
cookie_design_scroll = 0
cookie_design_scroll_max = 0

# Zustand und Button fuer das Inventar
inventar_offen = False
inventar_seite = "upgrades"
inventar_knopf = pygame.Rect(18, HOEHE - 58, 142, 38)
inventar_panel_y = float(HOEHE)
inventar_chests_feld = pygame.Rect(0, 0, 1, 1)
inventar_upgrades_feld = pygame.Rect(0, 0, 1, 1)
inventar_truhen_liste_feld = pygame.Rect(0, 0, 1, 1)
inventar_truhen_scroll = 0
inventar_truhen_scroll_max = 0

# Speichert die anklickbaren bereiche der sichbaren upgrade-symbole
inventar_symbol_bereiche = []
truhe_open_felder = []
truhe_alle_felder = []

# Sammelobjekte: zentrale Zeiten und Wahrschienlichkiten 
GOLDEN_COOKIE_INTERVALL = 90.0
GOLDEN_COOKIE_CHANCE = 0.10  # 10 % pro 90 Sekunden
GOLDEN_COOKIE_LEBENSZEIT = 15.0

TREASURE_CHEST_INTERVALL = 90.0
TREASURE_CHEST_CHANCE = 0.01  # 1 % pro 90 Sekunden
TREASURE_CHEST_LEBENSZEIT = 20.0

TREASURE_CHEST_ARTEN = (
    "Uncommon Chest",
    "Rare Chest",
    "Epic Chest",
    "Legendary Chest",
)
TREASURE_CHEST_GEWICHTE = (60, 25, 12, 3)
TREASURE_CHEST_FARBEN = {
    "Uncommon Chest": (105, 175, 95),
    "Rare Chest": (75, 145, 235),
    "Epic Chest": (175, 95, 230),
    "Legendary Chest": (255, 185, 45),
}

TRUHEN_OEFFNEN_DATEN = {
    "Uncommon Chest": {
        "preis": 1,
        "belohnung": (1_000_000, 3_000_000),
    },
    "Rare Chest": {
        "preis": 3,
        "belohnung": (3_000_000, 8_000_000),
    },
    "Epic Chest": {
        "preis": 7,
        "belohnung": (8_000_000, 20_000_000),
    },
    "Legendary Chest": {
        "preis": 15,
        "belohnung": (20_000_000, 50_000_000),
    },
}

# Feste, unregelmaessige Positionen relativ zum goldenen Cookie-Radius.
# Die Werte bleiben zwischen den Frames gleich.
GOLDENER_COOKIE_SCHOKO = (
    (-0.48, -0.24, 0.12, 0.72),
    (-0.30, -0.52, 0.15, 0.82),
    (0.08, -0.38, 0.10, 0.70),
    (0.39, -0.39, 0.13, 0.78),
    (0.52, -0.08, 0.10, 0.72),
    (0.31, 0.13, 0.16, 0.70),
    (0.49, 0.34, 0.12, 0.82),
    (0.07, 0.45, 0.11, 0.72),
    (-0.34, 0.41, 0.15, 0.78),
    (-0.53, 0.05, 0.10, 0.72),
    (-0.10, -0.04, 0.14, 0.80),
)
GOLDENER_COOKIE_SCHOKO_FARBEN = (
    (91, 48, 20),
    (112, 59, 23),
    (128, 70, 28),
    (99, 50, 19),
)

goldener_cookie_timer = 0.0
treasure_chest_timer = 0.0  # Der erste regulÃ¤re Versuch kommt nach 90 Sekunden
aktives_sammelobjekt = None
sammelobjekt_animationszeit = 0.0
goldener_cookie_verpasst_timer = 0.0

# Das vorhandene Inventar enhÃ¤lt Upgrage lebel aber keine kisten gegenstÃ¤nde.
#hier werden nur die gesammelten kistenarten abgelegt.
inventar_kisten = []

# Diese spielzeit stoppt im PausemenÃ¼ auch die Hintergrundanimation.
spiel_zeit = 0.0

# Aktueller Bildschirm: Spiel, MenÃ¼ oder Einstellungen
spiel_status = "game"

# Bereiche der Menue-Schaltflaechen
menue_oben = HOEHE // 2 - 190
weiter_feld = pygame.Rect(BREITE // 2 - 130, menue_oben + 70, 260, 52)
einstellungen_feld = pygame.Rect(BREITE // 2 - 130, menue_oben + 130, 260, 52)
spinning_wheel_menu_feld = pygame.Rect(
    BREITE // 2 - 130, menue_oben + 190, 260, 52
)
verlassen_feld = pygame.Rect(BREITE // 2 - 130, menue_oben + 250, 260, 52)
zurueck_feld = pygame.Rect(BREITE // 2 - 130, menue_oben + 245, 260, 52)

# GewÃ¤hlter Hintergrund und SchaltflÃ¤chen auf der Einstellungsseite
# Einstellungen bekommen einen eigenen, mittigen Bereich.
hintergrund_modus = "vanilla"
settings_panel_hoehe = min(460, HOEHE - 20)
settings_oben = max(10, (HOEHE - settings_panel_hoehe) // 2)

purple_feld = pygame.Rect(
    BREITE // 2 - 150, settings_oben + 78, 300, 50
)
vanilla_feld = pygame.Rect(
    BREITE // 2 - 150, settings_oben + 135, 300, 50
)

lautstaerke_linie = pygame.Rect(
    BREITE // 2 - 120, settings_oben + 225, 240, 8
)
lautstaerke_feld = pygame.Rect(
    BREITE // 2 - 140, settings_oben + 210, 280, 38
)
lautstaerke_ziehen = False

zurueck_feld = pygame.Rect(
    BREITE // 2 - 130,
    settings_oben + settings_panel_hoehe - 52,
    260,
    42
)

cookie_design_grid_rect = pygame.Rect(
    BREITE // 2 - 174,
    settings_oben + 270,
    348,
    max(1, settings_panel_hoehe - 330)
)

# Schokostuecke einmalig und gleichmaessig auf mehreren Ringen verteilen.
random.seed(7)
schokostuecke = []
ringe = [(0.0, 1), (0.30, 7), (0.57, 11), (0.80, 15)]

for ring_anteil, anzahl in ringe:
    startwinkel = random.uniform(0, math.tau)
    for index in range(anzahl):
        winkel = startwinkel + math.tau * index / anzahl
        winkel += random.uniform(-0.12, 0.12)
        groesse = random.randint(6, 11)
        abstand = ring_anteil * (cookie_radius - 28)
        if ring_anteil > 0:
            abstand += random.uniform(-5, 5)
        abstand = min(abstand, cookie_radius - groesse * 1.5 - 16)

        x = cookie_mitte[0] + math.cos(winkel) * abstand
        y = cookie_mitte[1] + math.sin(winkel) * abstand
        schokostuecke.append((
            int(x), int(y), groesse,
            random.choice(("rund", "oval", "eckig")),
            random.randrange(4)
        ))

schoko_farben = [
    (74, 38, 28),
    (91, 46, 32),
    (105, 56, 37),
    (63, 33, 26),
]

def zeichne_cookie_design(flaeche, mitte, radius, design, zeit=0.0):
    """Zeichnet Cookie und Spezialeffekt; Vorschau und Spiel nutzen denselben Code."""
    faktor = radius / cookie_radius
    design_name = design["name"]
    basisfarbe = design["farbe"]
    randfarbe = tuple(int(wert * 0.68) for wert in basisfarbe)
    innenfarbe = tuple(int(wert * 0.96) for wert in basisfarbe)
    lichtfarbe = tuple(
        min(255, int(wert * 1.18 + 8))
        for wert in basisfarbe
    )

    schatten_versatz = max(1, round(7 * faktor))
    rand_abstand = max(1, round(5 * faktor))
    licht_abstand = max(2, round(12 * faktor))

    # Einige Cookies leuchten passend zu ihrem eigenen Thema.
    aura_farben = {
        "Strawberry Cookie": (255, 100, 145),
        "Ice Cookie": (100, 220, 255),
        "Galaxy Cookie": (165, 85, 255),
        "Golden Cookie": (255, 190, 45),
    }
    if design_name in aura_farben:
        aura_farbe = aura_farben[design_name]
        aura_rand = max(3, round(9 * faktor))
        for zusatz, alpha in ((aura_rand, 18), (aura_rand // 2, 30)):
            pygame.draw.circle(
                flaeche,
                (*aura_farbe, alpha),
                mitte,
                radius + zusatz
            )

    # Galaxy und Golden bekommen einen klareren Leuchtring.
    if design_name in ("Galaxy Cookie", "Golden Cookie"):
        ring_farbe = (
            (212, 145, 255)
            if design_name == "Galaxy Cookie"
            else (255, 231, 130)
        )
        ring_rand = max(3, round(5 * faktor))
        pygame.draw.circle(
            flaeche,
            (*ring_farbe, 155),
            mitte,
            radius + max(1, round(2 * faktor)),
            ring_rand
        )

    pygame.draw.circle(
        flaeche,
        (105, 68, 39, 55),
        (mitte[0] + schatten_versatz, mitte[1] + schatten_versatz),
        radius + max(1, round(3 * faktor))
    )
    pygame.draw.circle(flaeche, randfarbe, mitte, radius)
    pygame.draw.circle(
        flaeche,
        innenfarbe,
        mitte,
        max(1, radius - rand_abstand)
    )
    pygame.draw.circle(
        flaeche,
        lichtfarbe,
        (mitte[0], mitte[1] - max(1, round(3 * faktor))),
        max(1, radius - licht_abstand)
    )
    pygame.draw.circle(
        flaeche,
        randfarbe,
        mitte,
        max(1, radius - max(2, round(8 * faktor))),
        max(1, round(2 * faktor))
    )

    bogen_rand = max(2, round(14 * faktor))
    bogen_rechteck = pygame.Rect(
        mitte[0] - radius + bogen_rand,
        mitte[1] - radius + bogen_rand,
        max(1, 2 * (radius - bogen_rand)),
        max(1, 2 * (radius - bogen_rand))
    )
    pygame.draw.arc(
        flaeche,
        lichtfarbe,
        bogen_rechteck,
        math.radians(200),
        math.radians(330),
        max(1, round(3 * faktor))
    )

    # Jedes Design bekommt hier sein eigenes Detail auf der Cookie-Fläche.
    if design_name == "Classic Cookie":
        # Helle Zuckerkristalle am Rand.
        for index in range(10):
            winkel = index * math.tau / 10 + 0.18
            kristall_radius = radius * 0.72
            kristall = (
                round(mitte[0] + math.cos(winkel) * kristall_radius),
                round(mitte[1] + math.sin(winkel) * kristall_radius)
            )
            pygame.draw.circle(
                flaeche,
                (255, 220, 155),
                kristall,
                max(1, round(2 * faktor))
            )

    elif design_name == "Chocolate Cookie":
        # Drei glänzende Kakaostreifen.
        kakaoglanz = (178, 117, 83)
        for index in range(3):
            y = mitte[1] + round((index - 1) * radius * 0.30)
            pygame.draw.arc(
                flaeche,
                kakaoglanz,
                pygame.Rect(
                    mitte[0] - round(radius * 0.58),
                    y - max(2, round(radius * 0.12)),
                    round(radius * 1.16),
                    max(3, round(radius * 0.24))
                ),
                math.radians(195),
                math.radians(345),
                max(1, round(2 * faktor))
            )

    elif design_name == "Strawberry Cookie":
        # Kleine rote Erdbeerkerne.
        kernfarbe = (157, 48, 66)
        for index in range(8):
            winkel = index * math.tau / 8 + 0.22
            kern_radius = radius * 0.55
            kern_mitte = (
                round(mitte[0] + math.cos(winkel) * kern_radius),
                round(mitte[1] + math.sin(winkel) * kern_radius)
            )
            kern = pygame.Rect(
                kern_mitte[0] - max(1, round(2 * faktor)),
                kern_mitte[1] - max(2, round(3 * faktor)),
                max(2, round(4 * faktor)),
                max(3, round(6 * faktor))
            )
            pygame.draw.ellipse(flaeche, kernfarbe, kern)

    elif design_name == "Rainbow Cookie":
        # Bunter Regenbogenring mit sechs gut sichtbaren Farbstücken.
        regenbogen = (
            (255, 75, 75), (255, 165, 55), (255, 230, 75),
            (75, 205, 105), (75, 155, 255), (180, 95, 235),
        )
        ring_rechteck = pygame.Rect(
            mitte[0] - round(radius * 0.82),
            mitte[1] - round(radius * 0.82),
            round(radius * 1.64),
            round(radius * 1.64)
        )
        for index, farbe in enumerate(regenbogen):
            start = -math.pi / 2 + index * math.tau / len(regenbogen)
            ende = start + math.tau / len(regenbogen) - 0.08
            pygame.draw.arc(
                flaeche,
                farbe,
                ring_rechteck,
                start,
                ende,
                max(2, round(5 * faktor))
            )

    elif design_name == "Ice Cookie":
        # Drei kleine Eiskristalle aus Linien.
        kristall_farbe = (235, 255, 255)
        for index in range(3):
            winkel = index * math.tau / 3 - math.pi / 2
            kristall_mitte = (
                round(mitte[0] + math.cos(winkel) * radius * 0.48),
                round(mitte[1] + math.sin(winkel) * radius * 0.48)
            )
            laenge = max(3, round(7 * faktor))
            pygame.draw.line(
                flaeche,
                kristall_farbe,
                (kristall_mitte[0] - laenge, kristall_mitte[1]),
                (kristall_mitte[0] + laenge, kristall_mitte[1]),
                max(1, round(2 * faktor))
            )
            pygame.draw.line(
                flaeche,
                kristall_farbe,
                (kristall_mitte[0], kristall_mitte[1] - laenge),
                (kristall_mitte[0], kristall_mitte[1] + laenge),
                max(1, round(2 * faktor))
            )

    elif design_name == "Galaxy Cookie":
        # Ein dünner Umlaufring und leuchtende Sterne.
        pygame.draw.ellipse(
            flaeche,
            (218, 165, 255),
            pygame.Rect(
                mitte[0] - round(radius * 0.78),
                mitte[1] - round(radius * 0.34),
                round(radius * 1.56),
                round(radius * 0.68)
            ),
            max(1, round(2 * faktor))
        )

    elif design_name == "Golden Cookie":
        # Kleine goldene Lichtstrahlen um den Rand.
        strahl_farbe = (255, 244, 170)
        for index in range(12):
            winkel = index * math.tau / 12
            innen = radius * 0.83
            aussen = radius * 0.94
            pygame.draw.line(
                flaeche,
                strahl_farbe,
                (round(mitte[0] + math.cos(winkel) * innen),
                 round(mitte[1] + math.sin(winkel) * innen)),
                (round(mitte[0] + math.cos(winkel) * aussen),
                 round(mitte[1] + math.sin(winkel) * aussen)),
                max(1, round(2 * faktor))
            )

    # Die schokostückchen kommen aus den bestehenden cookie daten.
    for x, y, groesse, form, farb_index in schokostuecke:
        stueck_x = round(mitte[0] + (x - cookie_mitte[0]) * faktor)
        stueck_y = round(mitte[1] + (y - cookie_mitte[1]) * faktor)
        stueck_groesse = max(1, round(groesse * faktor))
        stueck_farbe = design["schoko"]
        schatten_farbe = tuple(int(wert * 0.60) for wert in stueck_farbe)
        glaenz_farbe = tuple(
            min(255, int(wert * 1.4 + 18))
            for wert in stueck_farbe
        )

        pygame.draw.circle(
            flaeche,
            schatten_farbe,
            (stueck_x + max(1, round(faktor)),
             stueck_y + max(1, round(2 * faktor))),
            stueck_groesse + max(1, round(faktor))
        )

        if form == "oval":
            chip_rechteck = pygame.Rect(
                stueck_x - stueck_groesse,
                stueck_y - max(1, stueck_groesse // 2),
                max(2, stueck_groesse * 2),
                max(2, stueck_groesse)
            )
            pygame.draw.ellipse(flaeche, stueck_farbe, chip_rechteck)

        elif form == "eckig":
            ecken = [
                (stueck_x - stueck_groesse,
                 stueck_y - stueck_groesse // 2),
                (stueck_x - stueck_groesse // 2,
                 stueck_y - stueck_groesse),
                (stueck_x + stueck_groesse,
                 stueck_y - stueck_groesse // 3),
                (stueck_x + stueck_groesse // 2,
                 stueck_y + stueck_groesse),
                (stueck_x - stueck_groesse,
                 stueck_y + stueck_groesse // 2),
            ]
            pygame.draw.polygon(flaeche, stueck_farbe, ecken)

        else:
            pygame.draw.circle(
                flaeche,
                stueck_farbe,
                (stueck_x, stueck_y),
                stueck_groesse
            )

        pygame.draw.circle(
            flaeche,
            glaenz_farbe,
            (
                stueck_x - max(1, stueck_groesse // 3),
                stueck_y - max(1, stueck_groesse // 3)
            ),
            max(1, stueck_groesse // 3)
        )

    # Sterne werden zuletzt gezeichnet, damit sie sichtbar über den Chips liegen.
    if design_name in ("Galaxy Cookie", "Golden Cookie"):
        stern_farbe = (
            (245, 220, 255)
            if design_name == "Galaxy Cookie"
            else (255, 250, 205)
        )
        stern_anzahl = 6 if design_name == "Galaxy Cookie" else 4
        for index in range(stern_anzahl):
            winkel = index * math.tau / stern_anzahl + zeit * 0.12
            abstand = radius * (0.48 if index % 2 == 0 else 0.66)
            stern_mitte = (
                round(mitte[0] + math.cos(winkel) * abstand),
                round(mitte[1] + math.sin(winkel) * abstand)
            )
            funkeln = (math.sin(zeit * 2.2 + index * 1.7) + 1) / 2
            stern_radius = max(1, round((2 + funkeln * 2) * faktor))
            pygame.draw.line(
                flaeche,
                stern_farbe,
                (stern_mitte[0] - stern_radius, stern_mitte[1]),
                (stern_mitte[0] + stern_radius, stern_mitte[1]),
                max(1, round(faktor))
            )
            pygame.draw.line(
                flaeche,
                stern_farbe,
                (stern_mitte[0], stern_mitte[1] - stern_radius),
                (stern_mitte[0], stern_mitte[1] + stern_radius),
                max(1, round(faktor))
            )

def upgrade_kaufen(upgrade):
    global cookie_anzahl, cookies_pro_klick, cookies_pro_sekunde, auto_cursor_rate

    # Ein Kauf ist nur mÃ¶glich, wenn genug Cookies vorhanden sind.
    if cookie_anzahl < upgrade["preis"]:
        return

    cookie_anzahl -= upgrade["preis"]
    upgrade["level"] += 1

    # Der Cursor gibt beim ersten Kauf 1 CPS,
    # danach erhÃ¶ht jeder weitere Cursor die Produktion um 3 CPS.
    if upgrade["art"] == "cursor":
        if upgrade["level"] == 1:
            cookies_pro_sekunde += 1
            auto_cursor_rate += 1
        else:
            cookies_pro_sekunde += 3
            auto_cursor_rate += 3

    elif upgrade["art"] == "production":
        cookies_pro_sekunde += upgrade["menge"]

    elif upgrade["art"] == "click":
        cookies_pro_klick += upgrade["menge"]

    # Der nächste Preis ist 1,6 mal so hoch aufgerundet.
    upgrade["preis"] = math.ceil(upgrade["preis"] * 1.6)

def cookie_design_kaufen(design_name):
    """Kauft ein noch nicht Freigeschaltetes Design mit Golden Cookies."""
    global goldene_cookies

    design = next(
        (eintrag for eintrag in COOKIE_DESIGNS
         if eintrag["name"] == design_name),
         None
    )

    if design is None or design_name in COOKIE_DESIGNS_OWNED:
        return False

    if goldene_cookies < design["preis"]:
        return False

    goldene_cookies -= design["preis"]
    COOKIE_DESIGNS_OWNED.add(design_name)
    return True

def cookie_design_waehlen(richtung):
    """Wechselt zwischen den bereits gekauften Cookie-Designs."""
    global selected_cookie_design

    verfuegbare_designs = [
        design["name"]
        for design in COOKIE_DESIGNS
        if design["name"] in COOKIE_DESIGNS_OWNED
    ]

    if not verfuegbare_designs:
        return

    if selected_cookie_design not in verfuegbare_designs:
        selected_cookie_design = verfuegbare_designs[0]
        return

    aktuelle_position = verfuegbare_designs.index(selected_cookie_design)
    neue_position = (aktuelle_position + richtung) % len(verfuegbare_designs)
    selected_cookie_design = verfuegbare_designs[neue_position]

def auto_cursor_stufe_berechnen():
    """Berechnet die optische Cursor-Stufe aus dem vorhandenen Upgrade-Level."""
    for upgrade in upgrades:
        if upgrade["name"] == "Auto Cursor":
            return upgrade["level"] // 10 + 1

    return 1


def auto_cursor_farben(stufe):
    """Gibt FÃ¼llfarbe, Randfarbe und Leuchtfarbe der jewiligen Stufe zurÃ¼ck."""
    if stufe == 1:
        return (255, 255, 255), (45, 35, 48), None

    if stufe == 2:
        return (255, 210, 75), (112, 66, 25), None

    if stufe == 3:
        return (220, 185, 255), (100, 55, 155), (180, 105, 255)

    # Ab Stufe 4 wechseln die Farbe zwischen passenden magischen TÃ¶nen.
    weitere_farben = [
        ((100, 235, 205), (30, 105, 90), (70, 220, 190)),
        ((255, 145, 185), (135, 45, 80), (255, 100, 155)),
        ((125, 195, 255), (45, 75, 135), (90, 165, 255)),
        ((255, 175, 95), (135, 70, 30), (255, 140, 60)),
    ]

    return weitere_farben[(stufe - 4) % len(weitere_farben)]



def zeichne_inventar_symbol(upgrade, mitte, dunkelmodus, symbol_groesse):
    """Zeichnet ein einfaches Symbol fÃ¼r ein gekauftes Upgrade."""
    # Die Symbole auf eigener Flaeche zeichnen und anschliessend vergroessern.
    icon_flaeche = pygame.Surface((40, 40), pygame.SRCALPHA)
    cx, cy = 20, 20

    if dunkelmodus:
        hintergrund = (47, 37, 65)
        rand = (142, 111, 190)
        symbolfarbe = (248, 235, 255)
    else:
        hintergrund = (248, 240, 220)
        rand = (188, 116, 50)
        symbolfarbe = (74, 43, 30)

    pygame.draw.circle(icon_flaeche, hintergrund, (cx, cy), 18)
    pygame.draw.circle(icon_flaeche, rand, (cx, cy), 18, 2)

    name = upgrade["name"]

    if name == "Auto Cursor":
        # Das Inventar-Symbol verwndet dieselbe Stufe und Farbe wie der Spiel Cursor
        stufe = auto_cursor_stufe_berechnen()
        cursor_farbe, cursor_rand, cursor_leuchten = auto_cursor_farben(stufe)

        punkte = [
            (cx - 6, cy - 13),
            (cx - 6, cy + 10),
            (cx, cy + 5),
            (cx + 4, cy + 13),
            (cx + 8, cy + 11),
            (cx + 4, cy + 3),
            (cx + 10, cy + 2),
        ]

        if cursor_leuchten is not None:
            pygame.draw.circle(
                icon_flaeche,
                cursor_leuchten,
                (cx, cy),
                16,
                2
            )

        pygame.draw.polygon(icon_flaeche, cursor_farbe, punkte)
        pygame.draw.polygon(icon_flaeche, cursor_rand, punkte, 2)

    elif name == "Cookie Grandma":
        # Kopf, Haare und Schultern
        pygame.draw.circle(icon_flaeche, (112, 66, 42), (cx, cy - 5), 8)
        pygame.draw.circle(icon_flaeche, (244, 205, 157), (cx, cy - 4), 5)
        pygame.draw.ellipse(
            icon_flaeche,
            symbolfarbe,
            pygame.Rect(cx - 10, cy + 3, 20, 12)
        )
        pygame.draw.circle(icon_flaeche, (225, 190, 125), (cx + 9, cy + 7), 4)
        pygame.draw.circle(icon_flaeche, (74, 43, 30), (cx + 8, cy + 6), 1)

    elif name == "Cookie Oven":
        # Kleiner Ofen mit TÃ¼r und Reglern
        pygame.draw.rect(
            icon_flaeche,
            symbolfarbe,
            pygame.Rect(cx - 10, cy - 11, 20, 23),
            border_radius=4
        )
        pygame.draw.rect(
            icon_flaeche,
            rand,
            pygame.Rect(cx - 10, cy - 11, 20, 23),
            width=2,
            border_radius=4
        )
        pygame.draw.circle(icon_flaeche, rand, (cx - 4, cy - 6), 2)
        pygame.draw.circle(icon_flaeche, rand, (cx + 4, cy - 6), 2)
        pygame.draw.rect(
            icon_flaeche,
            hintergrund,
            pygame.Rect(cx - 6, cy - 1, 12, 9),
            border_radius=2
        )
        pygame.draw.rect(
            icon_flaeche,
            rand,
            pygame.Rect(cx - 6, cy - 1, 12, 9),
            width=1,
            border_radius=2
        )

    elif name == "More Cookies per Click":
        # Cookie mit Pluszeichen
        pygame.draw.circle(icon_flaeche, (225, 190, 125), (cx - 3, cy + 3), 9)
        pygame.draw.circle(icon_flaeche, rand, (cx - 3, cy + 3), 9, 2)
        pygame.draw.circle(icon_flaeche, (74, 38, 28), (cx - 6, cy), 2)
        pygame.draw.circle(icon_flaeche, (74, 38, 28), (cx, cy + 6), 2)
        pygame.draw.line(icon_flaeche, symbolfarbe, (cx + 7, cy - 11), (cx + 7, cy - 3), 2)
        pygame.draw.line(icon_flaeche, symbolfarbe, (cx + 3, cy - 7), (cx + 11, cy - 7), 2)

    elif name == "Magic Fingers":
        # HandflÃ¤che und drei Finger
        pygame.draw.ellipse(
            icon_flaeche,
            symbolfarbe,
            pygame.Rect(cx - 8, cy, 16, 11)
        )
        pygame.draw.line(icon_flaeche, symbolfarbe, (cx - 6, cy + 2), (cx - 8, cy - 9), 3)
        pygame.draw.line(icon_flaeche, symbolfarbe, (cx, cy + 1), (cx, cy - 12), 3)
        pygame.draw.line(icon_flaeche, symbolfarbe, (cx + 6, cy + 2), (cx + 8, cy - 8), 3)

    icon_flaeche = pygame.transform.smoothscale(
        icon_flaeche,
        (symbol_groesse, symbol_groesse)
    )
    FENSTER.blit(icon_flaeche, icon_flaeche.get_rect(center=mitte))


def inventar_upgrade_unter_maus(maus_position):
    """Gibt das Upgrade zurÃ¼ck, dessen Symbol gerade unter der Maus liegt."""
    for symbol_bereich, upgrade in inventar_symbol_bereiche:
        if symbol_bereich.collidepoint(maus_position):
            return upgrade

    return None

def spiele_sammel_sound(sound):
    if sound is not None:
        sound.play()


def starte_sammelobjekt(art):
    global aktives_sammelobjekt, sammelobjekt_animationszeit

    position = (
        random.uniform(0.10, 0.90),
        random.uniform(0.22, 0.82),
    )

    if art == "golden":
        name = "Golden Cookie"
        lebenszeit = GOLDEN_COOKIE_LEBENSZEIT
        sound = goldener_cookie_erscheint_sound
    else:
        name = random.choices(
            TREASURE_CHEST_ARTEN,
            weights=TREASURE_CHEST_GEWICHTE,
            k=1
        )[0]
        lebenszeit = TREASURE_CHEST_LEBENSZEIT
        sound = kiste_erscheint_sound

    aktives_sammelobjekt = {
        "art": art,
        "name": name,
        "position": position,
        "restzeit": lebenszeit
    }
    sammelobjekt_animationszeit = 0.0
    spiele_sammel_sound(sound)


def sammelobjekt_rechteck():
    """Liefert den sichtbaren und anklickbaren Bereich des Sammelobjekts."""
    if aktives_sammelobjekt is None:
        return None

    relative_x, relative_y = aktives_sammelobjekt["position"]
    groesse = max(40, min(68, min(BREITE, HOEHE) // 8))

    mitte_x = round(relative_x * BREITE)
    mitte_y = round(
        relative_y * HOEHE
        + math.sin(sammelobjekt_animationszeit * 2.8) * 5
    )

    mitte_x = max(groesse // 2, min(BREITE - groesse // 2, mitte_x))
    mitte_y = max(groesse // 2, min(HOEHE - groesse // 2, mitte_y))

    return pygame.Rect(
        mitte_x - groesse // 2,
        mitte_y - groesse // 2,
        groesse,
        groesse
    )

def inventar_panel_hoehe_berechnen():
    """Das Inventar bleibt kompakt und nimmt weniger als die halbe HÃ¶he ein."""
    return max(1, min(HOEHE - 1, int(HOEHE * 0.25)))


def truhe_oeffnen(truhen_typ, alle=False):
    """Ã–ffnet eine einzelne Truhe oder alle Truhen desselben Typs."""
    global cookie_anzahl, goldene_cookies
    global truhe_belohnung_text, truhe_belohnung_timer

    daten = TRUHEN_OEFFNEN_DATEN.get(truhen_typ)
    if daten is None:
        return False

    vorhanden = inventar_kisten.count(truhen_typ)
    if vorhanden == 0:
        return False

    anzahl = vorhanden if alle else 1
    gesamtkosten = daten["preis"] * anzahl

    # OPEN ALL Ã¶ffnet alles oder gar nichts, wenn Golden Cookies fehlen.
    if goldene_cookies < gesamtkosten:
        return False

    minimum, maximum = daten["belohnung"]
    gesamtbelohnung = sum(
        random.randint(minimum, maximum)
        for _ in range(anzahl)
    )

    goldene_cookies -= gesamtkosten
    for _ in range(anzahl):
        inventar_kisten.remove(truhen_typ)

    cookie_anzahl += gesamtbelohnung
    truhe_belohnung_text = f"+{gesamtbelohnung:,} Cookies!"
    truhe_belohnung_timer = 5.0
    return True


def cookie_klicken(klick_x, klick_y, auto=False):
    """Fuehrt einen Spieler- oder Auto-Cursor-Klick mit denselben Effekten aus."""
    global cookie_anzahl, skalierung_tempo, dreh_tempo

    # Auto Cursor gibt seine feste CPS-Menge; Klick-Upgrades gelten nur fuer den Spieler.
    klick_wert = int(auto_cursor_rate) if auto else cookies_pro_klick
    cookie_anzahl += klick_wert

    if klick_sound is not None:
        klick_sound.play()

    # Gleiche Pop- und Dreh-Animation wie bei einem normalen Mausklick.
    skalierung_tempo += 4.8
    dreh_tempo += random.choice((-1, 1)) * 105

    abstand_x = klick_x - cookie_mitte[0]
    abstand_y = klick_y - cookie_mitte[1]
    laenge = math.hypot(abstand_x, abstand_y)
    if laenge == 0:
        richtung_x, richtung_y = 0, -1
    else:
        richtung_x, richtung_y = abstand_x / laenge, abstand_y / laenge
    basis_winkel = math.atan2(richtung_y, richtung_x)

    # KrÃ¼mel fliegen beim Spieler- und Cursor-Klick nach auÃŸen.
    for _ in range(8):
        winkel = basis_winkel + random.uniform(-1.1, 1.1)
        tempo = random.uniform(90, 230)
        leben = random.uniform(0.35, 0.65)
        kruemel.append({
            "x": float(klick_x),
            "y": float(klick_y),
            "vx": math.cos(winkel) * tempo,
            "vy": math.sin(winkel) * tempo,
            "groesse": random.randint(3, 6),
            "leben": leben,
            "max_leben": leben,
        })

    klick_texte.append({
        "x": float(cookie_mitte[0]),
        "y": float(cookie_mitte[1] - cookie_radius),
        "wert": klick_wert,
        "leben": 0.8,
        "max_leben": 0.8,
    })

# Feste Lichtpunkte: Ihre Positionen bleiben wÃ¤hrend des Spiels gleich.
lichter = []
for _ in range(75):
    lichter.append({
        "x": random.randint(0, BREITE),
        "y": random.randint(0, HOEHE),
        "phase": random.uniform(0, math.tau),
        "tempo": random.uniform(0.25, 0.8),
        "groesse": random.choice((1, 1, 2, 2, 3)),
    })

def spinning_wheel_layout():
    """Berechnet die Positionen passend zur aktuellen Fenstergröße."""
    panel_breite = max(300, min(BREITE - 28, 1080))
    panel_hoehe = max(300, min(HOEHE - 28, 700))
    panel = pygame.Rect(
        (BREITE - panel_breite) // 2,
        (HOEHE - panel_hoehe) // 2,
        panel_breite,
        panel_hoehe
    )
    radius = max(70, min(205, int(panel_hoehe * 0.31), int(panel_breite * 0.23)))
    mitte = (panel.left + int(panel_breite * 0.31), panel.top + int(panel_hoehe * 0.49))
    rechte_x = panel.left + int(panel_breite * 0.59)
    bet_breite = max(110, min(190, panel.right - rechte_x - 28))

    return {
        "panel": panel,
        "radius": radius,
        "mitte": mitte,
        "close": pygame.Rect(panel.right - 48, panel.top + 14, 34, 34),
        "minus": pygame.Rect(rechte_x, panel.top + 162, 44, 42),
        "bet": pygame.Rect(rechte_x + 50, panel.top + 162, bet_breite - 100, 42),
        "plus": pygame.Rect(rechte_x + bet_breite - 44, panel.top + 162, 44, 42),
        "spin": pygame.Rect(rechte_x, panel.bottom - 126, bet_breite, 56),
        "rechte_x": rechte_x,
    }


def spiele_wheel_sound(sound):
    if sound is not None and sound_lautstaerke > 0:
        sound.play()


def spinning_wheel_loop_sound_starten():
    global wheel_spin_channel
    if wheel_spin_loop_sound is not None and wheel_spin_channel is None:
        wheel_spin_channel = wheel_spin_loop_sound.play(loops=-1)


def spinning_wheel_loop_sound_stoppen():
    global wheel_spin_channel
    if wheel_spin_channel is not None:
        wheel_spin_channel.stop()
        wheel_spin_channel = None


def spinning_wheel_starten():
    """Zieht den Einsatz ab und legt das Ergebnis vor dem Drehen fest."""
    global goldene_cookies, wheel_bet, wheel_current_bet, wheel_spinning
    global wheel_result_index, wheel_result, wheel_start_angle, wheel_final_angle
    global wheel_spin_elapsed

    if wheel_spinning or wheel_result_timer > 0 or goldene_cookies < 1:
        return

    wheel_bet = max(1, min(wheel_bet, goldene_cookies))
    wheel_current_bet = wheel_bet
    goldene_cookies -= wheel_current_bet

    # Das Ergebnis richtet sich nach 30/70; die vier sichtbaren Felder sind 50/50.
    if random.random() < 0.30:
        wheel_result = "win"
        wheel_result_index = random.choice((0, 1))
    else:
        wheel_result = "lose"
        wheel_result_index = random.choice((2, 3))

    # Auf zwei Gewinn- und zwei Verlustfelder verteilen, passend zum Ergebnis.
    zielwinkel = (-(wheel_result_index + 0.5) * math.tau / 4) % math.tau
    wheel_start_angle = wheel_angle
    wheel_final_angle = (
        wheel_start_angle + 6 * math.tau
        + ((zielwinkel - wheel_start_angle) % math.tau)
    )
    wheel_spin_elapsed = 0.0
    wheel_spinning = True
    spiele_wheel_sound(wheel_start_sound)
    spinning_wheel_loop_sound_starten()


def spinning_wheel_beenden():
    """Rechnet das Ergebnis nach der Drehung genau einmal ab."""
    global goldene_cookies, wheel_spinning, wheel_result_timer

    if not wheel_spinning:
        return

    wheel_spinning = False
    spinning_wheel_loop_sound_stoppen()
    if wheel_result == "win":
        goldene_cookies += wheel_current_bet * 2
        spiele_wheel_sound(wheel_win_sound)
    else:
        spiele_wheel_sound(wheel_lose_sound)

    wheel_result_timer = 4.0
    spiele_wheel_sound(wheel_stop_sound)


def zeichne_spinning_wheel():
    """Zeichnet Rad, Einsatz, mögliche Ergebnisse und aktuelle Meldung."""
    layout = spinning_wheel_layout()
    panel = layout["panel"]
    mitte = layout["mitte"]
    radius = layout["radius"]
    rechte_x = layout["rechte_x"]

    abdunklung = pygame.Surface((BREITE, HOEHE), pygame.SRCALPHA)
    abdunklung.fill((18, 9, 35, 238))
    FENSTER.blit(abdunklung, (0, 0))

    sterne = pygame.Surface((BREITE, HOEHE), pygame.SRCALPHA)
    for index in range(65):
        x = int(((index * 127 + 37) % 997) / 997 * BREITE)
        y = int(((index * 191 + 83) % 991) / 991 * HOEHE)
        alpha = int(45 + 100 * (0.5 + 0.5 * math.sin(wheel_zeit * 1.4 + index)))
        pygame.draw.circle(sterne, (190, 145, 255, alpha), (x, y), 2)
    FENSTER.blit(sterne, (0, 0))

    pygame.draw.rect(FENSTER, (31, 19, 54), panel, border_radius=24)
    pygame.draw.rect(FENSTER, (180, 126, 43), panel, width=5, border_radius=24)
    pygame.draw.rect(FENSTER, (245, 206, 112), panel.inflate(-14, -14), width=2, border_radius=19)

    # Kleine goldene Ornamente an den vier Ecken des Rahmens.
    for ecke_x, ecke_y, richtung_x, richtung_y in (
        (panel.left + 22, panel.top + 22, 1, 1),
        (panel.right - 22, panel.top + 22, -1, 1),
        (panel.left + 22, panel.bottom - 22, 1, -1),
        (panel.right - 22, panel.bottom - 22, -1, -1),
    ):
        pygame.draw.polygon(FENSTER, (255, 218, 130), [
            (ecke_x, ecke_y - 7),
            (ecke_x + richtung_x * 7, ecke_y),
            (ecke_x, ecke_y + 7),
            (ecke_x - richtung_x * 7, ecke_y),
        ])
        pygame.draw.line(
            FENSTER, (219, 174, 76),
            (ecke_x, ecke_y),
            (ecke_x + richtung_x * 18, ecke_y + richtung_y * 18),
            2
        )

    titel = schrift.render("SPINNING WHEEL", True, (255, 224, 145))
    FENSTER.blit(titel, titel.get_rect(center=(panel.centerx, panel.top + 46)))

    pygame.draw.circle(FENSTER, (58, 34, 22), mitte, radius + 21)
    pygame.draw.circle(FENSTER, (255, 208, 89), mitte, radius + 16, 8)
    pygame.draw.circle(FENSTER, (255, 239, 170), mitte, radius + 7, 2)

    # Vier gleich große Segmente: zwei Gewinn- und zwei Verlustfelder (optisch 50/50).
    beschriftungs_schrift = pygame.font.SysFont(
        "arial", max(15, round(radius * 0.10)), bold=True
    )
    for index in range(4):
        start = -math.pi / 2 + wheel_angle + index * math.tau / 4
        ende = start + math.tau / 4
        punkte = [mitte]
        for schritt in range(13):
            winkel = start + (ende - start) * schritt / 12
            punkte.append((
                round(mitte[0] + math.cos(winkel) * radius),
                round(mitte[1] + math.sin(winkel) * radius)
            ))
        if index < 2:
            farbe = (65, 157, 91) if index == 0 else (78, 174, 105)
            label = "WIN"
            label_farbe = (239, 255, 220)
        else:
            farbe = (105, 48, 105) if index == 2 else (126, 58, 120)
            label = "LOSE"
            label_farbe = (255, 232, 250)
        pygame.draw.polygon(FENSTER, farbe, punkte)
        pygame.draw.polygon(FENSTER, (255, 218, 130), punkte, width=2)

        label_winkel = start + math.tau / 8
        label_position = (
            round(mitte[0] + math.cos(label_winkel) * radius * 0.61),
            round(mitte[1] + math.sin(label_winkel) * radius * 0.61)
        )
        label_bild = beschriftungs_schrift.render(label, True, label_farbe)
        FENSTER.blit(label_bild, label_bild.get_rect(center=label_position))

    pygame.draw.circle(FENSTER, (255, 232, 153), mitte, radius, width=2)

    for index in range(20):
        winkel = index * math.tau / 20
        licht = (
            round(mitte[0] + math.cos(winkel) * (radius + 10)),
            round(mitte[1] + math.sin(winkel) * (radius + 10))
        )
        pygame.draw.circle(
            FENSTER, (255, 226, 130), licht,
            3 + round((0.5 + 0.5 * math.sin(wheel_zeit * 2 + index)) * 2)
        )

    pygame.draw.polygon(FENSTER, (255, 215, 92), [
        (mitte[0] - 20, mitte[1] - radius - 20),
        (mitte[0] + 20, mitte[1] - radius - 20),
        (mitte[0], mitte[1] - radius + 12),
    ])

    pygame.draw.circle(FENSTER, (75, 37, 21), mitte, 47)
    pygame.draw.circle(FENSTER, (234, 170, 57), mitte, 41)
    pygame.draw.circle(FENSTER, (255, 220, 115), (mitte[0] - 7, mitte[1] - 8), 30)
    for dx, dy, groesse in ((-14, -7, 5), (7, -15, 4), (13, 8, 5), (-7, 14, 4)):
        pygame.draw.circle(FENSTER, (92, 44, 28), (mitte[0] + dx, mitte[1] + dy), groesse)
    pygame.draw.arc(
        FENSTER,
        (255, 241, 176),
        pygame.Rect(mitte[0] - 27, mitte[1] - 29, 44, 40),
        math.radians(205),
        math.radians(310),
        2
    )

    titel_klein = pygame.font.SysFont("arial", 20, bold=True)
    text_klein = pygame.font.SysFont("arial", 18)
    FENSTER.blit(titel_klein.render("YOUR BET", True, (255, 239, 198)), (rechte_x, panel.top + 112))

    for feld, label in ((layout["minus"], "-"), (layout["plus"], "+")):
        pygame.draw.rect(FENSTER, (72, 49, 91), feld, border_radius=9)
        pygame.draw.rect(FENSTER, (219, 174, 76), feld, width=2, border_radius=9)
        label_bild = schrift.render(label, True, (255, 229, 154))
        FENSTER.blit(label_bild, label_bild.get_rect(center=feld.center))

    bet_bild = text_klein.render(f"{wheel_bet} GC", True, (255, 255, 235))
    FENSTER.blit(bet_bild, bet_bild.get_rect(center=layout["bet"].center))

    FENSTER.blit(titel_klein.render("GOOD LUCK!", True, (255, 224, 145)), (rechte_x, panel.top + 235))

    if wheel_spinning or wheel_result_timer > 0 or goldene_cookies < 1:
        for feld in (layout["minus"], layout["plus"]):
            pygame.draw.rect(FENSTER, (55, 48, 64), feld, border_radius=9)

    if wheel_spinning:
        button_text, button_farbe = "SKIP", (113, 73, 142)
    elif wheel_result_timer > 0:
        button_text, button_farbe = "WAIT", (75, 66, 82)
    else:
        button_text, button_farbe = "SPIN", (173, 119, 35)

    button_rect = layout["spin"]
    button_hover = button_rect.collidepoint(pygame.mouse.get_pos())
    if button_hover and button_text == "SPIN":
        button_farbe = (205, 151, 51)
    pygame.draw.rect(FENSTER, (31, 19, 30), button_rect.move(0, 4), border_radius=14)
    pygame.draw.rect(FENSTER, button_farbe, button_rect, border_radius=14)
    pygame.draw.rect(
        FENSTER,
        (255, 244, 180) if button_hover else (255, 222, 127),
        button_rect,
        width=3,
        border_radius=14
    )
    button_bild = schrift.render(button_text, True, (255, 246, 210))
    FENSTER.blit(button_bild, button_bild.get_rect(center=layout["spin"].center))

    balance = text_klein.render(f"Golden Cookies: {goldene_cookies} GC", True, (255, 224, 145))
    FENSTER.blit(balance, balance.get_rect(center=(panel.centerx, panel.bottom - 38)))

    if wheel_result_timer > 0 and not wheel_spinning:
        if wheel_result == "win":
            result, result_farbe = f"YOU WON! +{wheel_current_bet * 2} GC", (255, 226, 115)
        else:
            result, result_farbe = f"YOU LOST! -{wheel_current_bet} GC", (255, 150, 170)
        result_bild = text_klein.render(result, True, result_farbe)
        FENSTER.blit(result_bild, result_bild.get_rect(center=(mitte[0], mitte[1] + radius + 44)))

    close = layout["close"]
    pygame.draw.rect(FENSTER, (68, 43, 87), close, border_radius=8)
    pygame.draw.rect(FENSTER, (237, 190, 89), close, width=2, border_radius=8)
    x_bild = kleine_schrift.render("X", True, (255, 236, 190))
    FENSTER.blit(x_bild, x_bild.get_rect(center=close.center))

def fenstermodus_wechseln():
    global FENSTER, BREITE, HOEHE, ist_vollbild
    global cookie_mitte, shop_breite, shop_x, shop_panel, shop_schliessen, shop_button
    global inventar_knopf
    global menue_oben, weiter_feld, einstellungen_feld, verlassen_feld, zurueck_feld
    global spinning_wheel_menu_feld
    global purple_feld, vanilla_feld, lautstaerke_linie, lautstaerke_feld
    global cookie_design_zurueck_feld, cookie_design_weiter_feld
    global inventar_panel_y

    alte_breite, alte_hoehe = BREITE, HOEHE

    if ist_vollbild:
        bildschirm = pygame.display.Info()
        fenster_breite = min(1280, bildschirm.current_w - 80)
        fenster_hoehe = min(800, bildschirm.current_h - 100)
        FENSTER = pygame.display.set_mode((fenster_breite, fenster_hoehe))
        ist_vollbild = False
    else:
        FENSTER = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        ist_vollbild = True

    BREITE, HOEHE = FENSTER.get_size()
    cookie_mitte = (BREITE // 2, HOEHE // 2 + 35)

    # Schokostuecke behalten ihre Position relativ zur Cookie-Mitte.
    for index, stueck in enumerate(schokostuecke):
        stueck_x, stueck_y, groesse, form, farbe = stueck
        stueck_x = cookie_mitte[0] + stueck_x - alte_breite // 2
        stueck_y = cookie_mitte[1] + stueck_y - (alte_hoehe // 2 + 35)
        schokostuecke[index] = (
            stueck_x, stueck_y, groesse, form, farbe
        )

    # Lichtpunkte auf die neue Fenstergroesse umrechnen.
    for licht in lichter:
        licht["x"] = int(licht["x"] * BREITE / alte_breite)
        licht["y"] = int(licht["y"] * HOEHE / alte_hoehe)

    shop_breite = min(360, BREITE)
    shop_x = float(BREITE - shop_breite if shop_offen else BREITE)
    shop_panel = pygame.Rect(round(shop_x), 100, shop_breite, HOEHE - 130)
    shop_schliessen = pygame.Rect(shop_panel.right - 48, 112, 34, 34)
    shop_button = pygame.Rect(BREITE - 125, 18, 105, 46)
    inventar_knopf = pygame.Rect(18, HOEHE - 58, 142, 38)
    inventar_panel_y = float(
        HOEHE - inventar_panel_hoehe_berechnen()
        if inventar_offen else HOEHE
    )

    menue_oben = HOEHE // 2 - 190
    weiter_feld = pygame.Rect(BREITE // 2 - 130, menue_oben + 70, 260, 52)
    einstellungen_feld = pygame.Rect(BREITE // 2 - 130, menue_oben + 130, 260, 52)
    spinning_wheel_menu_feld = pygame.Rect(
        BREITE // 2 - 130, menue_oben + 190, 260, 52
    )
    verlassen_feld = pygame.Rect(BREITE // 2 - 130, menue_oben + 250, 260, 52)
    zurueck_feld = pygame.Rect(
        BREITE // 2 - 130,
        menue_oben + 340,
        260,
        45
    )
    cookie_design_zurueck_feld = pygame.Rect(
        BREITE // 2 - 104,
        menue_oben + 285,
        42,
        34
    )
    cookie_design_weiter_feld = pygame.Rect(
        BREITE // 2 + 62,
        menue_oben + 285,
        42,
        34
    )
    purple_feld = pygame.Rect(BREITE // 2 - 150, menue_oben + 78, 300, 50)
    vanilla_feld = pygame.Rect(BREITE // 2 - 150, menue_oben + 135, 300, 50)
    lautstaerke_linie = pygame.Rect(BREITE // 2 - 120, menue_oben + 225, 240, 8)
    lautstaerke_feld = pygame.Rect(BREITE // 2 - 140, menue_oben + 210, 280, 38)


laeuft = True
while laeuft:
    # dt macht alle Bewegungen unabhaengig von der Bildrate.
    dt = min(clock.tick(60) / 1000.0, 0.05)

    for ereignis in pygame.event.get():
        if ereignis.type == pygame.QUIT:
            laeuft = False

        elif (
            ereignis.type == pygame.MOUSEWHEEL
            and spiel_status == "game"
            and inventar_offen
            and inventar_seite == "chests"
            and inventar_truhen_liste_feld.collidepoint(pygame.mouse.get_pos())
        ):
            inventar_truhen_scroll -= ereignis.y * 36
            inventar_truhen_scroll = max(
                0,
                min(inventar_truhen_scroll, inventar_truhen_scroll_max)
            )
        
        elif (
            ereignis.type == pygame.MOUSEWHEEL
            and spiel_status == "settings"
            and cookie_design_grid_rect.collidepoint(pygame.mouse.get_pos())
        ):
            cookie_design_scroll -= ereignis.y * 36
            cookie_design_scroll = max(
                0,
                min(cookie_design_scroll, cookie_design_scroll_max)
            )
            
        elif ereignis.type == pygame.KEYDOWN and ereignis.key == pygame.K_F11:
            fenstermodus_wechseln()

        elif ereignis.type == pygame.KEYDOWN and ereignis.key == pygame.K_ESCAPE:
            if spiel_status == "game":
                spiel_status = "menu"
            elif spiel_status == "menu":
                spiel_status = "game"
            elif spiel_status == "wheel":
                spinning_wheel_loop_sound_stoppen()
                spiel_status = "menu"
            else:
                spiel_status = "menu"

        elif ereignis.type == pygame.MOUSEBUTTONDOWN and spiel_status != "game":
            maus_position = ereignis.pos

            if spiel_status == "menu":
                if weiter_feld.collidepoint(maus_position):
                    spiel_status = "game"

                elif einstellungen_feld.collidepoint(maus_position):
                    spiel_status = "settings"

                elif spinning_wheel_menu_feld.collidepoint(maus_position):
                    spiel_status = "wheel"
                    if wheel_spinning:
                        spinning_wheel_loop_sound_starten()

                elif verlassen_feld.collidepoint(maus_position):
                    laeuft = False

            elif spiel_status == "settings":
                if lautstaerke_feld.collidepoint(maus_position):
                    lautstaerke_ziehen = True
                    sound_lautstaerke = max(
                        0.0,
                        min(1.0, (maus_position[0] - lautstaerke_linie.left) / lautstaerke_linie.width)
                    )
                    if klick_sound is not None:
                        klick_sound.set_volume(sound_lautstaerke)

                elif purple_feld.collidepoint(maus_position):
                    hintergrund_modus = "purple"
                elif vanilla_feld.collidepoint(maus_position):
                    hintergrund_modus = "vanilla"
                elif cookie_design_grid_rect.collidepoint(maus_position):
                    for select_feld, design_name in cookie_design_select_felder:
                        if select_feld.collidepoint(maus_position):
                            if design_name in COOKIE_DESIGNS_OWNED:
                                selected_cookie_design = design_name
                            break

                elif zurueck_feld.collidepoint(maus_position):
                    spiel_status = "menu"

            elif spiel_status == "wheel":
                layout = spinning_wheel_layout()

                if layout["close"].collidepoint(maus_position):
                    # Zurück zum Pausenmenü; eine Drehung pausiert bis zur Rückkehr.
                    spinning_wheel_loop_sound_stoppen()
                    if klick_sound is not None:
                        klick_sound.play()
                    spiel_status = "menu"
                elif wheel_spinning and layout["spin"].collidepoint(maus_position):
                    # Das Ergebnis ist vorher festgelegt und wird durch SKIP nicht neu gewürfelt.
                    if klick_sound is not None:
                        klick_sound.play()
                    wheel_angle = wheel_final_angle
                    spinning_wheel_beenden()
                elif not wheel_spinning and wheel_result_timer <= 0:
                    if layout["minus"].collidepoint(maus_position):
                        wheel_bet = max(1, wheel_bet - 1)
                        if klick_sound is not None:
                            klick_sound.play()
                    elif layout["plus"].collidepoint(maus_position):
                        wheel_bet = min(goldene_cookies, wheel_bet + 1)
                        if klick_sound is not None:
                            klick_sound.play()
                    elif layout["spin"].collidepoint(maus_position):
                        spinning_wheel_starten()

        elif ereignis.type == pygame.MOUSEMOTION and lautstaerke_ziehen:
            maus_x = ereignis.pos[0]
            sound_lautstaerke = max(
                0.0,
                min(1.0, (maus_x - lautstaerke_linie.left) / lautstaerke_linie.width)
            )
            if klick_sound is not None:
                klick_sound.set_volume(sound_lautstaerke)

            sammelsounds_lautstaerke_setzen()

        elif ereignis.type == pygame.MOUSEBUTTONUP and ereignis.button == 1:
            lautstaerke_ziehen = False

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and spiel_status == "game"
            and aktives_sammelobjekt is not None
            and sammelobjekt_rechteck().collidepoint(ereignis.pos)
        ):
            if aktives_sammelobjekt["art"] == "golden":
                goldene_cookies += 1
                spiele_sammel_sound(goldener_cookie_einsammel_sound)
                goldener_cookie_verpasst_timer = 0.0
            else:
                inventar_kisten.append(aktives_sammelobjekt["name"])
                spiele_sammel_sound(kiste_einsammel_sound)

            aktives_sammelobjekt = None
            sammelobjekt_animationszeit = 0.0

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and spiel_status == "game"
            and inventar_offen
            and inventar_chests_feld.collidepoint(ereignis.pos)
        ):
            inventar_seite = "chests"

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and spiel_status == "game"
            and inventar_offen
            and inventar_upgrades_feld.collidepoint(ereignis.pos)
        ):
            inventar_seite = "upgrades"

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and spiel_status == "game"
            and inventar_offen
            and inventar_seite == "chests"
            and (
                any(feld.collidepoint(ereignis.pos) for feld, _ in truhe_alle_felder)
                or any(feld.collidepoint(ereignis.pos) for feld, _ in truhe_open_felder)
            )
        ):
            verarbeitet = False

            # OPEN ALL zuerst prÃ¼fen.
            for feld, truhen_typ in truhe_alle_felder:
                if feld.collidepoint(ereignis.pos):
                    truhe_oeffnen(truhen_typ, alle=True)
                    verarbeitet = True
                    break

            if not verarbeitet:
                for feld, truhen_typ in truhe_open_felder:
                    if feld.collidepoint(ereignis.pos):
                        truhe_oeffnen(truhen_typ)
                        break

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and spiel_status == "game"
            and shop_button.collidepoint(ereignis.pos)
        ):
            shop_offen = not shop_offen

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and spiel_status == "game"
            and inventar_knopf.collidepoint(ereignis.pos)
        ):
            inventar_offen = not inventar_offen
            if inventar_offen:
                inventar_seite = "upgrades"

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and shop_offen
            and shop_schliessen.collidepoint(ereignis.pos)
        ):
            shop_offen = False

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and shop_offen
            and shop_upgrades_tab.collidepoint(ereignis.pos)
        ):
            shop_seite = "upgrades"

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and shop_offen
            and shop_cookie_tab.collidepoint(ereignis.pos)
        ):
            shop_seite = "cookie"

        elif (
            ereignis.type == pygame.MOUSEBUTTONDOWN
            and ereignis.button == 1
            and shop_offen
            and shop_panel.collidepoint(ereignis.pos)
        ):
            if shop_seite == "upgrades":
                for kauf_feld, upgrade in upgrade_kauf_felder:
                    if kauf_feld.collidepoint(ereignis.pos):
                        upgrade_kaufen(upgrade)
                        break
            else:
                for kauf_feld, design_name in cookie_shop_kauf_felder:
                    if kauf_feld.collidepoint(ereignis.pos):
                        cookie_design_kaufen(design_name)
                        break

        elif ereignis.type == pygame.MOUSEBUTTONDOWN and ereignis.button == 1:
            maus_x, maus_y = ereignis.pos
            abstand_x = maus_x - cookie_mitte[0]
            abstand_y = maus_y - cookie_mitte[1]

            # Der Klickbereich folgt dem sichtbaren Hover-Cookie.
            if abstand_x**2 + abstand_y**2 <= (cookie_radius * hover_skalierung)**2:
                cookie_klicken(maus_x, maus_y)

    # Die normale Spielzeit stoppt im Menü; das Rad bekommt einen eigenen Timer.
    frame_dt = dt
    if spiel_status != "game":
        dt = 0

    if spiel_status == "wheel":
        wheel_zeit += frame_dt
        if wheel_spinning:
            wheel_spin_elapsed = min(
                wheel_spin_duration,
                wheel_spin_elapsed + frame_dt
            )
            fortschritt = wheel_spin_elapsed / wheel_spin_duration
            weich_gebremst = 1 - (1 - fortschritt) ** 4
            wheel_angle = (
                wheel_start_angle
                + (wheel_final_angle - wheel_start_angle) * weich_gebremst
            )
            if fortschritt >= 1:
                wheel_angle = wheel_final_angle
                spinning_wheel_beenden()
        elif wheel_result_timer > 0:
            wheel_result_timer = max(0.0, wheel_result_timer - frame_dt)
            if wheel_result_timer == 0:
                wheel_bet = min(max(1, wheel_bet), goldene_cookies) if goldene_cookies > 0 else 0

    if truhe_belohnung_timer > 0:
        truhe_belohnung_timer = max(0.0, truhe_belohnung_timer - dt)

    # Spielzeit, sammelobjekte und timer laufen nur auÃŸerhalb des pausenmenÃ¼s.
    spiel_zeit += dt
    objekt_war_aktiv = aktives_sammelobjekt is not None

    if goldener_cookie_verpasst_timer > 0:
        goldener_cookie_verpasst_timer = max(
            0.0,
            goldener_cookie_verpasst_timer - dt
        )

    if aktives_sammelobjekt is not None:
        aktives_sammelobjekt["restzeit"] -= dt
        sammelobjekt_animationszeit += dt

        if aktives_sammelobjekt["restzeit"] <= 0:
            if aktives_sammelobjekt["art"] == "golden":
                goldener_cookie_verpasst_timer = 3.0

            aktives_sammelobjekt = None
            sammelobjekt_animationszeit = 0.0

    goldener_cookie_timer += dt
    treasure_chest_timer += dt

    goldener_cookie_erfolg = False
    treasure_chest_erfolg = False

    while goldener_cookie_timer >= GOLDEN_COOKIE_INTERVALL:
        goldener_cookie_timer -= GOLDEN_COOKIE_INTERVALL
        if random.random() < GOLDEN_COOKIE_CHANCE:
            goldener_cookie_erfolg = True

    while treasure_chest_timer >= TREASURE_CHEST_INTERVALL:
        treasure_chest_timer -= TREASURE_CHEST_INTERVALL
        if random.random() < TREASURE_CHEST_CHANCE:
            treasure_chest_erfolg = True

    # Bei gleichzeitig erfolgreichen Versuchen hat der Golden Cookie Vorrang.
    # Der Truhenversuch wird dabei verworfen und nicht nachgeholt.
    if not objekt_war_aktiv and aktives_sammelobjekt is None:
        if goldener_cookie_erfolg:
            starte_sammelobjekt("golden")
        elif treasure_chest_erfolg:
            starte_sammelobjekt("chest")

    # Das Inventar gleitet weich nach oben oder wieder nach unten.
    inventar_panel_hoehe = inventar_panel_hoehe_berechnen()
    inventar_ziel_y = (
        HOEHE - inventar_panel_hoehe if inventar_offen else HOEHE
    )

    inventar_panel_y += (
        inventar_ziel_y - inventar_panel_y
    ) * (1 - math.exp(-6 * dt))

    if abs(inventar_ziel_y - inventar_panel_y) < 0.5:
        inventar_panel_y = float(inventar_ziel_y)

    # Der vorhandene Button faehrt mit dem Panel nach oben und bleibt darueber sichtbar.
    inventar_knopf.y = round(inventar_panel_y) - inventar_knopf.height - 10

    # Cookies werden im Spiel produziert. Der offene Shop pausiert das nicht.
    if spiel_status == "game":
        # Cursor machen sichtbare Klicks. Grandma und Ofen produzieren passiv.
        passive_produktion = max(0.0, cookies_pro_sekunde - auto_cursor_rate)
        cookie_anzahl += passive_produktion * dt

        if auto_cursor_rate > 0:
            auto_cursor_timer += dt
            # Ein sichtbarer Auto Cursor klickt einmal pro Sekunde.
            while auto_cursor_timer >= 1.0:
                auto_cursor_timer -= 1.0
                cookie_klicken(cookie_mitte[0], cookie_mitte[1], auto=True)

    # Der Shop gleitet auch im laufenden Spiel von rechts hinein und wieder hinaus.
    shop_ziel_x = BREITE - shop_breite if shop_offen else BREITE
    shop_x += (shop_ziel_x - shop_x) * (1 - math.exp(-10 * dt))

    if abs(shop_ziel_x - shop_x) < 0.5:
        shop_x = shop_ziel_x

    shop_panel = pygame.Rect(
        round(shop_x),
        100,
        shop_breite,
        HOEHE - 130
    )
    shop_schliessen = pygame.Rect(
        shop_panel.right - 48,
        shop_panel.top + 12,
        34,
        34
    )

    # Hover-Groesse weich an den Mauszustand anpassen.
    maus_x, maus_y = pygame.mouse.get_pos()
    maus_abstand = math.hypot(maus_x - cookie_mitte[0], maus_y - cookie_mitte[1])
    ueber_cookie = maus_abstand <= cookie_radius * hover_skalierung
    hover_ziel = 1.045 if ueber_cookie else 1.0
    hover_skalierung += (hover_ziel - hover_skalierung) * (1 - math.exp(-12 * dt))

    # GedÃ¤mpfte Feder fuer den Pop-Effekt.
    skalierung_tempo += ((1.0 - cookie_skalierung) * 115 - 16 * skalierung_tempo) * dt
    cookie_skalierung += skalierung_tempo * dt
    cookie_skalierung = max(0.92, min(1.28, cookie_skalierung))

    # Drehung sanft ausklingen lassen.
    dreh_winkel += dreh_tempo * dt
    dreh_tempo *= math.exp(-8 * dt)

    # KrÃ¼mel bewegen und nach Ablauf ihrer Lebenszeit entfernen.
    for teilchen in kruemel:
        teilchen["x"] += teilchen["vx"] * dt
        teilchen["y"] += teilchen["vy"] * dt
        teilchen["vx"] *= math.exp(-2 * dt)
        teilchen["vy"] *= math.exp(-2 * dt)
        teilchen["leben"] -= dt
    kruemel = [teilchen for teilchen in kruemel if teilchen["leben"] > 0]

    # +1 steigt auf und blendet aus.
    for text in klick_texte:
        text["y"] -= 45 * dt
        text["leben"] -= dt
    klick_texte = [text for text in klick_texte if text["leben"] > 0]

    zeit = spiel_zeit

    if hintergrund_modus == "purple":
        FENSTER.fill((13, 10, 25))

        # Sterne leuchten einzeln und langsam auf und ab.
        for licht in lichter:
            leuchten = (math.sin(zeit * licht["tempo"] + licht ["phase"]) + 1) / 2
            helligkeit = int(35 + leuchten * 115)
            sternfarbe = (helligkeit, int(helligkeit * 0.8), min(255, helligkeit + 35))
            pygame.draw.circle(
                FENSTER,
                sternfarbe,
                (licht["x"], licht["y"]),
                licht["groesse"]
            )
    else:
        FENSTER.fill((250, 242, 222))

        # Sanfte, warme Lichtpunkte fuer den Vanille Hintergrund.
        for licht in lichter:
            leuchten = (math.sin(zeit * licht["tempo"] + licht["phase"]) + 1) / 2
            helligkeit = int(8 + leuchten * 22)
            lichtfarbe = (
                250,
                min(255, 242 + helligkeit // 2),
                min(255, 220 + helligkeit)
            )
            pygame.draw.circle(
                FENSTER,
                lichtfarbe,
                (licht["x"], licht["y"]),
                licht["groesse"] + 2
            )

    # Inventar mit Upgrade-Symbolen und TruhenÃ¼bersicht.
    inventar_panel_hoehe = inventar_panel_hoehe_berechnen()
    inventar_panel = pygame.Rect(
        0,
        round(inventar_panel_y),
        BREITE // 2,
        inventar_panel_hoehe
    )
    inventar_panel_bottom = inventar_panel.bottom

    if hintergrund_modus == "purple":
        inventar_panel_farbe = (25, 20, 39)
        inventar_panel_rand = (142, 111, 190)
        inventar_panel_text = (248, 235, 255)
        karten_farbe = (39, 31, 56)
        karten_rand = (91, 72, 120)
        button_farbe = (47, 37, 65)
    else:
        inventar_panel_farbe = (255, 250, 240)
        inventar_panel_rand = (188, 116, 50)
        inventar_panel_text = TEXTFARBE
        karten_farbe = (248, 240, 220)
        karten_rand = (225, 211, 187)
        button_farbe = (238, 216, 180)

    inventar_symbol_bereiche = []
    truhe_open_felder = []
    truhe_alle_felder = []

    if inventar_panel_y < HOEHE:
        pygame.draw.rect(FENSTER, inventar_panel_farbe, inventar_panel)
        pygame.draw.rect(
            FENSTER,
            inventar_panel_rand,
            inventar_panel,
            width=3,
            border_radius=10
        )

        inventar_titel = inventar_kopf_schrift.render(
            "Inventory",
            True,
            inventar_panel_text
        )
        FENSTER.blit(
            inventar_titel,
            (18, inventar_panel.top + 4)
        )

        golden_text = inventar_detail_schrift.render(
            f"Golden Cookies (GC): {goldene_cookies}",
            True,
            inventar_panel_text
        )
        FENSTER.blit(
            golden_text,
            (inventar_panel.right - golden_text.get_width() - 12,
             inventar_panel.top + 7)
        )

        inventar_chests_feld = pygame.Rect(
            inventar_panel.right - 100,
            inventar_panel.top + 28,
            88,
            26
        )
        inventar_upgrades_feld = pygame.Rect(
            inventar_panel.left + 12,
            inventar_panel.top + 28,
            92,
            26
        )

        if inventar_seite == "upgrades":
            pygame.draw.rect(
                FENSTER,
                button_farbe,
                inventar_chests_feld,
                border_radius=6
            )
            chests_tab_text = inventar_detail_schrift.render(
                "CHESTS",
                True,
                inventar_panel_text
            )
            FENSTER.blit(
                chests_tab_text,
                chests_tab_text.get_rect(center=inventar_chests_feld.center)
            )
        else:
            pygame.draw.rect(
                FENSTER,
                button_farbe,
                inventar_upgrades_feld,
                border_radius=6
            )
            upgrades_tab_text = inventar_detail_schrift.render(
                "UPGRADES",
                True,
                inventar_panel_text
            )
            FENSTER.blit(
                upgrades_tab_text,
                upgrades_tab_text.get_rect(center=inventar_upgrades_feld.center)
            )

        if inventar_seite == "upgrades":
            # Die Upgrade-Seite zeigt nur bereits gekaufte Symbole.
            gekaufte_upgrades = [
                upgrade for upgrade in upgrades
                if upgrade["level"] > 0
            ]

            for index, upgrade in enumerate(gekaufte_upgrades):
                abstand = inventar_panel.width // (len(gekaufte_upgrades) + 1)
                symbol_groesse = min(48, max(32, abstand - 6))
                symbol_x = inventar_panel.left + abstand * (index + 1)
                symbol_y = inventar_panel.top + 78
                symbol_mitte = (symbol_x, symbol_y)

                symbol_bereich = pygame.Rect(
                    symbol_x - symbol_groesse // 2,
                    symbol_y - symbol_groesse // 2,
                    symbol_groesse,
                    symbol_groesse
                )
                inventar_symbol_bereiche.append((symbol_bereich, upgrade))

                zeichne_inventar_symbol(
                    upgrade,
                    symbol_mitte,
                    hintergrund_modus == "purple",
                    symbol_groesse
                )

        else:
            # Die Chest-Seite listet nur Truhen, die im Inventar liegen.
            vorhandene_truhen = [
                truhen_typ for truhen_typ in TREASURE_CHEST_ARTEN
                if inventar_kisten.count(truhen_typ) > 0
            ]

            if not vorhandene_truhen:
                keine_truhen_text = inventar_detail_schrift.render(
                    "No chests in your inventory.",
                    True,
                    inventar_panel_text
                )
                FENSTER.blit(
                    keine_truhen_text,
                    (inventar_panel.left + 16, inventar_panel.top + 68)
                )

            truhen_start_y = inventar_panel.top + 62
            inventar_truhen_liste_feld = pygame.Rect(
                inventar_panel.left + 6,
                truhen_start_y,
                inventar_panel.width - 12,
                max(0, inventar_panel_bottom - truhen_start_y - 8)
            )
            truhen_hoehe = 72
            inventar_truhen_scroll_max = max(
                0,
                len(vorhandene_truhen) * truhen_hoehe
                - inventar_truhen_liste_feld.height
            )
            inventar_truhen_scroll = min(
                inventar_truhen_scroll,
                inventar_truhen_scroll_max
            )

            if inventar_truhen_scroll_max > 0:
                scroll_hinweis = inventar_detail_schrift.render(
                    "Scroll to see more",
                    True,
                    inventar_panel_text
                )
                FENSTER.blit(
                    scroll_hinweis,
                    (inventar_panel.right - scroll_hinweis.get_width() - 12,
                     inventar_panel.top + 48)
                )

            vorheriger_clip = FENSTER.get_clip()
            FENSTER.set_clip(inventar_truhen_liste_feld)

            for index, truhen_typ in enumerate(vorhandene_truhen):
                preis = TRUHEN_OEFFNEN_DATEN[truhen_typ]["preis"]
                minimum, maximum = TRUHEN_OEFFNEN_DATEN[truhen_typ]["belohnung"]
                bestand = inventar_kisten.count(truhen_typ)
    
                karten = pygame.Rect(
                    inventar_panel.left + 8,
                    truhen_start_y + index * truhen_hoehe - inventar_truhen_scroll,
                    inventar_panel.width - 16,
                    truhen_hoehe - 4
                )
                truhenfarbe = TREASURE_CHEST_FARBEN[truhen_typ]
    
                pygame.draw.rect(FENSTER, karten_farbe, karten, border_radius=8)
                pygame.draw.rect(
                    FENSTER,
                    truhenfarbe,
                    karten,
                    width=2,
                    border_radius=8
                )
    
                # Kleines Kisten Icon passend zur Seltenheit.
                icon_x = karten.left + 8
                icon_y = karten.top + 7
                pygame.draw.rect(
                    FENSTER,
                    (91, 49, 27),
                    (icon_x, icon_y + 8, 34, 24),
                    border_radius=4
                )
                pygame.draw.rect(
                    FENSTER,
                    truhenfarbe,
                    (icon_x - 1, icon_y, 36, 13),
                    border_radius=4
                )
                pygame.draw.rect(
                    FENSTER,
                    (255, 215, 105),
                    (icon_x + 15, icon_y + 9, 4, 22)
                )
    
                name_text = inventar_detail_schrift.render(
                    f"{truhen_typ} x{bestand}",
                    True,
                    inventar_panel_text
                )
                FENSTER.blit(name_text, (karten.left + 48, karten.top + 3))
    
                kosten_text = inventar_detail_schrift.render(
                    f"Cost: {preis} GC | Reward: "
                    f"{minimum // 1_000_000}-{maximum // 1_000_000}M Cookies",
                    True,
                    inventar_panel_text
                )
                FENSTER.blit(kosten_text, (karten.left + 48, karten.top + 22))
    
                open_breite = min(76, max(58, karten.width // 4))
                all_breite = min(108, max(82, karten.width // 3))
                button_abstand = 6
                button_gesamt = open_breite + all_breite + button_abstand
                button_start_x = karten.right - button_gesamt - 8
                button_y = karten.bottom - 27
    
                open_feld = pygame.Rect(
                    button_start_x,
                    button_y,
                    open_breite,
                    22
                )
                open_all_feld = pygame.Rect(
                    button_start_x + open_breite + button_abstand,
                    button_y,
                    all_breite,
                    22
                )
    
                kann_einzeln = bestand > 0 and goldene_cookies >= preis
                kann_alle = bestand > 0 and goldene_cookies >= preis * bestand
    
                aktiv_farbe = (225, 190, 125) if hintergrund_modus != "purple" else (173, 137, 224)
                inaktiv_farbe = (125, 119, 108)
                open_farbe = aktiv_farbe if kann_einzeln else inaktiv_farbe
                all_farbe = aktiv_farbe if kann_alle else inaktiv_farbe
    
                pygame.draw.rect(FENSTER, open_farbe, open_feld, border_radius=6)
                pygame.draw.rect(FENSTER, all_farbe, open_all_feld, border_radius=6)
    
                open_text = inventar_detail_schrift.render(
                    "OPEN",
                    True,
                    TEXTFARBE
                )
                all_text = inventar_detail_schrift.render(
                    "OPEN ALL",
                    True,
                    TEXTFARBE
                )
                FENSTER.blit(open_text, open_text.get_rect(center=open_feld.center))
                FENSTER.blit(all_text, all_text.get_rect(center=open_all_feld.center))
    
                if inventar_truhen_liste_feld.colliderect(open_feld):
                    truhe_open_felder.append((open_feld, truhen_typ))
                if inventar_truhen_liste_feld.colliderect(open_all_feld):
                    truhe_alle_felder.append((open_all_feld, truhen_typ))

            FENSTER.set_clip(vorheriger_clip)
    

    # Kopfzeile passend zum ausgewaehlten Hintergrund
    if hintergrund_modus == "purple":
        kopf_farbe = (25, 20, 39)
        trenn_farbe = (75, 61, 96)
        kopf_textfarbe = (248, 235, 255)
    else:
        kopf_farbe = (255, 250, 240)
        trenn_farbe = (225, 211, 187)
        kopf_textfarbe = TEXTFARBE

    pygame.draw.rect(FENSTER, kopf_farbe, (0, 0, BREITE, 100))
    pygame.draw.line(FENSTER, trenn_farbe, (0, 99), (BREITE, 99), 2)

    titel = kleine_schrift.render("COOKIE CLICKER", True, kopf_textfarbe)
    FENSTER.blit(titel, (BREITE // 2 - titel.get_width() // 2, 14))
    zaehler = schrift.render(f"{int(cookie_anzahl)} Cookies", True, kopf_textfarbe)
    FENSTER.blit(zaehler, (BREITE // 2 - zaehler.get_width() // 2, 42))

    if spiel_status == "game":
        if hintergrund_modus == "purple":
            shop_button_farbe = (47, 37, 65)
            shop_rand_farbe = (142, 111, 190)
            shop_button_textfarbe = (248, 235, 255)
        else:
            shop_button_farbe = (238, 216, 180)
            shop_rand_farbe = (188, 116, 50)
            shop_button_textfarbe = TEXTFARBE

        if hintergrund_modus == "purple":
            inventar_farbe = (47, 37, 65)
            inventar_rand = (142, 111, 190)
            inventar_text_farbe = (248, 235, 255)
        else:
            inventar_farbe = (238, 216, 180)
            inventar_rand = (188, 116, 50)
            inventar_text_farbe = TEXTFARBE

        if inventar_offen:
            inventar_farbe = (255, 190, 125)

        pygame.draw.rect(
            FENSTER,
            inventar_farbe,
            inventar_knopf,
            border_radius=9
        )
        pygame.draw.rect(
            FENSTER,
            inventar_rand,
            inventar_knopf,
            width=1,
            border_radius=9
        )

        inventar_text = kleine_schrift.render(
            "INVENTORY",
            True,
            inventar_text_farbe
        )
        FENSTER.blit(
            inventar_text,
            inventar_text.get_rect(center=inventar_knopf.center)
        )

        pygame.draw.rect(FENSTER, shop_button_farbe, shop_button, border_radius=10)
        pygame.draw.rect(FENSTER, shop_rand_farbe, shop_button, width=2, border_radius=10)

        shop_text = kleine_schrift.render("SHOP", True, shop_button_textfarbe)
        FENSTER.blit(shop_text, shop_text.get_rect(center=shop_button.center))

    aktuelles_design = next(
        design
        for design in COOKIE_DESIGNS
        if design["name"] == selected_cookie_design
    )

    flaeche_groesse = cookie_radius * 2 + 140
    cookie_flaeche = pygame.Surface(
        (flaeche_groesse, flaeche_groesse),
        pygame.SRCALPHA
    )
    mitte = (flaeche_groesse // 2, flaeche_groesse // 2)
    radius = int(cookie_radius * cookie_skalierung * hover_skalierung)

    zeichne_cookie_design(
        cookie_flaeche,
        mitte,
        radius,
        aktuelles_design,
        zeit
    )

    gedreht = pygame.transform.rotate(cookie_flaeche, dreh_winkel)
    FENSTER.blit(gedreht, gedreht.get_rect(center=cookie_mitte))

    # Der Auto Cursor bleibt sichtbar auf dem Cookie liegen.
    if auto_cursor_rate > 0:
        cursor_x = cookie_mitte[0] + 24
        cursor_y = cookie_mitte[1] - 24

        stufe = auto_cursor_stufe_berechnen()
        cursor_farbe, cursor_rand, cursor_leuchten = auto_cursor_farben(stufe)

        cursor_form = [
            (int(cursor_x), int(cursor_y)),
            (int(cursor_x + 5), int(cursor_y + 22)),
            (int(cursor_x + 11), int(cursor_y + 15)),
            (int(cursor_x + 20), int(cursor_y + 25)),
            (int(cursor_x + 25), int(cursor_y + 21)),
            (int(cursor_x + 16), int(cursor_y + 12)),
            (int(cursor_x + 24), int(cursor_y + 10)),
        ]

        # Ab Stufe 3 bekommt der Cursor einen violetten Leuchteffekt.
        if cursor_leuchten is not None:
            leucht_flaeche = pygame.Surface((54, 54), pygame.SRCALPHA)
            pygame.draw.circle(leucht_flaeche, (*cursor_leuchten, 45), (27, 27), 25)
            pygame.draw.circle(leucht_flaeche, (*cursor_leuchten, 75), (27, 27), 17)
            FENSTER.blit(
                leucht_flaeche,
                (int(cursor_x - 15), int(cursor_y - 15))
            )

        pygame.draw.polygon(FENSTER, cursor_farbe, cursor_form)
        pygame.draw.polygon(FENSTER, cursor_rand, cursor_form, 2)
            

    # Kruemel fliegen nach aussen und werden transparent.
    for teilchen in kruemel:
        alpha = int(255 * min(1.0, teilchen["leben"] / 0.2))
        groesse = teilchen["groesse"]
        effekt = pygame.Surface((groesse * 2 + 2, groesse * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(effekt, (151, 91, 43, alpha), (groesse + 1, groesse + 1), groesse)
        FENSTER.blit(effekt, (int(teilchen["x"] - groesse), int(teilchen["y"] - groesse)))

    # +1 schwebt nach oben und verschwindet.
    for text in klick_texte:
        alpha = int(255 * text["leben"] / text["max_leben"])
        plus_eins = kleine_schrift.render(f"+{text['wert']}", True, BRAUN)
        plus_eins.set_alpha(alpha)
        FENSTER.blit(plus_eins, (int(text["x"] - plus_eins.get_width() / 2), int(text["y"])))

    # Der Shop liegt Ã¼ber dem Spiel, ohne den Spielzustand zu pausieren.
    if shop_offen or shop_x < BREITE:
        if hintergrund_modus == "purple":
            shop_farbe = (25, 20, 39)
            shop_rand_farbe = (142, 111, 190)
            shop_textfarbe = (248, 235, 255)
            shop_button_farbe = (47, 37, 65)
        else:
            shop_farbe = (255, 250, 240)
            shop_rand_farbe = (188, 116, 50)
            shop_textfarbe = TEXTFARBE
            shop_button_farbe = (238, 216, 180)

        pygame.draw.rect(FENSTER, shop_farbe, shop_panel)
        pygame.draw.line(
            FENSTER,
            shop_rand_farbe,
            (shop_panel.left, shop_panel.top),
            (shop_panel.left, shop_panel.bottom),
            3
        )

        shop_titel = schrift.render("Shop", True, shop_textfarbe)
        FENSTER.blit(
            shop_titel,
            (shop_panel.left + 24, shop_panel.top + 20)
        )

        pygame.draw.rect(FENSTER, shop_button_farbe, shop_schliessen, border_radius=8)
        x_text = kleine_schrift.render("X", True, shop_textfarbe)
        FENSTER.blit(x_text, x_text.get_rect(center=shop_schliessen.center))

        # Zwei Tabs innerhalb des vorhandenen Shop-Panel.
        tab_y = shop_panel.top + 58
        tab_abstand = 8
        tab_breite = (shop_panel.width - 40 - tab_abstand) // 2

        shop_upgrades_tab = pygame.Rect(
            shop_panel.left + 16,
            tab_y,
            tab_breite,
            30
        )
        shop_cookie_tab = pygame.Rect(
            shop_upgrades_tab.right + tab_abstand,
            tab_y,
            tab_breite,
            30
        )

        detail_schrift = pygame.font.SysFont("arial", 13)
        tab_aktiv = (173, 137, 224) if hintergrund_modus == "purple" else (225, 190, 125)
        tab_inaktiv = (47, 37, 65) if hintergrund_modus == "purple" else (238, 216, 180)

        for tab_feld, tab_name, tab_seite in (
            (shop_upgrades_tab, "UPGRADES", "upgrades"),
            (shop_cookie_tab, "COOKIE SHOP", "cookie"),
        ):
            tab_farbe = tab_aktiv if shop_seite == tab_seite else tab_inaktiv
            pygame.draw.rect(FENSTER, tab_farbe, tab_feld, border_radius=7)
            tab_text = detail_schrift.render(tab_name, True, shop_textfarbe)
            FENSTER.blit(tab_text, tab_text.get_rect(center=tab_feld.center))

        upgrade_kauf_felder = []
        cookie_shop_kauf_felder = []

        if shop_seite == "upgrades":
            aktuelle_produktion = cookies_pro_sekunde
            cps_text = kleine_schrift.render(
                f"Click: {cookies_pro_klick} | Production: "
                f"{aktuelle_produktion:g} CPS",
                True,
                shop_textfarbe
            )
            FENSTER.blit(cps_text, (shop_panel.left + 24, shop_panel.top + 94))

            reihen_hoehe = max(38, min(62, (shop_panel.height - 145) // 5))
            reihe_abstand = reihen_hoehe + 4

            for index, upgrade in enumerate(upgrades):
                reihe_y = shop_panel.top + 120 + index * reihe_abstand
                reihe = pygame.Rect(
                    shop_panel.left + 12,
                    reihe_y,
                    shop_panel.width - 24,
                    reihen_hoehe
                )

                kauf_feld = pygame.Rect(
                    reihe.right - 78,
                    reihe.centery - 17,
                    68,
                    34
                )
                upgrade_kauf_felder.append((kauf_feld, upgrade))

                if hintergrund_modus == "purple":
                    karten_farbe = (39, 31, 56)
                    karten_rand = (91, 72, 120)
                else:
                    karten_farbe = (248, 240, 220)
                    karten_rand = (225, 211, 187)

                pygame.draw.rect(FENSTER, karten_farbe, reihe, border_radius=8)
                pygame.draw.rect(
                    FENSTER, karten_rand, reihe, width=1, border_radius=8
                )

                name_text = detail_schrift.render(
                    upgrade["name"], True, shop_textfarbe
                )
                
                preis_text = detail_schrift.render(
                    f"Cost: {upgrade['preis']:,} | Level: {upgrade['level']}",
                    True,
                    shop_textfarbe
                )
                effekt_text = detail_schrift.render(
                    upgrade["effekt"], True, shop_textfarbe
                )

                FENSTER.blit(name_text, (reihe.left + 8, reihe.top + 3))
                FENSTER.blit(preis_text, (reihe.left + 8, reihe.top + 21))
                FENSTER.blit(effekt_text, (reihe.left + 8, reihe.top + 39))

                kann_kaufen = cookie_anzahl >= upgrade["preis"]
                if kann_kaufen:
                    kauf_farbe = (225, 190, 125)
                    kauf_textfarbe = TEXTFARBE
                else:
                    kauf_farbe = (105, 100, 108) if hintergrund_modus == "purple" else (205, 199, 188)
                    kauf_textfarbe = (248, 235, 255) if hintergrund_modus == "purple" else (120, 112, 101)

                pygame.draw.rect(FENSTER, kauf_farbe, kauf_feld, border_radius=8)
                kauf_text = detail_schrift.render("BUY", True, kauf_textfarbe)
                FENSTER.blit(kauf_text, kauf_text.get_rect(center=kauf_feld.center))

        else:
            # Cookie-Designs mit Vorschau, Preis und Besitzstatus.
            gc_text = kleine_schrift.render(
                f"Golden Cookies: {goldene_cookies} GC",
                True,
                shop_textfarbe
            )
            FENSTER.blit(gc_text, (shop_panel.left + 24, shop_panel.top + 94))

            start_y = shop_panel.top + 112
            verfuegbare_hoehe = max(1, shop_panel.bottom - start_y - 8)
            design_reihenhoehe = max(
                21,
                min(44, verfuegbare_hoehe // len(COOKIE_DESIGNS))
            )
            design_reihenabstand = design_reihenhoehe + 2

            for index, design in enumerate(COOKIE_DESIGNS):
                reihe = pygame.Rect(
                    shop_panel.left + 12,
                    start_y + index * design_reihenabstand,
                    shop_panel.width - 24,
                    design_reihenhoehe
                )

                if hintergrund_modus == "purple":
                    karten_farbe = (39, 31, 56)
                    karten_rand = (91, 72, 120)
                else:
                    karten_farbe = (248, 240, 220)
                    karten_rand = (225, 211, 187)

                pygame.draw.rect(FENSTER, karten_farbe, reihe, border_radius=7)
                pygame.draw.rect(FENSTER, karten_rand, reihe, width=1, border_radius=7)

                # Ein kleines Cookie-Icon wird ohne externe Bilddatei gezeichnet.
                vorschau_mitte = (reihe.left + 20, reihe.centery)
                vorschau_radius = max(8, min(13, reihe.height // 3))
                dunkle_farbe = tuple(int(wert * 0.65) for wert in design["farbe"])
                pygame.draw.circle(
                    FENSTER,
                    dunkle_farbe,
                    (vorschau_mitte[0] + 1, vorschau_mitte[1] + 2),
                    vorschau_radius + 1
                )
                pygame.draw.circle(
                    FENSTER,
                    design["farbe"],
                    vorschau_mitte,
                    vorschau_radius
                )
                for chip_x, chip_y in ((-4, -3), (4, -4), (1, 4)):
                    pygame.draw.circle(
                        FENSTER,
                        design["schoko"],
                        (vorschau_mitte[0] + chip_x, vorschau_mitte[1] + chip_y),
                        max(1, vorschau_radius // 4)
                    )

                preis_anzeige = "FREE" if design["preis"] == 0 else f"{design['preis']} GC"
                design_text = detail_schrift.render(
                    f"{design['name']} - {preis_anzeige}",
                    True,
                    shop_textfarbe
                )
                FENSTER.blit(
                    design_text,
                    (reihe.left + 42, reihe.centery - design_text.get_height() // 2)
                )

                status_feld = pygame.Rect(
                    reihe.right - 78,
                    reihe.centery - 13,
                    68,
                    26
                )

                if design["name"] in COOKIE_DESIGNS_OWNED:
                    pygame.draw.rect(FENSTER, tab_inaktiv, status_feld, border_radius=6)
                    status_text = detail_schrift.render("OWNED", True, shop_textfarbe)
                    FENSTER.blit(status_text, status_text.get_rect(center=status_feld.center))
                else:
                    kann_kaufen = goldene_cookies >= design["preis"]
                    if kann_kaufen:
                        button_farbe = (225, 190, 125)
                        button_textfarbe = TEXTFARBE
                    else:
                        button_farbe = (105, 100, 108) if hintergrund_modus == "purple" else (205, 199, 188)
                        button_textfarbe = (248, 235, 255) if hintergrund_modus == "purple" else (120, 112, 101)

                    pygame.draw.rect(FENSTER, button_farbe, status_feld, border_radius=6)
                    buy_text = detail_schrift.render("BUY", True, button_textfarbe)
                    FENSTER.blit(buy_text, buy_text.get_rect(center=status_feld.center))
                    cookie_shop_kauf_felder.append((status_feld, design["name"]))

    if spiel_status == "game":
        if aktives_sammelobjekt is not None:
            sammel_rect = sammelobjekt_rechteck()
            mitte = sammel_rect.center
            groesse = sammel_rect.width
            puls = (math.sin(sammelobjekt_animationszeit * 4.0) + 1.0) / 2.0

            if aktives_sammelobjekt["art"] == "golden":
                # Mehrschichtiges, pulsierendes Leuchten hinter dem Cookie.
                leucht_seite = groesse * 3
                leucht_flaeche = pygame.Surface(
                    (leucht_seite, leucht_seite),
                    pygame.SRCALPHA
                )
                leucht_mitte = (leucht_seite // 2, leucht_seite // 2)
                leucht_radius = max(18, groesse // 2 - 5)

                for zusatz, alpha in ((25, 18), (15, 30), (6, 48)):
                    pygame.draw.circle(
                        leucht_flaeche,
                        (255, 184, 35, min(100, alpha + int(puls * 18))),
                        leucht_mitte,
                        leucht_radius + zusatz + int(puls * 3)
                    )

                FENSTER.blit(
                    leucht_flaeche,
                    (mitte[0] - leucht_seite // 2, mitte[1] - leucht_seite // 2)
                )

                radius = max(16, groesse // 2 - 5)

                # Dunkler Rand, mehrere goldene Schichten und ein heller Glanzrand.
                pygame.draw.circle(FENSTER, (112, 65, 14), mitte, radius + 2)
                pygame.draw.circle(FENSTER, (205, 137, 24), mitte, radius)
                pygame.draw.circle(FENSTER, (255, 190, 39), mitte, radius - 3)
                pygame.draw.circle(FENSTER, (255, 220, 99), mitte, radius - 7)
                pygame.draw.circle(FENSTER, (255, 235, 145), mitte, radius - 11)
                pygame.draw.arc(
                    FENSTER,
                    (255, 250, 205),
                    (mitte[0] - radius + 5, mitte[1] - radius + 5,
                     (radius - 5) * 2, (radius - 5) * 2),
                    math.radians(205),
                    math.radians(315),
                    2
                )

                # Unterschiedlich grosse Schokostuecke mit Schatten und Glanz.
                for chip_index, (rel_x, rel_y, groessenfaktor, hoehenfaktor) in enumerate(
                    GOLDENER_COOKIE_SCHOKO
                ):
                    chip_groesse = max(2, int(radius * groessenfaktor))
                    chip_breite = chip_groesse * 2
                    chip_hoehe = max(2, int(chip_breite * hoehenfaktor))
                    chip_x = mitte[0] + int(rel_x * radius)
                    chip_y = mitte[1] + int(rel_y * radius)
                    chip_rect = pygame.Rect(
                        chip_x - chip_breite // 2,
                        chip_y - chip_hoehe // 2,
                        chip_breite,
                        chip_hoehe
                    )

                    pygame.draw.ellipse(
                        FENSTER,
                        (91, 52, 20),
                        chip_rect.move(1, 2)
                    )
                    pygame.draw.ellipse(
                        FENSTER,
                        GOLDENER_COOKIE_SCHOKO_FARBEN[
                            chip_index % len(GOLDENER_COOKIE_SCHOKO_FARBEN)
                        ],
                        chip_rect
                    )

                    glanz_rect = pygame.Rect(
                        chip_rect.left + max(1, chip_groesse // 3),
                        chip_rect.top + 1,
                        max(1, chip_groesse // 2),
                        max(1, chip_hoehe // 3)
                    )
                    pygame.draw.ellipse(FENSTER, (168, 103, 47), glanz_rect)

                # Kleine Sterne funkeln und bewegen sich langsam um den Cookie.
                for stern_index in range(6):
                    stern_phase = sammelobjekt_animationszeit * 0.75 + stern_index * math.tau / 6
                    stern_abstand = radius + 13 + math.sin(
                        sammelobjekt_animationszeit * 2.0 + stern_index
                    ) * 3
                    stern_x = mitte[0] + math.cos(stern_phase) * stern_abstand
                    stern_y = mitte[1] + math.sin(stern_phase) * stern_abstand
                    funkeln = (math.sin(sammelobjekt_animationszeit * 3.2 + stern_index * 1.8) + 1) / 2
                    stern_groesse = 2 + int(funkeln * 3)
                    sx, sy = int(stern_x), int(stern_y)
                    stern_punkte = [
                        (sx, sy - stern_groesse),
                        (sx + 1, sy - 1),
                        (sx + stern_groesse, sy),
                        (sx + 1, sy + 1),
                        (sx, sy + stern_groesse),
                        (sx - 1, sy + 1),
                        (sx - stern_groesse, sy),
                        (sx - 1, sy - 1),
                    ]
                    stern_farbe = (
                        255,
                        205 + int(funkeln * 45),
                        95 + int(funkeln * 130)
                    )
                    pygame.draw.polygon(FENSTER, stern_farbe, stern_punkte)


            else:
                # Die Kistefarbe zeigt ihre Seltenheit.
                kistenfarbe = TREASURE_CHEST_FARBEN[aktives_sammelobjekt["name"]]
                kistenleuchten = pygame.Surface((groesse * 2, groesse * 2), pygame.SRCALPHA)
                leucht_mitte = (groesse, groesse)

                pygame.draw.circle(
                    kistenleuchten,
                    (*kistenfarbe, 45 + int(puls * 25)),
                    leucht_mitte,
                    groesse // 2 + 12 + int(puls * 4)
                )
                FENSTER.blit(
                    kistenleuchten,
                    (mitte[0] - groesse, mitte[1] - groesse)
                )

                kisten_breite = int(groesse *0.82)
                kisten_hoehe = int(groesse * 0.58)
                kisten_body = pygame.Rect(
                    mitte[0] - kisten_breite // 2,
                    mitte[1] - kisten_hoehe // 2 + 5,
                    kisten_breite,
                    kisten_hoehe
                )
                kisten_deckel = pygame.Rect(
                    kisten_body.left - 2,
                    kisten_body.top - 9,
                    kisten_body.width + 4,
                    15
                )

                # Dunkler Schatten und Holzkoerper mit mehreren Schattierungen.
                pygame.draw.rect(
                    FENSTER,
                    (42, 25, 19),
                    kisten_body.move(2, 3),
                    border_radius=5
                )
                pygame.draw.rect(FENSTER, (91, 49, 27), kisten_body, border_radius=5)

                innen_body = kisten_body.inflate(-4, -4)
                pygame.draw.rect(FENSTER, (137, 78, 38), innen_body, border_radius=3)
                pygame.draw.rect(
                    FENSTER,
                    (164, 101, 51),
                    (innen_body.left + 2, innen_body.top + 2,
                     max(1, innen_body.width - 4), max(2, innen_body.height // 3)),
                    border_radius=2
                )

                # Bretter und feine Holzmaserung auf der Vorderseite.
                for plank_y in (kisten_body.top + kisten_body.height // 3,
                                kisten_body.top + 2 * kisten_body.height // 3):
                    pygame.draw.line(
                        FENSTER,
                        (78, 42, 25),
                        (kisten_body.left + 4, plank_y),
                        (kisten_body.right - 4, plank_y),
                        1
                    )
                pygame.draw.line(
                    FENSTER,
                    (190, 125, 66),
                    (kisten_body.left + 5, kisten_body.top + 5),
                    (kisten_body.left + 5, kisten_body.bottom - 5),
                    1
                )

                # Gewoelbter Deckel mit Holzfarbe und Seltenheits-Akzent.
                pygame.draw.rect(
                    FENSTER,
                    (55, 33, 23),
                    kisten_deckel.move(1, 2),
                    border_radius=5
                )
                pygame.draw.rect(FENSTER, (111, 61, 31), kisten_deckel, border_radius=5)
                deckel_innen = kisten_deckel.inflate(-4, -4)
                pygame.draw.rect(FENSTER, (166, 99, 45), deckel_innen, border_radius=4)
                pygame.draw.rect(
                    FENSTER,
                    kistenfarbe,
                    (kisten_deckel.left + 3, kisten_deckel.top + 2,
                     max(1, kisten_deckel.width - 6), max(3, kisten_deckel.height // 3)),
                    border_radius=3
                )
                pygame.draw.line(
                    FENSTER,
                    (238, 190, 103),
                    (kisten_deckel.left + 6, kisten_deckel.top + 3),
                    (kisten_deckel.right - 6, kisten_deckel.top + 3),
                    1
                )

                # Metallbaender und farbiger Mittelstreifen.
                band_breite = max(3, groesse // 14)
                band_farbe = (218, 169, 75)
                for band_x in (kisten_body.left + 4, kisten_body.right - 4 - band_breite):
                    pygame.draw.rect(
                        FENSTER,
                        (117, 74, 35),
                        (band_x - 1, kisten_body.top, band_breite + 2, kisten_body.height)
                    )
                    pygame.draw.rect(
                        FENSTER,
                        band_farbe,
                        (band_x, kisten_body.top, band_breite, kisten_body.height)
                    )

                pygame.draw.rect(
                    FENSTER,
                    kistenfarbe,
                    (mitte[0] - max(2, groesse // 18), kisten_body.top,
                     max(4, groesse // 9), kisten_body.height)
                )

                pygame.draw.rect(FENSTER, (225, 179, 83), kisten_body, width=2, border_radius=5)
                pygame.draw.rect(FENSTER, (245, 210, 125), kisten_deckel, width=2, border_radius=5)

                # Vier kleine Nieten und ein goldenes Schloss.
                nieten_radius = max(1, groesse // 30)
                for niet_x in (kisten_body.left + 3, kisten_body.right - 3):
                    for niet_y in (kisten_body.top + 3, kisten_body.bottom - 3):
                        pygame.draw.circle(
                            FENSTER,
                            (255, 222, 135),
                            (niet_x, niet_y),
                            nieten_radius
                        )

                schloss_breite = max(9, groesse // 5)
                schloss_hoehe = max(9, groesse // 5)
                schloss = pygame.Rect(
                    mitte[0] - schloss_breite // 2,
                    kisten_body.centery - schloss_hoehe // 2,
                    schloss_breite,
                    schloss_hoehe
                )
                pygame.draw.rect(FENSTER, (114, 68, 27), schloss.move(1, 1), border_radius=3)
                pygame.draw.rect(FENSTER, (255, 215, 105), schloss, border_radius=3)
                pygame.draw.rect(FENSTER, (255, 239, 174), schloss, width=1, border_radius=3)
                pygame.draw.circle(
                    FENSTER,
                    (104, 62, 25),
                    (schloss.centerx, schloss.centery - 1),
                    max(1, schloss_breite // 7)
                )
                pygame.draw.line(
                    FENSTER,
                    (104, 62, 25),
                    (schloss.centerx, schloss.centery),
                    (schloss.centerx, schloss.bottom - 2),
                    max(1, groesse // 30)
                )

            # Benachrichtugng und Countdown oben links.
            if aktives_sammelobjekt["art"] == "golden":
                meldung = "A GOLDEN COOKIE!!"
                meldungsrand = (255, 195, 45)
            else:
                meldung = f"{aktives_sammelobjekt['name'].upper()}!!"
                meldungsrand = TREASURE_CHEST_FARBEN[aktives_sammelobjekt["name"]]

            meldung_text = kleine_schrift.render(meldung, True, (255, 235, 180))
            countdown_text = kleine_schrift.render(
                f"{math.ceil(aktives_sammelobjekt['restzeit'])}s",
                True,
                (255, 255, 255)
            )

            meldungsbreite = min(
                BREITE - 24,
                meldung_text.get_width() + countdown_text.get_width() + 38
            )
            meldungsfeld = pygame.Rect(12, 108, meldungsbreite, 42)
            pygame.draw.rect(FENSTER, (38, 29, 17), meldungsfeld, border_radius=9)
            pygame.draw.rect(FENSTER, meldungsrand, meldungsfeld, width=2, border_radius=9)
            FENSTER.blit(meldung_text, (meldungsfeld.left + 10, meldungsfeld.top + 10))
            FENSTER.blit(
                countdown_text,
                (meldungsfeld.right - countdown_text.get_width() - 10, meldungsfeld.top + 10)
            )

        elif goldener_cookie_verpasst_timer > 0:
            verpasst_feld = pygame.Rect(12, 108, 280, 66)
            pygame.draw.rect(FENSTER, (45, 24, 25), verpasst_feld, border_radius=9)
            pygame.draw.rect(FENSTER, (190, 75, 65), verpasst_feld, width=2, border_radius=9)

            get_good_text = kleine_schrift.render("GET GOOD!", True, (255, 190, 140))
            verpasst_text = kleine_schrift.render(
                "You missed the Golden Cookie.",
                True,
                (255, 235, 220)
            )
            FENSTER.blit(get_good_text, (verpasst_feld.left + 10, verpasst_feld.top + 5))
            FENSTER.blit(verpasst_text, (verpasst_feld.left + 10, verpasst_feld.top + 34))

    # Kurz sichtbare Meldung nach dem Ã–ffnen einer oder mehrerer Truhen.
    if spiel_status == "game" and truhe_belohnung_timer > 0:
        belohnung_text = kleine_schrift.render(
            f"You won {truhe_belohnung_text}",
            True,
            (255, 239, 190)
        )
        belohnungsfeld = pygame.Rect(
            0,
            112,
            belohnung_text.get_width() + 32,
            belohnung_text.get_height() + 18
        )
        belohnungsfeld.centerx = BREITE // 2

        pygame.draw.rect(
            FENSTER,
            (38, 29, 17),
            belohnungsfeld,
            border_radius=10
        )
        pygame.draw.rect(
            FENSTER,
            (255, 195, 45),
            belohnungsfeld,
            width=2,
            border_radius=10
        )
        FENSTER.blit(
            belohnung_text,
            (belohnungsfeld.left + 16, belohnungsfeld.top + 9)
        )

    # MenÃ¼ liegt als halbtransparente FlÃ¤che Ã¼ber dem pausierten Spiel.
    if spiel_status in ("menu", "settings"):
        abdunklung = pygame.Surface((BREITE, HOEHE), pygame.SRCALPHA)
        abdunklung.fill((30, 18, 38, 185))
        FENSTER.blit(abdunklung, (0, 0))

        panel_hoehe = settings_panel_hoehe if spiel_status == "settings" else 350
        panel_oben = settings_oben if spiel_status == "settings" else menue_oben
        panel = pygame.Rect(
            BREITE // 2 - 190,
            panel_oben,
            380,
            panel_hoehe
        )
        pygame.draw.rect(FENSTER, (255, 250, 240), panel, border_radius=18)
        pygame.draw.rect(FENSTER, (188, 116, 50), panel, width=3, border_radius=18)

        if spiel_status == "menu":
            ueberschrift = schrift.render("Paused", True, TEXTFARBE)
            FENSTER.blit(
                ueberschrift,
                (BREITE // 2 - ueberschrift.get_width() // 2, menue_oben + 20)
            )

            menue_punkte = [
                (weiter_feld, "Continue"),
                (einstellungen_feld, "Settings"),
                (spinning_wheel_menu_feld, "SPINNING WHEEL"),
                (verlassen_feld, "Quit"),
            ]

            for feld, beschriftung in menue_punkte:
                pygame.draw.rect(FENSTER, (238, 216, 180), feld, border_radius=12)
                pygame.draw.rect(FENSTER, (188, 116, 50), feld, width=2, border_radius=12)
                text = kleine_schrift.render(beschriftung, True, TEXTFARBE)
                FENSTER.blit(text, text.get_rect(center=feld.center))

        else:
            ueberschrift = schrift.render("Settings", True, TEXTFARBE)
            FENSTER.blit(
                ueberschrift,
                (BREITE // 2 - ueberschrift.get_width() // 2, settings_oben + 20)
            )

            hintergrund_punkte = [
                (purple_feld, "Purple Night", "purple"),
                (vanilla_feld, "Vanilla Glow", "vanilla"),
            ]

            for feld, beschriftung, modus in hintergrund_punkte:
                if hintergrund_modus == modus:
                    feld_farbe = (225, 190, 125)
                else:
                    feld_farbe = (238, 216, 180)

                pygame.draw.rect(FENSTER, feld_farbe, feld, border_radius=12)
                pygame.draw.rect(FENSTER, (188, 116, 50), feld, width=2, border_radius=12)

                text = kleine_schrift.render(beschriftung, True, TEXTFARBE)
                FENSTER.blit(text, text.get_rect(center=feld.center))

            lautstaerke_text = kleine_schrift.render(
                f"Click sound: {int(sound_lautstaerke * 100)}%",
                True,
                TEXTFARBE
            )
            FENSTER.blit(
                lautstaerke_text,
                (BREITE // 2 - lautstaerke_text.get_width() // 2, settings_oben + 185)
            )

            # Hintergrundlinie und gefuellter Teil des Reglers
            pygame.draw.rect(FENSTER, (210, 190, 160), lautstaerke_linie, border_radius=4)
            gefuellte_breite = int(lautstaerke_linie.width * sound_lautstaerke)
            if gefuellte_breite > 0:
                pygame.draw.rect(
                    FENSTER,
                    (188, 116, 50),
                    (lautstaerke_linie.left, lautstaerke_linie.top,
                     gefuellte_breite, lautstaerke_linie.height),
                     border_radius=4
                )

            regler_x = int(
                lautstaerke_linie.left + lautstaerke_linie.width * sound_lautstaerke
            )
            pygame.draw.circle(
                FENSTER,
                (112, 66, 42),
                (regler_x, lautstaerke_linie.centery),
                10
            )

            cookie_design_titel = kleine_schrift.render(
                "COOKIE DESIGN",
                True,
                TEXTFARBE
            )
            FENSTER.blit(
                cookie_design_titel,
                cookie_design_titel.get_rect(
                    center=(BREITE // 2, settings_oben + 250)
                )
            )

            cookie_design_grid_rect = pygame.Rect(
                panel.left + 16,
                settings_oben + 270,
                panel.width - 32,
                max(1, panel.bottom - (settings_oben + 270) - 60)
            )
            cookie_design_select_felder = []

            spalten = 2
            kachel_hoehe = 64
            kachel_abstand = 8
            kachel_schritt = kachel_hoehe + kachel_abstand
            kachel_breite = (
                cookie_design_grid_rect.width - kachel_abstand
            ) // spalten
            zeilen = (len(COOKIE_DESIGNS) + spalten - 1) // spalten

            cookie_design_scroll_max = max(
                0,
                zeilen * kachel_schritt - cookie_design_grid_rect.height
            )
            cookie_design_scroll = min(
                cookie_design_scroll,
                cookie_design_scroll_max
            )

            vorheriger_clip = FENSTER.get_clip()
            FENSTER.set_clip(cookie_design_grid_rect)
            kachel_schrift = pygame.font.SysFont("arial", 11)

            for index, design in enumerate(COOKIE_DESIGNS):
                spalte = index % spalten
                zeile = index // spalten
                kachel = pygame.Rect(
                    cookie_design_grid_rect.left
                    + spalte * (kachel_breite + kachel_abstand),
                    cookie_design_grid_rect.top
                    + zeile * kachel_schritt
                    - cookie_design_scroll,
                    kachel_breite,
                    kachel_hoehe
                )

                if hintergrund_modus == "purple":
                    kachel_farbe = (39, 31, 56)
                    kachel_rand = (91, 72, 120)
                    kachel_textfarbe = (248, 235, 255)
                else:
                    kachel_farbe = (248, 240, 220)
                    kachel_rand = (225, 211, 187)
                    kachel_textfarbe = TEXTFARBE

                pygame.draw.rect(FENSTER, kachel_farbe, kachel, border_radius=7)
                pygame.draw.rect(
                    FENSTER,
                    kachel_rand,
                    kachel,
                    width=1,
                    border_radius=7
                )

                # Die Vorschau nutzt dieselbe Funktion wie der grosse Cookie.
                vorschau = pygame.Surface((56, 56), pygame.SRCALPHA)
                zeichne_cookie_design(vorschau, (28, 28), 22, design, spiel_zeit)
                FENSTER.blit(vorschau, (kachel.left + 3, kachel.top + 4))

                name_text = kachel_schrift.render(
                    design["name"],
                    True,
                    kachel_textfarbe
                )
                FENSTER.blit(name_text, (kachel.left + 62, kachel.top + 6))

                status_feld = pygame.Rect(
                    kachel.left + 62,
                    kachel.top + 34,
                    kachel.width - 68,
                    22
                )

                if design["name"] not in COOKIE_DESIGNS_OWNED:
                    status_text = kachel_schrift.render(
                        "LOCKED", True, (120, 112, 101)
                    )
                    pygame.draw.rect(
                        FENSTER,
                        (205, 199, 188),
                        status_feld,
                        border_radius=5
                    )
                elif design["name"] == selected_cookie_design:
                    status_text = kachel_schrift.render(
                        "EQUIPPED", True, TEXTFARBE
                    )
                    pygame.draw.rect(
                        FENSTER,
                        (225, 190, 125),
                        status_feld,
                        border_radius=5
                    )
                else:
                    status_text = kachel_schrift.render(
                        "SELECT", True, TEXTFARBE
                    )
                    pygame.draw.rect(
                        FENSTER,
                        (225, 190, 125),
                        status_feld,
                        border_radius=5
                    )
                    cookie_design_select_felder.append(
                        (status_feld, design["name"])
                    )

                FENSTER.blit(
                    status_text,
                    status_text.get_rect(center=status_feld.center)
                )

            FENSTER.set_clip(vorheriger_clip)

            pygame.draw.rect(FENSTER, (238, 216, 180), zurueck_feld, border_radius=12)
            pygame.draw.rect(FENSTER, (188, 116, 50), zurueck_feld, width=2, border_radius=12)
            text = kleine_schrift.render("Back", True, TEXTFARBE)
            FENSTER.blit(text, text.get_rect(center=zurueck_feld.center))

    # Level nur anzeigen, wenn das Inventar offen und ein Symbol getroffen ist.
    if spiel_status == "game" and inventar_offen:
        maus_position = pygame.mouse.get_pos()
        upgrade_hover = inventar_upgrade_unter_maus(maus_position)

        if upgrade_hover is not None:
            if hintergrund_modus == "purple":
                tooltip_hintergrund = (25, 20, 39)
                tooltip_rand = (142, 111, 190)
                tooltip_textfarbe = (248, 235, 255)
            else:
                tooltip_hintergrund = (255, 250, 240)
                tooltip_rand = (188, 116, 50)
                tooltip_textfarbe = TEXTFARBE

            tooltip_text = kleine_schrift.render(
                f"{upgrade_hover['name']} - Level {upgrade_hover['level']}",
                True,
                tooltip_textfarbe
            )

            tooltip_feld = pygame.Rect(
                maus_position[0] + 16,
                maus_position[1] + 16,
                tooltip_text.get_width() + 20,
                tooltip_text.get_height() + 12
            )
            tooltip_feld.clamp_ip(FENSTER.get_rect())

            pygame.draw.rect(
                FENSTER,
                tooltip_hintergrund,
                tooltip_feld,
                border_radius=8
            )
            pygame.draw.rect(
                FENSTER,
                tooltip_rand,
                tooltip_feld,
                width=2,
                border_radius=8
            )
            FENSTER.blit(
                tooltip_text,
                (tooltip_feld.left + 10, tooltip_feld.top + 6)
            )

    if spiel_status == "wheel":
        zeichne_spinning_wheel()

    # Jeden Frame anzeigen, auch wenn die Maus kein Upgrade-Symbol beruehrt.
    pygame.display.flip()

pygame.quit()




