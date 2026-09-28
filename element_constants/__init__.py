"""元素・同位体・物理定数テーブル(Graphica プラグイン、P-805)。

選択中のデータセットを使わない参照ツールなので、analyzer ではなく常設パネルにしている。
"""
from .panel import ElementConstantsPanel

PANEL_NAME = "元素・物理定数テーブル"


def _create_panel(ctx):
    return ElementConstantsPanel()


def register(api):
    api.register_panel(PANEL_NAME, _create_panel, area="right")
