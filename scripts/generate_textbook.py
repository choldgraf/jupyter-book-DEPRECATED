from subprocess import check_call
import os
import os.path as op
import shutil as sh
import yaml
from nbclean import NotebookCleaner
import nbformat as nbf
from tqdm import tqdm
import numpy as np
from glob import glob
import argparse
DESCRIPTION = ("Convert a collection of Jupyter Notebooks into Jekyll "
               "markdown suitable for a course textbook.")

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument("--site_root", default=None, help="Path to the root of the textbook repository.")
parser.add_argument("--overwrite", action='store_true', help="Overwrite md files if they already exist.")
parser.add_argument("--execute", action='store_true', help="Execute notebooks before converting to MD.")
parser.set_defaults(overwrite=False, execute=False)


def _prepare_toc(toc):
    """Prepare the TOC for processing."""
    # Drop toc items w/o links
    toc = [ii for ii in toc if ii.get('url', None) is not None]
    # Un-nest the TOC so it's a flat list
    new_toc = []
    for ii in toc:
        sections = ii.pop('sections', None)
        new_toc.append(ii)
        if sections is None:
            continue
        for jj in sections:
            new_toc.append(jj)
    return new_toc


def _prepare_link(link):
    """Prep the formatting for a link."""
    link = _strip_suffixes(link)
    link = link.lstrip('._')
    if not link.startswith('/'):
        link = '/' + link
    link = link.replace(NOTEBOOKS_FOLDER_NAME + os.sep,
                        TEXTBOOK_FOLDER_NAME.lstrip('_') + os.sep)
    return link


def _strip_suffixes(string, suffixes=None):
    """Remove suffixes so we can create links."""
    suffixes = ['.ipynb', '.md'] if suffixes is None else suffixes
    for suff in suffixes:
        string = string.replace(suff, '')
    return string


def _clean_notebook_cells(path_ntbk):
    """Clean up cell text of an nbformat NotebookNode."""
    ntbk = nbf.read(path_ntbk, nbf.NO_CONVERT)
    # Remove '#' from the end of markdown headers
    for cell in ntbk.cells:
        if cell.cell_type == "markdown":
            cell_lines = cell.source.split('\n')
            for ii, line in enumerate(cell_lines):
                if line.startswith('#'):
                    cell_lines[ii] = line.rstrip('#').rstrip()
            cell.source = '\n'.join(cell_lines)
    nbf.write(ntbk, path_ntbk)


def _clean_lines(lines, filepath):
    """Replace images with jekyll image root and add escape chars as needed."""
    inline_replace_chars = ['#']
    for ii, line in enumerate(lines):
        # Images: replace absolute nbconvert image paths to baseurl paths
        path_rel_root = op.relpath(SITE_ROOT, op.dirname(filepath))
        line = line.replace(IMAGES_FOLDER, op.join(path_rel_root, 'images'))

        # Adding escape slashes since Jekyll removes them
        # Make sure we have at least two dollar signs and they
        # Aren't right next to each other
        dollars = np.where(['$' == char for char in line])[0]
        if len(dollars) > 2 and all(ii > 1 for ii in (dollars[1:] - dollars[:1])):
            for char in inline_replace_chars:
                line = line.replace('\\{}'.format(char), '\\\\{}'.format(char))
        line = line.replace(' \\$', ' \\\\$')
        lines[ii] = line
    return lines


def _copy_non_content_files():
    """Copy non-markdown/notebook files in the notebooks/ folder into Chapters so relative links work."""
    all_files = glob(op.join(NOTEBOOKS_FOLDER, '**', '*'), recursive=True)
    non_content_files = [ii for ii in all_files if not any(ii.endswith(ext) for ext in ['.ipynb', '.md'])]
    for ifile in non_content_files:
        if op.isdir(ifile):
            continue
        # Convert the old link to the new path, note this may change folder name structure
        old_link = ifile.split(NOTEBOOKS_FOLDER)[-1]
        new_link = _prepare_link(old_link)

        # The folder name may change if the permalink sanitizing changes it.
        # this ensures that a new folder exists if needed
        new_path = ifile.replace(NOTEBOOKS_FOLDER, TEXTBOOK_FOLDER).replace(old_link, new_link)
        if not op.isdir(op.dirname(new_path)):
            os.makedirs(op.dirname(new_path))
        sh.copy2(ifile, new_path)


