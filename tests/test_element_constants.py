# tests/test_element_constants.py
"""
元素・同位体・物理定数テーブルプラグイン(Graphica P-805)のテスト。

データ検索(data.py)は本体に依存しないので直接テストする。register() の配線は
FakeGraphicaPluginAPI で、本番と同じ読み込み経路は load_plugin_like_graphica で確かめる
(どちらも graphica.plugin.testing。本体が入っていなければ skip)。
"""
import os
import sys

import pytest

# リポジトリルート(element_constants/ の親)を import パスに載せる。
# 本番では PluginManager が graphica_plugin_element_constants という動的
# モジュール名で読み込むため、この sys.path 追加はテスト専用の便宜。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from element_constants.data import (  # noqa: E402
    COMMON_CONSTANT_KEYWORDS, ELEMENTS_BY_NUMBER, all_elements, all_isotopes, common_constants,
    find_constant, find_element, find_isotope, isotope_abundance, isotope_mass, isotopes_of,
)
from element_constants.isotopes import ISOTOPE_ROWS  # noqa: E402
from conftest import requires_graphica, GRAPHICA_AVAILABLE  # noqa: E402

if GRAPHICA_AVAILABLE:
    from graphica.plugin.testing import (
        FakeGraphicaPluginAPI, FakePluginContext, install_zip_like_graphica, load_plugin_like_graphica,
    )


# --- 元素 ---

FE = (26, "Fe", "Iron", "鉄", 55.845)


def test_find_element_by_symbol_case_insensitive():
    assert find_element("Fe") == [FE]
    assert find_element("fe") == [FE]
    assert find_element("FE") == [FE]


def test_find_element_by_atomic_number():
    assert find_element("1") == [(1, "H", "Hydrogen", "水素", 1.008)]
    assert find_element("118") == [(118, "Og", "Oganesson", "オガネソン", 294)]


def test_find_element_by_name_exact():
    assert find_element("Iron") == [FE]
    assert find_element("iron") == [FE]


def test_find_element_by_japanese_name():
    assert find_element("鉄") == [FE]
    assert [row[1] for row in find_element("ニホニウム")] == ["Nh"]


def test_find_element_japanese_partial_match():
    symbols = [row[1] for row in find_element("ケイ")]
    assert symbols == ["Si"]


def test_find_element_by_name_partial_match_returns_multiple():
    results = find_element("hy")
    symbols = [row[1] for row in results]
    assert "H" in symbols  # Hydrogen


def test_find_element_no_match_returns_empty_list():
    assert find_element("xx") == []
    assert find_element("999") == []


def test_find_element_empty_query_returns_empty_list():
    assert find_element("") == []
    assert find_element("   ") == []


def test_all_118_elements_present_and_unique():
    assert len(ELEMENTS_BY_NUMBER) == 118
    assert set(ELEMENTS_BY_NUMBER.keys()) == set(range(1, 119))
    assert len({row[1] for row in all_elements()}) == 118
    assert len({row[3] for row in all_elements()}) == 118


# --- 同位体 ---

def test_every_element_has_isotopes():
    assert {row[0] for row in ISOTOPE_ROWS} == set(range(1, 119))


def test_isotope_mass_rounds_to_its_mass_number():
    for row in all_isotopes():
        assert round(isotope_mass(row)) == row[2], row


def test_natural_abundances_sum_to_one():
    for z in range(1, 119):
        abundances = [isotope_abundance(r) for r in isotopes_of(z)]
        natural = [a for a in abundances if a is not None]
        if natural:
            assert None not in abundances, z
            assert sum(natural) == pytest.approx(1.0, abs=2e-3), z


def test_abundance_weighted_mass_matches_atomic_weight():
    """同位体データと原子量の表を突き合わせ、どちらかの転記ミスを捕まえる。
    Se と Pb は IUPAC が原子量だけを改訂したため、NIST の代表組成とは 0.01 以上ずれる。"""
    for z in range(1, 119):
        rows = isotopes_of(z)
        if isotope_abundance(rows[0]) is None:
            continue
        weighted = sum(isotope_mass(r) * isotope_abundance(r) for r in rows)
        assert weighted == pytest.approx(ELEMENTS_BY_NUMBER[z][4], abs=0.02), ELEMENTS_BY_NUMBER[z]


def test_elements_without_natural_isotopes_list_long_lived_ones():
    assert [row[0] for row in find_isotope("Tc")] == ["Tc-97", "Tc-98", "Tc-99"]
    assert all(row[4] == "—" for row in find_isotope("Tc"))


def test_find_isotope_by_element_lists_all_isotopes():
    assert [row[0] for row in find_isotope("Fe")] == ["Fe-54", "Fe-56", "Fe-57", "Fe-58"]
    assert find_isotope("鉄") == find_isotope("26") == find_isotope("iron")


@pytest.mark.parametrize("query", ["Fe-56", "Fe56", "56Fe", "56-Fe", "fe 56", "鉄56", "Iron-56"])
def test_find_isotope_by_nuclide_notation(query):
    assert find_isotope(query) == [("Fe-56", "Fe", 56, "55.93493633(49)", "0.91754(36)")]


def test_find_isotope_unknown_nuclide_returns_empty_list():
    assert find_isotope("Fe-99") == []
    assert find_isotope("Xx-1") == []
    assert find_isotope("") == []


# --- 物理定数 ---

