"""元素・同位体・物理定数のデータと検索。GUI にも Graphica 本体にも依存しない。

プラグイン同士は import できないので、他のプラグインで使うときはこのファイルと
isotopes.py をコピーして同梱する。
"""
import re

import scipy.constants as _scipy_constants

from .isotopes import ISOTOPE_ROWS

# (原子番号, 元素記号, 英語名, 日本語名, 原子量)。原子量は IUPAC 標準原子量(2021)の略値で、
# 安定同位体を持たない元素は最も安定な同位体の質量数。
# mendeleev などの周期表パッケージは Graphica の配布版に入っていないので自前で持つ。
_ELEMENT_ROWS = [
    (1, "H", "Hydrogen", "水素", 1.008),
    (2, "He", "Helium", "ヘリウム", 4.0026),
    (3, "Li", "Lithium", "リチウム", 6.94),
    (4, "Be", "Beryllium", "ベリリウム", 9.0122),
    (5, "B", "Boron", "ホウ素", 10.81),
    (6, "C", "Carbon", "炭素", 12.011),
    (7, "N", "Nitrogen", "窒素", 14.007),
    (8, "O", "Oxygen", "酸素", 15.999),
    (9, "F", "Fluorine", "フッ素", 18.998),
    (10, "Ne", "Neon", "ネオン", 20.180),
    (11, "Na", "Sodium", "ナトリウム", 22.990),
    (12, "Mg", "Magnesium", "マグネシウム", 24.305),
    (13, "Al", "Aluminium", "アルミニウム", 26.982),
    (14, "Si", "Silicon", "ケイ素", 28.085),
    (15, "P", "Phosphorus", "リン", 30.974),
    (16, "S", "Sulfur", "硫黄", 32.06),
    (17, "Cl", "Chlorine", "塩素", 35.45),
    (18, "Ar", "Argon", "アルゴン", 39.948),
    (19, "K", "Potassium", "カリウム", 39.098),
    (20, "Ca", "Calcium", "カルシウム", 40.078),
    (21, "Sc", "Scandium", "スカンジウム", 44.956),
    (22, "Ti", "Titanium", "チタン", 47.867),
    (23, "V", "Vanadium", "バナジウム", 50.942),
    (24, "Cr", "Chromium", "クロム", 51.996),
    (25, "Mn", "Manganese", "マンガン", 54.938),
    (26, "Fe", "Iron", "鉄", 55.845),
    (27, "Co", "Cobalt", "コバルト", 58.933),
    (28, "Ni", "Nickel", "ニッケル", 58.693),
    (29, "Cu", "Copper", "銅", 63.546),
    (30, "Zn", "Zinc", "亜鉛", 65.38),
    (31, "Ga", "Gallium", "ガリウム", 69.723),
    (32, "Ge", "Germanium", "ゲルマニウム", 72.630),
    (33, "As", "Arsenic", "ヒ素", 74.922),
    (34, "Se", "Selenium", "セレン", 78.971),
    (35, "Br", "Bromine", "臭素", 79.904),
    (36, "Kr", "Krypton", "クリプトン", 83.798),
    (37, "Rb", "Rubidium", "ルビジウム", 85.468),
    (38, "Sr", "Strontium", "ストロンチウム", 87.62),
    (39, "Y", "Yttrium", "イットリウム", 88.906),
    (40, "Zr", "Zirconium", "ジルコニウム", 91.224),
    (41, "Nb", "Niobium", "ニオブ", 92.906),
    (42, "Mo", "Molybdenum", "モリブデン", 95.95),
    (43, "Tc", "Technetium", "テクネチウム", 98),
    (44, "Ru", "Ruthenium", "ルテニウム", 101.07),
    (45, "Rh", "Rhodium", "ロジウム", 102.91),
    (46, "Pd", "Palladium", "パラジウム", 106.42),
    (47, "Ag", "Silver", "銀", 107.87),
    (48, "Cd", "Cadmium", "カドミウム", 112.41),
    (49, "In", "Indium", "インジウム", 114.82),
    (50, "Sn", "Tin", "スズ", 118.71),
    (51, "Sb", "Antimony", "アンチモン", 121.76),
    (52, "Te", "Tellurium", "テルル", 127.60),
    (53, "I", "Iodine", "ヨウ素", 126.90),
    (54, "Xe", "Xenon", "キセノン", 131.29),
    (55, "Cs", "Caesium", "セシウム", 132.91),
    (56, "Ba", "Barium", "バリウム", 137.33),
    (57, "La", "Lanthanum", "ランタン", 138.91),
    (58, "Ce", "Cerium", "セリウム", 140.12),
    (59, "Pr", "Praseodymium", "プラセオジム", 140.91),
    (60, "Nd", "Neodymium", "ネオジム", 144.24),
    (61, "Pm", "Promethium", "プロメチウム", 145),
    (62, "Sm", "Samarium", "サマリウム", 150.36),
    (63, "Eu", "Europium", "ユウロピウム", 151.96),
    (64, "Gd", "Gadolinium", "ガドリニウム", 157.25),
    (65, "Tb", "Terbium", "テルビウム", 158.93),
    (66, "Dy", "Dysprosium", "ジスプロシウム", 162.50),
    (67, "Ho", "Holmium", "ホルミウム", 164.93),
    (68, "Er", "Erbium", "エルビウム", 167.26),
    (69, "Tm", "Thulium", "ツリウム", 168.93),
    (70, "Yb", "Ytterbium", "イッテルビウム", 173.05),
    (71, "Lu", "Lutetium", "ルテチウム", 174.97),
    (72, "Hf", "Hafnium", "ハフニウム", 178.49),
    (73, "Ta", "Tantalum", "タンタル", 180.95),
    (74, "W", "Tungsten", "タングステン", 183.84),
    (75, "Re", "Rhenium", "レニウム", 186.21),
    (76, "Os", "Osmium", "オスミウム", 190.23),
    (77, "Ir", "Iridium", "イリジウム", 192.22),
    (78, "Pt", "Platinum", "白金", 195.08),
    (79, "Au", "Gold", "金", 196.97),
    (80, "Hg", "Mercury", "水銀", 200.59),
    (81, "Tl", "Thallium", "タリウム", 204.38),
    (82, "Pb", "Lead", "鉛", 207.2),
    (83, "Bi", "Bismuth", "ビスマス", 208.98),
    (84, "Po", "Polonium", "ポロニウム", 209),
    (85, "At", "Astatine", "アスタチン", 210),
    (86, "Rn", "Radon", "ラドン", 222),
    (87, "Fr", "Francium", "フランシウム", 223),
    (88, "Ra", "Radium", "ラジウム", 226),
    (89, "Ac", "Actinium", "アクチニウム", 227),
    (90, "Th", "Thorium", "トリウム", 232.04),
    (91, "Pa", "Protactinium", "プロトアクチニウム", 231.04),
    (92, "U", "Uranium", "ウラン", 238.03),
    (93, "Np", "Neptunium", "ネプツニウム", 237),
    (94, "Pu", "Plutonium", "プルトニウム", 244),
    (95, "Am", "Americium", "アメリシウム", 243),
    (96, "Cm", "Curium", "キュリウム", 247),
    (97, "Bk", "Berkelium", "バークリウム", 247),
    (98, "Cf", "Californium", "カリホルニウム", 251),
    (99, "Es", "Einsteinium", "アインスタイニウム", 252),
    (100, "Fm", "Fermium", "フェルミウム", 257),
    (101, "Md", "Mendelevium", "メンデレビウム", 258),
    (102, "No", "Nobelium", "ノーベリウム", 259),
    (103, "Lr", "Lawrencium", "ローレンシウム", 266),
    (104, "Rf", "Rutherfordium", "ラザホージウム", 267),
    (105, "Db", "Dubnium", "ドブニウム", 268),
    (106, "Sg", "Seaborgium", "シーボーギウム", 269),
    (107, "Bh", "Bohrium", "ボーリウム", 270),
    (108, "Hs", "Hassium", "ハッシウム", 269),
    (109, "Mt", "Meitnerium", "マイトネリウム", 278),
    (110, "Ds", "Darmstadtium", "ダームスタチウム", 281),
    (111, "Rg", "Roentgenium", "レントゲニウム", 282),
    (112, "Cn", "Copernicium", "コペルニシウム", 285),
    (113, "Nh", "Nihonium", "ニホニウム", 286),
    (114, "Fl", "Flerovium", "フレロビウム", 289),
    (115, "Mc", "Moscovium", "モスコビウム", 290),
    (116, "Lv", "Livermorium", "リバモリウム", 293),
    (117, "Ts", "Tennessine", "テネシン", 294),
    (118, "Og", "Oganesson", "オガネソン", 294),
]

