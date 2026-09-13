# tests/conftest.py
"""
テスト共通のフィクスチャ。

Graphica本体(core.plugin_api / core.plugin_testing)は `pip install -e` で
入れておく必要がある。入っていない環境では、本体に依存しない純粋な
データ検索のテストだけが走り、配線・読み込みのテストは skip される
(README の「開発環境の準備」参照)。
"""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

try:
    from PySide6.QtWidgets import QApplication
except ImportError:  # pragma: no cover - PySide6が無い環境
    QApplication = None

# Graphica本体が入っているか。テスト側は graphica_available で分岐する。
try:
    import core.plugin_api  # noqa: F401
    import core.plugin_testing  # noqa: F401
    GRAPHICA_AVAILABLE = True
except ImportError:
    GRAPHICA_AVAILABLE = False


requires_graphica = pytest.mark.skipif(
    not GRAPHICA_AVAILABLE,
    reason="Graphica本体が未インストールです(pip install -e <Graphica_project>)",
)


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """
    Graphica本体と同じく、セッション全体で1つだけQApplicationを用意する
    (パネルのQWidgetを生成するテストに必要)。
    """
    if QApplication is None:
        yield None
        return
    app = QApplication.instance() or QApplication([])
    yield app
