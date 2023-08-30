# ArcoLinux RepoXPlorer

A GTK Python application which lets you explore Arch packages from only the ArcoLinux Pacman repositories.

The following repositories are explorable:

- arcolinux_repo
- arcolinux_repo_3party
- arcolinux_repo_xlarge
- arcolinux_repo_testing

###### Main Window

![Main Window](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/45d3d7f6-1ddf-4d13-93fc-35965b93b06d)

- Any installed packages with pending updates will be highlighted
- Double clicking a package name displays more details
- Clicking Refresh runs a ```pacman -Sy``` to synchronize the pacman repositories and bring in the latest package details

###### Package Details Window

![Package Details Window](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/93a60ada-c033-47b4-b952-4702c66a27f5)

###### Download option

![Download Package](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/e64964b1-4f9a-4946-b59f-ed4dba157f92)

The download package option lets you download the associated .zst package file to disk for offline installations. This is stored inside $HOME/repoxp/packages.

###### Files view
![Files Stack](https://github.com/DeltaCopy/arcolinux-repo-explorer/assets/121581829/a088600d-576e-4137-b202-c50a44985966)

# Requirements

- Python 3.11
- GTK3
- Pacman configured to use ArcoLinux repositories

This application requires sudo access to run Pacman commands successfully.

# Usage

```bash
git clone https://github.com/DeltaCopy/arcolinux-repo-explorer.git
cd arcolinux-repo-explorer/usr/share/repoxp
sudo python repoxp.py
```
