import asciimatics as am
import asciimatics.widgets as am_widgets
import asciimatics.scene as am_scene
import asciimatics.screen as am_screen
import asciimatics.exceptions as am_exceptions
import sys
from collections import defaultdict

options_main = [
                ("t", "Use pure tones", "Frame_Tone"),
                ("n", "Use noise", "Frame_Noise")
               ]
options_tone = [
                ("f", "Specify frequency in Hz.", "Frame_Tone_Freq"),
                ("a", "Specify amplitude in v.", "Frame_Tone_Amp"),
                ("d", "Specify duration in s.", "Frame_Tone_Dur"),
                ("p", "Play stimulus", "Frame_Play"),
               ]
options_noise = [
                ("h", "Specify hi-pass (lo-side) cutoff in Hz.", "Frame_Noise_hp"),
                ("l", "Specify lo-pass (hi-side) cutoff in Hz.", "Frame_Noise_lp"),
                ("a", "Specify amplitude in v.", "Frame_Noise_Amp"),
                ("d", "Specify duration in s.", "Frame_Noise_Dur"),
                ("p", "Play stimulus", "Frame_Play"),
               ]

class Interface():
    def __init__(self):
        am_screen.Screen.wrapper(main, catch_interrupt=True, arguments=[last_scene])

    class Frame_Main(am_widgets.Frame):
        def __init__(self, screen, options, breadcrumb, prev_frame=None):
            super(Frame_Main, self).__init__(screen,
                                            screen.height,
                                            screen.width,
                                            title="Calibrate!")

            self 

            self.options = options
            self.breadcrumb = breadcrumb
            self.frame_previous = prev_frame

            layout = am_widgets.Layout([1], fill_frame=True)
            self._breadcrumb = am_widgets.Label(self.breadcrumb)
            self._hl = am_widgets.Divider()
            self._blankline = am_widgets.Divider(height=1, draw_line=False)
            self._explain = am_widgets.Label("Option - Explanation")
            self._list = am_widgets.ListBox(
                am_widgets.Widget.FILL_FRAME,
                options=[],
                on_select=self._on_select,
                name="list_main")
            options_l = []
            self.keys = []
            for val in self.options:
                options_l.append( ("     {} - {}".format(val[0], val[1]), self.options.index(val)) )
                self.keys.append(ord(val[0]))
            if self.frame_previous:
                options_l.append(("     b - Back", len(self.options)))
                self._instructions = am_widgets.Label("Choose an option, `b` to go back or `q` to quit.")
            else:
                self._instructions = am_widgets.Label("Choose an option or `q` to quit.")
            options_l.append(("     q - Quit", len(self.options)))
            self._list.options = options_l
            self.add_layout(layout)
            layout.add_widget(self._breadcrumb)
            layout.add_widget(self._hl)
            layout.add_widget(self._blankline)
            layout.add_widget(self._explain)
            layout.add_widget(self._blankline)
            layout.add_widget(self._list)
            layout.add_widget(self._instructions)
            self.fix()

            # Add my own colour palette
            self.palette = defaultdict(
                lambda: (am_screen.Screen.COLOUR_WHITE, am_screen.Screen.A_NORMAL, am_screen.Screen.COLOUR_BLACK))
            for key in ["selected_focus_field", "label"]:
                self.palette[key] = (am_screen.Screen.COLOUR_WHITE, am_screen.Screen.A_BOLD, am_screen.Screen.COLOUR_BLACK)
            self.palette["title"] = (am_screen.Screen.COLOUR_BLACK, am_screen.Screen.A_NORMAL, am_screen.Screen.COLOUR_WHITE)

        def process_event(self, event):

            if isinstance(event, am.event.KeyboardEvent):

                if event.key_code in self.keys:
                    frame = self.options[ self.keys.index(event.key_code) ] [2]
                    self.next_scene(frame)

                elif event.key_code in [ord('b')] and self.frame_previous:
                    self.next_scene(self.frame_previous)

                elif event.key_code in [ord('q')]:
                    self._scene.add_effect(
                        am_widgets.PopUpDialog(self._screen,
                                    "Really quit?",
                                    ["No", "Yes"],
                                    on_close=self._confirm_quit))


                elif event.key_code in [10, 12, 13]:
                    self._on_select()

                # Force a refresh for improved responsiveness
                self._last_frame = 0

            # Now pass on to lower levels for normal handling of the event.
            return super(Frame_Main, self).process_event(event)

        def _on_select(self):
            value = self._list.value
            if value < len(self.options):
                raise am_exceptions.NextScene(self.options[value][2])

            elif value == len(self.options):
                if self.frame_previous != "":
                    raise am_exceptions.NextScene(self.frame_previous)
                else:
                    self._scene.add_effect(
                        am_widgets.PopUpDialog(self._screen,
                                    "Really quit?",
                                    ["No", "Yes"],
                                    on_close=self._confirm_quit))
            elif value == len(self.options) + 1:
                self._scene.add_effect(
                    am_widgets.PopUpDialog(self._screen,
                                "Really quit?",
                                ["No", "Yes"],
                                on_close=self._confirm_quit))


    def get_resp(self):
        """Waits modally for a keypress
        """
        self.dialog.waitingForResponse = True
        sys.stdout.flush() # In case the output of a prior print statement has been buffered
        while self.dialog.waitingForResponse:
            self.app.processEvents()
            time.sleep(.1)
        curchar = self.dialog.char
        self.dialog.char = ''
        return curchar

    def showPlaying(self, playing):
        self.dialog.isPlaying.setVisible(playing)
        self.update_form()

    def updateInfo_Exp(self, s):
        self.dialog.expLabel.setText(s)
        self.update_form()

    def updateInfo_Block(self, s):
        self.dialog.blockLabel.setText(s)
        self.update_form()

    def updateInfo_Trial(self, s):
        self.dialog.trialLabel.setText(s)
        self.update_form()

    def updateInfo_BlockScore(self, s):
        self.dialog.blockScore.setText(s)
        self.update_form()

    def updateInfo_TrialScore(self, s):
        self.dialog.trialScore.setText(s)
        self.update_form()

    def updateInfo_blockVariables(self, s):
        self.dialog.blockVariables.setText(s)
        self.update_form()

    def updateInfo_expVariables(self, s):
        self.dialog.expVariables.setText(s)
        self.update_form()

    def updateInfo_BlockCount(self, s):
        self.dialog.blocks.setText(s)
        self.update_form()
        
    def update_form(self):
        # have to call this twice or some widgets won't update
        self.app.processEvents()
        self.app.processEvents()


    def main(screen, scene):
        scenes = [
            am_scene.Scene([Frame_Main(screen, options_main, "Main")], -1, name="Frame_Main"),
            am_scene.Scene([Frame_Tone(screen, options_tone, "Main / Pure Tones", "Frame_Main")], -1, name="Frame_Tone"),
            am_scene.Scene([Frame_Noise(screen, options_noise, "Main / Noise", "Frame_Main")], -1, name="Frame_Noise"),
        ]
        screen.play(scenes, stop_on_resize=True, start_scene=scene)

last_scene = None
while True:
    try:
        am_screen.Screen.wrapper(main, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except am_exceptions.ResizeScreenError as e:
        last_scene = e.scene
