#!/usr/bin/env python

import sys
sys.path.append("debian/lib/python")

import os
import os.path
import re
import shutil
import subprocess

from debian_linux.debian import Changelog, VersionLinux
from debian_linux.patches import PatchSeries

class Main(object):
    def __init__(self, input_tar, input_patch, override_version):
        self.log = sys.stdout.write

        self.input_tar = input_tar
        self.input_patch = input_patch

        changelog = Changelog(version = VersionLinux)[0]
        source = changelog.source
        version = changelog.version

        if override_version:
            version = VersionLinux('%s-undef' % override_version)

        self.version_dfsg = version.linux_dfsg
        if self.version_dfsg is None:
            self.version_dfsg = '0'

        self.log('Using source name %s, version %s, dfsg %s\n' % (source, version.upstream, self.version_dfsg))

        self.orig = '%s-%s' % (source, version.upstream)
        self.orig_tar = '%s_%s.orig.tar.gz' % (source, version.upstream)

    def __call__(self):
        import tempfile
        self.dir = tempfile.mkdtemp(prefix = 'genorig', dir = 'debian')
        try:
            self.upstream_extract()
            self.upstream_patch()
            self.debian_patch()
            self.tar()
        finally:
            shutil.rmtree(self.dir)

    def upstream_extract(self):
        self.log("Extracting tarball %s\n" % self.input_tar)
        match = re.match(r'(^|.*/)(?P<dir>linux-\d+\.\d+\.\d+(-\S+)?)\.tar(\.(?P<extension>(bz2|gz)))?$', self.input_tar)
        if not match:
            raise RuntimeError("Can't identify name of tarball")

        cmdline = ['tar', '-xf', self.input_tar, '-C', self.dir]
        if match.group('extension') == 'bz2':
            cmdline.append('-j')
        elif match.group('extension') == 'gz':
            cmdline.append('-z')

        print cmdline
        if subprocess.Popen(cmdline).wait():
            raise RuntimeError("Can't extract tarball")

        os.rename(os.path.join(self.dir, match.group('dir')), os.path.join(self.dir, self.orig))

    def upstream_patch(self):
        if self.input_patch is None:
            return
        self.log("Patching source with %s\n" % self.input_patch)
        match = re.match(r'(^|.*/)patch-\d+\.\d+\.\d+(-\S+?)?(\.(?P<extension>(bz2|gz)))?$', self.input_patch)
        if not match:
            raise RuntimeError("Can't identify name of patch")
        cmdline = []
        if match.group('extension') == 'bz2':
            cmdline.append('bzcat')
        elif match.group('extension') == 'gz':
            cmdline.append('zcat')
        else:
            cmdline.append('cat')
        cmdline.append(self.input_patch)
        cmdline.append('| (cd %s; patch -p1 -f -s -t --no-backup-if-mismatch)' % os.path.join(self.dir, self.orig))
        if os.spawnv(os.P_WAIT, '/bin/sh', ['sh', '-c', ' '.join(cmdline)]):
            raise RuntimeError("Can't patch source")

    def debian_patch(self):
        name = "orig-" + self.version_dfsg
        self.log("Patching source with debian patch (series %s)\n" % name)
        fp = file("debian/patches/series/" + name)
        series = PatchSeries(name, "debian/patches", fp)
        series(dir = os.path.join(self.dir, self.orig))

    def tar(self):
        out = os.path.join("../orig", self.orig_tar)
        try:
            os.mkdir("../orig")
        except OSError: pass
        try:
            os.stat(out)
            raise RuntimeError("Destination already exists")
        except OSError: pass
        self.log("Generate tarball %s\n" % out)
        cmdline = ['tar -czf', out, '-C', self.dir, self.orig]
        try:
            if os.spawnv(os.P_WAIT, '/bin/sh', ['sh', '-c', ' '.join(cmdline)]):
                raise RuntimeError("Can't patch source")
            os.chmod(out, 0644)
        except:
            try:
                os.unlink(out)
            except OSError:
                pass
            raise

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = "%prog [OPTION]... TAR [PATCH]")
    parser.add_option("-V", "--override-version", dest = "override_version", help = "Override version", metavar = "VERSION")
    options, args = parser.parse_args()

    input_tar = args[0]
    input_patch = None
    if len(args) > 1:
        input_patch = args[1]

    Main(input_tar, input_patch, options.override_version)()
