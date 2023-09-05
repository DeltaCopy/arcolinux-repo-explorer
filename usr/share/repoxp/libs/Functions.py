import logging
import subprocess
import gi
import threading
import shutil
from threading import Thread
from queue import Queue
import requests
import os
from os import makedirs
import datetime
from datetime import datetime, timedelta
from ui.MessageDialog import MessageDialog

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib


class Functions(object):
    pacman_data_queue = Queue()
    package_treestore_queue = Queue()

    arco_repos = [
        "arcolinux_repo_testing",
        "arcolinux_repo",
        "arcolinux_repo_3party",
        "arcolinux_repo_xlarge",
    ]
    # 10m timeout
    process_timeout = 20
    sudo_username = os.getlogin()
    home = "/home/" + str(sudo_username)
    zst_download_path_nousername = "$HOME/repoxp/packages"
    zst_download_path = "%s/repoxp/packages" % home
    headers = {"Content-Type": "application/octet-stream"}
    installed_count = 0
    installed_package = {}

    logger = logging.getLogger("logger")

    # create console handler and set level to debug
    ch = logging.StreamHandler()

    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s > %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    def __init__(self):
        # mkdir zst_download_path
        if not os.path.exists(self.zst_download_path):
            makedirs(self.zst_download_path)

        self.permissions("%s/repoxp/" % self.home)
        self.permissions(self.zst_download_path)

    # set ownership of $HOME/repoxp, set it to the actual user running the app
    def permissions(self, dst):
        try:
            groups = subprocess.run(
                ["sh", "-c", "id " + self.sudo_username],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            for x in groups.stdout.decode().split(" "):
                if "gid" in x:
                    g = x.split("(")[1]
                    group = g.replace(")", "").strip()
            subprocess.call(
                ["chown", "-R", self.sudo_username + ":" + group, dst], shell=False
            )

        except Exception as e:
            self.logger.error(e)

    # download the corresponding zst file
    def get_zst(self, url, filename):
        try:
            # package is in the pacman cache use that one
            if "file://" in url:
                shutil.copyfile(url.replace("file://", ""), filename)
                self.permissions(self.zst_download_path)
                return "completed"
            else:
                requests_queue = Queue()
                dl_zst_thread = Thread(
                    target=self.download_zst_file,
                    args=(
                        url,
                        requests_queue,
                    ),
                    daemon=True,
                )

                dl_zst_thread.start()

                r = requests_queue.get()
                requests_queue.task_done()

                if type(r) is requests.exceptions.ConnectionError:
                    message_dialog = MessageDialog(
                        "Error",
                        "Download failed",
                        "ConnectionError: Cannot connect to any configured pacman mirrors",
                        "",
                        "error",
                        False,
                    )

                    message_dialog.show_all()
                    return "ConnectionError"

                if r.status_code == 200:
                    with open(filename, "wb") as zst_file:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                zst_file.write(chunk)

                    if os.path.exists(filename):
                        self.permissions(self.zst_download_path)
                        return "completed"

                    else:
                        return "failed"

                else:
                    message_dialog = MessageDialog(
                        "Error",
                        "Download failed",
                        r.text,
                        "",
                        "error",
                        True,
                    )

                    message_dialog.show_all()
                    return "failed"

        except Exception as e:
            self.logger.error(e)

            message_dialog = MessageDialog(
                "Error",
                "Download failed",
                r.text,
                "",
                "error",
                True,
            )

            message_dialog.show_all()

            return "failed"

    def download_zst_file(self, url, requests_queue):
        try:
            r = requests.get(
                url, headers=self.headers, allow_redirects=True, stream=True
            )

            requests_queue.put(r)
        except Exception as e:
            requests_queue.put(e)

    # run pacman sync files database - pacman -Fy
    def sync_file_db(self):
        try:
            sync_str = ["pacman", "-Fy"]

            process_sync = subprocess.run(
                sync_str,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=self.process_timeout,
            )

            if process_sync.returncode == 0:
                self.pacman_data_queue.put(None)
            else:
                if process_sync.stdout:
                    out = str(process_sync.stdout.decode("utf-8"))
                    # self.logger.error(out)

                    message_dialog = MessageDialog(
                        "Error",
                        "Pacman file syncronization failed",
                        out,
                        "",
                        "error",
                        True,
                    )

                    message_dialog.show_all()
                    self.pacman_data_queue.put("Pacman file syncronization failed")

        except Exception as e:
            self.logger.error("Exception in sync_package_db(): %s" % e)

    # run pacman sync database - pacman -Syu
    def sync_package_db(self):
        try:
            sync_str = ["pacman", "-Sy"]

            process_sync = subprocess.run(
                sync_str,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=self.process_timeout,
            )

            if process_sync.returncode == 0:
                self.pacman_data_queue.put(None)
            else:
                if process_sync.stdout:
                    out = str(process_sync.stdout.decode("utf-8"))
                    # self.logger.error(out)

                    message_dialog = MessageDialog(
                        "Error",
                        "Pacman syncronization failed",
                        out,
                        "",
                        "error",
                        True,
                    )

                    message_dialog.show_all()
                    self.pacman_data_queue.put("Pacman syncronization failed")

        except Exception as e:
            self.logger.error("Exception in sync_package_db(): %s" % e)

    # retrieve package lists
    def get_packagelist(self, repo, pacman_data):
        installed_packages_list = self.get_all_arco_packages_state()

        packages = []
        self.installed_count = 0
        self.update_count = 0
        self.built_today = 0
        today = datetime.now().strftime("%Y-%m-%d")

        installed_version = ""
        installed = False
        update_required = False

        for package in pacman_data:
            installed = False
            installed_version = ""
            update_required = False
            if package[0] == repo:
                for installed_package in installed_packages_list:
                    if installed_package[0] == package[1]:
                        installed = True
                        installed_version = installed_package[1]
                        update_required = installed_package[2]

                        break
                if installed == True:
                    self.installed_count += 1

                build_date = package[3]
                if len(build_date) > 0:
                    try:
                        if (
                            datetime.strptime(
                                build_date, "%a %d %b %Y %H:%M:%S %Z"
                            ).date()
                            == today
                        ):
                            self.built_today += 1
                    except ValueError as ve:
                        # fn.logger.error("ValueError in compare_install_date: %s" % ve)
                        # compare fails due to the format of the datetime string, which hasn't been tested
                        pass
                    except Exception as e:
                        self.logger.error("Exception in extracting build date: %s" % e)

                packages.append(
                    (
                        package[1],  # package
                        package[2],  # latest version
                        installed_version,
                        package[3],  # build date
                        installed,
                        update_required,
                    )
                )
            # installed = False

        if len(packages) > 0:
            # treestore_packages = Gtk.TreeStore(str, str, str, str, bool, bool)
            treestore_packages = Gtk.TreeStore(str, str, str, str, bool, int, str, str)
            for item in sorted(packages):
                # treestore_packages.append(None, list(item))

                if item[5] == True:
                    self.update_count += 1
                    treestore_packages.append(
                        None,
                        [
                            item[0],
                            item[3],
                            item[2],
                            item[1],
                            item[4],
                            Pango.Weight.BOLD,
                            "#F75D59",
                            "#FEFCFF",
                        ],
                    )
                else:
                    treestore_packages.append(
                        None,
                        [
                            item[0],
                            item[3],
                            item[2],
                            item[1],
                            item[4],
                            Pango.Weight.NORMAL,
                            None,
                            None,
                        ],
                    )

            return treestore_packages

        else:
            return None

    # noqa: any locales other than en_GB.UTF-8 / en_US.UTF-8 are untested
    def compare_build_date(self, model, row1, row2, user_data):
        try:
            sort_column, _ = model.get_sort_column_id()
            str_value1 = model.get_value(row1, sort_column)
            str_value2 = model.get_value(row2, sort_column)

            datetime_value1 = None
            datetime_value2 = None

            # convert string into datetime object, check if time format is 12H format with AM/PM
            if str_value1.lower().find("am") > 0 or str_value1.lower().find("pm") > 0:
                # 12H format
                datetime_value1 = datetime.strptime(
                    str_value1, "%a %d %b %Y %I:%M:%S %p %Z"
                ).replace(tzinfo=None)
                datetime_value2 = datetime.strptime(
                    str_value2, "%a %d %b %Y %I:%M:%S %p %Z"
                ).replace(tzinfo=None)
            else:
                # 24H format
                datetime_value1 = datetime.strptime(
                    str_value1, "%a %d %b %Y %H:%M:%S %Z"
                ).replace(tzinfo=None)
                datetime_value2 = datetime.strptime(
                    str_value2, "%a %d %b %Y %H:%M:%S %Z"
                ).replace(tzinfo=None)

            if datetime_value1 is not None and datetime_value2 is not None:
                if datetime_value1 < datetime_value2:
                    return -1
                elif datetime_value1 == datetime_value2:
                    return 0
                else:
                    return 1
        except ValueError as ve:
            # fn.logger.error("ValueError in compare_install_date: %s" % ve)
            # compare fails due to the format of the datetime string, which hasn't been tested
            pass
        except Exception as e:
            self.logger.error("Exception in compare_install_date: %s" % e)

    # use pacman to get the download link of a package
    def get_download_link(self, package_name):
        query_str = ["pacman", "-Sp", package_name]

        try:
            process_pkg_query = subprocess.Popen(
                query_str, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            out, err = process_pkg_query.communicate(timeout=self.process_timeout)

            if process_pkg_query.returncode == 0:
                for line in out.decode("utf-8").splitlines():
                    if package_name in line:
                        return line

        except Exception as e:
            self.logger.error(e)

    # retrieve package version
    def get_package_version(self, package):
        query_str = ["pacman", "-Q", package]

        try:
            process_pkg_query = subprocess.Popen(
                query_str, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            out, err = process_pkg_query.communicate(timeout=self.process_timeout)

            if process_pkg_query.returncode == 0:
                line = out.decode("utf-8").splitlines()

                return line[0].split(" ")[1]

                return True
            else:
                return False
        except Exception as e:
            self.logger.error(e)

    # is the package installed
    def check_package_installed(self, package):
        query_str = ["pacman", "-Qi", package]

        try:
            process_pkg_query = subprocess.Popen(
                query_str, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            out, err = process_pkg_query.communicate(timeout=self.process_timeout)

            if process_pkg_query.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(e)

    # entry completion: unused code
    def update_entry_completion(self, treestore):
        try:
            # liststore = Gtk.ListStore(str)
            treestore_completion = Gtk.TreeStore(str)
            for row in treestore:
                # liststore.append([data["name"]])
                treestore_completion.append(None, [row[0]])

            completion = Gtk.EntryCompletion()
            completion.set_model(treestore_completion)

            completion.set_text_column(0)
            completion.set_popup_completion(True)

            return completion
        except Exception as e:
            fn.logger.error("Exception in update_entry_completion(): %s" % e)

    def search(self, search_term, treestore):
        try:
            results = []
            treestore_packages = Gtk.TreeStore(str, str, str, str, bool, int, str, str)
            for row in treestore:
                if search_term in row[0]:
                    results.append(row)

                    treestore_packages.append(
                        None,
                        [
                            row[0],
                            row[1],
                            row[2],
                            row[3],
                            False,
                            Pango.Weight.NORMAL,
                            None,
                            None,
                        ],
                    )

            return treestore_packages
        except Exception as e:
            self.logger.error(e)

    # get all packages from specified repository
    def get_all_arco_packages_state(self):
        self.logger.debug("Getting package state data")
        installed_packages = []
        update_required = False

        for repo in self.arco_repos:
            query_str = ["pacman", "-Sl", repo]

            try:
                process_pkg_query = subprocess.Popen(
                    query_str,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                out, err = process_pkg_query.communicate(timeout=self.process_timeout)

                for line in out.decode("utf-8").splitlines():
                    package_info = line.split(" ")

                    if len(package_info) == 5:
                        if "[installed:" in package_info[3]:
                            update_required = True
                            installed_version = package_info[4].replace("]", "").strip()
                            installed_packages.append(
                                (package_info[1], installed_version, update_required)
                            )

                    else:
                        update_required = False

                    if len(package_info) == 4:
                        if package_info[3] == "[installed]":
                            # installed_packages.append(package_info[1])
                            installed_packages.append(
                                (package_info[1], package_info[2], update_required)
                            )

            except Exception as e:
                self.logger.error(e)

        return installed_packages

    # obtain all files from specific package
    def get_package_files(self, package):
        self.logger.info("Retrieving package files for %s" % package)
        query_str = ["pacman", "-Fl", package]

        try:
            process_pkg_query = subprocess.Popen(
                query_str, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            out, err = process_pkg_query.communicate(timeout=self.process_timeout)

            return out.decode("utf-8").splitlines()
            # self.pacman_data_queue.put(out.decode("utf-8").splitlines())
        except Exception as e:
            self.logger.error(e)

    # retrieve package info
    def get_package_sync_data(self):
        self.logger.info("Getting package syncronization data")
        query_str = ["pacman", "-Si"]
        try:
            process_pkg_query = subprocess.Popen(
                query_str, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            out, err = process_pkg_query.communicate(timeout=self.process_timeout)

            package_data = []
            package_name = "Unknown"
            package_version = "Unknown"
            package_description = "Unknown"
            package_repository = "Unknown"
            package_dl_link = "Unknown"
            package_build_date = "Unknown"
            package_dl_size = "Unknown"
            package_installed_size = "Unknown"
            package_arch = "Unknown"
            package_url = "Unknown"
            package_depends = []
            package_conflicts = []
            packager = "Unknown"
            package_replaces = []
            package_licenses = []
            package_groups = []

            for line in out.decode("utf-8").splitlines():
                if line.startswith("Name            :"):
                    package_name = line.replace(" ", "").split("Name:")[1].strip()

                if line.startswith("Version         :"):
                    package_version = line.replace(" ", "").split("Version:")[1].strip()

                if line.startswith("Description     :"):
                    package_description = line.split("Description     :")[1].strip()

                if line.startswith("Build Date      :"):
                    package_build_date = line.split("Build Date      :")[1].strip()

                if line.startswith("Download Size   :"):
                    package_dl_size = line.split("Download Size   :")[1].strip()

                if line.startswith("Installed Size  :"):
                    package_installed_size = line.split("Installed Size  :")[1].strip()

                if line.startswith("Architecture    :"):
                    package_arch = line.split("Architecture    :")[1].strip()

                if line.startswith("URL             :"):
                    package_url = line.split("URL             :")[1].strip()

                if line.startswith("Depends On      :"):
                    if line.split("Depends On      :")[1].strip() != "None":
                        pkg_depends_on_str = line.split("Depends On      :")[1].strip()

                        for pkg_dep in pkg_depends_on_str.split("  "):
                            package_depends.append((pkg_dep, None))
                    else:
                        package_depends = []

                if line.startswith("Conflicts With  :"):
                    if line.split("Conflicts With  :")[1].strip() != "None":
                        pkg_conflicts_with_str = line.split("Conflicts With  :")[
                            1
                        ].strip()

                        for pkg_con in pkg_conflicts_with_str.split("  "):
                            package_conflicts.append((pkg_con, None))
                    else:
                        package_conflicts = []

                if line.startswith("Replaces        :"):
                    if line.split("Replaces        :")[1].strip() != "None":
                        pkg_replaces_with_str = line.split("Replaces        :")[
                            1
                        ].strip()

                        for pkg_rep in pkg_replaces_with_str.split("  "):
                            package_replaces.append((pkg_rep, None))
                    else:
                        package_replaces = []

                if line.startswith("Licenses        :"):
                    if line.split("Licenses        :")[1].strip() != "None":
                        pkg_licenses_str = line.split("Licenses        :")[1].strip()

                        for pkg_lic in pkg_licenses_str.split("  "):
                            package_licenses.append(pkg_lic)
                    else:
                        package_licenses = []

                if line.startswith("Groups          :"):
                    if line.split("Groups          :")[1].strip() != "None":
                        pkg_groups_str = line.split("Groups          :")[1].strip()

                        for pkg_group in pkg_groups_str.split("  "):
                            package_groups.append(pkg_group)
                    else:
                        package_groups = []

                if line.startswith("Packager        :"):
                    packager = line.split("Packager        :")[1].strip()

                if line.startswith("Repository      :") and package_name != "Unknown":
                    package_repository = line.split("Repository      :")[1].strip()
                    if "arcolinux_" in package_repository:
                        package_data.append(
                            (
                                package_repository,
                                package_name,
                                package_version,
                                package_build_date,
                                package_dl_size,
                                package_installed_size,
                                package_description,
                                package_arch,
                                package_url,
                                package_depends,
                                package_conflicts,
                                packager,
                                package_replaces,
                                package_licenses,
                                package_groups,
                            )
                        )
                        package_depends = []
                        package_conflicts = []
                        package_replaces = []
                        package_licenses = []
                        package_groups = []
            self.pacman_data_queue.put(package_data)

        except Exception as e:
            self.logger.error(e)
