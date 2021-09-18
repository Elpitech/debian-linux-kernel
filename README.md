# Debian linux kernel with Baikal-M support

## Preparing and building packages

1. Clone packaging repository

```
git clone --depth=1 --branch=lpt-bm-5.x.y <repo> linux
```

2. Download linux kernel source

```
wget https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.x.y.tar.xz
```

3. Prepare origin source package

```
cd linux
debian/bin/genorig.py ../linux-5.x.y.tar.xz
debian/rules orig
```

4. Generate control file

```
debian/rules debian/control
```

5. Build packages

```
fakeroot debian/rules binary -j`nproc`
```

Also architecture dependent packages may be built separately:

```
fakeroot debian/rules binary-indep -j`nproc`
fakeroot debian/rules binary-arch -j`nproc`
```

## Using docker container to build

1. Clone helper repository

```
git clone --depth=1 --branch=docker <repo> .
```

2. Build docker container

```
make build-docker
```

3. Clone packaging repository

```
git clone --depth=1 --branch=lpt-bm-5.x.y <repo> linux
```

4. Download linux kernel source

```
wget https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.x.y.tar.xz
```

5. Login to docker container

```
make enter-docker
```

6. Prepare origin source package

```
cd linux
debian/bin/genorig.py ../linux-5.x.y.tar.xz
debian/rules orig
```

7. Generate control file

```
debian/rules debian/control
```

NOTE: This command will fail but it's expected behavior.

8. Build packages

```
fakeroot debian/rules binary -j`nproc`
```

