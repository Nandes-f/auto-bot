import sys
import time
import random
import os
import traceback
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QSpinBox, QSystemTrayIcon, 
                            QMenu, QDialog, QFormLayout, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap
import pyautogui
import ctypes
import winreg

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedSize(400, 150)
        
        layout = QFormLayout()
        
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 9999)
        self.time_input.setValue(30)
        layout.addRow("Session duration (minutes):", self.time_input)
        

        self.interval_input = QSpinBox()
        self.interval_input.setRange(5, 120)
        self.interval_input.setValue(25)
        layout.addRow("Action interval (seconds):", self.interval_input)
        
        buttons = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        buttons.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_btn)
        
        layout.addRow(buttons)
        self.setLayout(layout)

class XamppBot(QWidget):
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.remaining_time = 30 * 60  
        self.action_interval = 25  
        self.lock_scheduled = False
        self.current_action_index = 0  
        self.action_sequence = ['alt_tab', 'ctrl_tab', 'scroll']  
        
        
        self.setup_tray_icon()
        
        self.setup_ui()
        
        self.action_timer = QTimer()
        self.action_timer.timeout.connect(self.perform_actions)
        
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        
        self.screen_width, self.screen_height = pyautogui.size()
        
        self.add_to_startup()
        
        pyautogui.FAILSAFE = False  
        pyautogui.PAUSE = 0.1       

    def setup_ui(self):
        self.setWindowTitle("Xampp")
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Not Working")
        self.status_label.setStyleSheet("font-weight: bold; color: #555;")
        layout.addWidget(self.status_label)
        
        self.time_label = QLabel("Remaining: --:--")
        layout.addWidget(self.time_label)
        
        layout.addStretch(1)
        
        button_layout = QHBoxLayout()
        
        self.toggle_button = QPushButton("Start")
        self.toggle_button.setFixedHeight(40)
        self.toggle_button.clicked.connect(self.toggle_bot)
        button_layout.addWidget(self.toggle_button)
        
        settings_button = QPushButton("Settings")
        settings_button.setFixedHeight(40)
        settings_button.clicked.connect(self.show_settings)
        button_layout.addWidget(settings_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.hide()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("system-run"))
        
        self.tray_menu = QMenu()
        
        self.show_action = self.tray_menu.addAction("Show Control Panel")
        self.show_action.triggered.connect(self.show_normal)
        
        self.status_action = self.tray_menu.addAction("Status: Not Working")
        self.status_action.setEnabled(False)
        
        self.time_action = self.tray_menu.addAction("Remaining: --:--")
        self.time_action.setEnabled(False)
        
        self.tray_menu.addSeparator()
        
        self.toggle_action = self.tray_menu.addAction("Start Session")
        self.toggle_action.triggered.connect(self.toggle_bot)
        
        settings_action = self.tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings)
        
        self.tray_menu.addSeparator()
        
        exit_action = self.tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_app)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_normal()

    def show_normal(self):
        self.show()
        self.activateWindow()
        self.raise_()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def toggle_bot(self):
        if self.is_running:
            self.stop_bot()
        else:
            self.start_bot()

    def start_bot(self):
        if not self.is_running:
            self.is_running = True
            self.lock_scheduled = False
            self.current_action_index = 0  
            self.update_ui_status("Running")
            
            self.update_time_display()
            
            self.perform_actions()
            
            self.action_timer.start(self.action_interval * 1000)
            self.countdown_timer.start(1000)

    def stop_bot(self):
        if self.is_running:
            self.is_running = False
            self.update_ui_status("Stopped")
            
            self.action_timer.stop()
            self.countdown_timer.stop()

    def update_ui_status(self, status):
        color = "#008800" if status == "Running" else "#555555"
        
        self.status_action.setText(f"Status: {status}")
        self.status_label.setText(f"Status: {status}")
        self.status_label.setStyleSheet(f"font-weight: bold; color: {color};")
        self.toggle_action.setText("Stop Session" if status == "Running" else "Start Session")
        self.toggle_button.setText("Stop" if status == "Running" else "Start")
        if status == "Running":
            self.toggle_button.setStyleSheet("background-color: #ffcccc;")
        else:
            self.toggle_button.setStyleSheet("")

    def perform_actions(self):
        if not self.is_running:
            return
            
        try:
            action_type = self.action_sequence[self.current_action_index]
            
            self.current_action_index = (self.current_action_index + 1) % len(self.action_sequence)
            
            
            if action_type == 'alt_tab':
                pyautogui.keyDown('alt')
                time.sleep(random.uniform(0.1, 0.2))
                
                tab_count = random.choice([1, 1, 1, 2, 2, 3])
                for _ in range(tab_count):
                    pyautogui.press('tab')
                    time.sleep(random.uniform(0.1, 0.3))
                
                time.sleep(random.uniform(0.2, 0.5))
                pyautogui.keyUp('alt')
                
                if random.random() > 0.5:
                    time.sleep(random.uniform(0.5, 1.0))
                
            elif action_type == 'ctrl_tab':
                pyautogui.keyDown('ctrl')
                time.sleep(random.uniform(0.1, 0.2))
                
                tab_count = random.choice([1, 1, 2, 2, 3])
                for _ in range(tab_count):
                    pyautogui.press('tab')
                    time.sleep(random.uniform(0.1, 0.25))
                
                time.sleep(random.uniform(0.1, 0.3))
                pyautogui.keyUp('ctrl')
                
            else:  # scroll
                direction = random.choice([-1, 1])
                
                scroll_count = random.randint(2, 5)
                for _ in range(scroll_count):
                    if not self.is_running:
                        break
                    
                    amount = random.randint(50, 150) * direction
                    pyautogui.scroll(amount)
                    time.sleep(random.uniform(0.1, 0.4))
                
                if random.random() > 0.7:
                    time.sleep(random.uniform(0.3, 0.7))
                    direction = -direction
                    for _ in range(random.randint(1, 3)):
                        amount = random.randint(30, 100) * direction
                        pyautogui.scroll(amount)
                        time.sleep(random.uniform(0.1, 0.3))
                
        except Exception as e:
            traceback.print_exc()

    def update_countdown(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_time_display()
        else:
            if not self.lock_scheduled:
                self.lock_scheduled = True
                self.perform_final_actions()
                QTimer.singleShot(2000, self.finalize_session)

    def perform_final_actions(self):
        try:
            pyautogui.keyDown('alt')
            time.sleep(0.2)
            
            tab_count = 3
            for _ in range(tab_count):
                pyautogui.press('tab')
                time.sleep(0.2)
            
            time.sleep(0.3)
            pyautogui.keyUp('alt')
            time.sleep(0.7)
            
            pyautogui.keyDown('ctrl')
            time.sleep(0.2)
            
            for _ in range(2):
                pyautogui.press('tab')
                time.sleep(0.2)
            
            pyautogui.keyUp('ctrl')
            time.sleep(0.7)
            
            for _ in range(3):
                pyautogui.scroll(100)
                time.sleep(0.3)
            
            time.sleep(0.5)
            
            for _ in range(3):
                pyautogui.scroll(-100)
                time.sleep(0.3)
            
        except Exception as e:
            traceback.print_exc()

    def finalize_session(self):
        self.stop_bot()
        self.cleanup_before_lock()
        QTimer.singleShot(1000, self.lock_computer)

    def cleanup_before_lock(self):
        try:
            for key in ['alt', 'ctrl', 'shift', 'win']:
                pyautogui.keyUp(key)
            
            pyautogui.moveTo(self.screen_width - 10, self.screen_height - 10, duration=0.5)
            
            pyautogui.press('esc')
            time.sleep(0.5)
        except Exception as e:
            traceback.print_exc()

    def update_time_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_str = f"Time remaining: {minutes:02d}:{seconds:02d}"
        self.time_action.setText(time_str)
        self.time_label.setText(time_str)

    def show_settings(self):
        try:
            dialog = SettingsDialog()
            dialog.time_input.setValue(self.remaining_time // 60)
            dialog.interval_input.setValue(self.action_interval)
            
            if dialog.exec_():
                new_time_minutes = dialog.time_input.value()
                self.remaining_time = new_time_minutes * 60
                self.action_interval = dialog.interval_input.value()
                
                
                if self.is_running:
                    self.action_timer.setInterval(self.action_interval * 1000)
                self.update_time_display()
        except Exception as e:
            traceback.print_exc()

    def lock_computer(self):
        try:
            for _ in range(3):
                result = ctypes.windll.user32.LockWorkStation()
                if result == 1:
                    break
                time.sleep(0.5)
            
            QTimer.singleShot(5000, self.exit_after_lock)
            
        except Exception as e:
            traceback.print_exc()
            QMessageBox.warning(None, "Lock Failed",)
            QTimer.singleShot(5000, self.exit_after_lock)

    def exit_after_lock(self):
        self.tray_icon.hide()
        QApplication.quit()

    def add_to_startup(self):
        try:
            key = winreg.HKEY_CURRENT_USER
            key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                winreg.SetValueEx(reg_key, "Xampp", 0, winreg.REG_SZ, 
                               f'"{sys.executable}" "{os.path.abspath(__file__)}"')
        except WindowsError as e:
            pass

    def exit_app(self):
        self.stop_bot()
        self.tray_icon.hide()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    def exception_hook(exctype, value, traceback):
        sys.__excepthook__(exctype, value, traceback)
    sys.excepthook = exception_hook
    
    bot = XamppBot()
    sys.exit(app.exec_())