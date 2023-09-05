# ArcoLinux RepoXPlorer

A GTK Python application which lets you explore Arch packages from only the ArcoLinux Pacman repositories.

The following repositories are explorable:

- arcolinux_repo
- arcolinux_repo_3party
- arcolinux_repo_xlarge
- arcolinux_repo_testing

###### Main Window

![Main Window](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/dfe486aa-fd74-472e-8c55-b17cae5c83c3)

- Any installed packages with pending updates will be highlighted
- Double clicking a package name displays more details
- Clicking Refresh runs a ```pacman -Sy``` to synchronize the pacman repositories and bring in the latest package details

###### Package Details Window

![Package Details Window](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/adc6cd4b-5709-44a6-9436-8b71ae6ae87a)

###### Download option

![Download Package](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/e64964b1-4f9a-4946-b59f-ed4dba157f92)

The download package option lets you download the associated .zst package file to disk for offline installations.

This is stored inside $HOME/repoxp/packages

###### Files view
![Files Stack](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/a088600d-576e-4137-b202-c50a44985966)

# Requirements

- Python 3.11 or above
- GTK3
- Pacman configured to use ArcoLinux repositories
- Polkit running and configured correctly on system

This application requires sudo access to run Pacman commands successfully.

# Installation

Download prebuilt .zst file.
```bash
sudo pacman -U arcolinux-repo-explorer-23.09-05-x86_64.pkg.tar.zst
```
This will install the package into /usr/share/repoxp

# Running
Open a terminal and type:
```bash
repoxp
```
