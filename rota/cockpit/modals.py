"""
The two modal screens the cockpit pushes.

Copied from the old TUI's `src/ui/modals.py` when rota moved to its own
repository. Both were imported inside a function, from a module outside the
package, so the cockpit reached across the repository root to find them. In a
repository that holds only rota there is no outside.

The cockpit already carries the CSS for both. `#input_modal_container` and
`#confirmation_container` are styled in `tui.py`, so the appearance does not
change.
"""
from __future__ import annotations

from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class ConfirmationModal(ModalScreen):
    """Ask the principal to confirm, and report True or False."""

    def __init__(self, prompt_text, callback=None):
        super().__init__()
        self.prompt_text = prompt_text
        self.callback = callback

    def compose(self):
        with Center():
            with Vertical(id="confirmation_container"):
                yield Label(self.prompt_text)
                with Horizontal():
                    yield Button("Confirm", id="modal_confirm", variant="primary")
                    yield Button("Cancel", id="modal_cancel")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "modal_confirm":
            if self.callback:
                self.callback(True)
            self.app.pop_screen()
        elif event.button.id == "modal_cancel":
            if self.callback:
                self.callback(False)
            self.app.pop_screen()


class InputModal(ModalScreen):
    """Ask the principal for a line of text, and report it or None."""

    def __init__(self, title, message, callback=None):
        super().__init__()
        self.title = title
        self.message = message
        self.callback = callback

    def compose(self):
        with Vertical(id="input_modal_container"):
            yield Label(f"{self.title}: {self.message}")
            yield Input(placeholder="Enter value...", id="modal_input")
            with Horizontal():
                yield Button("Submit", id="modal_submit", variant="primary")
                yield Button("Cancel", id="modal_cancel")

    def on_mount(self):
        self.query_one("#modal_input", Input).focus()

    def on_input_submitted(self, event):
        self.handle_submit(event.value)

    def on_button_pressed(self, event):
        if event.button.id == "modal_submit":
            input_widget = self.query_one("#modal_input", Input)
            self.handle_submit(input_widget.value)
        elif event.button.id == "modal_cancel":
            self.handle_cancel()

    def handle_submit(self, value):
        if self.callback:
            self.callback(value)
        self.app.pop_screen()

    def handle_cancel(self):
        if self.callback:
            self.callback(None)
        self.app.pop_screen()
