#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiteWeek Memo (轻周备忘) v3.2 Pro — Windows 端轻量级桌面悬浮日程备忘本
开发者署名：By：Exusiailmc绿毛虫

v3.2 Pro 全面进化特性：
1. 极光渐变描边外框（Aurora Gradient Border）：内置 QPainter 双层抗锯齿极光渐变边框，在纯白底色软件上依然拥有极佳的立体边界辨识度。
2. 零截断下拉菜单与自定义优先级选择器：
   - 底部优先级按钮直观显示「● 优先级: 中 ▾」，点击弹出「高 / 中 / 低」圆角菜单，彻底根治高分屏文字吞字与遮挡。
   - 顶部排序选择器改用自绘菜单按钮，完美显示「并行顺序 ▾」全称，永不裁切。
3. 深度定制 DDL 日历弹窗画风：去除老式 Windows 网格与灰蓝条，日历面板完全跟随深色/浅色主题。
4. 单实例防多开引擎（Single Instance Lock）：基于 QLocalServer/Socket，重复打开自动唤醒已有窗口，彻底杜绝多开覆写丢数据。
5. 真正的「纯粹极简模式」：一键折叠周次导航、工具栏与底部输入区，仅保留微型顶栏与纯粹的任务列表（支持双击顶栏快速切换）。
"""

from __future__ import annotations

import html
import json
import math
import os
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# ==============================================================================
# Qt 框架顶层导入（兼容 PySide6 / PyQt6 / PyQt5，且对 PyInstaller 静态分析友好）
# ==============================================================================
try:
    import site
    user_site = site.getusersitepackages()
    if user_site and user_site not in sys.path:
        sys.path.append(user_site)
except Exception:
    pass

QT_LIB = None
try:
    from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork
    QT_LIB = "PySide6"
except ImportError:
    try:
        from PyQt6 import QtCore, QtGui, QtWidgets, QtNetwork
        QT_LIB = "PyQt6"
    except ImportError:
        try:
            from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
            QT_LIB = "PyQt5"
        except ImportError:
            print("未检测到 PySide6 / PyQt6 / PyQt5，请先安装：pip install PySide6")
            sys.exit(1)

Qt = QtCore.Qt
QPoint = QtCore.QPoint
QPointF = QtCore.QPointF
QRectF = QtCore.QRectF
QDate = QtCore.QDate
QTimer = QtCore.QTimer
QSize = QtCore.QSize
QUrl = QtCore.QUrl

QColor = QtGui.QColor
QFont = QtGui.QFont
QIcon = QtGui.QIcon
QPixmap = QtGui.QPixmap
QPainter = QtGui.QPainter
QPen = QtGui.QPen
QBrush = QtGui.QBrush
QPainterPath = QtGui.QPainterPath
QLinearGradient = QtGui.QLinearGradient
QDesktopServices = QtGui.QDesktopServices
QAction = getattr(QtGui, "QAction", None) or getattr(QtWidgets, "QAction", None)

QApplication = QtWidgets.QApplication
QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QLabel = QtWidgets.QLabel
QPushButton = QtWidgets.QPushButton
QLineEdit = QtWidgets.QLineEdit
QComboBox = QtWidgets.QComboBox
QCheckBox = QtWidgets.QCheckBox
QDateEdit = QtWidgets.QDateEdit
QCalendarWidget = QtWidgets.QCalendarWidget
QSlider = QtWidgets.QSlider
QScrollArea = QtWidgets.QScrollArea
QFrame = QtWidgets.QFrame
QDialog = QtWidgets.QDialog
QFormLayout = QtWidgets.QFormLayout
QDialogButtonBox = QtWidgets.QDialogButtonBox
QSizeGrip = QtWidgets.QSizeGrip
QSystemTrayIcon = QtWidgets.QSystemTrayIcon
QMenu = QtWidgets.QMenu
QWidgetAction = QtWidgets.QWidgetAction

QLocalServer = QtNetwork.QLocalServer
QLocalSocket = QtNetwork.QLocalSocket

IS_QT6 = QT_LIB in ("PySide6", "PyQt6")
AlignTop = Qt.AlignmentFlag.AlignTop if IS_QT6 else Qt.AlignTop
AlignCenter = Qt.AlignmentFlag.AlignCenter if IS_QT6 else Qt.AlignCenter
AlignVCenter = Qt.AlignmentFlag.AlignVCenter if IS_QT6 else Qt.AlignVCenter
AlignBottom = Qt.AlignmentFlag.AlignBottom if IS_QT6 else Qt.AlignBottom
AlignRight = Qt.AlignmentFlag.AlignRight if IS_QT6 else Qt.AlignRight
PointingHand = Qt.CursorShape.PointingHandCursor if IS_QT6 else Qt.PointingHandCursor
LeftButton = Qt.MouseButton.LeftButton if IS_QT6 else Qt.LeftButton
Horizontal = Qt.Orientation.Horizontal if IS_QT6 else Qt.Horizontal
ScrollOff = Qt.ScrollBarPolicy.ScrollBarAlwaysOff if IS_QT6 else Qt.ScrollBarAlwaysOff
FramelessHint = Qt.WindowType.FramelessWindowHint if IS_QT6 else Qt.FramelessWindowHint
WindowFlag = Qt.WindowType.Window if IS_QT6 else Qt.Window
StaysOnTopHint = Qt.WindowType.WindowStaysOnTopHint if IS_QT6 else Qt.WindowStaysOnTopHint
TranslucentBg = Qt.WidgetAttribute.WA_TranslucentBackground if IS_QT6 else Qt.WA_TranslucentBackground
Antialiasing = QPainter.RenderHint.Antialiasing if IS_QT6 else QPainter.Antialiasing
SolidLine = Qt.PenStyle.SolidLine if IS_QT6 else Qt.SolidLine
RoundCap = Qt.PenCapStyle.RoundCap if IS_QT6 else Qt.RoundCap
RoundJoin = Qt.PenJoinStyle.RoundJoin if IS_QT6 else Qt.RoundJoin
NoPen = Qt.PenStyle.NoPen if IS_QT6 else Qt.NoPen
NoBrush = Qt.BrushStyle.NoBrush if IS_QT6 else Qt.NoBrush
BtnSave = QDialogButtonBox.StandardButton.Save if IS_QT6 else QDialogButtonBox.Save
BtnCancel = QDialogButtonBox.StandardButton.Cancel if IS_QT6 else QDialogButtonBox.Cancel
DialogAccepted = QDialog.DialogCode.Accepted if IS_QT6 else QDialog.Accepted


# ==============================================================================
# 第一部分：核心数据模型、周历引擎、Deadline 倒计时与 Markdown 导出引擎
# ==============================================================================

APP_SINGLETON_KEY = "LiteWeekMemo_SingleInstance_Exusiailmc_v3"
APP_AUTORUN_NAME = "LiteWeekMemo"

PRIORITY_HIGH = 3
PRIORITY_MEDIUM = 2
PRIORITY_LOW = 1

PRIORITY_META = {
    PRIORITY_HIGH: {
        "label": "高",
        "short": "高",
        "md": "🔴 高优先级",
        "light_fg": "#DC2626", "light_bg": "#FEF2F2", "light_border": "#FECACA",
        "dark_fg": "#F87171",  "dark_bg": "#3B181E",  "dark_border": "#7F1D1D",
        "bar": "#EF4444",
    },
    PRIORITY_MEDIUM: {
        "label": "中",
        "short": "中",
        "md": "🟡 中优先级",
        "light_fg": "#D97706", "light_bg": "#FFFBEB", "light_border": "#FDE68A",
        "dark_fg": "#FBBF24",  "dark_bg": "#362814",  "dark_border": "#78350F",
        "bar": "#F59E0B",
    },
    PRIORITY_LOW: {
        "label": "低",
        "short": "低",
        "md": "🔵 低优先级",
        "light_fg": "#2563EB", "light_bg": "#EFF6FF", "light_border": "#BFDBFE",
        "dark_fg": "#60A5FA",  "dark_bg": "#172554",  "dark_border": "#1E3A8A",
        "bar": "#3B82F6",
    },
}


@dataclass
class TaskItem:
    id: str
    title: str
    completed: bool = False
    priority: int = PRIORITY_MEDIUM        # 3=高, 2=中, 1=低
    parallel_order: int = 0                # 并行自定义排序序号
    category: str = ""                     # 可选分类标签
    deadline: Optional[str] = None         # 可选截止日期 YYYY-MM-DD
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TaskItem":
        return cls(
            id=str(data.get("id") or uuid.uuid4().hex[:8]),
            title=str(data.get("title", "")).strip(),
            completed=bool(data.get("completed", False)),
            priority=int(data.get("priority", PRIORITY_MEDIUM)),
            parallel_order=int(data.get("parallel_order", 0)),
            category=str(data.get("category", "")).strip(),
            deadline=data.get("deadline") or None,
            created_at=str(data.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            completed_at=data.get("completed_at") or None,
        )


class WeekEngine:
    """自然周时间计算与 Deadline 倒计时状态引擎"""

    WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    @staticmethod
    def get_monday(target_date: Optional[date] = None) -> date:
        d = target_date or date.today()
        return d - timedelta(days=d.weekday())

    @staticmethod
    def get_week_key(monday_date: date) -> str:
        m = WeekEngine.get_monday(monday_date)
        return m.strftime("%Y-%m-%d")

    @staticmethod
    def get_week_range(monday_date: date) -> Tuple[date, date]:
        m = WeekEngine.get_monday(monday_date)
        sunday = m + timedelta(days=6)
        return m, sunday

    @staticmethod
    def format_week_header(monday_date: date, today: Optional[date] = None) -> Tuple[str, str, str]:
        t = today or date.today()
        m, s = WeekEngine.get_week_range(monday_date)
        iso_year, iso_week, _ = m.isocalendar()
        current_monday = WeekEngine.get_monday(t)

        diff_weeks = (m - current_monday).days // 7
        if diff_weeks == 0:
            tag = "本周"
        elif diff_weeks == -1:
            tag = "上周"
        elif diff_weeks == 1:
            tag = "下周"
        elif diff_weeks < 0:
            tag = f"{abs(diff_weeks)}周前"
        else:
            tag = f"{diff_weeks}周后"

        title = f"{iso_year}年 第{iso_week:02d}周 · {tag}"
        short_title = f"第{iso_week:02d}周({tag})"
        if m.year == s.year:
            subtitle = f"{m.strftime('%m.%d')} (周一) — {s.strftime('%m.%d')} (周日)"
        else:
            subtitle = f"{m.strftime('%Y.%m.%d')} — {s.strftime('%Y.%m.%d')}"
        return title, subtitle, short_title

    @staticmethod
    def evaluate_deadline(
        deadline_str: Optional[str],
        completed: bool = False,
        reference_date: Optional[date] = None,
        dark_mode: bool = False,
    ) -> Optional[Dict[str, object]]:
        if not deadline_str:
            return None
        try:
            dl_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        except ValueError:
            return None

        ref = reference_date or date.today()
        days_left = (dl_date - ref).days
        weekday_cn = WeekEngine.WEEKDAY_NAMES[dl_date.weekday()]
        short_date = dl_date.strftime("%m-%d")

        if completed:
            return {
                "text": f"截止 {short_date}",
                "badge_text": f"截止 {short_date}",
                "detail": f"截止日期：{dl_date.strftime('%Y-%m-%d')} ({weekday_cn}) · 已完成",
                "level": "done",
                "fg": "#64748B" if dark_mode else "#94A3B8",
                "bg": "#1E293B" if dark_mode else "#F1F5F9",
                "border": "#334155" if dark_mode else "#E2E8F0",
                "days_left": days_left,
            }

        if days_left < 0:
            overdue_days = abs(days_left)
            return {
                "text": f"逾期 {overdue_days} 天",
                "badge_text": f"逾期 {overdue_days} 天 ({short_date})",
                "detail": f"截止：{short_date} ({weekday_cn}) · 已逾期 {overdue_days} 天",
                "level": "overdue",
                "fg": "#FCA5A5" if dark_mode else "#B91C1C",
                "bg": "#451A1D" if dark_mode else "#FEE2E2",
                "border": "#991B1B" if dark_mode else "#FCA5A5",
                "days_left": days_left,
            }
        elif days_left == 0:
            return {
                "text": "今天截止",
                "badge_text": f"今天截止 ({short_date})",
                "detail": f"截止：{short_date} ({weekday_cn}) · 今天到期！",
                "level": "urgent",
                "fg": "#F87171" if dark_mode else "#DC2626",
                "bg": "#3B181E" if dark_mode else "#FEF2F2",
                "border": "#7F1D1D" if dark_mode else "#F87171",
                "days_left": 0,
            }
        elif days_left <= 3:
            return {
                "text": f"剩 {days_left} 天",
                "badge_text": f"还剩 {days_left} 天 ({short_date})",
                "detail": f"截止：{short_date} ({weekday_cn}) · 距离 Deadline 还有 {days_left} 天",
                "level": "warning",
                "fg": "#FBBF24" if dark_mode else "#D97706",
                "bg": "#362814" if dark_mode else "#FFFBEB",
                "border": "#78350F" if dark_mode else "#FCD34D",
                "days_left": days_left,
            }
        else:
            return {
                "text": f"剩 {days_left} 天",
                "badge_text": f"剩余 {days_left} 天 ({short_date})",
                "detail": f"截止：{short_date} ({weekday_cn}) · 距离 Deadline 还有 {days_left} 天",
                "level": "normal",
                "fg": "#38BDF8" if dark_mode else "#0284C7",
                "bg": "#0F2942" if dark_mode else "#F0F9FF",
                "border": "#0369A1" if dark_mode else "#BAE6FD",
                "days_left": days_left,
            }


class AutoRunManager:
    """Windows 注册表开机自启管理器"""

    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @staticmethod
    def get_launch_command() -> str:
        if getattr(sys, "frozen", False):
            return f'"{sys.executable}"'
        script_path = os.path.abspath(__file__)
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        exe = str(pythonw) if pythonw.exists() else sys.executable
        return f'"{exe}" "{script_path}"'

    @classmethod
    def is_enabled(cls) -> bool:
        if sys.platform != "win32":
            return False
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, APP_AUTORUN_NAME)
                return bool(val)
        except Exception:
            return False

    @classmethod
    def set_enabled(cls, enable: bool) -> bool:
        if sys.platform != "win32":
            return False
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, APP_AUTORUN_NAME, 0, winreg.REG_SZ, cls.get_launch_command())
                else:
                    try:
                        winreg.DeleteValue(key, APP_AUTORUN_NAME)
                    except FileNotFoundError:
                        pass
            return True
        except Exception:
            return False


class TaskDataStore:
    """本地 JSON 自动持久化数据管理与排序、导出引擎"""

    SORT_PARALLEL = "parallel"
    SORT_PRIORITY = "priority"
    SORT_DEADLINE = "deadline"

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            self.storage_path = self._resolve_default_storage_path()
        else:
            self.storage_path = Path(storage_path)

        self.weeks: Dict[str, List[TaskItem]] = {}
        self.settings: Dict[str, object] = {
            "always_on_top": True,
            "opacity": 0.96,
            "sort_mode": self.SORT_PARALLEL,
            "sink_completed": True,
            "compact_mode": False,
            "dark_mode": False,
            "show_index": False,
            "normal_width": 385,
            "normal_height": 540,
            "compact_height": 340,
        }
        self._last_deleted: Optional[Tuple[str, TaskItem]] = None
        self.load()

    @staticmethod
    def _resolve_default_storage_path() -> Path:
        if getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).parent
        else:
            exe_dir = Path(os.path.dirname(os.path.abspath(__file__)))

        portable_file = exe_dir / "schedule_data.json"
        if portable_file.exists():
            return portable_file

        try:
            test_file = exe_dir / ".write_test.tmp"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()
            return portable_file
        except Exception:
            appdata = Path(os.environ.get("APPDATA", str(Path.home()))) / "LiteWeekMemo"
            appdata.mkdir(parents=True, exist_ok=True)
            return appdata / "schedule_data.json"

    @property
    def base_dir(self) -> Path:
        return self.storage_path.parent

    def load(self) -> None:
        if not self.storage_path.exists():
            self._seed_initial_welcome_tasks()
            self.save()
            return

        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
            settings_raw = raw.get("settings", {})
            if isinstance(settings_raw, dict):
                self.settings.update(settings_raw)

            weeks_raw = raw.get("weeks", {})
            self.weeks = {}
            if isinstance(weeks_raw, dict):
                for wk, item_list in weeks_raw.items():
                    if isinstance(item_list, list):
                        self.weeks[wk] = [TaskItem.from_dict(x) for x in item_list]
        except Exception:
            self.weeks = {}
            self._seed_initial_welcome_tasks()

    def _seed_initial_welcome_tasks(self) -> None:
        today = date.today()
        monday = WeekEngine.get_monday(today)
        wk = WeekEngine.get_week_key(monday)
        dl_soon = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        dl_week_end = (monday + timedelta(days=6)).strftime("%Y-%m-%d")

        self.weeks[wk] = [
            TaskItem(
                id=uuid.uuid4().hex[:8],
                title="点击顶栏「极简图标」或双击顶栏，可切换为纯任务列表模式",
                completed=False,
                priority=PRIORITY_HIGH,
                parallel_order=0,
                category="新特性",
                deadline=today.strftime("%Y-%m-%d"),
            ),
            TaskItem(
                id=uuid.uuid4().hex[:8],
                title="点击齿轮按钮可调节窗口透明度、开启开机自启",
                completed=False,
                priority=PRIORITY_MEDIUM,
                parallel_order=1,
                category="指南",
                deadline=dl_soon,
            ),
            TaskItem(
                id=uuid.uuid4().hex[:8],
                title="已内置防多开保护，再次启动会自动唤醒本窗口",
                completed=True,
                priority=PRIORITY_LOW,
                parallel_order=2,
                category="系统",
                deadline=dl_week_end,
                completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        ]

    def save(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "version": "3.2.0",
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "settings": self.settings,
                "weeks": {
                    wk: [t.to_dict() for t in tasks]
                    for wk, tasks in self.weeks.items()
                },
            }
            tmp_path = self.storage_path.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp_path.replace(self.storage_path)
        except Exception as e:
            print(f"[Warn] Save schedule data failed: {e}")

    def get_tasks(
        self,
        monday_date: date,
        sort_mode: Optional[str] = None,
        sink_completed: Optional[bool] = None,
        reference_date: Optional[date] = None,
    ) -> List[TaskItem]:
        wk = WeekEngine.get_week_key(monday_date)
        tasks = list(self.weeks.get(wk, []))
        mode = sort_mode or str(self.settings.get("sort_mode", self.SORT_PARALLEL))
        sink = bool(self.settings.get("sink_completed", True)) if sink_completed is None else sink_completed
        ref = reference_date or date.today()

        def sort_key(item: TaskItem):
            completed_rank = (1 if item.completed else 0) if sink else 0
            dl_info = WeekEngine.evaluate_deadline(item.deadline, item.completed, ref)
            dl_days = int(dl_info["days_left"]) if dl_info is not None else 999999

            if mode == self.SORT_PRIORITY:
                return (completed_rank, -item.priority, dl_days, item.parallel_order)
            elif mode == self.SORT_DEADLINE:
                return (completed_rank, dl_days, -item.priority, item.parallel_order)
            else:
                return (completed_rank, item.parallel_order, -item.priority)

        return sorted(tasks, key=sort_key)

    def add_task(
        self,
        monday_date: date,
        title: str,
        priority: int = PRIORITY_MEDIUM,
        category: str = "",
        deadline: Optional[str] = None,
    ) -> TaskItem:
        wk = WeekEngine.get_week_key(monday_date)
        current_list = self.weeks.setdefault(wk, [])
        next_order = max((t.parallel_order for t in current_list), default=-1) + 1
        item = TaskItem(
            id=uuid.uuid4().hex[:8],
            title=title.strip(),
            completed=False,
            priority=priority,
            parallel_order=next_order,
            category=category.strip(),
            deadline=deadline if deadline else None,
        )
        current_list.append(item)
        self._normalize_parallel_order(wk)
        self.save()
        return item

    def toggle_task(self, monday_date: date, task_id: str) -> Optional[TaskItem]:
        wk = WeekEngine.get_week_key(monday_date)
        for t in self.weeks.get(wk, []):
            if t.id == task_id:
                t.completed = not t.completed
                t.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if t.completed else None
                self.save()
                return t
        return None

    def update_task(
        self,
        monday_date: date,
        task_id: str,
        title: str,
        priority: int,
        category: str,
        deadline: Optional[str],
    ) -> Optional[TaskItem]:
        wk = WeekEngine.get_week_key(monday_date)
        for t in self.weeks.get(wk, []):
            if t.id == task_id:
                t.title = title.strip()
                t.priority = priority
                t.category = category.strip()
                t.deadline = deadline if deadline else None
                self.save()
                return t
        return None

    def delete_task(self, monday_date: date, task_id: str) -> bool:
        wk = WeekEngine.get_week_key(monday_date)
        tasks = self.weeks.get(wk, [])
        target = next((t for t in tasks if t.id == task_id), None)
        if target is None:
            return False

        self._last_deleted = (wk, TaskItem.from_dict(target.to_dict()))
        self.weeks[wk] = [t for t in tasks if t.id != task_id]
        self._normalize_parallel_order(wk)
        self.save()
        return True

    def undo_last_delete(self) -> Optional[str]:
        if not self._last_deleted:
            return None
        wk, item = self._last_deleted
        self._last_deleted = None
        curr = self.weeks.setdefault(wk, [])
        if all(t.id != item.id for t in curr):
            curr.append(item)
            self._normalize_parallel_order(wk)
            self.save()
            return wk
        return None

    def move_task_parallel(self, monday_date: date, task_id: str, direction: int) -> bool:
        wk = WeekEngine.get_week_key(monday_date)
        tasks = self.weeks.get(wk, [])
        target = next((t for t in tasks if t.id == task_id), None)
        if not target:
            return False

        sink = bool(self.settings.get("sink_completed", True))
        if sink:
            same_group = sorted(
                [t for t in tasks if t.completed == target.completed],
                key=lambda x: x.parallel_order,
            )
        else:
            same_group = sorted(tasks, key=lambda x: x.parallel_order)

        idx = next((i for i, t in enumerate(same_group) if t.id == task_id), -1)
        new_idx = idx + direction
        if idx < 0 or new_idx < 0 or new_idx >= len(same_group):
            return False

        same_group[idx].parallel_order, same_group[new_idx].parallel_order = (
            same_group[new_idx].parallel_order,
            same_group[idx].parallel_order,
        )
        self._normalize_parallel_order(wk)
        self.save()
        return True

    def carry_over_previous_week(self, target_monday: date) -> int:
        prev_monday = WeekEngine.get_monday(target_monday) - timedelta(days=7)
        prev_wk = WeekEngine.get_week_key(prev_monday)
        curr_wk = WeekEngine.get_week_key(target_monday)

        prev_unfinished = [t for t in self.weeks.get(prev_wk, []) if not t.completed]
        if not prev_unfinished:
            return 0

        curr_tasks = self.weeks.setdefault(curr_wk, [])
        existing_titles = {t.title for t in curr_tasks}
        next_order = max((t.parallel_order for t in curr_tasks), default=-1) + 1

        added_count = 0
        for pt in sorted(prev_unfinished, key=lambda x: x.parallel_order):
            if pt.title not in existing_titles:
                curr_tasks.append(
                    TaskItem(
                        id=uuid.uuid4().hex[:8],
                        title=pt.title,
                        completed=False,
                        priority=pt.priority,
                        parallel_order=next_order,
                        category=pt.category,
                        deadline=pt.deadline,
                    )
                )
                existing_titles.add(pt.title)
                next_order += 1
                added_count += 1

        if added_count > 0:
            self._normalize_parallel_order(curr_wk)
            self.save()
        return added_count

    def _normalize_parallel_order(self, wk: str) -> None:
        tasks = sorted(self.weeks.get(wk, []), key=lambda x: x.parallel_order)
        for idx, item in enumerate(tasks):
            item.parallel_order = idx

    def export_week_markdown(self, monday_date: date, reference_date: Optional[date] = None) -> str:
        ref = reference_date or date.today()
        m, s = WeekEngine.get_week_range(monday_date)
        iso_year, iso_week, _ = m.isocalendar()

        tasks = self.get_tasks(monday_date, reference_date=ref)
        total = len(tasks)
        done_tasks = [t for t in tasks if t.completed]
        todo_tasks = [t for t in tasks if not t.completed]
        rate = int(round((len(done_tasks) / total) * 100)) if total > 0 else 0

        lines = [
            f"# 📅 {iso_year}年第{iso_week:02d}周 任务备忘录 ({m.strftime('%Y.%m.%d')} - {s.strftime('%Y.%m.%d')})",
            "",
            f"> **完成进度**：`{len(done_tasks)} / {total}` ({rate}%) ｜ **导出时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ *By：Exusiailmc绿毛虫*",
            "",
        ]

        def format_task_line(idx: int, item: TaskItem) -> str:
            checkbox = "[x]" if item.completed else "[ ]"
            p_short = PRIORITY_META.get(item.priority, PRIORITY_META[PRIORITY_MEDIUM])["label"]
            cat_str = f"`#{item.category}` " if item.category else ""
            dl_info = WeekEngine.evaluate_deadline(item.deadline, item.completed, ref)
            if dl_info:
                if item.completed:
                    dl_str = f" *(截止: {item.deadline})*"
                else:
                    dl_str = f" *(截止: {item.deadline} · {dl_info['text']})*"
            else:
                dl_str = ""
            return f"- {checkbox} **{idx}.** [{p_short}] {cat_str}{item.title}{dl_str}"

        lines.append(f"## 待办与进行中 ({len(todo_tasks)})")
        if todo_tasks:
            for i, t in enumerate(todo_tasks, 1):
                lines.append(format_task_line(i, t))
        else:
            lines.append("- 本周待办任务已全部清零！")
        lines.append("")

        lines.append(f"## 已完成任务 ({len(done_tasks)})")
        if done_tasks:
            for i, t in enumerate(done_tasks, 1):
                lines.append(format_task_line(i, t))
        else:
            lines.append("- 暂无已完成项")
        lines.append("")

        return "\n".join(lines)


# ==============================================================================
# 第二部分：单实例进程通信守卫（防止重复启动打开多个窗口）
# ==============================================================================

class SingleInstanceGuard(QtCore.QObject):
    """跨进程单实例锁：若检测到已有进程运行，则发送唤醒指令并退出当前新进程"""

    def __init__(self, key: str = APP_SINGLETON_KEY):
        super().__init__()
        self.key = key
        self.server: Optional[QLocalServer] = None
        self.on_activate_callback: Optional[Callable[[], None]] = None

    def try_acquire_or_notify_existing(self) -> bool:
        probe = QLocalSocket()
        probe.connectToServer(self.key)
        if probe.waitForConnected(250):
            probe.write(b"SHOW_WINDOW")
            probe.flush()
            probe.waitForBytesWritten(150)
            probe.disconnectFromServer()
            return False

        QLocalServer.removeServer(self.key)
        self.server = QLocalServer(self)
        if self.server.listen(self.key):
            self.server.newConnection.connect(self._on_new_client)
        return True

    def _on_new_client(self) -> None:
        if not self.server:
            return
        conn = self.server.nextPendingConnection()
        if conn:
            conn.waitForReadyRead(200)
            _ = conn.readAll()
            conn.close()
            if self.on_activate_callback:
                self.on_activate_callback()


# ==============================================================================
# 第三部分：高分屏抗锯齿矢量图标引擎（VectorIcons）与极光渐变边框主题引擎
# ==============================================================================

class VectorIcons:
    _arrow_cache: Dict[str, str] = {}

    @staticmethod
    def app_logo(size: int = 64) -> QIcon:
        pix = QPixmap(size, size)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(Antialiasing, True)

        grad = QLinearGradient(0, 0, size, size)
        grad.setColorAt(0.0, QColor("#2563EB"))
        grad.setColorAt(1.0, QColor("#06B6D4"))
        p.setPen(NoPen)
        p.setBrush(QBrush(grad))
        margin = size * 0.06
        p.drawRoundedRect(QRectF(margin, margin, size - 2 * margin, size - 2 * margin), size * 0.24, size * 0.24)

        p.setBrush(QColor(255, 255, 255, 65))
        p.drawRoundedRect(QRectF(size * 0.18, size * 0.18, size * 0.64, size * 0.14), size * 0.05, size * 0.05)

        pen = QPen(QColor("#FFFFFF"), max(2.2, size * 0.105), SolidLine, RoundCap, RoundJoin)
        p.setPen(pen)
        path = QPainterPath()
        path.moveTo(size * 0.28, size * 0.55)
        path.lineTo(size * 0.44, size * 0.71)
        path.lineTo(size * 0.74, size * 0.39)
        p.drawPath(path)
        p.end()
        return QIcon(pix)

    @staticmethod
    def save_ico_file(target_path: Path) -> None:
        try:
            if not target_path.exists():
                icon = VectorIcons.app_logo(128)
                pix = icon.pixmap(128, 128)
                pix.save(str(target_path), "ICO")
        except Exception:
            pass

    @classmethod
    def get_chevron_down_url(cls, dark: bool) -> str:
        """生成用于 QDateEdit 的抗锯齿下拉箭头图标"""
        key = "dark" if dark else "light"
        if key in cls._arrow_cache and Path(cls._arrow_cache[key]).exists():
            return cls._arrow_cache[key]

        import tempfile
        pix = QPixmap(14, 14)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(Antialiasing, True)
        color = QColor("#94A3B8" if dark else "#64748B")
        pen = QPen(color, 1.8, SolidLine, RoundCap, RoundJoin)
        p.setPen(pen)
        p.drawLine(QPointF(3.5, 5.2), QPointF(7.0, 8.8))
        p.drawLine(QPointF(7.0, 8.8), QPointF(10.5, 5.2))
        p.end()

        out_path = Path(tempfile.gettempdir()) / f"liteweek_chevron_{key}.png"
        pix.save(str(out_path), "PNG")
        url_path = str(out_path).replace("\\", "/")
        cls._arrow_cache[key] = url_path
        return url_path

    @staticmethod
    def draw(kind: str, color_hex: str, size: int = 16) -> QIcon:
        pix = QPixmap(size, size)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(Antialiasing, True)
        c = QColor(color_hex)
        pen = QPen(c, 1.65, SolidLine, RoundCap, RoundJoin)
        p.setPen(pen)

        s = float(size)
        if kind == "sun":
            p.setBrush(NoBrush)
            p.drawEllipse(QRectF(s * 0.28, s * 0.28, s * 0.44, s * 0.44))
            for deg in range(0, 360, 45):
                rad = math.radians(deg)
                x1 = s * 0.5 + math.cos(rad) * s * 0.30
                y1 = s * 0.5 + math.sin(rad) * s * 0.30
                x2 = s * 0.5 + math.cos(rad) * s * 0.43
                y2 = s * 0.5 + math.sin(rad) * s * 0.43
                p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        elif kind == "moon":
            path = QPainterPath()
            path.addEllipse(QRectF(s * 0.20, s * 0.20, s * 0.60, s * 0.60))
            cut = QPainterPath()
            cut.addEllipse(QRectF(s * 0.36, s * 0.12, s * 0.55, s * 0.55))
            moon_path = path.subtracted(cut)
            p.setBrush(c)
            p.drawPath(moon_path)
        elif kind == "pin":
            p.drawLine(QPointF(s * 0.32, s * 0.20), QPointF(s * 0.68, s * 0.20))
            p.drawLine(QPointF(s * 0.38, s * 0.20), QPointF(s * 0.32, s * 0.54))
            p.drawLine(QPointF(s * 0.62, s * 0.20), QPointF(s * 0.68, s * 0.54))
            p.drawLine(QPointF(s * 0.22, s * 0.54), QPointF(s * 0.78, s * 0.54))
            p.drawLine(QPointF(s * 0.50, s * 0.54), QPointF(s * 0.50, s * 0.86))
        elif kind == "compact":
            p.drawRoundedRect(QRectF(s * 0.18, s * 0.20, s * 0.64, s * 0.60), 2.0, 2.0)
            p.drawLine(QPointF(s * 0.32, s * 0.38), QPointF(s * 0.68, s * 0.38))
            p.drawLine(QPointF(s * 0.32, s * 0.52), QPointF(s * 0.68, s * 0.52))
            p.drawLine(QPointF(s * 0.32, s * 0.66), QPointF(s * 0.54, s * 0.66))
        elif kind == "expand":
            p.drawRoundedRect(QRectF(s * 0.18, s * 0.18, s * 0.64, s * 0.64), 2.0, 2.0)
            p.drawLine(QPointF(s * 0.18, s * 0.38), QPointF(s * 0.82, s * 0.38))
            p.drawLine(QPointF(s * 0.50, s * 0.48), QPointF(s * 0.50, s * 0.70))
            p.drawLine(QPointF(s * 0.39, s * 0.59), QPointF(s * 0.61, s * 0.59))
        elif kind == "settings":
            p.drawLine(QPointF(s * 0.20, s * 0.30), QPointF(s * 0.80, s * 0.30))
            p.drawLine(QPointF(s * 0.20, s * 0.52), QPointF(s * 0.80, s * 0.52))
            p.drawLine(QPointF(s * 0.20, s * 0.74), QPointF(s * 0.80, s * 0.74))
            p.setBrush(c)
            p.drawEllipse(QRectF(s * 0.54, s * 0.21, s * 0.18, s * 0.18))
            p.drawEllipse(QRectF(s * 0.28, s * 0.43, s * 0.18, s * 0.18))
            p.drawEllipse(QRectF(s * 0.48, s * 0.65, s * 0.18, s * 0.18))
        elif kind == "copy_md":
            p.drawRoundedRect(QRectF(s * 0.22, s * 0.20, s * 0.56, s * 0.64), 2.0, 2.0)
            p.drawLine(QPointF(s * 0.35, s * 0.40), QPointF(s * 0.65, s * 0.40))
            p.drawLine(QPointF(s * 0.35, s * 0.54), QPointF(s * 0.65, s * 0.54))
            p.drawLine(QPointF(s * 0.35, s * 0.68), QPointF(s * 0.53, s * 0.68))
        elif kind == "carry":
            p.drawLine(QPointF(s * 0.50, s * 0.18), QPointF(s * 0.50, s * 0.65))
            p.drawLine(QPointF(s * 0.34, s * 0.50), QPointF(s * 0.50, s * 0.66))
            p.drawLine(QPointF(s * 0.66, s * 0.50), QPointF(s * 0.50, s * 0.66))
            p.drawLine(QPointF(s * 0.24, s * 0.80), QPointF(s * 0.76, s * 0.80))
        elif kind == "up":
            p.drawLine(QPointF(s * 0.50, s * 0.76), QPointF(s * 0.50, s * 0.24))
            p.drawLine(QPointF(s * 0.28, s * 0.46), QPointF(s * 0.50, s * 0.24))
            p.drawLine(QPointF(s * 0.72, s * 0.46), QPointF(s * 0.50, s * 0.24))
        elif kind == "down":
            p.drawLine(QPointF(s * 0.50, s * 0.24), QPointF(s * 0.50, s * 0.76))
            p.drawLine(QPointF(s * 0.28, s * 0.54), QPointF(s * 0.50, s * 0.76))
            p.drawLine(QPointF(s * 0.72, s * 0.54), QPointF(s * 0.50, s * 0.76))
        elif kind == "edit":
            path = QPainterPath()
            path.moveTo(s * 0.24, s * 0.76)
            path.lineTo(s * 0.36, s * 0.72)
            path.lineTo(s * 0.74, s * 0.34)
            path.lineTo(s * 0.66, s * 0.26)
            path.lineTo(s * 0.28, s * 0.64)
            path.closeSubpath()
            p.drawPath(path)
        elif kind == "delete":
            p.drawLine(QPointF(s * 0.30, s * 0.30), QPointF(s * 0.70, s * 0.70))
            p.drawLine(QPointF(s * 0.70, s * 0.30), QPointF(s * 0.30, s * 0.70))
        elif kind == "dot":
            p.setPen(NoPen)
            p.setBrush(c)
            p.drawEllipse(QRectF(s * 0.24, s * 0.24, s * 0.52, s * 0.52))
        p.end()
        return QIcon(pix)


def style_calendar_widget(cal: Optional[QCalendarWidget], dark: bool) -> None:
    """将 QDateEdit 弹出的 QCalendarWidget 美化为与主界面一致的无网格现代风格"""
    if cal is None:
        return
    try:
        no_v_header = (
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
            if IS_QT6 else QCalendarWidget.NoVerticalHeader
        )
        cal.setVerticalHeaderFormat(no_v_header)
        cal.setGridVisible(False)
    except Exception:
        pass


def build_theme_qss(dark: bool, alpha_int: int = 248) -> Tuple[str, Dict[str, str]]:
    chevron_url = VectorIcons.get_chevron_down_url(dark)

    if dark:
        pal = {
            "root_rgba": f"rgba(15, 23, 42, {alpha_int})",
            "header_rgba": f"rgba(30, 41, 59, {alpha_int})",
            "toolbar_rgba": f"rgba(23, 33, 50, {alpha_int})",
            "composer_rgba": f"rgba(30, 41, 59, {alpha_int})",
            "border": "#334155",
            "divider": "#1E293B",
            "text_main": "#F1F5F9",
            "text_sub": "#94A3B8",
            "text_muted": "#64748B",
            "card_bg": "#1E293B",
            "card_done_bg": "#151F30",
            "card_border": "#334155",
            "card_hover_border": "#475569",
            "input_bg": "#0F172A",
            "input_focus_bg": "#1E293B",
            "btn_sec_bg": "#1E293B",
            "btn_sec_hover": "#334155",
            "icon_fg": "#94A3B8",
            "icon_hover_bg": "#334155",
            "cat_bg": "#312E81",
            "cat_fg": "#C7D2FE",
        }
    else:
        pal = {
            "root_rgba": f"rgba(241, 245, 249, {alpha_int})",
            "header_rgba": f"rgba(255, 255, 255, {alpha_int})",
            "toolbar_rgba": f"rgba(248, 250, 252, {alpha_int})",
            "composer_rgba": f"rgba(255, 255, 255, {alpha_int})",
            "border": "#CBD5E1",
            "divider": "#E2E8F0",
            "text_main": "#0F172A",
            "text_sub": "#475569",
            "text_muted": "#94A3B8",
            "card_bg": "#FFFFFF",
            "card_done_bg": "#F8FAFC",
            "card_border": "#CBD5E1",
            "card_hover_border": "#94A3B8",
            "input_bg": "#F8FAFC",
            "input_focus_bg": "#FFFFFF",
            "btn_sec_bg": "#FFFFFF",
            "btn_sec_hover": "#F1F5F9",
            "icon_fg": "#475569",
            "icon_hover_bg": "#F1F5F9",
            "cat_bg": "#E0E7FF",
            "cat_fg": "#4338CA",
        }

    qss = f"""
    QWidget#RootContainer {{
        background-color: {pal['root_rgba']};
        border: none;
        border-radius: 14px;
    }}
    QFrame#HeaderBar {{
        background-color: {pal['header_rgba']};
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        border-bottom: 1px solid {pal['divider']};
    }}
    QFrame#ToolbarFrame {{
        background-color: {pal['toolbar_rgba']};
        border-bottom: 1px solid {pal['divider']};
    }}
    QFrame#ComposerFrame {{
        background-color: {pal['composer_rgba']};
        border-top: 1px solid {pal['divider']};
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
    }}
    QScrollArea#TaskScroll {{
        background: transparent;
        border: none;
    }}
    QWidget#TaskListContainer {{
        background: transparent;
    }}
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 5px;
        margin: 4px 1px 4px 1px;
    }}
    QScrollBar::handle:vertical {{
        background: {pal['border']};
        min-height: 24px;
        border-radius: 2px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QPushButton.IconBtn {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
        color: {pal['icon_fg']};
        font-size: 11.5px;
        font-weight: 600;
        padding: 2px 4px;
    }}
    QPushButton.IconBtn:hover {{
        background-color: {pal['icon_hover_bg']};
        color: {pal['text_main']};
    }}
    QPushButton.IconBtn:checked {{
        background-color: rgba(37, 99, 235, 38);
        border: 1px solid rgba(59, 130, 246, 120);
        color: #3B82F6;
    }}
    QPushButton.PrimaryBtn {{
        background-color: #2563EB;
        border: none;
        border-radius: 7px;
        color: #FFFFFF;
        font-size: 12px;
        font-weight: 700;
        padding: 5px 12px;
    }}
    QPushButton.PrimaryBtn:hover {{
        background-color: #1D4ED8;
    }}
    QPushButton.SecondaryBtn {{
        background-color: {pal['btn_sec_bg']};
        border: 1px solid {pal['border']};
        border-radius: 6px;
        color: {pal['text_main']};
        font-size: 11px;
        font-weight: 600;
        padding: 3px 7px;
    }}
    QPushButton.SecondaryBtn:hover {{
        background-color: {pal['btn_sec_hover']};
        border: 1px solid #3B82F6;
    }}
    QLineEdit, QComboBox, QDateEdit {{
        background-color: {pal['input_bg']};
        border: 1px solid {pal['border']};
        border-radius: 7px;
        padding: 3px 7px;
        color: {pal['text_main']};
        font-size: 11.5px;
    }}
    QComboBox::drop-down, QDateEdit::drop-down {{
        subcontrol-origin: border;
        subcontrol-position: center right;
        width: 18px;
        border: none;
        background: transparent;
    }}
    QComboBox::down-arrow, QDateEdit::down-arrow {{
        image: url("{chevron_url}");
        width: 12px;
        height: 12px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {pal['card_bg']};
        color: {pal['text_main']};
        selection-background-color: #2563EB;
        selection-color: #FFFFFF;
        border: 1px solid {pal['border']};
        border-radius: 6px;
        padding: 3px;
        outline: none;
    }}
    /* 深度美化 DDL 弹出的 QCalendarWidget 日历面板，与深浅色主题完全统一 */
    QCalendarWidget QWidget {{
        background-color: {pal['card_bg']};
        color: {pal['text_main']};
        alternate-background-color: {pal['input_bg']};
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {pal['toolbar_rgba']};
        border-bottom: 1px solid {pal['border']};
        padding: 2px 4px;
    }}
    QCalendarWidget QToolButton {{
        background-color: transparent;
        color: {pal['text_main']};
        font-size: 11.5px;
        font-weight: 700;
        border: none;
        border-radius: 5px;
        padding: 3px 6px;
        margin: 1px;
    }}
    QCalendarWidget QToolButton:hover {{
        background-color: {pal['icon_hover_bg']};
    }}
    QCalendarWidget QToolButton::menu-indicator {{
        image: none;
    }}
    QCalendarWidget QSpinBox {{
        background-color: {pal['input_bg']};
        color: {pal['text_main']};
        border: 1px solid {pal['border']};
        border-radius: 4px;
        padding: 1px 4px;
    }}
    QCalendarWidget QAbstractItemView:enabled {{
        background-color: {pal['card_bg']};
        color: {pal['text_main']};
        selection-background-color: #2563EB;
        selection-color: #FFFFFF;
        font-size: 11px;
        outline: none;
    }}
    QCalendarWidget QAbstractItemView:disabled {{
        color: {pal['text_muted']};
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border: 1px solid #3B82F6;
        background-color: {pal['input_focus_bg']};
    }}
    QCheckBox {{
        color: {pal['text_sub']};
        font-size: 11px;
        font-weight: 600;
    }}
    QSlider::groove:horizontal {{
        height: 4px;
        background: {pal['border']};
        border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: #3B82F6;
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: #2563EB;
        width: 12px;
        height: 12px;
        margin: -4px 0;
        border-radius: 6px;
    }}
    """
    return qss, pal


# ==============================================================================
# 第四部分：极光渐变容器、任务编辑弹窗、任务卡片组件与主窗口实现
# ==============================================================================

class GradientRootWidget(QWidget):
    """带有蓝-青-紫极光渐变描边外框的圆角主容器，与纯白背景软件形成鲜明区分度"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False

    def paintEvent(self, event):
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        p.setRenderHint(Antialiasing, True)

        # 1. 先绘制原本 QSS 的圆角背景
        pe_widget = QtWidgets.QStyle.PrimitiveElement.PE_Widget if IS_QT6 else QtWidgets.QStyle.PE_Widget
        self.style().drawPrimitive(pe_widget, opt, p, self)

        # 2. 叠加 2.2px 抗锯齿蓝青紫极光渐变外框（修复 NoBrush 参数类型）
        w, h = float(self.width()), float(self.height())
        grad = QLinearGradient(0.0, 0.0, w, h)
        if self.dark_mode:
            grad.setColorAt(0.0, QColor("#3B82F6"))
            grad.setColorAt(0.5, QColor("#06B6D4"))
            grad.setColorAt(1.0, QColor("#8B5CF6"))
        else:
            grad.setColorAt(0.0, QColor("#2563EB"))
            grad.setColorAt(0.5, QColor("#06B6D4"))
            grad.setColorAt(1.0, QColor("#6366F1"))

        pen = QPen(QBrush(grad), 2.2)
        p.setPen(pen)
        p.setBrush(NoBrush)
        p.drawRoundedRect(QRectF(1.1, 1.1, w - 2.2, h - 2.2), 13.5, 13.5)
        p.end()


class TaskEditDialog(QDialog):
    def __init__(self, parent: QWidget, task: TaskItem, dark: bool):
        super().__init__(parent)
        self.setWindowTitle("编辑任务详情")
        self.setModal(True)
        self.setFixedWidth(330)
        qss, pal = build_theme_qss(dark, 255)
        self.setStyleSheet(
            f"QDialog {{ background-color: {pal['card_bg']}; }} "
            f"QLabel {{ color: {pal['text_main']}; font-size: 12px; font-weight: 600; }}"
            + qss
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        self.title_input = QLineEdit(task.title)
        form.addRow("任务内容：", self.title_input)

        self.cat_input = QLineEdit(task.category)
        self.cat_input.setPlaceholderText("如：科研 / 社团 / 课程")
        form.addRow("分类标签：", self.cat_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItem(VectorIcons.draw("dot", "#EF4444", 12), "高", PRIORITY_HIGH)
        self.priority_combo.addItem(VectorIcons.draw("dot", "#F59E0B", 12), "中", PRIORITY_MEDIUM)
        self.priority_combo.addItem(VectorIcons.draw("dot", "#3B82F6", 12), "低", PRIORITY_LOW)
        idx = self.priority_combo.findData(task.priority)
        if idx >= 0:
            self.priority_combo.setCurrentIndex(idx)
        form.addRow("优先级：", self.priority_combo)

        dl_row = QHBoxLayout()
        self.dl_check = QCheckBox("启用")
        self.dl_date = QDateEdit()
        self.dl_date.setCalendarPopup(True)
        self.dl_date.setDisplayFormat("yyyy-MM-dd")
        style_calendar_widget(self.dl_date.calendarWidget(), dark)

        if task.deadline:
            try:
                d = datetime.strptime(task.deadline, "%Y-%m-%d").date()
                self.dl_date.setDate(QDate(d.year, d.month, d.day))
                self.dl_check.setChecked(True)
            except ValueError:
                self.dl_date.setDate(QDate.currentDate())
                self.dl_check.setChecked(False)
        else:
            self.dl_date.setDate(QDate.currentDate())
            self.dl_check.setChecked(False)

        self.dl_date.setEnabled(self.dl_check.isChecked())
        self.dl_check.toggled.connect(self.dl_date.setEnabled)
        dl_row.addWidget(self.dl_check)
        dl_row.addWidget(self.dl_date, 1)
        form.addRow("截止日期：", dl_row)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(BtnSave | BtnCancel)
        btn_box.button(BtnSave).setText("保存")
        btn_box.button(BtnCancel).setText("取消")
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_values(self) -> Tuple[str, int, str, Optional[str]]:
        title = self.title_input.text().strip()
        priority = int(self.priority_combo.currentData())
        category = self.cat_input.text().strip()
        deadline = self.dl_date.date().toString("yyyy-MM-dd") if self.dl_check.isChecked() else None
        return title, priority, category, deadline


class TaskCardWidget(QFrame):
    def __init__(
        self,
        task: TaskItem,
        index_num: int,
        show_index: bool,
        compact_mode: bool,
        allow_parallel_move: bool,
        dark_mode: bool,
        pal: Dict[str, str],
        on_toggle,
        on_move,
        on_edit,
        on_delete,
    ):
        super().__init__()
        self.task = task
        self.on_edit = on_edit
        self.setCursor(PointingHand)

        p_meta = PRIORITY_META.get(task.priority, PRIORITY_META[PRIORITY_MEDIUM])
        border_left_color = pal["border"] if task.completed else str(p_meta["bar"])
        card_bg = pal["card_done_bg"] if task.completed else pal["card_bg"]

        self.setStyleSheet(f"""
            TaskCardWidget {{
                background-color: {card_bg};
                border: 1px solid {pal['card_border']};
                border-left: 4px solid {border_left_color};
                border-radius: 8px;
            }}
            TaskCardWidget:hover {{
                border: 1px solid {pal['card_hover_border']};
                border-left: 4px solid {border_left_color};
            }}
        """)

        main_v = QVBoxLayout(self)
        v_pad = 5 if compact_mode else 7
        main_v.setContentsMargins(9, v_pad, 7, v_pad)
        main_v.setSpacing(3)

        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        self.chk = QCheckBox()
        self.chk.setChecked(task.completed)
        self.chk.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 15px; height: 15px; border-radius: 4px;
                border: 1.5px solid {pal['text_muted']}; background: {pal['input_bg']};
            }}
            QCheckBox::indicator:hover {{ border-color: #3B82F6; }}
            QCheckBox::indicator:checked {{ background-color: #2563EB; border-color: #2563EB; }}
        """)
        self.chk.clicked.connect(lambda: on_toggle(task.id))
        top_row.addWidget(self.chk, 0, AlignTop)

        center_col = QVBoxLayout()
        center_col.setSpacing(3)

        safe_title = html.escape(task.title)
        safe_cat = html.escape(task.category)

        title_lbl = QLabel()
        title_lbl.setWordWrap(True)
        prefix_num = (
            f"<span style='color:{pal['text_sub']}; font-weight:700;'>{index_num}.</span> "
            if show_index else ""
        )
        cat_html = (
            f"<span style='background:{pal['cat_bg']}; color:{pal['cat_fg']}; padding:1px 5px; "
            f"border-radius:4px; font-size:10px; font-weight:600;'>{safe_cat}</span> "
            if safe_cat else ""
        )
        if task.completed:
            title_html = f"{prefix_num}{cat_html}<span style='color:{pal['text_muted']}; text-decoration:line-through;'>{safe_title}</span>"
        else:
            title_html = f"{prefix_num}{cat_html}<span style='color:{pal['text_main']}; font-weight:500;'>{safe_title}</span>"
        title_lbl.setText(title_html)
        title_lbl.setStyleSheet("font-size: 12.2px; border: none; background: transparent;")
        center_col.addWidget(title_lbl)

        dl_info = WeekEngine.evaluate_deadline(task.deadline, task.completed, dark_mode=dark_mode)
        if (not compact_mode) or (dl_info is not None and not task.completed):
            meta_row = QHBoxLayout()
            meta_row.setSpacing(5)

            if not compact_mode:
                p_fg = p_meta["dark_fg"] if dark_mode else p_meta["light_fg"]
                p_bg = p_meta["dark_bg"] if dark_mode else p_meta["light_bg"]
                p_bd = p_meta["dark_border"] if dark_mode else p_meta["light_border"]

                prio_lbl = QLabel(f"● {p_meta['short']}")
                prio_lbl.setStyleSheet(
                    f"color: {p_fg}; background: {p_bg}; border: 1px solid {p_bd}; "
                    f"border-radius: 4px; padding: 0px 5px; font-size: 9.5px; font-weight: 700;"
                )
                meta_row.addWidget(prio_lbl)

            if dl_info:
                dl_lbl = QLabel(str(dl_info["badge_text"]))
                dl_lbl.setToolTip(str(dl_info["detail"]))
                dl_lbl.setStyleSheet(
                    f"color: {dl_info['fg']}; background: {dl_info['bg']}; "
                    f"border: 1px solid {dl_info['border']}; border-radius: 4px; "
                    f"padding: 0px 5px; font-size: 9.5px; font-weight: 700;"
                )
                meta_row.addWidget(dl_lbl)

            meta_row.addStretch(1)
            center_col.addLayout(meta_row)

        top_row.addLayout(center_col, 1)

        if not compact_mode:
            btn_col = QHBoxLayout()
            btn_col.setSpacing(1)
            ic_color = pal["icon_fg"]

            if allow_parallel_move:
                up_btn = QPushButton()
                up_btn.setIcon(VectorIcons.draw("up", ic_color, 13))
                up_btn.setToolTip("上移任务")
                up_btn.setFixedSize(20, 20)
                up_btn.setProperty("class", "IconBtn")
                up_btn.clicked.connect(lambda: on_move(task.id, -1))
                btn_col.addWidget(up_btn)

                down_btn = QPushButton()
                down_btn.setIcon(VectorIcons.draw("down", ic_color, 13))
                down_btn.setToolTip("下移任务")
                down_btn.setFixedSize(20, 20)
                down_btn.setProperty("class", "IconBtn")
                down_btn.clicked.connect(lambda: on_move(task.id, 1))
                btn_col.addWidget(down_btn)

            edit_btn = QPushButton()
            edit_btn.setIcon(VectorIcons.draw("edit", ic_color, 13))
            edit_btn.setToolTip("编辑任务（或双击卡片）")
            edit_btn.setFixedSize(20, 20)
            edit_btn.setProperty("class", "IconBtn")
            edit_btn.clicked.connect(lambda: on_edit(task))
            btn_col.addWidget(edit_btn)

            del_btn = QPushButton()
            del_btn.setIcon(VectorIcons.draw("delete", ic_color, 13))
            del_btn.setToolTip("删除任务（支持撤回）")
            del_btn.setFixedSize(20, 20)
            del_btn.setProperty("class", "IconBtn")
            del_btn.clicked.connect(lambda: on_delete(task.id))
            btn_col.addWidget(del_btn)
            top_row.addLayout(btn_col)

        main_v.addLayout(top_row)

    def mouseDoubleClickEvent(self, event):
        if event.button() == LeftButton:
            self.on_edit(self.task)
        super().mouseDoubleClickEvent(event)


class LiteWeekMemoWindow(QWidget):
    SORT_LABELS = {
        TaskDataStore.SORT_PARALLEL: "并行顺序",
        TaskDataStore.SORT_PRIORITY: "按优先级",
        TaskDataStore.SORT_DEADLINE: "按DDL",
    }

    def __init__(self, store: TaskDataStore):
        super().__init__()
        self.store = store
        self.current_monday: date = WeekEngine.get_monday(date.today())
        self._last_known_today: date = date.today()
        self._drag_pos: Optional[QPoint] = None
        self.pal: Dict[str, str] = {}
        self.current_input_prio: int = PRIORITY_MEDIUM

        self._save_debounce_timer = QTimer(self)
        self._save_debounce_timer.setSingleShot(True)
        self._save_debounce_timer.timeout.connect(self.store.save)

        self._midnight_timer = QTimer(self)
        self._midnight_timer.timeout.connect(self._check_date_rollover)
        self._midnight_timer.start(60 * 1000)

        self.setWindowTitle("轻周备忘 LiteWeek Memo")
        self.app_icon = VectorIcons.app_logo(64)
        self.setWindowIcon(self.app_icon)
        VectorIcons.save_ico_file(self.store.base_dir / "app_icon.ico")

        init_w = max(385, int(self.store.settings.get("normal_width", 385)))
        init_h = (
            int(self.store.settings.get("compact_height", 340))
            if self.store.settings.get("compact_mode", False)
            else int(self.store.settings.get("normal_height", 540))
        )
        self.resize(init_w, init_h)

        self.setAttribute(TranslucentBg, True)
        self._apply_window_flags()

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(4, 4, 4, 4)

        self.root_container = GradientRootWidget()
        self.root_container.setObjectName("RootContainer")
        outer_layout.addWidget(self.root_container)

        self.root_layout = QVBoxLayout(self.root_container)
        self.root_layout.setContentsMargins(2, 2, 2, 2)
        self.root_layout.setSpacing(0)

        self._build_header()
        self._build_toolbar()
        self._build_task_list_area()
        self._build_composer_and_footer()
        self._setup_system_tray()

        self._apply_theme_and_opacity()
        self._update_compact_mode_ui(initial=True)
        self.refresh_ui()

    def _apply_window_flags(self) -> None:
        flags = FramelessHint | WindowFlag
        if self.store.settings.get("always_on_top", True):
            flags |= StaysOnTopHint
        self.setWindowFlags(flags)

    def _build_header(self) -> None:
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderBar")
        self.header_frame.setToolTip("按住此处可拖动窗口；双击此处可快速切换「极简纯列表模式」")
        self.header_v = QVBoxLayout(self.header_frame)
        self.header_v.setContentsMargins(10, 7, 8, 7)
        self.header_v.setSpacing(5)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(3)

        logo_lbl = QLabel()
        logo_lbl.setPixmap(self.app_icon.pixmap(17, 17))
        top_bar.addWidget(logo_lbl)

        self.app_title_lbl = QLabel("轻周备忘")
        top_bar.addWidget(self.app_title_lbl)

        self.compact_info_lbl = QLabel("")
        self.compact_info_lbl.setVisible(False)
        top_bar.addWidget(self.compact_info_lbl)

        top_bar.addStretch(1)

        self.compact_btn = QPushButton()
        self.compact_btn.setCheckable(True)
        self.compact_btn.setChecked(bool(self.store.settings.get("compact_mode", False)))
        self.compact_btn.setFixedSize(24, 22)
        self.compact_btn.setProperty("class", "IconBtn")
        self.compact_btn.setToolTip("切换「纯粹极简模式」（仅显示任务列表，也可双击顶栏切换）")
        self.compact_btn.toggled.connect(self._on_toggle_compact)
        top_bar.addWidget(self.compact_btn)

        self.pin_btn = QPushButton()
        self.pin_btn.setCheckable(True)
        self.pin_btn.setChecked(bool(self.store.settings.get("always_on_top", True)))
        self.pin_btn.setFixedSize(24, 22)
        self.pin_btn.setProperty("class", "IconBtn")
        self.pin_btn.setToolTip("窗口始终置顶")
        self.pin_btn.toggled.connect(self._on_toggle_pin)
        top_bar.addWidget(self.pin_btn)

        self.theme_btn = QPushButton()
        self.theme_btn.setFixedSize(24, 22)
        self.theme_btn.setProperty("class", "IconBtn")
        self.theme_btn.setToolTip("切换深色 / 浅色模式")
        self.theme_btn.clicked.connect(self._on_toggle_theme)
        top_bar.addWidget(self.theme_btn)

        self.settings_btn = QPushButton()
        self.settings_btn.setFixedSize(24, 22)
        self.settings_btn.setProperty("class", "IconBtn")
        self.settings_btn.setToolTip("偏好设置（透明度调节 / 开机自启 / 数据目录）")
        self.settings_btn.clicked.connect(self._show_settings_menu)
        top_bar.addWidget(self.settings_btn)

        min_btn = QPushButton("—")
        min_btn.setFixedSize(22, 22)
        min_btn.setProperty("class", "IconBtn")
        min_btn.setToolTip("最小化窗口")
        min_btn.clicked.connect(self.showMinimized)
        top_bar.addWidget(min_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(22, 22)
        close_btn.setProperty("class", "IconBtn")
        close_btn.setStyleSheet("QPushButton:hover { background:#EF4444; color:#FFFFFF; }")
        close_btn.setToolTip("隐藏至系统托盘（右键托盘图标可完全退出）")
        close_btn.clicked.connect(self._on_close_button)
        top_bar.addWidget(close_btn)

        self.header_v.addLayout(top_bar)

        self.week_nav_widget = QWidget()
        week_bar = QHBoxLayout(self.week_nav_widget)
        week_bar.setContentsMargins(0, 2, 0, 0)
        week_bar.setSpacing(6)

        prev_btn = QPushButton("◀")
        prev_btn.setFixedSize(24, 24)
        prev_btn.setProperty("class", "IconBtn")
        prev_btn.setToolTip("上一周")
        prev_btn.clicked.connect(lambda: self._shift_week(-1))
        week_bar.addWidget(prev_btn)

        week_text_col = QVBoxLayout()
        week_text_col.setSpacing(1)
        self.week_title_lbl = QLabel()
        self.week_sub_lbl = QLabel()
        week_text_col.addWidget(self.week_title_lbl)
        week_text_col.addWidget(self.week_sub_lbl)
        week_bar.addLayout(week_text_col, 1)

        self.today_btn = QPushButton("回本周")
        self.today_btn.setProperty("class", "IconBtn")
        self.today_btn.setStyleSheet("color: #3B82F6; font-size: 11px; font-weight: 700;")
        self.today_btn.clicked.connect(self._jump_to_current_week)
        week_bar.addWidget(self.today_btn)

        next_btn = QPushButton("▶")
        next_btn.setFixedSize(24, 24)
        next_btn.setProperty("class", "IconBtn")
        next_btn.setToolTip("下一周")
        next_btn.clicked.connect(lambda: self._shift_week(1))
        week_bar.addWidget(next_btn)

        self.header_v.addWidget(self.week_nav_widget)
        self.root_layout.addWidget(self.header_frame)

    def _build_toolbar(self) -> None:
        self.toolbar_frame = QFrame()
        self.toolbar_frame.setObjectName("ToolbarFrame")
        tb_layout = QHBoxLayout(self.toolbar_frame)
        tb_layout.setContentsMargins(10, 5, 10, 5)
        tb_layout.setSpacing(6)

        self.stats_lbl = QLabel("0/0 (0%)")
        self.stats_lbl.setToolTip("本周任务完成进度")
        tb_layout.addWidget(self.stats_lbl)
        tb_layout.addStretch(1)

        # 使用自定义菜单按钮替代原生 QComboBox，彻底解决「并行顺序」后两字在高分屏下被切掉的问题
        self.sort_btn = QPushButton()
        self.sort_btn.setProperty("class", "SecondaryBtn")
        self.sort_btn.setCursor(PointingHand)
        self.sort_btn.setToolTip("切换任务排序方式")
        self._update_sort_btn_display()
        self.sort_btn.clicked.connect(self._show_sort_select_menu)
        tb_layout.addWidget(self.sort_btn)

        self.carry_btn = QPushButton("顺延上周")
        self.carry_btn.setProperty("class", "SecondaryBtn")
        self.carry_btn.setCursor(PointingHand)
        self.carry_btn.setToolTip("将上周未完成的任务一键顺延至当前周")
        self.carry_btn.clicked.connect(self._on_carry_over)
        tb_layout.addWidget(self.carry_btn)

        self.export_btn = QPushButton("导出MD")
        self.export_btn.setProperty("class", "SecondaryBtn")
        self.export_btn.setCursor(PointingHand)
        self.export_btn.setToolTip("一键将当前周任务及完成情况复制为 Markdown 格式")
        self.export_btn.clicked.connect(self._on_export_markdown)
        tb_layout.addWidget(self.export_btn)

        self.root_layout.addWidget(self.toolbar_frame)

    def _build_task_list_area(self) -> None:
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("TaskScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(ScrollOff)

        self.task_list_container = QWidget()
        self.task_list_container.setObjectName("TaskListContainer")
        self.task_list_layout = QVBoxLayout(self.task_list_container)
        self.task_list_layout.setContentsMargins(9, 7, 9, 7)
        self.task_list_layout.setSpacing(6)

        self.scroll_area.setWidget(self.task_list_container)
        self.root_layout.addWidget(self.scroll_area, 1)

    def _build_composer_and_footer(self) -> None:
        self.composer_frame = QFrame()
        self.composer_frame.setObjectName("ComposerFrame")
        self.comp_v = QVBoxLayout(self.composer_frame)
        self.comp_v.setContentsMargins(10, 7, 10, 5)
        self.comp_v.setSpacing(5)

        self.input_section = QWidget()
        in_v = QVBoxLayout(self.input_section)
        in_v.setContentsMargins(0, 0, 0, 0)
        in_v.setSpacing(5)

        row1 = QHBoxLayout()
        row1.setSpacing(6)
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("输入新任务，回车添加...")
        self.task_input.returnPressed.connect(self._on_add_task)
        row1.addWidget(self.task_input, 1)

        add_btn = QPushButton("＋ 添加")
        add_btn.setProperty("class", "PrimaryBtn")
        add_btn.setCursor(PointingHand)
        add_btn.clicked.connect(self._on_add_task)
        row1.addWidget(add_btn)
        in_v.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(6)

        # 自定义优先级选择按钮：清晰显示「● 优先级: 中 ▾」，点击弹出「高 / 中 / 低」三项，绝不截断覆盖
        self.prio_btn = QPushButton()
        self.prio_btn.setProperty("class", "SecondaryBtn")
        self.prio_btn.setCursor(PointingHand)
        self.prio_btn.setToolTip("点击选择新任务的紧迫优先级（高 / 中 / 低）")
        self._update_prio_btn_display()
        self.prio_btn.clicked.connect(self._show_prio_select_menu)
        row2.addWidget(self.prio_btn)

        self.cat_input = QLineEdit()
        self.cat_input.setPlaceholderText("标签")
        self.cat_input.setToolTip("可选分类标签（如：科研 / 社团 / 课程）")
        self.cat_input.setFixedWidth(68)
        row2.addWidget(self.cat_input)

        self.dl_toggle = QCheckBox("DDL")
        self.dl_toggle.setToolTip("勾选后指定截止日期，实时显示倒计时天数")
        row2.addWidget(self.dl_toggle)

        self.dl_picker = QDateEdit()
        self.dl_picker.setCalendarPopup(True)
        self.dl_picker.setDisplayFormat("MM-dd")
        self.dl_picker.setDate(QDate.currentDate().addDays(2))
        style_calendar_widget(self.dl_picker.calendarWidget(), bool(self.store.settings.get("dark_mode", False)))
        self.dl_picker.setEnabled(False)
        self.dl_toggle.toggled.connect(self.dl_picker.setEnabled)
        row2.addWidget(self.dl_picker, 1)

        in_v.addLayout(row2)
        self.comp_v.addWidget(self.input_section)

        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(2, 0, 0, 0)
        footer_row.setSpacing(6)

        self.toast_lbl = QLabel("")
        self.toast_lbl.setStyleSheet("color: #10B981; font-size: 10.5px; font-weight: 700;")
        footer_row.addWidget(self.toast_lbl)

        self.undo_btn = QPushButton("撤回删除")
        self.undo_btn.setVisible(False)
        self.undo_btn.setCursor(PointingHand)
        self.undo_btn.setStyleSheet(
            "QPushButton { color: #3B82F6; background: transparent; border: none; "
            "font-size: 10.5px; font-weight: 800; text-decoration: underline; padding: 0 2px; }"
            "QPushButton:hover { color: #2563EB; }"
        )
        self.undo_btn.clicked.connect(self._on_undo_delete)
        footer_row.addWidget(self.undo_btn)

        footer_row.addStretch(1)

        self.watermark_lbl = QLabel("By：Exusiailmc绿毛虫")
        footer_row.addWidget(self.watermark_lbl, 0, AlignVCenter)

        size_grip = QSizeGrip(self)
        size_grip.setFixedSize(11, 11)
        footer_row.addWidget(size_grip, 0, AlignBottom | AlignRight)

        self.comp_v.addLayout(footer_row)
        self.root_layout.addWidget(self.composer_frame)

    def _create_styled_popup_menu(self) -> QMenu:
        menu = QMenu(self)
        bg = self.pal.get("card_bg", "#1E293B")
        fg = self.pal.get("text_main", "#F1F5F9")
        bd = self.pal.get("border", "#334155")
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {bd};
                border-radius: 8px;
                padding: 5px;
                font-size: 11.5px;
            }}
            QMenu::item {{
                padding: 5px 18px 5px 10px;
                border-radius: 5px;
            }}
            QMenu::item:selected {{
                background-color: #2563EB;
                color: #FFFFFF;
            }}
            QMenu::separator {{
                height: 1px;
                background: {bd};
                margin: 4px 2px;
            }}
        """)
        return menu

    def _update_sort_btn_display(self) -> None:
        curr_mode = str(self.store.settings.get("sort_mode", TaskDataStore.SORT_PARALLEL))
        label = self.SORT_LABELS.get(curr_mode, "并行顺序")
        self.sort_btn.setText(f"{label} ▾")

    def _show_sort_select_menu(self) -> None:
        menu = self._create_styled_popup_menu()
        curr_mode = str(self.store.settings.get("sort_mode", TaskDataStore.SORT_PARALLEL))
        for mode_key, text in self.SORT_LABELS.items():
            act = QAction(text, menu)
            act.setCheckable(True)
            act.setChecked(mode_key == curr_mode)
            act.triggered.connect(lambda checked=False, m=mode_key: self._set_sort_mode(m))
            menu.addAction(act)
        pos = self.sort_btn.mapToGlobal(QPoint(0, self.sort_btn.height() + 3))
        exec_fn = getattr(menu, "exec", None) or getattr(menu, "exec_", None)
        exec_fn(pos)

    def _set_sort_mode(self, mode: str) -> None:
        self.store.settings["sort_mode"] = mode
        self.store.save()
        self._update_sort_btn_display()
        self.refresh_ui()

    def _update_prio_btn_display(self) -> None:
        meta = {
            PRIORITY_HIGH: ("#EF4444", "优先级: 高"),
            PRIORITY_MEDIUM: ("#F59E0B", "优先级: 中"),
            PRIORITY_LOW: ("#3B82F6", "优先级: 低"),
        }.get(self.current_input_prio, ("#F59E0B", "优先级: 中"))
        self.prio_btn.setIcon(VectorIcons.draw("dot", meta[0], 11))
        self.prio_btn.setText(f"{meta[1]} ▾")

    def _show_prio_select_menu(self) -> None:
        menu = self._create_styled_popup_menu()
        for p_val, color, label in [
            (PRIORITY_HIGH, "#EF4444", "高"),
            (PRIORITY_MEDIUM, "#F59E0B", "中"),
            (PRIORITY_LOW, "#3B82F6", "低"),
        ]:
            act = QAction(VectorIcons.draw("dot", color, 11), label, menu)
            act.triggered.connect(lambda checked=False, v=p_val: self._set_input_prio(v))
            menu.addAction(act)
        pos = self.prio_btn.mapToGlobal(QPoint(0, self.prio_btn.height() + 3))
        exec_fn = getattr(menu, "exec", None) or getattr(menu, "exec_", None)
        exec_fn(pos)

    def _set_input_prio(self, prio_val: int) -> None:
        self.current_input_prio = prio_val
        self._update_prio_btn_display()

    def _show_settings_menu(self) -> None:
        menu = self._create_styled_popup_menu()
        fg = self.pal["text_main"]

        op_widget = QWidget()
        op_layout = QHBoxLayout(op_widget)
        op_layout.setContentsMargins(10, 4, 10, 4)
        op_layout.setSpacing(8)
        op_title = QLabel("透明度")
        op_title.setStyleSheet(f"color: {fg}; font-size: 11px; font-weight: 600;")
        op_slider = QSlider(Horizontal)
        op_slider.setRange(55, 100)
        op_slider.setFixedWidth(95)
        curr_op = int(float(self.store.settings.get("opacity", 0.96)) * 100)
        op_slider.setValue(curr_op)
        op_val_lbl = QLabel(f"{curr_op}%")
        op_val_lbl.setFixedWidth(30)
        op_val_lbl.setStyleSheet(f"color: {self.pal['text_sub']}; font-size: 10.5px;")

        def on_slide(v: int):
            op_val_lbl.setText(f"{v}%")
            self._on_opacity_changed(v)

        op_slider.valueChanged.connect(on_slide)
        op_layout.addWidget(op_title)
        op_layout.addWidget(op_slider)
        op_layout.addWidget(op_val_lbl)

        op_action = QWidgetAction(menu)
        op_action.setDefaultWidget(op_widget)
        menu.addAction(op_action)
        menu.addSeparator()

        act_sink = QAction("已完成任务自动沉底", menu)
        act_sink.setCheckable(True)
        act_sink.setChecked(bool(self.store.settings.get("sink_completed", True)))
        act_sink.toggled.connect(self._on_toggle_sink)
        menu.addAction(act_sink)

        act_idx = QAction("显示任务编号 (#1, #2...)", menu)
        act_idx.setCheckable(True)
        act_idx.setChecked(bool(self.store.settings.get("show_index", False)))
        act_idx.toggled.connect(self._on_toggle_show_index)
        menu.addAction(act_idx)

        if sys.platform == "win32":
            act_autorun = QAction("Windows 开机自动启动", menu)
            act_autorun.setCheckable(True)
            act_autorun.setChecked(AutoRunManager.is_enabled())
            act_autorun.toggled.connect(self._on_toggle_autorun)
            menu.addAction(act_autorun)

        menu.addSeparator()
        act_folder = QAction("📂 打开本地数据存储目录", menu)
        act_folder.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.store.base_dir)))
        )
        menu.addAction(act_folder)

        btn_pos = self.settings_btn.mapToGlobal(QPoint(0, self.settings_btn.height() + 4))
        exec_fn = getattr(menu, "exec", None) or getattr(menu, "exec_", None)
        exec_fn(btn_pos)

    def _setup_system_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = None
            return
        self.tray_icon = QSystemTrayIcon(self.app_icon, self)
        self.tray_icon.setToolTip("轻周备忘 LiteWeek Memo — By：Exusiailmc绿毛虫")

        tray_menu = QMenu(self)
        act_show = QAction("显示 / 唤醒主窗口", self)
        act_show.triggered.connect(self.bring_to_front)
        act_compact = QAction("切换极简纯列表模式", self)
        act_compact.triggered.connect(lambda: self.compact_btn.setChecked(not self.compact_btn.isChecked()))
        act_export = QAction("一键复制本周 Markdown", self)
        act_export.triggered.connect(self._on_export_markdown)
        act_quit = QAction("完全退出程序", self)
        act_quit.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(act_show)
        tray_menu.addAction(act_compact)
        tray_menu.addAction(act_export)
        tray_menu.addSeparator()
        tray_menu.addAction(act_quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def bring_to_front(self) -> None:
        if self.isMinimized() or not self.isVisible():
            self.showNormal()
        else:
            self.show()
        self.raise_()
        self.activateWindow()
        self._show_toast("✓ 已唤醒轻周备忘")

    def _toggle_visibility(self) -> None:
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self.bring_to_front()

    def _on_tray_activated(self, reason) -> None:
        trigger_val = QSystemTrayIcon.ActivationReason.Trigger if IS_QT6 else QSystemTrayIcon.Trigger
        if reason == trigger_val:
            self._toggle_visibility()

    def _on_close_button(self) -> None:
        if getattr(self, "tray_icon", None) is not None and self.tray_icon.isVisible():
            self.hide()
            if not self.store.settings.get("_tray_notified", False):
                self.store.settings["_tray_notified"] = True
                self.store.save()
                self.tray_icon.showMessage(
                    "轻周备忘仍在后台运行",
                    "点击托盘图标或再次双击桌面快捷方式均可直接呼出窗口。",
                    QSystemTrayIcon.MessageIcon.Information if IS_QT6 else QSystemTrayIcon.Information,
                    2000,
                )
        else:
            self.close()

    def _check_date_rollover(self) -> None:
        today = date.today()
        if today != self._last_known_today:
            old_monday = WeekEngine.get_monday(self._last_known_today)
            new_monday = WeekEngine.get_monday(today)
            self._last_known_today = today
            if self.current_monday == old_monday and new_monday != old_monday:
                self.current_monday = new_monday
            self.refresh_ui()

    def _apply_theme_and_opacity(self) -> None:
        dark = bool(self.store.settings.get("dark_mode", False))
        op = float(self.store.settings.get("opacity", 0.96))
        alpha_int = int(max(0.55, min(1.0, op)) * 255)

        qss, self.pal = build_theme_qss(dark, alpha_int)
        self.root_container.dark_mode = dark
        self.root_container.setStyleSheet(qss)
        self.root_container.update()

        self.app_title_lbl.setStyleSheet(f"color: {self.pal['text_main']}; font-size: 12.5px; font-weight: 800;")
        self.compact_info_lbl.setStyleSheet(
            f"color: #3B82F6; background: rgba(59, 130, 246, 24); "
            f"border-radius: 4px; padding: 1px 6px; font-size: 10.5px; font-weight: 700;"
        )
        self.week_title_lbl.setStyleSheet(f"color: {self.pal['text_main']}; font-size: 13.5px; font-weight: 800;")
        self.week_sub_lbl.setStyleSheet(f"color: {self.pal['text_sub']}; font-size: 11px; font-weight: 500;")
        self.stats_lbl.setStyleSheet(f"color: {self.pal['text_main']}; font-size: 11.5px; font-weight: 700;")
        self.watermark_lbl.setStyleSheet(f"color: {self.pal['text_muted']}; font-size: 9.5px; font-weight: 600;")

        ic_color = self.pal["icon_fg"]
        compact = bool(self.store.settings.get("compact_mode", False))
        pinned = bool(self.store.settings.get("always_on_top", True))

        self.compact_btn.setIcon(VectorIcons.draw("expand" if compact else "compact", "#3B82F6" if compact else ic_color, 15))
        self.pin_btn.setIcon(VectorIcons.draw("pin", "#3B82F6" if pinned else ic_color, 15))
        self.theme_btn.setIcon(VectorIcons.draw("sun" if dark else "moon", "#FBBF24" if dark else ic_color, 15))
        self.settings_btn.setIcon(VectorIcons.draw("settings", ic_color, 15))
        self.carry_btn.setIcon(VectorIcons.draw("carry", ic_color, 12))
        self.export_btn.setIcon(VectorIcons.draw("copy_md", "#3B82F6", 12))

    def refresh_ui(self) -> None:
        title, subtitle, short_title = WeekEngine.format_week_header(self.current_monday)
        self.week_title_lbl.setText(title)
        self.week_sub_lbl.setText(subtitle)

        is_this_week = self.current_monday == WeekEngine.get_monday(date.today())
        self.today_btn.setVisible(not is_this_week)

        tasks = self.store.get_tasks(self.current_monday)
        total = len(tasks)
        done_cnt = sum(1 for t in tasks if t.completed)
        pct = int(round((done_cnt / total) * 100)) if total > 0 else 0
        self.stats_lbl.setText(f"完成 {done_cnt}/{total} ({pct}%)")
        self.compact_info_lbl.setText(f"{short_title} · {done_cnt}/{total}")
        self._update_sort_btn_display()

        while self.task_list_layout.count():
            item = self.task_list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        compact = bool(self.store.settings.get("compact_mode", False))
        show_index = bool(self.store.settings.get("show_index", False))
        allow_move = self.store.settings.get("sort_mode") == TaskDataStore.SORT_PARALLEL
        dark = bool(self.store.settings.get("dark_mode", False))

        if not tasks:
            hint = "本周暂无任务\n双击顶栏可展开添加栏" if compact else "本周暂无任务安排\n在下方输入框按回车即可快速添加"
            empty_lbl = QLabel(hint)
            empty_lbl.setAlignment(AlignCenter)
            empty_lbl.setStyleSheet(f"color: {self.pal['text_muted']}; font-size: 12px; padding: 32px 10px;")
            self.task_list_layout.addWidget(empty_lbl)
        else:
            for idx, task in enumerate(tasks, 1):
                card = TaskCardWidget(
                    task=task,
                    index_num=idx,
                    show_index=show_index,
                    compact_mode=compact,
                    allow_parallel_move=allow_move,
                    dark_mode=dark,
                    pal=self.pal,
                    on_toggle=self._on_toggle_task,
                    on_move=self._on_move_task,
                    on_edit=self._on_edit_task,
                    on_delete=self._on_delete_task,
                )
                self.task_list_layout.addWidget(card)

        self.task_list_layout.addStretch(1)

    def _show_toast(self, message: str, color: str = "#10B981", show_undo: bool = False) -> None:
        self.toast_lbl.setStyleSheet(f"color: {color}; font-size: 10.5px; font-weight: 700;")
        self.toast_lbl.setText(message)
        self.undo_btn.setVisible(show_undo)
        timeout = 5000 if show_undo else 2400
        QTimer.singleShot(timeout, self._clear_toast_if_expired)

    def _clear_toast_if_expired(self) -> None:
        self.toast_lbl.setText("")
        self.undo_btn.setVisible(False)

    def _on_add_task(self) -> None:
        title = self.task_input.text().strip()
        if not title:
            self._show_toast("请输入任务内容", "#F59E0B")
            return
        priority = self.current_input_prio
        category = self.cat_input.text().strip()
        deadline = self.dl_picker.date().toString("yyyy-MM-dd") if self.dl_toggle.isChecked() else None
        self.store.add_task(self.current_monday, title, priority, category, deadline)
        self.task_input.clear()
        self.refresh_ui()
        self._show_toast("✓ 已添加任务")

    def _on_toggle_task(self, task_id: str) -> None:
        self.store.toggle_task(self.current_monday, task_id)
        self.refresh_ui()

    def _on_move_task(self, task_id: str, direction: int) -> None:
        if self.store.move_task_parallel(self.current_monday, task_id, direction):
            self.refresh_ui()

    def _on_edit_task(self, task: TaskItem) -> None:
        dark = bool(self.store.settings.get("dark_mode", False))
        dlg = TaskEditDialog(self, task, dark)
        exec_fn = getattr(dlg, "exec", None) or getattr(dlg, "exec_", None)
        if exec_fn() == DialogAccepted:
            title, prio, cat, dl = dlg.get_values()
            if title:
                self.store.update_task(self.current_monday, task.id, title, prio, cat, dl)
                self.refresh_ui()
                self._show_toast("✓ 已保存修改")

    def _on_delete_task(self, task_id: str) -> None:
        if self.store.delete_task(self.current_monday, task_id):
            self.refresh_ui()
            self._show_toast("已删除任务", "#94A3B8", show_undo=True)

    def _on_undo_delete(self) -> None:
        restored_wk = self.store.undo_last_delete()
        if restored_wk:
            self.undo_btn.setVisible(False)
            self.refresh_ui()
            self._show_toast("✓ 已恢复删除的任务")

    def _on_toggle_sink(self, checked: bool) -> None:
        self.store.settings["sink_completed"] = checked
        self.store.save()
        self.refresh_ui()

    def _on_toggle_show_index(self, checked: bool) -> None:
        self.store.settings["show_index"] = checked
        self.store.save()
        self.refresh_ui()

    def _on_toggle_autorun(self, checked: bool) -> None:
        if AutoRunManager.set_enabled(checked):
            self._show_toast("✓ 已开启开机自启" if checked else "已关闭开机自启")
        else:
            self._show_toast("设置开机自启失败", "#EF4444")

    def _on_carry_over(self) -> None:
        count = self.store.carry_over_previous_week(self.current_monday)
        if count > 0:
            self.refresh_ui()
            self._show_toast(f"✓ 已顺延 {count} 项")
        else:
            self._show_toast("上周无未完成项", "#94A3B8")

    def _on_export_markdown(self) -> None:
        md_text = self.store.export_week_markdown(self.current_monday)
        QApplication.clipboard().setText(md_text)
        self._show_toast("✓ 已复制本周 Markdown")

    def _shift_week(self, delta_weeks: int) -> None:
        self.current_monday = self.current_monday + timedelta(days=delta_weeks * 7)
        target_default = max(date.today(), self.current_monday + timedelta(days=4))
        self.dl_picker.setDate(QDate(target_default.year, target_default.month, target_default.day))
        self.refresh_ui()

    def _jump_to_current_week(self) -> None:
        self.current_monday = WeekEngine.get_monday(date.today())
        d = date.today() + timedelta(days=2)
        self.dl_picker.setDate(QDate(d.year, d.month, d.day))
        self.refresh_ui()

    def _on_opacity_changed(self, val: int) -> None:
        op = round(val / 100.0, 2)
        self.store.settings["opacity"] = op
        self._apply_theme_and_opacity()
        self._save_debounce_timer.start(400)

    def _on_toggle_theme(self) -> None:
        curr = bool(self.store.settings.get("dark_mode", False))
        self.store.settings["dark_mode"] = not curr
        self.store.save()
        self._apply_theme_and_opacity()
        self.refresh_ui()

    def _on_toggle_pin(self, checked: bool) -> None:
        self.store.settings["always_on_top"] = checked
        self.store.save()
        self._apply_theme_and_opacity()
        pos = self.pos()
        self._apply_window_flags()
        self.move(pos)
        self.show()

    def _on_toggle_compact(self, checked: bool) -> None:
        if checked:
            self.store.settings["normal_height"] = self.height()
            self.store.settings["normal_width"] = self.width()
        else:
            self.store.settings["compact_height"] = self.height()

        self.store.settings["compact_mode"] = checked
        self.store.save()
        self._apply_theme_and_opacity()
        self._update_compact_mode_ui(initial=False)
        self.refresh_ui()

    def _update_compact_mode_ui(self, initial: bool = False) -> None:
        compact = bool(self.store.settings.get("compact_mode", False))

        self.week_nav_widget.setVisible(not compact)
        self.toolbar_frame.setVisible(not compact)
        self.input_section.setVisible(not compact)

        self.app_title_lbl.setVisible(not compact)
        self.compact_info_lbl.setVisible(compact)

        if compact:
            self.header_v.setContentsMargins(10, 5, 8, 5)
            self.comp_v.setContentsMargins(10, 2, 6, 2)
            self.setMinimumSize(270, 200)
            if not initial:
                target_h = int(self.store.settings.get("compact_height", 340))
                self.resize(self.width(), max(220, target_h))
        else:
            self.header_v.setContentsMargins(10, 7, 8, 7)
            self.comp_v.setContentsMargins(10, 7, 10, 5)
            self.setMinimumSize(375, 390)
            if not initial:
                target_h = int(self.store.settings.get("normal_height", 540))
                self.resize(max(385, self.width()), max(420, target_h))

    def _global_pos(self, event) -> QPoint:
        if hasattr(event, "globalPosition"):
            return event.globalPosition().toPoint()
        return event.globalPos()

    def mouseDoubleClickEvent(self, event):
        if event.button() == LeftButton:
            local_pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            if local_pos.y() <= self.header_frame.height() + 8:
                self.compact_btn.setChecked(not self.compact_btn.isChecked())
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == LeftButton:
            local_pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            in_header = local_pos.y() <= self.header_frame.height() + 10
            in_footer = local_pos.y() >= self.height() - 28
            if in_header or in_footer:
                self._drag_pos = self._global_pos(event) - self.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and (event.buttons() & LeftButton):
            self.move(self._global_pos(event) - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)


def launch_gui() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 9))

    guard = SingleInstanceGuard(APP_SINGLETON_KEY)
    if not guard.try_acquire_or_notify_existing():
        sys.exit(0)

    store = TaskDataStore()
    win = LiteWeekMemoWindow(store)
    guard.on_activate_callback = win.bring_to_front
    win.show()

    exec_app = getattr(app, "exec", None) or getattr(app, "exec_", None)
    sys.exit(exec_app())


if __name__ == "__main__":
    launch_gui()