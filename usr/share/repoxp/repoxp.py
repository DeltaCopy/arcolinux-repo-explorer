#!/usr/bin/env python3

import gi
import os
import signal
import datetime
import threading
from threading import Thread
from libs.Functions import Functions
from ui.PackageDialog import PackageDialog
from ui.MessageDialog import MessageDialog

fn = Functions()


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib

base_dir = os.path.dirname(os.path.realpath(__file__))
app_name = "ArcoLinux RepoXPlorer"
app_desc = "Explore ArcoLinux Package Repos"


class Main(Gtk.Window):
    def __init__(self):
        try:
            super(Main, self).__init__(title=app_name)

            self.set_border_width(10)
            self.connect("delete-event", self.on_close)
            self.set_position(Gtk.WindowPosition.CENTER)

            self.set_default_size(800, 500)

            headerbar = Gtk.HeaderBar()
            headerbar.set_title("%s" % app_name)
            headerbar.set_show_close_button(True)

            self.set_titlebar(headerbar)
            self.package_name = None

            self.lbl_pacman_sync_db = Gtk.Label(xalign=0, yalign=0)
            self.lbl_pacman_sync_db.set_selectable(True)

            self.sync_data()

            if self.pacman_sync == "Pacman syncronization failed":
                self.lbl_pacman_sync_db.set_markup(
                    "Pacman DB Synchronization: <b>Failed </b>"
                )
            else:
                self.lbl_pacman_sync_db.set_markup(
                    "Pacman DB Synchronized at <b>%s</b>"
                    % datetime.datetime.now().strftime("%H:%M:%S")
                )

            self.setup_gui()

        except Exception as e:
            fn.logger.error("Exception in Main() : %s" % e)

    def sync_data(self):
        fn.logger.info("Synchronizing pacman package database")

        thread_pacman_sync_db = Thread(
            target=fn.sync_package_db,
            daemon=True,
        )
        thread_pacman_sync_db.start()
        self.pacman_sync = fn.pacman_data_queue.get()
        fn.pacman_data_queue.task_done()

        try:
            thread_pacman_sync_data = Thread(
                target=fn.get_package_sync_data,
                daemon=True,
            )
            thread_pacman_sync_data.start()

            self.pacman_data = fn.pacman_data_queue.get()
            fn.pacman_data_queue.task_done()

        except Exception as e:
            fn.logger.error(e)

    def setup_gui(self):
        # fn.get_package_sync_data
        self.treeview_loaded = False
        self.repo_selected = "arcolinux_repo"

        rb_arco_repo = Gtk.RadioButton.new_with_label_from_widget(
            None, "arcolinux_repo"
        )
        rb_arco_repo.set_name("rb_arco_repo")

        rb_arco_repo.connect(
            "toggled", self.on_rb_toggled, self.pacman_data, "arcolinux_repo"
        )

        rb_arco_3rdparty_repo = Gtk.RadioButton.new_from_widget(rb_arco_repo)
        rb_arco_3rdparty_repo.set_label("arcolinux_repo_3party")
        rb_arco_3rdparty_repo.connect(
            "toggled",
            self.on_rb_toggled,
            self.pacman_data,
            "arcolinux_repo_3party",
        )
        rb_arco_3rdparty_repo.set_name("rb_arco_3rdparty_repo")

        rb_arco_xl_repo = Gtk.RadioButton.new_from_widget(rb_arco_repo)
        rb_arco_xl_repo.set_label("arcolinux_repo_xlarge")
        rb_arco_xl_repo.connect(
            "toggled",
            self.on_rb_toggled,
            self.pacman_data,
            "arcolinux_repo_xlarge",
        )
        rb_arco_xl_repo.set_name("rb_arco_xl_repo")

        rb_arco_testing_repo = Gtk.RadioButton.new_from_widget(rb_arco_3rdparty_repo)
        rb_arco_testing_repo.set_label("arcolinux_repo_testing")
        rb_arco_testing_repo.connect(
            "toggled",
            self.on_rb_toggled,
            self.pacman_data,
            "arcolinux_repo_testing",
        )

        rb_arco_testing_repo.set_name("rb_arco_testing_repo")

        hbox_repo = Gtk.Box(spacing=6)
        hbox_repo.set_border_width(10)

        hbox_repo.pack_start(rb_arco_repo, False, False, 0)
        hbox_repo.pack_start(rb_arco_3rdparty_repo, False, False, 0)
        hbox_repo.pack_start(rb_arco_xl_repo, False, False, 0)
        hbox_repo.pack_start(rb_arco_testing_repo, False, False, 0)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.vbox.pack_start(hbox_repo, False, True, 0)

        self.add(self.vbox)

        self.get_packages("arcolinux_repo", self.pacman_data)

    def on_rb_toggled(self, rb, pacman_data, repo_name):
        if rb.get_active():
            try:
                self.repo_selected = repo_name
                self.get_packages(repo_name, pacman_data)

            except Exception as e:
                fn.logger.error(e)

    def get_packages(self, repo_name, pacman_data):
        if repo_name:
            if self.treeview_loaded is True:
                self.scrolled_window.destroy()
                self.hbox_close.destroy()

                if self.lbl_packages_count is not None:
                    self.lbl_packages_count.destroy()

                if self.vbox_padding is not None:
                    self.vbox_padding.destroy()

                if self.lbl_pacman_sync_db is not None:
                    self.lbl_pacman_sync_db.destroy()

                if self.lbl_packages_installed_count is not None:
                    self.lbl_packages_installed_count.destroy()

                if self.lbl_packages_repo is not None:
                    self.lbl_packages_repo.destroy()

                if self.lbl_package_updates is not None:
                    self.lbl_package_updates.destroy()

                if self.lbl_no_packages is not None:
                    self.lbl_no_packages.destroy()

            treestore_packages = fn.get_packagelist(repo_name, pacman_data)

            self.lbl_packages_count = Gtk.Label(xalign=0, yalign=0)
            self.lbl_packages_installed_count = Gtk.Label(xalign=0, yalign=0)
            self.lbl_packages_repo = Gtk.Label(xalign=0, yalign=0)
            self.lbl_package_updates = Gtk.Label(xalign=0, yalign=0)

            btn_quit = Gtk.Button(label="Quit")
            btn_quit.set_size_request(100, 30)
            btn_quit.set_halign(Gtk.Align.END)
            btn_quit_context = btn_quit.get_style_context()
            btn_quit_context.add_class("destructive-action")
            btn_quit.connect("clicked", self.on_close, "delete-event")

            btn_refresh = Gtk.Button(label="Refresh")
            btn_refresh.set_size_request(100, 30)
            btn_refresh.set_halign(Gtk.Align.END)
            btn_refresh.connect("clicked", self.on_refresh)

            lbl_btn_padding1 = Gtk.Label(xalign=0)
            lbl_btn_padding1.set_text("  ")

            lbl_btn_padding2 = Gtk.Label(xalign=0)
            lbl_btn_padding2.set_text("  ")

            self.hbox_close = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

            grid_btns = Gtk.Grid()
            grid_btns.attach(lbl_btn_padding1, 0, 1, 1, 1)
            grid_btns.attach(btn_refresh, 0, 2, 1, 1)
            grid_btns.attach_next_to(
                lbl_btn_padding2, btn_refresh, Gtk.PositionType.RIGHT, 1, 1
            )
            grid_btns.attach_next_to(
                btn_quit, lbl_btn_padding2, Gtk.PositionType.RIGHT, 1, 1
            )

            self.hbox_close.pack_start(grid_btns, False, False, 0)

            self.vbox_padding = Gtk.Box()
            lbl_padding_lbls = Gtk.Label(xalign=0, yalign=0)
            lbl_padding_lbls.set_text("")
            self.vbox_padding.pack_start(lbl_padding_lbls, False, False, 0)

            self.lbl_no_packages = Gtk.Label(xalign=0, yalign=0)
            self.lbl_no_packages.set_markup("<b>No packages found</b>")

            if treestore_packages is not None:
                self.treeview_packages = Gtk.TreeView()

                self.treeview_packages.set_model(treestore_packages)

                renderer_col_name = Gtk.CellRendererText()
                col_name = Gtk.TreeViewColumn(
                    "Name",
                    renderer_col_name,
                    text=0,
                    weight=5,
                    background=6,
                    foreground=7,
                )

                col_name.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
                col_name.set_resizable(True)
                col_name.set_reorderable(False)
                col_name.set_sort_indicator(True)
                col_name.set_clickable(True)
                col_name.set_sort_column_id(0)

                self.treeview_packages.append_column(col_name)

                renderer_col_build_date = Gtk.CellRendererText()
                col_build_date = Gtk.TreeViewColumn(
                    "Build Date",
                    renderer_col_build_date,
                    text=1,
                    weight=5,
                    background=6,
                    foreground=7,
                )

                self.treeview_packages.append_column(col_build_date)

                treestore_packages.set_sort_column_id(1, Gtk.SortType.DESCENDING)
                col_build_date.set_sort_order(Gtk.SortType.DESCENDING)
                col_build_date.set_sort_indicator(True)
                col_build_date.set_clickable(True)
                col_build_date.set_sort_column_id(1)

                treestore_packages.set_sort_func(1, fn.compare_build_date, None)

                renderer_col_installed_version = Gtk.CellRendererText()
                col_installed_version = Gtk.TreeViewColumn(
                    "Installed Version",
                    renderer_col_installed_version,
                    text=2,
                    weight=5,
                    background=6,
                    foreground=7,
                )
                col_installed_version.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
                col_installed_version.set_resizable(True)
                col_installed_version.set_reorderable(False)
                col_installed_version.set_sort_indicator(True)
                col_installed_version.set_sort_column_id(2)
                # col_installed_version.set_sort_order(Gtk.SortType.DESCENDING)

                self.treeview_packages.append_column(col_installed_version)

                renderer_col_latest_version = Gtk.CellRendererText()
                col_latest_version = Gtk.TreeViewColumn(
                    "Latest Version",
                    renderer_col_latest_version,
                    text=3,
                    weight=5,
                    background=6,
                    foreground=7,
                )
                col_latest_version.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
                col_latest_version.set_resizable(True)
                col_latest_version.set_reorderable(False)
                col_latest_version.set_sort_indicator(True)
                col_latest_version.set_sort_column_id(3)
                # col_latest_version.set_sort_order(Gtk.SortType.DESCENDING)

                self.treeview_packages.append_column(col_latest_version)

                self.treeview_packages.set_headers_clickable(True)
                if self.treeview_packages is not None:
                    self.lbl_packages_repo.set_selectable(True)
                    self.lbl_packages_repo.set_markup(
                        "Repository = <b>%s</b>" % repo_name
                    )

                    self.lbl_packages_count.set_selectable(True)
                    self.lbl_packages_count.set_markup(
                        "Available Packages = <b>%s</b>"
                        % str(len(self.treeview_packages.get_model()))
                    )

                    self.lbl_packages_installed_count.set_selectable(True)
                    self.lbl_packages_installed_count.set_markup(
                        "Installed Packages = <b>%s</b>" % str(fn.installed_count)
                    )

                    self.lbl_package_updates.set_selectable(True)
                    self.lbl_package_updates.set_markup(
                        "Updates = <b>%s</b>" % str(fn.update_count)
                    )

                    self.treeview_packages.connect(
                        "row-activated", self.on_row_activated
                    )

                    # col_installed_date = self.treeview_packages.get_column(2)
                    # col_installed_date.set_sort_column_id(2)

                    self.scrolled_window = Gtk.ScrolledWindow()
                    # scrolled_window.set_vexpand(True)
                    self.scrolled_window.set_propagate_natural_height(True)
                    self.scrolled_window.set_propagate_natural_width(True)
                    self.scrolled_window.set_policy(
                        Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
                    )

                    self.scrolled_window.add(self.treeview_packages)

                    self.vbox.pack_start(self.scrolled_window, True, True, 0)
                    self.vbox.pack_start(self.vbox_padding, False, False, 0)
                    self.vbox.pack_start(self.lbl_packages_repo, False, False, 0)
                    self.vbox.pack_start(self.lbl_packages_count, False, False, 0)
                    self.vbox.pack_start(
                        self.lbl_packages_installed_count, False, False, 0
                    )
                    self.vbox.pack_start(self.lbl_package_updates, False, False, 0)

                    self.vbox.pack_start(self.lbl_pacman_sync_db, False, False, 0)

                    self.vbox.pack_start(self.hbox_close, False, False, 0)

                    self.show_all()

                    selection = self.treeview_packages.get_selection()
                    selection.set_mode(Gtk.SelectionMode.SINGLE)

                    self.treeview_loaded = True
            else:
                self.vbox.pack_start(self.lbl_pacman_sync_db, False, False, 0)
                self.vbox.pack_start(self.lbl_no_packages, False, False, 0)
                self.vbox.pack_start(self.vbox_padding, False, False, 0)
                self.vbox.pack_start(self.hbox_close, False, False, 0)

                self.show_all()

                self.treeview_loaded = True

    def on_row_activated(self, treeview, path, col):
        model = treeview.get_model()
        tree_iter = model.get_iter(path)
        row = path[0]
        if tree_iter:
            package_name = model.get_value(tree_iter, 0)
            if package_name:
                thread_files_list = Thread(
                    target=fn.get_package_files, daemon=True, args=(package_name,)
                )
                thread_files_list.start()
                files_list = fn.pacman_data_queue.get()
                fn.pacman_data_queue.task_done()
                package_dialog = PackageDialog(
                    package_name, self.pacman_data, files_list
                )
                package_dialog.show_all()

    def on_close(self, widget, data):
        Gtk.main_quit()
        print(
            "---------------------------------------------------------------------------"
        )
        print("Thanks for using ArcoRepoXP")
        # print("Report issues to make it even better")
        # print("---------------------------------------------------------------------------")
        # print("You can report issues on https://discord.gg/stBhS4taje")
        # print("---------------------------------------------------------------------------")

    def on_refresh(self, widget):
        self.sync_data()

        if self.pacman_sync == "Pacman syncronization failed":
            self.lbl_pacman_sync_db.set_markup(
                "Pacman DB Synchronization: <b>Failed </b>"
            )
        else:
            self.lbl_pacman_sync_db.set_markup(
                "Pacman DB Synchronized at <b>%s</b>"
                % datetime.datetime.now().strftime("%H:%M:%S")
            )

        self.get_packages(self.repo_selected, self.pacman_data)


