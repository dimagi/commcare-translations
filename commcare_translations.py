from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from packaging.version import Version, InvalidVersion
from os import listdir
from os.path import join, normpath
import re
from io import StringIO
from io import open


def loads(s):
    # okay this is an abstraction violation, but I wrote load(f) so I know this will work
    f = s.split('\n')
    return load(f)
    

def load(f):
    messages = {}
    for line in f:
        # i think this line is wrong, but i don't want to break anything
        # clayton says there's no \# escaping on the phone
        line = re.split(r'(?<!\\)#', line)[0] # strip comments starting with '#', ignoring '\#'
        line = line.strip()
        if not line: continue
        i = line.index('=')
        messages[line[:i].strip()] = line[i+1:]
    return messages


def get_translation_file_paths(lang, version=1, commcare_version=None):
    paths_to_try = []
    if commcare_version == 'latest':
        files = listdir(normpath(join(__file__, "../historical-translations-by-version/")))
        if len(files):
            files.sort()
            files.reverse()
            paths_to_try.append(
                '../historical-translations-by-version/{file}'
                    .format(file=files[0])
            )
            commcare_version = None

    elif commcare_version:
        try:
            commcare_version = Version(commcare_version)
        except InvalidVersion:
            commcare_version = None
    if version == 2 and lang == 'en' and commcare_version:
        # the earliest version we have is 2.23
        if commcare_version < Version('2.23'):
            commcare_version = Version('2.23')
        major = commcare_version.major
        minor = commcare_version.minor
        bugfix = commcare_version.micro
        while bugfix >= 0:
            new_version = (
                '{}.{}.{}'.format(major, minor, bugfix) if bugfix > 0
                else '{}.{}'.format(major, minor)
            )
            commcare_version = Version(new_version)
            paths_to_try.append(
                '../historical-translations-by-version/{commcare_version}-'
                'messages_{lang}-{version}.txt'.format(
                    commcare_version=commcare_version,
                    lang=lang,
                    version=version,
                )
            )
            bugfix -= 1

    while version:
        paths_to_try.append('../messages_{lang}-{version}.txt'
                            .format(lang=lang, version=version))
        version -= 1
    return paths_to_try


def load_translations(lang, version=1, commcare_version=None):
    # pt => por: hack for backwards compatibility
    if lang == 'pt':
        lang = 'por'

    try:
        str(lang)
    except UnicodeEncodeError:
        return {}

    paths_to_try = get_translation_file_paths(lang, version, commcare_version)

    for rel_path in paths_to_try:
        path = normpath(join(__file__, rel_path))
        try:
            with open(path, encoding='utf-8') as f:
                return load(f)
        except IOError:
            pass
    return {}


def dumps(dct):
    io = StringIO()
    for key, val in sorted(dct.items()):
        # replace all blanks with non-breaking spaces
        if not val.strip():
            val = '\u00A0'
        # get rid of newlines
        val = val.replace('\n', '\\n')
        # escape starting # character
        val = re.sub(r'(?<!\\)#', r'\#', val)
        io.write("{key}={val}\n".format(key=key.strip(), val=val))
    return io.getvalue()
