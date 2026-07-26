"""
generate_pyrightconfig.py

src/components, src/simulations配下で、直接.pyファイルを持つディレクトリを
自動で探し出し、pyrightconfig.jsonのextraPathsとして書き出す。
あわせて、.devcontainer/devcontainer.json内のpython.analysis.extraPaths
(VSCode + Dev Containers利用者向け)も同じ内容で更新する。

各スクリプトはsys.path.append()で実行時にモジュール検索パスを追加しているが、
pyright/Pylance(静的解析)はそれを読み取れないため、同等の情報を別途与える。
新しいモジュール(ディレクトリ)を追加したときは、このスクリプトを再実行するだけで
両方の設定が最新の状態に更新される。

Author: Shisato Yano
"""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
TARGET_DIRS = ["src/components", "src/simulations"]
PYRIGHTCONFIG_PATH = PROJECT_ROOT / "pyrightconfig.json"
DEVCONTAINER_PATH = PROJECT_ROOT / ".devcontainer" / "devcontainer.json"
# devcontainer.json側はコンテナ内のパス(workspaceFolder)を基準にする
CONTAINER_WORKSPACE = "/home/dev-user/workspace"


def find_extra_paths():
    extra_paths = []
    for target in TARGET_DIRS:
        base = PROJECT_ROOT / target
        for path in sorted(base.rglob("*")):
            if not path.is_dir():
                continue
            if any(p.suffix == ".py" for p in path.glob("*.py")):
                extra_paths.append(str(path.relative_to(PROJECT_ROOT)))
    return sorted(extra_paths)


def update_pyrightconfig(extra_paths):
    with open(PYRIGHTCONFIG_PATH, "w") as f:
        json.dump({"extraPaths": extra_paths}, f, indent=2)
        f.write("\n")
    print(f"{len(extra_paths)}件のパスを{PYRIGHTCONFIG_PATH}に書き出しました")


def update_devcontainer(extra_paths):
    with open(DEVCONTAINER_PATH) as f:
        config = json.load(f)

    container_paths = [f"{CONTAINER_WORKSPACE}/{p}" for p in extra_paths]
    config["customizations"]["vscode"]["settings"]["python.analysis.extraPaths"] = container_paths

    with open(DEVCONTAINER_PATH, "w") as f:
        json.dump(config, f, indent=4)
        f.write("\n")
    print(f"{len(container_paths)}件のパスを{DEVCONTAINER_PATH}に書き出しました")


def main():
    extra_paths = find_extra_paths()
    update_pyrightconfig(extra_paths)
    update_devcontainer(extra_paths)


if __name__ == "__main__":
    main()