ELEMENTS_BY_NUMBER = {row[0]: row for row in _ELEMENT_ROWS}
ELEMENTS_BY_SYMBOL = {row[1].lower(): row for row in _ELEMENT_ROWS}
ELEMENTS_BY_NAME = {row[2].lower(): row for row in _ELEMENT_ROWS}
ELEMENTS_BY_JAPANESE_NAME = {row[3]: row for row in _ELEMENT_ROWS}

ELEMENT_COLUMNS = ["原子番号", "元素記号", "英語名", "日本語名", "原子量"]


def all_elements():
    return list(_ELEMENT_ROWS)


def find_element(query):
    """元素記号・原子番号・英語名・日本語名で探す。完全一致が無ければ英語名・日本語名の部分一致。"""
    query = query.strip()
    if not query:
        return []

    if query.isdigit():
        row = ELEMENTS_BY_NUMBER.get(int(query))
        return [row] if row else []

    lowered = query.lower()
    exact = (ELEMENTS_BY_SYMBOL.get(lowered) or ELEMENTS_BY_NAME.get(lowered)
             or ELEMENTS_BY_JAPANESE_NAME.get(query))
    if exact:
        return [exact]

    return [row for row in _ELEMENT_ROWS if lowered in row[2].lower() or query in row[3]]


