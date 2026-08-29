import os
import webbrowser
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, QLabel, 
                             QPushButton, QApplication, QListWidgetItem, QSystemTrayIcon, QMenu, QTabWidget)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QImage, QKeyEvent, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from database import get_clips, get_favorites, toggle_favorite_db, delete_clip_db, clear_history_db

class ContextFlowWindow(QWidget):
    clip_added = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.is_dark_theme = True
        self.init_ui()
        self.init_tray()
        self.load_data()
        self.clip_added.connect(self.on_clip_added)

    def init_ui(self):
        self.setWindowTitle("ContextFlow")
        self.resize(620, 740)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        self.apply_theme_styles()
        
        # Глобальный/контекстный хокей на открытие/скрытие по Ctrl + Shift + Space
        self.shortcut = QShortcut(QKeySequence("Ctrl+Shift+Space"), self)
        self.shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut.activated.connect(self.toggle_window)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search history or press 1-9 to quick-copy...")
        self.search_input.textChanged.connect(self.filter_clips)
        top_layout.addWidget(self.search_input)
        
        self.theme_btn = QPushButton("☀️")
        self.theme_btn.setObjectName("iconBtn")
        self.theme_btn.setToolTip("Toggle Theme")
        self.theme_btn.setFixedSize(42, 42)
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_layout.addWidget(self.theme_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setToolTip("Clear unlocked history")
        self.clear_btn.clicked.connect(self.clear_history_action)
        top_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(top_layout)
        
        self.tabs = QTabWidget()
        
        self.history_list = QListWidget()
        self.setup_list_widget(self.history_list)
        
        self.favorites_list = QListWidget()
        self.setup_list_widget(self.favorites_list)
        
        self.tabs.addTab(self.history_list, "🕒 History")
        self.tabs.addTab(self.favorites_list, "⭐ Favorites")
        main_layout.addWidget(self.tabs)
        
        self.hint_label = QLabel("Double-click to copy  •  Press [1-9] for quick copy  •  Right-click for options")
        self.hint_label.setStyleSheet("color: #71717a; font-size: 11px; font-weight: 500;")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.hint_label)
        
        self.setLayout(main_layout)

    def apply_theme_styles(self):
        if self.is_dark_theme:
            self.setStyleSheet("""
                QWidget {
                    background-color: #0b0b0e;
                    color: #f1f1f4;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-size: 13px;
                }
                QTabWidget::pane {
                    border: 1px solid #1c1c21;
                    border-radius: 14px;
                    background-color: #0f0f13;
                }
                QTabBar::tab {
                    background-color: transparent;
                    color: #6c6c75;
                    padding: 10px 24px;
                    font-weight: 600;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    margin-right: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #17171c;
                    color: #ffffff;
                    border-bottom: 2px solid #3b82f6;
                }
                QLineEdit {
                    background-color: #141418;
                    border: 1px solid #22222b;
                    border-radius: 12px;
                    padding: 12px 18px;
                    color: #ffffff;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #3b82f6;
                    background-color: #18181e;
                }
                QPushButton#clearBtn {
                    background-color: #141418;
                    border: 1px solid #22222b;
                    border-radius: 12px;
                    color: #9ca3af;
                    padding: 0 16px;
                    font-weight: 600;
                }
                QPushButton#clearBtn:hover {
                    background-color: #1f1f26;
                    color: #ef4444;
                    border: 1px solid #ef4444;
                }
                QPushButton#iconBtn {
                    background-color: #141418;
                    border: 1px solid #22222b;
                    border-radius: 12px;
                    font-size: 16px;
                }
                QPushButton#iconBtn:hover {
                    background-color: #1f1f26;
                }
                QListWidget {
                    background-color: transparent;
                    border: none;
                    padding: 6px;
                }
                QListWidget::item {
                    background-color: #15151a;
                    margin-bottom: 10px;
                    padding: 12px;
                    border-radius: 12px;
                    border: 1px solid #23232d;
                    color: #d1d1d6;
                }
                QListWidget::item:hover {
                    background-color: #1a1a23;
                    border: 1px solid #333342;
                }
                QListWidget::item:selected {
                    background-color: #1b2230;
                    border: 1px solid #3b82f6;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fc;
                    color: #1f2937;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-size: 13px;
                }
                QTabWidget::pane {
                    border: 1px solid #e5e7eb;
                    border-radius: 14px;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: transparent;
                    color: #6b7280;
                    padding: 10px 24px;
                    font-weight: 600;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    margin-right: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #f3f4f6;
                    color: #111827;
                    border-bottom: 2px solid #2563eb;
                }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #d1d5db;
                    border-radius: 12px;
                    padding: 12px 18px;
                    color: #111827;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #2563eb;
                    background-color: #ffffff;
                }
                QPushButton#clearBtn {
                    background-color: #ffffff;
                    border: 1px solid #d1d5db;
                    border-radius: 12px;
                    color: #4b5563;
                    padding: 0 16px;
                    font-weight: 600;
                }
                QPushButton#clearBtn:hover {
                    background-color: #fee2e2;
                    color: #dc2626;
                    border: 1px solid #fca5a5;
                }
                QPushButton#iconBtn {
                    background-color: #ffffff;
                    border: 1px solid #d1d5db;
                    border-radius: 12px;
                    font-size: 16px;
                }
                QPushButton#iconBtn:hover {
                    background-color: #f3f4f6;
                }
                QListWidget {
                    background-color: transparent;
                    border: none;
                    padding: 6px;
                }
                QListWidget::item {
                    background-color: #ffffff;
                    margin-bottom: 10px;
                    padding: 12px;
                    border-radius: 12px;
                    border: 1px solid #e5e7eb;
                    color: #374151;
                }
                QListWidget::item:hover {
                    background-color: #f9fafb;
                    border: 1px solid #d1d5db;
                }
                QListWidget::item:selected {
                    background-color: #eff6ff;
                    border: 1px solid #2563eb;
                    color: #1e3a8a;
                }
            """)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.theme_btn.setText("☀️" if self.is_dark_theme else "🌙")
        self.apply_theme_styles()
        self.load_data()

    def setup_list_widget(self, list_widget):
        list_widget.setIconSize(QSize(160, 100))
        list_widget.setStyleSheet("QListWidget::item { height: 115px; }")
        list_widget.itemDoubleClicked.connect(self.copy_selected_clip)
        list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(self.open_context_menu)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        tray_menu = QMenu()
        show_action = QAction("Show ContextFlow", self)
        show_action.triggered.connect(self.toggle_window)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_clicked)

    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_window()

    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def create_item(self, clip_id, category, content, is_favorite, index=None):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, (clip_id, category, content))
        
        star = "★ " if is_favorite else "☆ "
        idx_prefix = f"[{index}] " if index is not None else ""
        
        cat_lower = category.lower()
        if cat_lower == "code":
            badge = "💻 CODE"
            item.setForeground(QColor("#60a5fa") if self.is_dark_theme else QColor("#2563eb"))
        elif cat_lower == "link":
            badge = "🔗 LINK"
            item.setForeground(QColor("#34d399") if self.is_dark_theme else QColor("#059669"))
        elif cat_lower == "image":
            badge = "🖼 IMAGE"
            item.setForeground(QColor("#c084fc") if self.is_dark_theme else QColor("#7c3aed"))
        else:
            badge = "📄 TEXT"
        
        if cat_lower == "image" and os.path.exists(content):
            item.setText(f"{idx_prefix}{star}  {badge}    {os.path.basename(content)}")
            pixmap = QPixmap(content)
            if not pixmap.isNull():
                icon = QIcon(pixmap.scaled(160, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
                item.setIcon(icon)
        else:
            clean_content = content.replace(chr(10), ' ')
            if len(clean_content) > 80:
                clean_content = clean_content[:80] + "..."
            item.setText(f"{idx_prefix}{star}  {badge}\n\n{clean_content}")
            
        return item

    def load_data(self):
        self.history_list.clear()
        for idx, (clip_id, category, content, created_at, is_favorite) in enumerate(get_clips(), start=1):
            item = self.create_item(clip_id, category, content, is_favorite, index=idx if idx <= 9 else None)
            self.history_list.addItem(item)
            
        self.favorites_list.clear()
        for idx, (clip_id, category, content, created_at, is_favorite) in enumerate(get_favorites(), start=1):
            item = self.create_item(clip_id, category, content, is_favorite, index=idx if idx <= 9 else None)
            self.favorites_list.addItem(item)

    def on_clip_added(self, content, category):
        self.load_data()

    def filter_clips(self, query):
        current_list = self.tabs.currentWidget()
        for i in range(current_list.count()):
            item = current_list.item(i)
            item.setHidden(query.lower() not in item.text().lower())

    def clear_history_action(self):
        clear_history_db()
        self.load_data()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            index = key - Qt.Key.Key_1
            current_list = self.tabs.currentWidget()
            if current_list.count() > index:
                item = current_list.item(index)
                if item:
                    self.copy_selected_clip(item)
                    return
        super().keyPressEvent(event)

    def open_context_menu(self, position):
        current_list = self.tabs.currentWidget()
        item = current_list.itemAt(position)
        if not item:
            return
            
        clip_id, category, content = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        if self.is_dark_theme:
            menu.setStyleSheet("""
                QMenu {
                    background-color: #17171c;
                    color: #f1f1f4;
                    border: 1px solid #2b2b36;
                    border-radius: 10px;
                    padding: 6px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-weight: 500;
                }
                QMenu::item:selected {
                    background-color: #3b82f6;
                    color: #ffffff;
                }
            """)
        else:
            menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    color: #1f2937;
                    border: 1px solid #d1d5db;
                    border-radius: 10px;
                    padding: 6px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-weight: 500;
                }
                QMenu::item:selected {
                    background-color: #2563eb;
                    color: #ffffff;
                }
            """)
        
        fav_action = menu.addAction("⭐ Toggle Favorite")
        
        open_action = None
        if category.lower() == "link":
            open_action = menu.addAction("🌐 Open in Browser")
            
        delete_action = menu.addAction("🗑️ Delete Clip")
        
        action = menu.exec(current_list.mapToGlobal(position))
        
        if action == fav_action:
            toggle_favorite_db(clip_id)
            self.load_data()
        elif open_action and action == open_action:
            webbrowser.open(content)
            self.hide()
        elif action == delete_action:
            delete_clip_db(clip_id)
            self.load_data()

    def copy_selected_clip(self, item):
        _, _, raw_content = item.data(Qt.ItemDataRole.UserRole)
        if raw_content:
            app = QApplication.instance()
            if os.path.exists(raw_content):
                app.clipboard().setImage(QImage(raw_content))
                print(f"copied image back: {raw_content}")
            else:
                app.clipboard().setText(raw_content)
                print(f"copied text back: {raw_content[:30]}...")
            self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()