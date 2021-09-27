# Debian kernel build instructions

Original manual: https://wiki.debian.org/HowToCrossBuildAnOfficialDebianKernelPackage

## Prepare

Install Cross-Build Dependency

```
apt install fakeroot git kernel-wedge quilt ccache flex bison libssl-dev dh-exec rsync libelf-dev bc crossbuild-essential-arm64
```

Clone Git Repo of Kernel

```
git clone ssh://git@lpt.uprojects.org:766/common/linux.git lpt-linux
```

Clone this repo next to lpt-linux

```
ssh://git@lpt.uprojects.org:766/debian/debian-linux-kernel.git linux
```

Generate orig kernel source archive

```
cd linux
debian/bin/genorig.py ../lpt-linux
```

## Cross build

```
# This triplet is defined in
#   https://salsa.debian.org/kernel-team/linux/tree/master/debian/config/<ARCH>/
# and its sub-directories.
# Here is just an example
ARCH=arm64
FEATURESET=none
FLAVOUR=arm64

export $(dpkg-architecture -a$ARCH)
export PATH=/usr/lib/ccache:$PATH

# Build profiles is from: https://salsa.debian.org/kernel-team/linux/blob/master/debian/README.source
export DEB_BUILD_PROFILES="cross nopython nodoc pkg.linux.notools pkg.linux.udeb-unsigned-test-build"
# Enable build in parallel
export MAKEFLAGS="-j$(($(nproc)*2))"
# Disable -dbg (debug) package is only possible when distribution="UNRELEASED" in debian/changelog
export DEBIAN_KERNEL_DISABLE_DEBUG=
[ "$(dpkg-parsechangelog --show-field Distribution)" = "UNRELEASED" ] &&
  export DEBIAN_KERNEL_DISABLE_DEBUG=yes

fakeroot make -f debian/rules clean
fakeroot make -f debian/rules orig
fakeroot make -f debian/rules source
fakeroot make -f debian/rules.gen setup_${ARCH}_${FEATURESET}_${FLAVOUR}
fakeroot make -f debian/rules.gen binary-arch_${ARCH}_${FEATURESET}_${FLAVOUR}
```

The last two lines can also be simplified, but with a "sed" hack to debian/rules.gen below. In this way, udeb packages will be also built.

```
fakeroot make -f debian/rules.gen setup_${ARCH}
sed -i "s/binary-arch_${ARCH}:: binary-arch_${ARCH}_extra binary-arch_${ARCH}_${FEATURESET} binary-arch_${ARCH}_real/binary-arch_${ARCH}:: binary-arch_${ARCH}_extra binary-arch_${ARCH}_${FEATURESET}/" debian/rules.gen
fakeroot make -f debian/rules.gen binary-arch_${ARCH}
```