# --- 同位体 ---

ISOTOPE_COLUMNS = ["核種", "元素", "質量数", "相対原子質量", "天然存在比"]

# 「Fe-56」「Fe56」「56Fe」「鉄56」「C 13」のような核種の書き方
_NUCLIDE_ELEMENT_FIRST = re.compile(r"^(\D+?)[\s\-]*(\d+)$")
_NUCLIDE_MASS_FIRST = re.compile(r"^(\d+)[\s\-]*(\D+)$")


def _isotope_row(z, a, mass, abundance):
    symbol = ELEMENTS_BY_NUMBER[z][1]
    return (f"{symbol}-{a}", symbol, a, mass, abundance if abundance is not None else "—")


def _nist_value(text):
    """NIST 表記(例: '55.93493633(49)'、'294.21392(71#)')の数値部分。"""
    return float(re.match(r"[\d.]+", text).group(0))


def isotope_mass(row):
    return _nist_value(row[3])


def isotope_abundance(row):
    """天然存在比(0〜1)。天然に存在しない核種は None。"""
    return None if row[4] == "—" else _nist_value(row[4])


def isotopes_of(atomic_number):
    """その元素の同位体。天然に存在する核種がある元素はそれだけ、無い元素は代表的な長寿命核種。"""
    return [_isotope_row(*r) for r in ISOTOPE_ROWS if r[0] == atomic_number]


def all_isotopes():
    return [_isotope_row(*r) for r in ISOTOPE_ROWS]


def _single_element(text):
    found = find_element(text)
    return found[0] if len(found) == 1 else None


def find_isotope(query):
    """核種(Fe-56、56Fe、鉄56)ならその1件、元素(Fe、26、Iron、鉄)ならその元素の同位体すべて。"""
    query = query.strip()
    if not query:
        return []

    for pattern, element_group, mass_group in ((_NUCLIDE_ELEMENT_FIRST, 1, 2),
                                               (_NUCLIDE_MASS_FIRST, 2, 1)):
        m = pattern.match(query)
        if m:
            element = _single_element(m.group(element_group))
            if element is None:
                return []
            mass_number = int(m.group(mass_group))
            return [row for row in isotopes_of(element[0]) if row[2] == mass_number]

    return [row for element in find_element(query) for row in isotopes_of(element[0])]


# --- 物理定数(scipy.constants.physical_constants の CODATA 値をそのまま使う) ---

# 日本語の呼び名 → scipy の名称。空の検索語のときの一覧も兼ねる。
COMMON_CONSTANT_KEYWORDS = {
    "光速": "speed of light in vacuum",
    "プランク定数": "Planck constant",
    "換算プランク定数": "reduced Planck constant",
    "電気素量": "elementary charge",
    "アボガドロ定数": "Avogadro constant",
    "ボルツマン定数": "Boltzmann constant",
    "気体定数": "molar gas constant",
    "ファラデー定数": "Faraday constant",
    "万有引力定数": "Newtonian constant of gravitation",
    "標準重力加速度": "standard acceleration of gravity",
    "電子質量": "electron mass",
    "陽子質量": "proton mass",
    "中性子質量": "neutron mass",
    "原子質量定数": "atomic mass constant",
    "真空の誘電率": "vacuum electric permittivity",
    "真空の透磁率": "vacuum mag. permeability",
    "ボーア半径": "Bohr radius",
    "ボーア磁子": "Bohr magneton",
    "リュードベリ定数": "Rydberg constant",
    "微細構造定数": "fine-structure constant",
    "ステファン・ボルツマン定数": "Stefan-Boltzmann constant",
    "電子ボルト": "electron volt",
    "標準大気圧": "standard atmosphere",
}
_JAPANESE_BY_CONSTANT = {v: k for k, v in COMMON_CONSTANT_KEYWORDS.items()}

CONSTANT_COLUMNS = ["名称", "値", "単位", "標準不確かさ"]


def _constant_row(name):
    value, unit, uncertainty = _scipy_constants.physical_constants[name]
    return (name, value, unit, uncertainty)


def japanese_constant_name(name):
    """よく使う定数の日本語の呼び名(無ければ None)。"""
    return _JAPANESE_BY_CONSTANT.get(name)


def common_constants():
    return [_constant_row(name) for name in COMMON_CONSTANT_KEYWORDS.values()]


def find_constant(query):
    """日本語の呼び名(部分一致)と、scipy の名称(大文字小文字を無視した部分一致)で探す。"""
    query = query.strip()
    if not query:
        return []

    names = [name for ja, name in COMMON_CONSTANT_KEYWORDS.items() if query in ja]
    lowered = query.lower()
    names += [name for name in _scipy_constants.physical_constants
              if lowered in name.lower() and name not in names]
    return [_constant_row(name) for name in names]