def test_find_constant_common_keyword_speed_of_light():
    results = find_constant("光速")
    assert len(results) == 1
    name, value, unit, uncertainty = results[0]
    assert value == pytest.approx(299792458.0)
    assert unit == "m s^-1"


def test_find_constant_common_keyword_planck():
    results = find_constant("プランク定数")
    assert results[0][0] == "Planck constant"
    assert results[0][1] == pytest.approx(6.62607015e-34, rel=1e-6)


def test_find_constant_japanese_partial_match():
    names = [r[0] for r in find_constant("ボーア")]
    assert names[:2] == ["Bohr radius", "Bohr magneton"]


def test_find_constant_generic_substring_search():
    results = find_constant("electron mass")
    names = [r[0] for r in results]
    assert "electron mass" in names
    assert len(names) == len(set(names))


def test_common_constants_exist_in_scipy():
    import scipy.constants
    for name in COMMON_CONSTANT_KEYWORDS.values():
        assert name in scipy.constants.physical_constants, name
    assert len(common_constants()) == len(COMMON_CONSTANT_KEYWORDS)


def test_find_constant_no_match_returns_empty_list():
    assert find_constant("this-does-not-exist-anywhere") == []


def test_find_constant_empty_query_returns_empty_list():
    assert find_constant("") == []


# --- パネル ---

@pytest.fixture
def panel(qapp):
    pytest.importorskip("PySide6")
    from element_constants.panel import ElementConstantsPanel
    widget = ElementConstantsPanel()
    yield widget
    widget.deleteLater()


def _column(table, col):
    return [table.item(r, col).text() for r in range(table.rowCount())]


def test_panel_shows_everything_for_an_empty_query(panel):
    assert panel.result_table.rowCount() == 118
    panel.mode_combo.setCurrentText("同位体")
    assert panel.result_table.rowCount() == len(ISOTOPE_ROWS)
    panel.mode_combo.setCurrentText("物理定数")
    assert panel.result_table.rowCount() == len(COMMON_CONSTANT_KEYWORDS)
    assert panel.result_table.item(0, 0).text() == "光速(speed of light in vacuum)"


def test_panel_search_and_no_match(panel):
    panel.search_edit.setText("鉄")
    assert _column(panel.result_table, 1) == ["Fe"]
    panel.search_edit.setText("zzz")
    assert panel.result_table.rowCount() == 0
    assert panel.status_label.text() == "該当なし"


def test_panel_double_click_on_element_shows_its_isotopes(panel):
    panel.search_edit.setText("Cu")
    panel.result_table.cellDoubleClicked.emit(0, 0)
    assert panel.mode_combo.currentText() == "同位体"
    assert _column(panel.result_table, 0) == ["Cu-63", "Cu-65"]


def test_panel_copies_selected_cells_as_tab_separated_text(panel):
    from PySide6.QtGui import QGuiApplication
    panel.search_edit.setText("Fe")
    panel.result_table.selectRow(0)
    panel.result_table.copy_selection()
    assert QGuiApplication.clipboard().text() == "26	Fe	Iron	鉄	55.845"


def test_panel_keeps_full_precision_of_constants(panel):
    panel.mode_combo.setCurrentText("物理定数")
    panel.search_edit.setText("電子質量")
    import scipy.constants
    assert float(panel.result_table.item(0, 1).text()) == scipy.constants.m_e


# --- register()の配線 (FakeGraphicaPluginAPI経由) ---

@requires_graphica
def test_register_adds_exactly_one_panel():
    import element_constants as plugin

    api = FakeGraphicaPluginAPI()
    plugin.register(api)

    assert len(api.panels) == 1
    assert "元素・物理定数テーブル" in api.panels
    assert api.panels["元素・物理定数テーブル"]["area"] == "right"


@requires_graphica
def test_registered_widget_factory_returns_a_qwidget(qapp):
    import element_constants as plugin
    from PySide6.QtWidgets import QWidget

    api = FakeGraphicaPluginAPI()
    plugin.register(api)

    widget_factory = api.panels["元素・物理定数テーブル"]["widget_factory"]
    widget = widget_factory(FakePluginContext())
    assert isinstance(widget, QWidget)


# --- 本番と同じ読み込み経路のスモークテスト ---

@requires_graphica
def test_plugin_loads_like_graphica(qapp, tmp_path):
    """api_version の誤りや相対 import の失敗など、本番の読み込み経路でしか出ない不具合を捕まえる。"""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api, record = load_plugin_like_graphica(os.path.join(repo_root, "element_constants"), work_dir=str(tmp_path))

    assert record["error"] is None
    assert any(panel.name == "元素・物理定数テーブル" for panel in api.get_panels())


# --- 配布用zipの往復 ---

@requires_graphica
def test_built_zip_installs_through_the_real_installer(tmp_path):
    """scripts/build_zip.py が作るzipが、本体のインストーラで実際に入ること。
    これが通らなければ配布物として意味がない。"""
    sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    import build_zip

    zip_path = build_zip.build_plugin_zip("element_constants", out_dir=str(tmp_path / "out"))

    install_target = tmp_path / "installed"
    install_target.mkdir()
    installed_name = install_zip_like_graphica(zip_path, str(install_target))

    assert installed_name == "element_constants"
    assert (install_target / "element_constants" / "data.py").exists()
    assert (install_target / "element_constants" / "plugin.json").exists()
