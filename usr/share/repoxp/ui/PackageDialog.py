import os
import gi
from libs.Functions import Functions
import threading
from threading import Thread

fn = Functions()

from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib, Pango


class PackageDialog(Gtk.Dialog):
    def __init__(self, package_name, pacman_data, files_list):
        Gtk.Dialog.__init__(self)

        package = None
        for package in pacman_data:
            if package[1] == package_name:
                break

        self.set_resizable(True)
        self.set_size_request(500, 500)
        self.set_modal(True)

        headerbar = Gtk.HeaderBar()
        headerbar.set_title("%s" % package_name)
        headerbar.set_show_close_button(True)

        self.set_titlebar(headerbar)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        stack.set_transition_duration(350)
        stack.set_hhomogeneous(False)
        stack.set_vhomogeneous(False)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
        stack_switcher.set_stack(stack)
        stack_switcher.set_homogeneous(True)

        btn_close = Gtk.Button(label="Close")
        btn_close.set_size_request(100, 30)
        btn_close.set_halign(Gtk.Align.END)

        btn_close.connect("clicked", self.on_close)

        vbox_padding = Gtk.Box(spacing=500)

        hbox_close = Gtk.Box(spacing=6)

        hbox_close.set_border_width(10)

        hbox_close.pack_start(btn_close, True, True, 1)

        zst_download_link = fn.get_download_link(package_name)

        vbox_package_details = Gtk.Box()
        vbox_package_details.set_border_width(10)

        grid_package_details = Gtk.Grid()

        self.vbox.add(stack_switcher)
        self.vbox.add(stack)
        self.vbox.pack_start(vbox_padding, True, True, 0)
        self.vbox.add(hbox_close)

        lbl_package_name_title = Gtk.Label(xalign=0, yalign=0)
        lbl_package_name_title.set_markup("<b>Package</b>")

        lbl_package_value = Gtk.Label(xalign=0, yalign=0)
        lbl_package_value.set_markup("<b>%s</b>" % package_name)

        lbl_package_value.set_selectable(True)

        lbl_padding_repo = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_repo.set_text("  ")

        lbl_repository_title = Gtk.Label(xalign=0, yalign=0)
        lbl_repository_title.set_markup("<b>Repository</b>")

        lbl_repository_value = Gtk.Label(xalign=0, yalign=0)
        lbl_repository_value.set_text(package[0])
        lbl_repository_value.set_selectable(True)

        grid_package_details.attach(lbl_repository_title, 0, 1, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding_repo, lbl_repository_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_repository_value, lbl_padding_repo, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_padding_package = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_package.set_text("  ")

        grid_package_details.attach(lbl_package_name_title, 0, 2, 1, 1)
        grid_package_details.attach_next_to(
            lbl_padding_package, lbl_package_name_title, Gtk.PositionType.RIGHT, 1, 1
        )
        grid_package_details.attach_next_to(
            lbl_package_value, lbl_padding_package, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_version_title = Gtk.Label(xalign=0, yalign=0)
        lbl_version_title.set_markup("<b>Latest Version</b>")

        lbl_version_value = Gtk.Label(xalign=0, yalign=0)
        lbl_version_value.set_text(package[2])
        lbl_version_value.set_selectable(True)

        lbl_padding_version = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_version.set_text("  ")

        grid_package_details.attach(lbl_version_title, 0, 3, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding_version, lbl_version_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_version_value, lbl_padding_version, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_build_date_title = Gtk.Label(xalign=0, yalign=0)
        lbl_build_date_title.set_markup("<b>Build Date</b>")

        lbl_build_date_value = Gtk.Label(xalign=0, yalign=0)
        lbl_build_date_value.set_text(package[3])
        lbl_build_date_value.set_selectable(True)

        lbl_padding_build_date = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_build_date.set_text("  ")

        grid_package_details.attach(lbl_build_date_title, 0, 4, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding_build_date, lbl_build_date_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_build_date_value, lbl_padding_build_date, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_installed_title = Gtk.Label(xalign=0, yalign=0)
        lbl_installed_title.set_markup("<b>Installed</b>")

        checkbox_installed = Gtk.CheckButton()
        checkbox_installed.set_sensitive(False)
        lbl_installed_version_title = Gtk.Label(xalign=0, yalign=0)
        lbl_installed_version_title.set_markup("<b>Installed Version</b>")

        lbl_installed_version_value = Gtk.Label(xalign=0, yalign=0)
        lbl_installed_version_value.set_selectable(True)

        if fn.check_package_installed(package_name):
            # lbl_installed_value.set_text("Yes")
            checkbox_installed.set_active(True)
            version = fn.get_package_version(package_name)

            lbl_installed_version_value.set_text(version)
            lbl_padding_installed = Gtk.Label(xalign=0, yalign=0)
            lbl_padding_installed.set_text("  ")

            lbl_padding_installed_version = Gtk.Label(xalign=0, yalign=0)
            lbl_padding_installed_version.set_text("  ")

            grid_package_details.attach(lbl_installed_title, 0, 5, 1, 1)

            grid_package_details.attach_next_to(
                lbl_padding_installed, lbl_installed_title, Gtk.PositionType.RIGHT, 1, 1
            )

            grid_package_details.attach_next_to(
                checkbox_installed, lbl_padding_installed, Gtk.PositionType.RIGHT, 1, 1
            )

            grid_package_details.attach(lbl_installed_version_title, 0, 6, 1, 1)

            grid_package_details.attach_next_to(
                lbl_padding_installed_version,
                lbl_installed_version_title,
                Gtk.PositionType.RIGHT,
                1,
                1,
            )

            grid_package_details.attach_next_to(
                lbl_installed_version_value,
                lbl_padding_installed_version,
                Gtk.PositionType.RIGHT,
                1,
                1,
            )
        else:
            # lbl_installed_value.set_text("No")
            checkbox_installed.set_active(False)

        #

        lbl_description_title = Gtk.Label(xalign=0, yalign=0)
        lbl_description_title.set_markup("<b>Description</b>")

        lbl_description_value = Gtk.Label(xalign=0, yalign=0)
        lbl_description_value.set_text(package[6])
        lbl_description_value.set_selectable(True)
        lbl_description_value.set_line_wrap(True)
        lbl_description_value.set_max_width_chars(50)

        lbl_padding_description = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_description.set_text("  ")

        grid_package_details.attach(lbl_description_title, 0, 7, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding_description, lbl_description_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_description_value,
            lbl_padding_description,
            Gtk.PositionType.RIGHT,
            1,
            1,
        )

        if len(package[14]) > 0:
            lbl_groups_title = Gtk.Label(xalign=0, yalign=0)
            lbl_groups_title.set_markup("<b>Groups</b>")

            lbl_groups_value = Gtk.Label(xalign=0, yalign=0)
            lbl_groups_value.set_text(" ".join(package[14]))
            lbl_groups_value.set_selectable(True)

            lbl_padding_groups = Gtk.Label(xalign=0, yalign=0)
            lbl_padding_groups.set_text("  ")

            grid_package_details.attach(lbl_groups_title, 0, 8, 1, 1)

            grid_package_details.attach_next_to(
                lbl_padding_groups, lbl_groups_title, Gtk.PositionType.RIGHT, 1, 1
            )

            grid_package_details.attach_next_to(
                lbl_groups_value, lbl_padding_groups, Gtk.PositionType.RIGHT, 1, 1
            )

        lbl_replaces_title = Gtk.Label(xalign=0, yalign=0)
        lbl_replaces_title.set_markup("<b>Replaces</b>")

        lbl_padding_replaces = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_replaces.set_text("  ")

        if len(package[12]) > 0:
            lbl_replaces_title = Gtk.Label(xalign=0, yalign=0)
            lbl_replaces_title.set_markup("<b>Replaces</b>")

            treestore_replaces = Gtk.TreeStore(str, str)

            for item in package[12]:
                treestore_replaces.append(None, list(item))

            treeview_replaces = Gtk.TreeView(model=treestore_replaces)

            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn("Package", renderer, text=0)

            treeview_replaces.append_column(column)

            grid_package_details.attach(lbl_replaces_title, 0, 9, 1, 1)

            scrolled_window_replaces = Gtk.ScrolledWindow()
            scrolled_window_replaces.set_propagate_natural_height(True)
            scrolled_window_replaces.add(treeview_replaces)

            grid_package_details.attach_next_to(
                lbl_padding_replaces, lbl_replaces_title, Gtk.PositionType.RIGHT, 1, 1
            )

            grid_package_details.attach_next_to(
                scrolled_window_replaces,
                lbl_padding_replaces,
                Gtk.PositionType.RIGHT,
                1,
                1,
            )

        lbl_licenses_title = Gtk.Label(xalign=0, yalign=0)
        lbl_licenses_title.set_markup("<b>Licenses</b>")

        lbl_licenses_value = Gtk.Label(xalign=0, yalign=0)
        lbl_licenses_value.set_text(" ".join(package[13]))
        lbl_licenses_value.set_selectable(True)

        lbl_padding_licenses = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_licenses.set_text("  ")

        grid_package_details.attach(lbl_licenses_title, 0, 10, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding_licenses, lbl_licenses_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_licenses_value, lbl_padding_licenses, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_dl_size_title = Gtk.Label(xalign=0, yalign=0)
        lbl_dl_size_title.set_markup("<b>Download Size</b>")

        lbl_dl_size_value = Gtk.Label(xalign=0, yalign=0)
        lbl_dl_size_value.set_text(package[4])
        lbl_dl_size_value.set_selectable(True)

        lbl_padding_dl_size = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_dl_size.set_text("  ")

        grid_package_details.attach(lbl_dl_size_title, 0, 11, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding_dl_size, lbl_dl_size_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_dl_size_value, lbl_padding_dl_size, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_installed_size_title = Gtk.Label(xalign=0, yalign=0)
        lbl_installed_size_title.set_markup("<b>Installed Size</b>")

        lbl_installed_size_value = Gtk.Label(xalign=0, yalign=0)
        lbl_installed_size_value.set_text(package[5])
        lbl_installed_size_value.set_selectable(True)

        lbl_padding6 = Gtk.Label(xalign=0, yalign=0)
        lbl_padding6.set_text("  ")

        grid_package_details.attach(lbl_installed_size_title, 0, 12, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding6, lbl_installed_size_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_installed_size_value, lbl_padding6, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_arch_title = Gtk.Label(xalign=0, yalign=0)
        lbl_arch_title.set_markup("<b>Arch</b>")

        lbl_arch_value = Gtk.Label(xalign=0, yalign=0)
        lbl_arch_value.set_text(package[7])
        lbl_arch_value.set_selectable(True)

        lbl_padding_arch = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_arch.set_text("  ")

        grid_package_details.attach(lbl_arch_title, 0, 13, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding_arch, lbl_arch_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_arch_value, lbl_padding_arch, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_url_title = Gtk.Label(xalign=0, yalign=0)
        lbl_url_title.set_markup("<b>URL</b>")

        lbl_url_value = Gtk.Label(xalign=0, yalign=0)
        lbl_url_value.set_text(package[8])
        lbl_url_value.set_selectable(True)

        lbl_padding_url = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_url.set_text("  ")

        grid_package_details.attach(lbl_url_title, 0, 14, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding_url, lbl_url_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_url_value, lbl_padding_url, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_packager_title = Gtk.Label(xalign=0, yalign=0)
        lbl_packager_title.set_markup("<b>Packager</b>")

        lbl_packager_value = Gtk.Label(xalign=0, yalign=0)
        lbl_packager_value.set_text(package[11])
        lbl_packager_value.set_selectable(True)

        lbl_padding_packager = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_packager.set_text("  ")

        grid_package_details.attach(lbl_packager_title, 0, 15, 1, 1)

        grid_package_details.attach_next_to(
            lbl_padding_packager, lbl_packager_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_packager_value, lbl_padding_packager, Gtk.PositionType.RIGHT, 1, 1
        )

        last_index = 0
        last_index = len(zst_download_link.split("/")) - 1

        lbl_dl_zst_save_title = Gtk.Label(xalign=0, yalign=0)
        lbl_dl_zst_save_value = Gtk.Label(xalign=0, yalign=0)
        lbl_dl_zst_save_value.set_selectable(True)

        lbl_dl_zst_save_title.set_markup("<b>Download Path</b>")

        if last_index > 0:
            zst_filename = zst_download_link.split("/")[last_index]
            lbl_dl_zst_save_value.set_text(
                "%s/%s" % (fn.zst_download_path, zst_filename)
            )

        self.lbl_dl_status = Gtk.Label(xalign=0, yalign=0)
        self.lbl_dl_status.set_selectable(True)
        self.lbl_dl_status.set_line_wrap(True)
        self.lbl_dl_status.set_max_width_chars(50)

        switch_dl_zst = Gtk.Switch()
        switch_dl_zst.set_valign(Gtk.Align.FILL)
        switch_dl_zst.connect(
            "notify::active",
            self.dl_zst_toggle,
            zst_download_link,
            "%s/%s" % (fn.zst_download_path, zst_filename),
        )

        lbl_dl_zst_title = Gtk.Label(xalign=0, yalign=0)
        lbl_dl_zst_title.set_markup("<b>Download Package</b>")

        lbl_padding_dl_zst = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_dl_zst.set_text("  ")

        lbl_padding_hint = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_hint.set_text("  ")

        vbox_switch = Gtk.Box()
        vbox_switch.pack_start(switch_dl_zst, False, True, 0)
        vbox_switch.pack_start(lbl_padding_hint, False, True, 0)
        vbox_switch.pack_start(self.lbl_dl_status, False, True, 0)

        grid_package_details.attach(lbl_dl_zst_save_title, 0, 16, 1, 1)
        grid_package_details.attach_next_to(
            lbl_padding_dl_zst, lbl_dl_zst_save_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            lbl_dl_zst_save_value, lbl_padding_dl_zst, Gtk.PositionType.RIGHT, 1, 1
        )

        lbl_padding_switch = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_switch.set_text("  ")

        grid_package_details.attach(lbl_dl_zst_title, 0, 17, 1, 1)
        grid_package_details.attach_next_to(
            lbl_padding_switch, lbl_dl_zst_title, Gtk.PositionType.RIGHT, 1, 1
        )

        grid_package_details.attach_next_to(
            vbox_switch, lbl_padding_switch, Gtk.PositionType.RIGHT, 1, 1
        )

        depends_on = package[9]

        if len(depends_on) > 0:
            lbl_depends_title = Gtk.Label(xalign=0, yalign=0)
            lbl_depends_title.set_markup("<b>Depends On</b>")

            treestore_depends = Gtk.TreeStore(str, str)

            for item in depends_on:
                treestore_depends.append(None, list(item))

            treeview_depends = Gtk.TreeView(model=treestore_depends)

            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn("Package", renderer, text=0)

            treeview_depends.append_column(column)

            lbl_padding_depends = Gtk.Label(xalign=0, yalign=0)
            lbl_padding_depends.set_text("  ")

            grid_package_details.attach(lbl_depends_title, 0, 18, 1, 1)

            scrolled_window_depends = Gtk.ScrolledWindow()

            scrolled_window_depends.set_policy(
                Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
            )
            scrolled_window_depends.add(treeview_depends)

            grid_package_details.attach_next_to(
                lbl_padding_depends, lbl_depends_title, Gtk.PositionType.RIGHT, 1, 1
            )

            grid_package_details.attach_next_to(
                scrolled_window_depends,
                lbl_padding_depends,
                Gtk.PositionType.RIGHT,
                1,
                1,
            )

        conflicts_with = package[10]

        if len(conflicts_with) > 0:
            lbl_conflicts_title = Gtk.Label(xalign=0, yalign=0)
            lbl_conflicts_title.set_markup("<b> Conflicts With</b>")
            treestore_conflicts = Gtk.TreeStore(str, str)

            for item in conflicts_with:
                treestore_conflicts.append(None, list(item))

            treeview_conflicts = Gtk.TreeView(model=treestore_conflicts)

            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn("Package", renderer, text=0)

            treeview_conflicts.append_column(column)

            lbl_padding_conflicts = Gtk.Label(xalign=0, yalign=0)
            lbl_padding_conflicts.set_text("  ")

            lbl_padding_newline1 = Gtk.Label(xalign=0, yalign=0)
            lbl_padding_newline1.set_text("")

            grid_package_details.attach(lbl_padding_newline1, 0, 19, 1, 1)

            grid_package_details.attach(lbl_conflicts_title, 0, 20, 1, 1)

            scrolled_window_conflicts = Gtk.ScrolledWindow()

            scrolled_window_conflicts.set_policy(
                Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
            )
            scrolled_window_conflicts.add(treeview_conflicts)

            grid_package_details.attach_next_to(
                lbl_padding_conflicts, lbl_conflicts_title, Gtk.PositionType.RIGHT, 1, 1
            )

            grid_package_details.attach_next_to(
                scrolled_window_conflicts,
                lbl_padding_conflicts,
                Gtk.PositionType.RIGHT,
                1,
                1,
            )

        vbox_package_details.pack_start(grid_package_details, True, True, 0)

        stack.add_titled(vbox_package_details, "Information", "Information")

        scrolled_window_files = Gtk.ScrolledWindow()
        scrolled_window_files.set_propagate_natural_height(True)
        scrolled_window_files.set_propagate_natural_width(True)
        scrolled_window_files.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )

        textbuffer_files = Gtk.TextBuffer()
        end_iter = textbuffer_files.get_end_iter()
        for line in files_list:
            textbuffer_files.insert(end_iter, "  %s\n" % line, len("  %s\n" % line))

        textview_files = Gtk.TextView(buffer=textbuffer_files)
        # textview_files.set_vexpand(True)
        # textview_files.set_hexpand(True)
        textview_files.set_property("editable", False)
        textview_files.set_property("monospace", True)

        scrolled_window_files.add(textview_files)

        vbox_package_files = Gtk.Box()
        vbox_package_files.set_border_width(10)
        vbox_package_files.pack_start(scrolled_window_files, True, True, 0)

        stack.add_titled(vbox_package_files, "Files", "Files")

    def dl_zst_toggle(self, widget, data, url, filename):
        try:
            if widget.get_active() == True:
                dl_status = fn.get_zst(url, filename)

                if dl_status == "completed":
                    widget.set_sensitive(False)
                    self.lbl_dl_status.set_markup("<b>Download completed </b>")

                elif dl_status == "ConnectionError":
                    widget.set_sensitive(False)
                    self.lbl_dl_status.set_markup(
                        "<b>Download failed: ConnectionError </b>"
                    )
                else:
                    widget.set_active(False)
                    self.lbl_dl_status.set_markup("<b>Download failed </b>")
        except Exception as e:
            widget.set_active(True)
            self.lbl_dl_status.set_markup("<b>Download failed </b>")
            fn.logger.error(e)

    def on_close(self, widget):
        self.hide()
        self.destroy()
