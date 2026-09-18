# tests/test_element_constants.py
"""
元素・物理定数テーブルプラグイン(Graphica バックログ P-805)のテスト。

データ検索(data.py)は本体にも GUI にも依存しないので直接テストする。register() の配線は
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
    find_element, find_constant, ELEMENTS_BY_NUMBER,
)
from conftest import requires_graphica, GRAPHICA_AVAILABLE  # noqa: E402

if GRAPHICA_AVAILABLE:
    from graphica.plugin.testing import (
        FakeGraphicaPluginAPI, FakePluginContext, install_zip_like_graphica, load_plugin_like_graphica,
    )


# --- data.py: find_element ---

def test_find_element_by_symbol_case_insensitive():
    assert find_element("Fe") == [(26, "Fe", "Iron", 55.845)]
    assert find_element("fe") == [(26, "Fe", "Iron", 55.845)]
    assert find_element("FE") == [(26, "Fe", "Iron", 55.845)]


def test_find_element_by_atomic_number():
    assert find_element("1") == [(1, "H", "Hydrogen", 1.008)]
    assert find_element("118") == [(118, "Og", "Oganesson", 294)]


def test_find_element_by_name_exact():
    assert find_element("Iron") == [(26, "Fe", "Iron", 55.845)]
    assert find_element("iron") == [(26, "Fe", "Iron", 55.845)]


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


# --- data.py: find_constant ---

def test_find_constant_common_keyword_speed_of_light():
    results = find_constant("光速")
    assert len(results) == 1
    name, value, unit, uncertainty = results[0]
    assert value == pytest.approx(299792458.0)
    assert unit == "m s^-1"


def test_find_constant_common_keyword_planck():
    results = find_constant("プランク定数")
    assert len(results) == 1
    name, value, unit, uncertainty = results[0]
    assert value == pytest.approx(6.62607015e-34, rel=1e-6)


def test_find_constant_generic_substring_search():
    results = find_constant("electron mass")
    names = [r[0] for r in results]
    assert "electron mass" in names


def test_find_constant_no_match_returns_empty_list():
    assert find_constant("this-does-not-exist-anywhere") == []


def test_find_constant_empty_query_returns_empty_list():
    assert find_constant("") == []


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
