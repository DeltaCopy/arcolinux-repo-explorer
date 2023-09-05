import os
import gi
from libs.Functions import Functions
import threading
from threading import Thread

fn = Functions()

from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib, Pango


# A message dialog window to show package details
class PackageDialog(Gtk.Dialog):
    def __init__(self, package_name, pacman_data, files_list):
        Gtk.Dialog.__init__(self)

        package = None
        for package in pacman_data:
            if package[1] == package_name:
                break

        self.set_resizable(True)
        self.set_size_request(700, 300)
        self.set_modal(True)

        headerbar = Gtk.HeaderBar()
        headerbar.set_title("%s" % package_name)
        headerbar.set_show_close_button(True)

        self.set_titlebar(headerbar)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        stack.set_transition_duration(350)
        # stack.set_hhomogeneous(False)
        # stack.set_vhomogeneous(False)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
        stack_switcher.set_stack(stack)
        stack_switcher.set_homogeneous(True)

        btn_close = Gtk.Button(label="Close")
        btn_close.set_size_request(100, 30)
        btn_close.set_halign(Gtk.Align.END)

        btn_close.connect("clicked", self.on_close)

        vbox_padding = Gtk.Box()

        vbox_close = Gtk.Box()

        vbox_close.set_border_width(10)
        vbox_close.pack_start(btn_close, True, True, 0)

        zst_download_link = fn.get_download_link(package_name)

        self.vbox.add(stack_switcher)
        self.vbox.add(stack)

        # self.vbox.pack_start(vbox_padding, True, True, 0)
        self.vbox.pack_start(vbox_close, False, False, 0)

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(listbox, True, True, 0)
        box_outer.set_border_width(10)

        # package name

        lbl_package_name_title = Gtk.Label(xalign=0, yalign=0)
        lbl_package_name_title.set_markup("<b>Package</b>")

        lbl_package_name_value = Gtk.Label(xalign=0, yalign=0)
        lbl_package_name_value.set_markup("<b>%s</b>" % package_name)
        lbl_package_name_value.set_selectable(True)

        # package name
        row_package_title = Gtk.ListBoxRow()
        vbox_package_title = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        row_package_title.add(vbox_package_title)

        vbox_package_title.pack_start(lbl_package_name_title, True, True, 0)
        vbox_package_title.pack_start(lbl_package_name_value, True, True, 0)

        listbox.add(row_package_title)

        # repository

        lbl_repository_title = Gtk.Label(xalign=0, yalign=0)
        lbl_repository_title.set_markup("<b>Repository</b>")

        lbl_repository_value = Gtk.Label(xalign=0, yalign=0)
        lbl_repository_value.set_text(package[0])
        lbl_repository_value.set_selectable(True)

        row_package_repository = Gtk.ListBoxRow()
        vbox_package_repository_title = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0
        )
        vbox_package_repository_title.pack_start(lbl_repository_title, True, True, 0)
        vbox_package_repository_title.pack_start(lbl_repository_value, True, True, 0)
        row_package_repository.add(vbox_package_repository_title)

        listbox.add(row_package_repository)

        # version

        lbl_version_title = Gtk.Label(xalign=0, yalign=0)
        lbl_version_title.set_markup("<b>Latest Version</b>")

        lbl_version_value = Gtk.Label(xalign=0, yalign=0)
        lbl_version_value.set_text(package[2])
        lbl_version_value.set_selectable(True)

        row_package_version = Gtk.ListBoxRow()
        vbox_package_version_title = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0
        )
        vbox_package_version_title.pack_start(lbl_version_title, True, True, 0)
        vbox_package_version_title.pack_start(lbl_version_value, True, True, 0)
        row_package_version.add(vbox_package_version_title)

        listbox.add(row_package_version)

        # package installed

        lbl_installed_title = Gtk.Label(xalign=0, yalign=0)
        lbl_installed_title.set_markup("<b>Installed</b>")

        checkbox_installed = Gtk.CheckButton()
        checkbox_installed.set_sensitive(False)

        lbl_installed_version_title = Gtk.Label(xalign=0, yalign=0)
        lbl_installed_version_title.set_markup("<b>Installed Version</b>")
        lbl_installed_version_value = Gtk.Label(xalign=0, yalign=0)
        lbl_installed_version_value.set_selectable(True)

        row_package_installed = Gtk.ListBoxRow()
        vbox_package_installed = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0
        )

        if fn.check_package_installed(package_name):
            # installed size

            lbl_installed_size_title = Gtk.Label(xalign=0, yalign=0)
            lbl_installed_size_title.set_markup("<b>Installed Size</b>")

            lbl_installed_size_value = Gtk.Label(xalign=0, yalign=0)
            lbl_installed_size_value.set_text(package[5])
            lbl_installed_size_value.set_selectable(True)

            # lbl_installed_value.set_text("Yes")
            checkbox_installed.set_active(True)
            version = fn.get_package_version(package_name)

            lbl_installed_version_value.set_text(version)

            vbox_package_installed.pack_start(lbl_installed_title, True, True, 0)
            vbox_package_installed.pack_start(checkbox_installed, True, True, 0)
            vbox_package_installed.pack_start(
                lbl_installed_version_title, True, True, 0
            )
            vbox_package_installed.pack_start(
                lbl_installed_version_value, True, True, 0
            )
            vbox_package_installed.pack_start(lbl_installed_size_title, True, True, 0)
            vbox_package_installed.pack_start(lbl_installed_size_value, True, True, 0)

        else:
            checkbox_installed.set_active(False)
            vbox_package_installed.pack_start(lbl_installed_title, True, True, 0)
            vbox_package_installed.pack_start(checkbox_installed, True, True, 0)

        row_package_installed.add(vbox_package_installed)
        listbox.add(row_package_installed)

        # build date

        lbl_build_date_title = Gtk.Label(xalign=0, yalign=0)
        lbl_build_date_title.set_markup("<b>Build Date</b>")

        lbl_build_date_value = Gtk.Label(xalign=0, yalign=0)
        lbl_build_date_value.set_text(package[3])
        lbl_build_date_value.set_selectable(True)

        row_package_build_date = Gtk.ListBoxRow()
        vbox_package_build_date = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0
        )
        vbox_package_build_date.pack_start(lbl_build_date_title, True, True, 0)
        vbox_package_build_date.pack_start(lbl_build_date_value, True, True, 0)
        row_package_build_date.add(vbox_package_build_date)

        listbox.add(row_package_build_date)

        # description

        lbl_description_title = Gtk.Label(xalign=0, yalign=0)
        lbl_description_title.set_markup("<b>Description</b>")

        lbl_description_value = Gtk.Label(xalign=0, yalign=0)
        lbl_description_value.set_text(package[6])
        lbl_description_value.set_selectable(True)
        lbl_description_value.set_line_wrap(True)
        lbl_description_value.set_max_width_chars(50)

        row_package_description = Gtk.ListBoxRow()
        vbox_package_description = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0
        )
        vbox_package_description.pack_start(lbl_description_title, True, True, 0)
        vbox_package_description.pack_start(lbl_description_value, True, True, 0)
        row_package_description.add(vbox_package_description)

        listbox.add(row_package_description)

        # groups

        if len(package[14]) > 0:
            lbl_groups_title = Gtk.Label(xalign=0, yalign=0)
            lbl_groups_title.set_markup("<b>Groups</b>")

            lbl_groups_value = Gtk.Label(xalign=0, yalign=0)
            lbl_groups_value.set_text(" ".join(package[14]))
            lbl_groups_value.set_selectable(True)

            row_package_groups = Gtk.ListBoxRow()
            vbox_package_groups = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL, spacing=0
            )
            vbox_package_groups.pack_start(lbl_groups_title, True, True, 0)
            vbox_package_groups.pack_start(lbl_groups_value, True, True, 0)
            row_package_groups.add(vbox_package_groups)

            listbox.add(row_package_groups)

        # Replaces

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

            scrolled_window_replaces = Gtk.ScrolledWindow()
            scrolled_window_replaces.set_policy(
                Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
            )
            # scrolled_window_replaces.add(treeview_replaces)

            row_package_replaces = Gtk.ListBoxRow()
            vbox_package_replaces = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL, spacing=0
            )
            vbox_package_replaces.pack_start(lbl_replaces_title, True, True, 0)
            vbox_package_replaces.pack_start(treeview_replaces, True, True, 0)
            row_package_replaces.add(vbox_package_replaces)

            listbox.add(row_package_replaces)

        # licenses

        lbl_licenses_title = Gtk.Label(xalign=0, yalign=0)
        lbl_licenses_title.set_markup("<b>Licenses</b>")

        lbl_licenses_value = Gtk.Label(xalign=0, yalign=0)
        lbl_licenses_value.set_text(" ".join(package[13]))
        lbl_licenses_value.set_selectable(True)

        row_package_licenses = Gtk.ListBoxRow()
        vbox_package_licenses = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox_package_licenses.pack_start(lbl_licenses_title, True, True, 0)
        vbox_package_licenses.pack_start(lbl_licenses_value, True, True, 0)
        row_package_licenses.add(vbox_package_licenses)

        listbox.add(row_package_licenses)

        # download size

        lbl_dl_size_title = Gtk.Label(xalign=0, yalign=0)
        lbl_dl_size_title.set_markup("<b>Download Size</b>")

        lbl_dl_size_value = Gtk.Label(xalign=0, yalign=0)
        lbl_dl_size_value.set_text(package[4])
        lbl_dl_size_value.set_selectable(True)

        row_package_dl_size = Gtk.ListBoxRow()
        vbox_package_dl_size = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox_package_dl_size.pack_start(lbl_dl_size_title, True, True, 0)
        vbox_package_dl_size.pack_start(lbl_dl_size_value, True, True, 0)
        row_package_dl_size.add(vbox_package_dl_size)

        listbox.add(row_package_dl_size)

        # arch

        lbl_arch_title = Gtk.Label(xalign=0, yalign=0)
        lbl_arch_title.set_markup("<b>Arch</b>")

        lbl_arch_value = Gtk.Label(xalign=0, yalign=0)
        lbl_arch_value.set_text(package[7])
        lbl_arch_value.set_selectable(True)

        row_package_arch = Gtk.ListBoxRow()
        vbox_package_arch = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox_package_arch.pack_start(lbl_arch_title, True, True, 0)
        vbox_package_arch.pack_start(lbl_arch_value, True, True, 0)
        row_package_arch.add(vbox_package_arch)

        listbox.add(row_package_arch)

        # url

        lbl_url_title = Gtk.Label(xalign=0, yalign=0)
        lbl_url_title.set_markup("<b>URL</b>")

        lbl_url_value = Gtk.Label(xalign=0, yalign=0)
        lbl_url_value.set_text(package[8])
        lbl_url_value.set_selectable(True)

        row_package_url = Gtk.ListBoxRow()
        vbox_package_url = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox_package_url.pack_start(lbl_url_title, True, True, 0)
        vbox_package_url.pack_start(lbl_url_value, True, True, 0)
        row_package_url.add(vbox_package_url)

        listbox.add(row_package_url)

        # packager

        lbl_packager_title = Gtk.Label(xalign=0, yalign=0)
        lbl_packager_title.set_markup("<b>Packager</b>")

        lbl_packager_value = Gtk.Label(xalign=0, yalign=0)
        lbl_packager_value.set_text(package[11])
        lbl_packager_value.set_selectable(True)

        row_packager = Gtk.ListBoxRow()
        vbox_packager = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox_packager.pack_start(lbl_packager_title, True, True, 0)
        vbox_packager.pack_start(lbl_packager_value, True, True, 0)
        row_packager.add(vbox_packager)

        listbox.add(row_packager)

        last_index = 0
        last_index = len(zst_download_link.split("/")) - 1

        lbl_dl_zst_save_title = Gtk.Label(xalign=0, yalign=0)
        lbl_dl_zst_save_value = Gtk.Label(xalign=0, yalign=0)
        lbl_dl_zst_save_value.set_selectable(True)

        lbl_dl_zst_save_title.set_markup("<b>Download Path</b>")

        if last_index > 0:
            zst_filename = zst_download_link.split("/")[last_index]
            lbl_dl_zst_save_value.set_text(
                "%s/%s" % (fn.zst_download_path_nousername, zst_filename)
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

        lbl_padding_dl_zst1 = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_dl_zst1.set_text("   ")

        lbl_padding_dl_zst2 = Gtk.Label(xalign=0, yalign=0)
        lbl_padding_dl_zst2.set_text("   ")

        row_dl_zst = Gtk.ListBoxRow()
        vbox_switch = Gtk.Box()
        vbox_switch.pack_start(lbl_dl_zst_title, False, True, 0)
        vbox_switch.pack_start(lbl_padding_dl_zst1, False, True, 0)
        vbox_switch.pack_start(switch_dl_zst, False, True, 0)
        vbox_switch.pack_start(lbl_padding_dl_zst2, False, True, 0)
        vbox_switch.pack_start(self.lbl_dl_status, False, True, 0)

        row_dl_zst.add(vbox_switch)

        listbox.add(row_dl_zst)

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

            scrolled_window_depends = Gtk.ScrolledWindow()

            scrolled_window_depends.set_policy(
                Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
            )
            # scrolled_window_depends.add(treeview_depends)

            row_depends = Gtk.ListBoxRow()
            vbox_depends = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            vbox_depends.pack_start(lbl_depends_title, True, True, 0)
            vbox_depends.pack_start(treeview_depends, True, True, 0)
            row_depends.add(vbox_depends)

            listbox.add(row_depends)

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

            scrolled_window_conflicts = Gtk.ScrolledWindow()

            scrolled_window_conflicts.set_policy(
                Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
            )
            # scrolled_window_conflicts.add(treeview_conflicts)

            row_conflicts = Gtk.ListBoxRow()
            vbox_conflicts = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            vbox_conflicts.pack_start(lbl_conflicts_title, True, True, 0)
            vbox_conflicts.pack_start(treeview_conflicts, True, True, 0)
            row_conflicts.add(vbox_conflicts)

            listbox.add(row_conflicts)

        scrolled_window_package_info = Gtk.ScrolledWindow()

        # scrolled_window_package_info.set_propagate_natural_height(True)
        scrolled_window_package_info.set_propagate_natural_width(True)
        scrolled_window_package_info.set_size_request(0, 300)

        scrolled_window_package_info.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )

        scrolled_window_package_info.add(box_outer)

        vbox_package_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        vbox_package_info.pack_start(scrolled_window_package_info, True, True, 0)
        # vbox_package_info.pack_start(vbox_close, True, True, 0)

        stack.add_titled(vbox_package_info, "Information", "Information")

        scrolled_window_files = Gtk.ScrolledWindow()
        scrolled_window_files.set_propagate_natural_height(True)
        # scrolled_window_files.set_propagate_natural_width(True)
        scrolled_window_files.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )

        textbuffer_files = Gtk.TextBuffer()
        end_iter = textbuffer_files.get_end_iter()
        for line in files_list:
            textbuffer_files.insert(end_iter, "  %s\n" % line, len("  %s\n" % line))

        textview_files = Gtk.TextView(buffer=textbuffer_files)

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