def _between_symbols(string, c1, c2):
    """Grab characters between symbols in a string.
    Will return empty string if nothing is between c1 and c2."""
    for char in [c1, c2]:
        if char not in string:
            raise ValueError("Couldn't find character {} in string {}".format(
                char, string))
    return string[string.index(c1)+1:string.index(c2)]


if __name__ == '__main__':
    args = parser.parse_args()
    overwrite = bool(args.overwrite)
    execute = bool(args.execute)
    if args.site_root is None:
        args.site_root = op.join(op.dirname(op.abspath(__file__)), '..')

    # Paths for our notebooks
    SITE_ROOT = op.abspath(args.site_root)
    TOC_YAML = op.join(SITE_ROOT, '_data', 'toc.yml')
    CONFIG_FILE = op.join(SITE_ROOT, '_config.yml')
    TEMPLATE_PATH = op.join(SITE_ROOT, 'assets', 'templates', 'jekyllmd.tpl')
    TEXTBOOK_FOLDER_NAME = '_ch'
    NOTEBOOKS_FOLDER_NAME = 'notebooks'
    TEXTBOOK_FOLDER = op.join(SITE_ROOT, TEXTBOOK_FOLDER_NAME)
    NOTEBOOKS_FOLDER = op.join(SITE_ROOT, NOTEBOOKS_FOLDER_NAME)
    IMAGES_FOLDER = op.join(SITE_ROOT, 'images')
    SUPPORTED_FILE_SUFFIXES = ['.ipynb', '.md']

    # Load the yaml for this site
    with open(CONFIG_FILE, 'r') as ff:
        site_yaml = yaml.load(ff.read())
    # Load the textbook yaml for this site
    if not op.exists(TOC_YAML):
        raise ValueError("No toc.yml file found, please create one")
    with open(TOC_YAML, 'r') as ff:
        toc = yaml.load(ff.read())

    # Drop divider items and non-linked pages in the sidebar, un-nest sections
    toc = _prepare_toc(toc)

    # --- Loop through all ipynb/md files, convert to md as necessary and copy. ---
    n_skipped_files = 0
    n_built_files = 0

    for ix_file, page in enumerate(tqdm(list(toc))):
        link = page.get('url', None)
        title = page.get('title', None)
        pageclass = page.get('class', None)
        numbered = page.get('not_numbered', None)
        sections = page.get('sections', None)

        path_link = os.path.join(SITE_ROOT, link.replace('/ch/', 'notebooks/'))
        if not any(path_link.endswith(ii) for ii in SUPPORTED_FILE_SUFFIXES):
            for suf in SUPPORTED_FILE_SUFFIXES:
                if op.exists(path_link + suf):
                    link = link + suf
                    path_link = path_link + suf
                    break

        if not op.exists(path_link):
            raise ValueError("Could not find file {}.".format(path_link))

        # Check new folder / file path
        filename = op.basename(path_link)
        new_folder = op.dirname(path_link).replace(NOTEBOOKS_FOLDER_NAME, TEXTBOOK_FOLDER_NAME)
        new_file_path = op.join(new_folder, filename.replace('.ipynb', '.md'))

        if overwrite is False and op.exists(new_file_path):
            n_skipped_files += 1
            continue

        if not op.isdir(new_folder):
            os.makedirs(new_folder)

        # Generate previous/next page links
        if ix_file == 0:
            prev_page_link = ''
            prev_file_title = ''
        else:
            prev_file_title = toc[ix_file-1].get('title')
            prev_page_link = toc[ix_file-1].get('url')
            prev_page_link = _prepare_link(prev_page_link)

        if ix_file == len(toc) - 1:
            next_page_link = ''
            next_file_title = ''
        else:
            next_file_title = toc[ix_file+1].get('title')
            next_page_link = toc[ix_file+1].get('url')
            next_page_link = _prepare_link(next_page_link)

        # Convert notebooks or just copy md if no notebook.
        if link.endswith('.ipynb'):
            # Create a temporary version of the notebook we can modify
            tmp_notebook = path_link + '_TMP'
            sh.copy2(path_link, tmp_notebook)

            # Clean up the file before converting
            cleaner = NotebookCleaner(tmp_notebook)
            cleaner.remove_cells(empty=True)
            if site_yaml.get('hide_cell_text', False):
                cleaner.remove_cells(search_text=site_yaml.get('hide_cell_text'))
            if site_yaml.get('hide_code_text', False):
                cleaner.clear(kind="content", search_text=site_yaml.get('hide_code_text'))
            cleaner.clear('stderr')
            cleaner.save(tmp_notebook)
            _clean_notebook_cells(tmp_notebook)

            # Run nbconvert moving it to the output folder
            # This is the output directory for `.md` files
            build_call = '--FilesWriter.build_directory={}'.format(new_folder)
            # This is where images go - remove the _ so Jekyll will copy them over
            images_call = '--NbConvertApp.output_files_dir={}'.format(
                op.join(IMAGES_FOLDER, new_folder.lstrip('_')))
            call = ['jupyter', 'nbconvert', '--log-level="CRITICAL"',
                    '--to', 'markdown', '--template', TEMPLATE_PATH,
                    images_call, build_call, tmp_notebook]
            if execute is True:
                call.insert(-1, '--execute')
            check_call(call)
            os.remove(tmp_notebook)
        elif link.endswith('.md'):
            # If a non-notebook file, just copy it over.
            # If markdown we'll add frontmatter later
            sh.copy2(path_link, new_file_path)
        else:
            raise ValueError("Files must end in ipynb or md")

        # Extra slash to the inline math before `#` since Jekyll strips it
        with open(new_file_path, 'r') as ff:
            lines = ff.readlines()
        lines = _clean_lines(lines, new_file_path)

        # Front-matter YAML
        yaml_fm = []
        yaml_fm += ['---']

        if link.endswith('.ipynb'):
            yaml_fm += ['interact_link: {}'.format(link.lstrip('./'))]
        yaml_fm += ["title: '{}'".format(title)]
        yaml_fm += ["permalink: '{}'".format(_prepare_link(link))]
        yaml_fm += ['prev_page:']
        yaml_fm += ['  url: {}'.format(_prepare_link(prev_page_link).replace('"', "'"))]
        yaml_fm += ["  title: '{}'".format(prev_file_title)]
        yaml_fm += ['next_page:']
        yaml_fm += ['  url: {}'.format(_prepare_link(next_page_link).replace('"', "'"))]
        yaml_fm += ["  title: '{}'".format(next_file_title)]
        yaml_fm += ['---']
        yaml_fm = [ii + '\n' for ii in yaml_fm]
        lines = yaml_fm + lines

        # Write the result
        with open(new_file_path, 'w') as ff:
            ff.writelines(lines)
        n_built_files += 1

    print("\n***\nGenerated {} new files\nSkipped {} already-built files".format(n_built_files, n_skipped_files))
    if n_built_files == 0:
        print("\nDelete the markdown files in '{}' for any pages that you wish to re-build.".format(TEXTBOOK_FOLDER_NAME))
    print('***\n')

    # Copy non-markdown files in notebooks/ in case they're referenced in the notebooks
    print('Copying non-content files inside `notebooks/`...')
    _copy_non_content_files()

    print('Done!')
