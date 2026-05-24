"""Read cco stdout and inject GitHub Actions log-grouping markers per stage."""
import re
import sys

DISPATCH_RE = re.compile(r'^\[cco\] \[([^\]]+)\] dispatching ')
PIPELINE_END_RE = re.compile(r'^\[cco\] \[pipeline\] (?:core pipeline|draft PR|PR finalisation|finaliser)')

in_group = False

for line in sys.stdin:
    sys.stdout.write(line)
    sys.stdout.flush()

    if DISPATCH_RE.match(line):
        stage = DISPATCH_RE.match(line).group(1)
        if in_group:
            print('::endgroup::', flush=True)
        print(f'::group::{stage}', flush=True)
        in_group = True
    elif in_group and PIPELINE_END_RE.match(line):
        print('::endgroup::', flush=True)
        in_group = False

if in_group:
    print('::endgroup::', flush=True)
