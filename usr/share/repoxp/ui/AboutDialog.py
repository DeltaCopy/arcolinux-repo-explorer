# This class stores static information about the app, and is displayed in the about dialog
import os
import gi

from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib

gi.require_version("Gtk", "3.0")

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class AboutDialog(Gtk.Dialog):
    def __init__(self, app_name, app_description, app_github, app_website):
        Gtk.Dialog.__init__(self)

        app_title = "About %s" % app_name

        app_secondary_message = "Explore Packages on your ArcoLinux system from only the ArcoLinux repositories"
        app_secondary_description = "Report issues to make it even better"
        app_version = "pkgversion-pkgrelease"

        app_authors = []
        app_authors.append(("Fennec (DeltaCopy)", None))

        pixbuf1 = GdkPixbuf.Pixbuf().new_from_file_at_size(
            os.path.join(base_dir, "images/search.png"), 100, 100
        )
        app_image1 = Gtk.Image().new_from_pixbuf(pixbuf1)

        self.set_resizable(False)
        self.set_size_request(560, 350)
        self.set_icon_from_file(os.path.join(base_dir, "images/search.png"))
        self.set_border_width(10)

        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.set_title(app_title)
        pixbuf2 = GdkPixbuf.Pixbuf().new_from_file_at_size(
            os.path.join(base_dir, "images/search.png"), 20, 20
        )
        app_image2 = Gtk.Image().new_from_pixbuf(pixbuf2)
        headerbar.pack_start(app_image2)

        self.set_titlebar(headerbar)

        btn_about_close = Gtk.Button(label="OK")
        btn_about_close.connect("clicked", self.on_response, "response")

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        stack.set_transition_duration(350)
        stack.set_hhomogeneous(False)
        stack.set_vhomogeneous(False)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
        stack_switcher.set_stack(stack)
        stack_switcher.set_homogeneous(True)

        lbl_main_title = Gtk.Label(xalign=0, yalign=0)
        lbl_main_title.set_markup("<b>%s</b>" % app_name)

        lbl_secondary_message = Gtk.Label(xalign=0, yalign=0)
        lbl_secondary_message.set_text("%s" % app_secondary_message)

        lbl_secondary_description = Gtk.Label(xalign=0, yalign=0)
        lbl_secondary_description.set_text("%s" % app_secondary_description)

        lbl_version = Gtk.Label(xalign=0, yalign=0)
        lbl_version.set_markup("<b>Version:</b> %s" % app_version)

        lbl_main_padding = Gtk.Label(xalign=0, yalign=0)

        ivbox_about = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        ivbox_about.pack_start(app_image1, True, True, 0)
        ivbox_about.pack_start(lbl_main_padding, True, True, 0)
        ivbox_about.pack_start(lbl_main_title, True, True, 0)
        ivbox_about.pack_start(lbl_version, True, True, 0)
        ivbox_about.pack_start(lbl_secondary_message, True, True, 0)
        ivbox_about.pack_start(lbl_secondary_description, True, True, 0)

        stack.add_titled(ivbox_about, "About %s" % app_name, "About")

        grid_support = Gtk.Grid()

        lbl_padding1 = Gtk.Label(xalign=0, yalign=0)
        lbl_padding1.set_text(" ")

        grid_support.attach(lbl_padding1, 0, 1, 1, 1)

        lbl_website_title = Gtk.Label(xalign=0, yalign=0)
        lbl_website_title.set_markup("<b>Website  </b>")

        lbl_website_value = Gtk.Label(xalign=0, yalign=0)
        lbl_website_value.set_text(app_website)
        lbl_website_value.set_selectable(True)
        lbl_website_value.set_justify(Gtk.Justification.LEFT)

        lbl_github_title = Gtk.Label(xalign=0, yalign=0)
        lbl_github_title.set_markup("<b>GitHub  </b>")

        lbl_author_title = Gtk.Label(xalign=0, yalign=0)
        lbl_author_title.set_markup("<b>Author  </b>")

        lbl_author_value = Gtk.Label(xalign=0, yalign=0)
        lbl_author_value.set_text("Fennec")
        lbl_author_value.set_selectable(True)
        lbl_author_value.set_justify(Gtk.Justification.LEFT)

        lbl_github_value = Gtk.Label(xalign=0, yalign=0)
        lbl_github_value.set_text(app_github)
        lbl_github_value.set_selectable(True)
        lbl_github_value.set_justify(Gtk.Justification.LEFT)

        grid_support.attach(lbl_website_title, 0, 3, 1, 1)
        grid_support.attach_next_to(
            lbl_website_value, lbl_website_title, Gtk.PositionType.RIGHT, 20, 1
        )

        grid_support.attach(lbl_github_title, 0, 4, 1, 1)
        grid_support.attach_next_to(
            lbl_github_value, lbl_github_title, Gtk.PositionType.RIGHT, 20, 1
        )

        grid_support.attach(lbl_author_title, 0, 5, 1, 1)
        grid_support.attach_next_to(
            lbl_author_value, lbl_author_title, Gtk.PositionType.RIGHT, 20, 1
        )

        stack.add_titled(grid_support, "Support", "Support")

        self.connect("response", self.on_response)

        self.vbox.add(stack_switcher)
        self.vbox.add(stack)

        self.show_all()

    def on_response(self, dialog, response):
        self.hide()
        self.destroy()