# ====================================================================
#                       MAIN
# ====================================================================


def signal_handler(sig, frame):
    Gtk.main_quit(0)


# These should be kept as it ensures that multiple installation instances can't be run concurrently.
if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)

        if not os.path.isfile("/tmp/repoxp.lock"):
            with open("/tmp/repoxp.pid", "w") as f:
                f.write(str(os.getpid()))

            style_provider = Gtk.CssProvider()
            style_provider.load_from_path(base_dir + "/repoxp.css")

            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                style_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
            w = Main()

            w.show_all()

            Gtk.main()
        else:
            # fn.logger.info("ArcoRepoXP lock file found")

            md = Gtk.MessageDialog(
                parent=Main(),
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Sofirem Lock File Found",
            )
            md.format_secondary_markup(
                "A ArcoRepoXP lock file has been found. This indicates there is already an instance of <b>ArcoRepoXP</b> running.\n\
                Click 'Yes' to remove the lock file and try running again"
            )  # noqa

            result = md.run()
            md.destroy()

            if result in (Gtk.ResponseType.OK, Gtk.ResponseType.YES):
                pid = ""
                if os.path.exists("/tmp/repoxp.pid"):
                    with open("/tmp/repoxp.pid", "r") as f:
                        line = f.read()
                        pid = line.rstrip().lstrip()

                    # if fn.check_if_process_running(int(pid)):
                    #     print("You first need to close the existing application")
                    # else:
                    #     os.unlink("/tmp/arcorepoxp.lock")
                    #     sys.exit(1)
                else:
                    # in the rare event that the lock file is present, but the pid isn't
                    os.unlink("/tmp/repoxp.lock")
                    sys.exit(1)
            else:
                sys.exit(1)
    except Exception as e:
        # fn.logger.error("Exception in __main__: %s" % e)
        print("Exception in __main__: %s" % e)
