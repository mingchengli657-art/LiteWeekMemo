#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiteWeek Memo 一键稳定打包脚本 (专为 Conda + PySide6 环境优化)
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    base_dir = Path(__file__).parent.resolve()
    main_script = base_dir / "lite_week_memo.py"
    icon_path = base_dir / "app_icon.ico"

    # 1. 生成高清 app_icon.ico
    print("[1/3] 正在生成高清矢量图标 app_icon.ico ...")
    from lite_week_memo import QApplication, VectorIcons, QT_LIB
    _app = QApplication.instance() or QApplication([])
    VectorIcons.save_ico_file(icon_path)
    print(f"      当前生效的 GUI 引擎为: {QT_LIB}")

    # 2. 只排除未使用的另外两个 Qt 绑定库与数据科学大包（绝不误删 PySide6 内部必需的 DLL！）
    all_qt_bindings = ["PySide6", "PyQt6", "PyQt5"]
    unused_qt_bindings = [b for b in all_qt_bindings if b != QT_LIB]

    exclude_modules = unused_qt_bindings + [
        "PyQt5.sip", "PyQt6.sip",
        "matplotlib", "numpy", "scipy", "pandas", "PIL", "tkinter",
        "unittest", "pydoc", "sqlite3", "zmq", "IPython", "notebook",
        # 仅排除体积巨大且完全无关的 Chromium 浏览器内核与 3D/多媒体模块
        f"{QT_LIB}.QtWebEngineCore",
        f"{QT_LIB}.QtWebEngineWidgets",
        f"{QT_LIB}.Qt3DCore",
        f"{QT_LIB}.QtMultimedia",
    ]

    # 针对 Anaconda 环境：确保 Conda 的 Library/bin 在 PATH 中，防止打包后找不到基础 DLL
    conda_prefix = Path(sys.executable).parent
    conda_bin = conda_prefix / "Library" / "bin"
    env = os.environ.copy()
    if conda_bin.exists():
        env["PATH"] = f"{conda_bin}{os.pathsep}{env.get('PATH', '')}"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",                   # 无黑框控制台
        "--onefile",                    # 打包为单个独立的 .exe 文件
        "--name", "轻周备忘_LiteWeekMemo",
        f"--icon={icon_path}",
    ]

    if conda_bin.exists():
        cmd.extend(["--paths", str(conda_bin)])

    for mod in exclude_modules:
        cmd.extend(["--exclude-module", mod.strip()])

    cmd.append(str(main_script))

    print(f"[2/3] 开始调用 PyInstaller 打包 (已保留完整 QtGui/Svg 渲染链)...")
    res = subprocess.run(cmd, cwd=str(base_dir), env=env)
    if res.returncode == 0:
        dist_exe = base_dir / "dist" / "轻周备忘_LiteWeekMemo.exe"
        size_mb = dist_exe.stat().st_size / (1024 * 1024) if dist_exe.exists() else 0
        print("\n" + "=" * 65)
        print(f"[3/3] 🎉 打包成功！文件大小: {size_mb:.1f} MB")
        print(f"👉 独立可执行文件位于: {dist_exe}")
        print("=" * 65)
    else:
        print("\n❌ 打包失败，请检查上方错误日志。")


if __name__ == "__main__":
    main()