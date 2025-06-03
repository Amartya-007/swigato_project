import customtkinter as ctk
import os
from gui_constants import (
    FRAME_FG_COLOR, FRAME_BORDER_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, 
    TEXT_COLOR, ICON_PATH, set_swigato_icon, safe_focus, center_window
)

class SwigatoDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Swigato", message="", icon_path=ICON_PATH, buttons=None, width=350, height=160):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        
        # Center the dialog on screen
        center_window(self, width, height)
        
        self.grab_set()
        self.transient(parent)
        self.configure(fg_color=FRAME_FG_COLOR, border_color=FRAME_BORDER_COLOR, border_width=1)
        
        # Set Swigato icon safely
        set_swigato_icon(self)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # Message
        self.message_label = ctk.CTkLabel(self, text=message, text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        self.message_label.grid(row=0, column=0, padx=24, pady=(28, 10), sticky="nwe")        # Buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="e")
        
        if buttons:
            for btn in buttons:
                button = ctk.CTkButton(
                    self.button_frame,
                    text=btn.get("text", "OK"),
                    command=btn.get("command", self.destroy),
                    fg_color=btn.get("fg_color", PRIMARY_COLOR),
                    hover_color=btn.get("hover_color", BUTTON_HOVER_COLOR),
                    text_color=btn.get("text_color", "white"),
                    width=btn.get("width", 90),
                    font=ctk.CTkFont(size=13, weight="bold")                )
                button.pack(side="right", padx=(10, 0))
        else:
            ok_button = ctk.CTkButton(
                self.button_frame,
                text="OK",
                command=self.destroy,
                fg_color=PRIMARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color="white",
                width=90,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            ok_button.pack(side="right")
            
        # Removed focus call to avoid TclError when dialog is destroyed
        # self.after(100, lambda: safe_focus(self))

    @staticmethod
    def show_info(parent, title, message):
        SwigatoDialog(parent, title=title, message=message)

    @staticmethod
    def show_error(parent, title, message):
        SwigatoDialog(parent, title=title, message=message, buttons=[{"text": "OK", "fg_color": "#E53935"}])

    @staticmethod
    def show_warning(parent, title, message):
        SwigatoDialog(parent, title=title, message=message, buttons=[{"text": "OK", "fg_color": "#FFA000"}])

    @staticmethod
    def ask_yes_no(parent, title, message):
        result = {"value": False}
        def on_yes():
            result["value"] = True
            dialog.destroy()
        def on_no():
            result["value"] = False
            dialog.destroy()
        dialog = SwigatoDialog(
            parent,
            title=title,
            message=message,
            buttons=[
                {"text": "Yes", "fg_color": PRIMARY_COLOR, "command": on_yes},
                {"text": "No", "fg_color": "#B0BEC5", "command": on_no}
            ]
        )
        parent.wait_window(dialog)
        return result["value"]
