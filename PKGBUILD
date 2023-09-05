# Maintainer: John Patrick <john.patrick@gmail.com>
pkgname=arcolinux-repoxp
_pkgname=arcolinux-repoxp
pkgver=23.09.01
pkgrel=1
pkgdesc="ArcoLinux repository explorer"
arch=('x86_64')
url="https://github.com/DeltaCopy/arcolinux-repo-explorer"
license=('GPL3')
depends=('python-gobject' 'polkit-gnome')
makedepends=('git')
options=(!strip !emptydirs)
source=(git+${url})
sha256sums=('SKIP')
pkgver() {
    cd "${srcdir}/repoxp"
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}
package() {
	install -m755 -d "${pkgdir}/usr/"
	cp -r ${srcdir}/${_pkgname}/usr ${pkgdir}
}
