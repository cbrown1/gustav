import os
import json
import requests


class Interface():
    def __init__(self, alternatives=2, prompt='Choose an alternative'):
        self.prompt = prompt
        self.alternatives = alternatives
        with open('style.json') as f:
            self.style = json.load(f)

    def get_resp(self, timeout=None):
        try:
            waiting = True
            timeout_start = time.time()
            while waiting:
                # Check if new output generated by the server
                if new_output:
                    waiting = False
                    ret = output
            return ret

        except:
            self.destroy()
            raise Exception('Error getting input')

    def destroy(self):
        # Stop experiment
        pass

    def update(self, filename="test.json"):
        """
        Update the interface
        """
        self.out = {}
        with open(filename, 'w') as f:
            json.dump(self.out, f)

    # Use instead of update_Status_Right etc
    def update_text(self):
        pass

    def show_Notify_Left(self, show=None):
        """Show the left notify text

            If show==None, toggle.
            Otherwise show should be a bool.
        """
        if show is not None:
            self.notify_l_show = show
        else:
            self.notify_l_show = not self.notify_l_show

    def update_Notify_Right(self, s, show=None):
        """Update the notify text to the left of the face.

            show is a bool specifying whether to show the text,
            set to None to leave this param unchanged [default].
            show can also be set with show_Notify_Left.
        """
        self.notify_r_str = s
        if show is not None:
            self.notify_r_show = show

    def show_Notify_Right(self, show=None):
        """Show the right notify text

            If show==None, toggle.
            Otherwise show should be a bool.
        """

        if show is not None:
            self.notify_r_show = show
        else:
            self.notify_r_show = not self.notify_r_show

    def update_Notify_Right(self, s, show=None):
        """Update the notify text to the left of the face.

            show is a bool specifying whether to show the text,
            set to None to leave this param unchanged [default].
            show can also be set with show_Notify_Left.
        """
        self.notify_r_str = s
        if show is not None:
            self.notify_r_show = show

    def show_Buttons(self, show=None):
        """Show the position bar

           If show==None, toggle show.
           Otherwise show should be a bool.
        """
        if show is not None:
            self.buttons_show = show
        else:
            self.buttons_show = not self.buttons_show

    def show_Prompt(self, show=None):
        """Show the prompt

           If show==None, toggle show.
           Otherwise show should be a bool.
        """
        if show is not None:
            self.prompt_show = show
        else:
            self.prompt_show = not self.prompt_show

    def update_Prompt(self, s, show=True):
        """Update the text of the prompt

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.prompt = s
        self.prompt_show = show

    def show_Buttons(self, show=None):
        """Show the position bar

           If show==None, toggle show and force a redraw. Otherwise
            show should be a bool.

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        if show is not None:
            self.buttons_show = show
        else:
            self.buttons_show = not self.buttons_show

    def update_Status_Left(self, s, redraw=False):
        """Update the text on the left side of the status bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.status_l_str = s
        if redraw:
            self.redraw()

    def update_Status_Right(self, s, redraw=False):
        """Update the text on the right side of the status bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.status_r_str = s

    def update_Status_Center(self, s, redraw=False):
        """Update the text in the center of the status bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.status_c_str = s
        if redraw:
            self.redraw()

    def update_Title_Left(self, s, redraw=False):
        """Update the text on the left side of the title bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.title_l_str = s
        if redraw:
            self.redraw()

    def update_Title_Right(self, s, redraw=False):
        """Update the text on the right side of the title bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.title_r_str = s
        if redraw:
            self.redraw()

    def update_Title_Center(self, s, redraw=False):
        """Update the text in the center of the title bar

            redraw is a bool specifying whether to redraw window.
            A window redraw can also be set with update.
        """
        self.title_c_str = s
        if redraw:
            self.redraw()