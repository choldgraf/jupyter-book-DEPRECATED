"""A helper script to "clean up" all of your notebooks and
generated markdown files."""
import shutil as sh
import os.path as op

path_root = op.join(op.dirname(op.abspath(__file__)), '..')

paths = [op.join(path_root, 'images', 'chapters'),
         op.join(path_root, '_site'),
         op.join(path_root, 'ch'),
for path in paths:
    print('Removing {}...'.format(path))
    sh.rmtree(path, ignore_errors=True)

print('Done!')
