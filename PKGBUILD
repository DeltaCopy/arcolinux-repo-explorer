# Maintainer: DeltaCopy (fennec)
pkgname=arcolinux-repo-explorer
_pkgname=arcolinux-repo-explorer
_destname1="/usr"
_licensedir="/usr/share/repoxp/licenses/"
pkgver=23.09
pkgrel=02
pkgdesc="ArcoLinux Repository Explorer"
arch=('x86_64')
url="https://github.com/DeltaCopy/${_pkgname}"
license=('GPL3')
depends=('python-gobject' 'polkit-gnome')
makedepends=('git')
options=(!strip !emptydirs)
source=("${_pkgname}::git+${url}")
sha256sums=('SKIP')
package() {
	install -dm755 ${pkgdir}${_licensedir}${_pkgname}
	install -m644  ${srcdir}/${_pkgname}/LICENSE ${pkgdir}${_licensedir}${_pkgname}
	sed -i -e s/pkgversion/$pkgver/ $srcdir/${_pkgname}/usr/share/repoxp/repoxp.py
	sed -i -e s/pkgrelease/$pkgrel/ $srcdir/${_pkgname}/usr/share/repoxp/repoxp.py
	sed -i -e s/pkgversion/$pkgver/ $srcdir/${_pkgname}/usr/share/repoxp/ui/AboutDialog.py
	sed -i -e s/pkgrelease/$pkgrel/ $srcdir/${_pkgname}/usr/share/repoxp/ui/AboutDialog.py

	cp -r ${srcdir}/${_pkgname}/${_destname1} ${pkgdir}
}
