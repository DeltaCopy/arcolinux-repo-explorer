# ArcoLinux RepoXPlorer

A GTK Python application which lets you explore Arch packages from only the ArcoLinux Pacman repositories.

The following repositories are explorable:

- arcolinux_repo
- arcolinux_repo_3party
- arcolinux_repo_xlarge
- arcolinux_repo_testing

###### Main Window

![Main Window](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/5861e1be-5f5b-40e0-bd9b-2706713b66d2)

- Any installed packages with pending updates will be highlighted
- Double clicking a package name displays more details
- Clicking Refresh runs a ```pacman -Sy``` to synchronize the pacman repositories and bring in the latest package details

###### Package Details Window

![Package Details Window](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/25967b8f-fded-4324-97a9-852e69af8cda)

###### Download option

![Download Package](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/b0947d7c-0cac-4002-ab11-f8f44bb9bb4f)

The download package option lets you download the associated .zst package file to disk for offline installations.

This is stored inside $HOME/repoxp/packages

###### Files view
![Files Stack](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/a3480b2a-3a2b-4e7d-8b5a-6dbe8ad9e3e1)

###### Searching
![Searching](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/d32b59e7-9f2a-4bf2-945d-0924e564806a)

Fuzzy searching based on entered string.

# Requirements

- OS: Arch Linux only
- Python 3.11 or above
- GTK3
- Pacman configured to use ArcoLinux repositories
- Polkit running and configured correctly on system

This application requires sudo access to run Pacman commands successfully.

# Building the package

```bash
mkdir /tmp/arcolinux-repo-explorer && cd /tmp/arcolinux-repo-explorer
wget https://raw.githubusercontent.com/DeltaCopy/arcolinux-repo-explorer/main/PKGBUILD
makepkg -si
```

If those steps fail use the offline method described below.

# Offline installation method

```bash
wget https://github.com/DeltaCopy/arcolinux-repo-explorer/releases/download/release-23.09-05/arcolinux-repo-explorer-23.09-05-x86_64.pkg.tar.zst
sudo pacman -U arcolinux-repo-explorer-23.09-05-x86_64.pkg.tar.zst
```
This will install the package into /usr/share/repoxp

# Running
Open a terminal and type:
```bash
repoxp
```
