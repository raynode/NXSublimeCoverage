import os
import sys
import json
import fnmatch

import sublime
import sublime_plugin

from .lcovParse import walkFile

ST3 = int(sublime.version()) >= 3000

debug = lambda *args: sys.stdout.write("\n%s" % " ".join(map(str, args)))

REGION_KEY_COVERED = 'NXSublimeCoverageCovered'
REGION_KEY_UNCOVERED = 'NXSublimeCoverageUnCovered'

def getCoverageDir():
  settings = sublime.load_settings("NXSublimeCoverage.sublime-settings")

  return settings.get("coverageDir") or 'coverage'

def find_project_root(file_path):
  """
    Project Root is defined as the parent directory
    that contains a directory called 'coverage'
  """
  if os.access(os.path.join(file_path, getCoverageDir()), os.R_OK):
    return file_path
  parent, current = os.path.split(file_path)
  if current:
    return find_project_root(parent)

def find_lcov_filename(coverage_dir):
  """
    Returns latest coverage json for specifed file or None if cannot find it
    in specifed coverage direcotry
  """
  files = []
  for root, dirnames, filenames in os.walk(coverage_dir):
  	for filename in fnmatch.filter(filenames, 'lcov.info'):
   		files.append(os.path.join(root, filename))

  debug("found lcov file: " + ",".join(files or []))
  getmtime = lambda key: os.path.getmtime(os.path.join(coverage_dir, key))
  coverage_file_name = None

  if files:
    files.sort(key=getmtime, reverse=True)
    coverage_file_name = files.pop(0)

  return coverage_file_name

def parse_lcov(report):
  print(report)
  return report

def read_lcov(file_path):
  debug("reading " + file_path)
  with open(file_path, 'r', encoding='utf-8') as coverage_file:
    try:
      lcov = walkFile(coverage_file.read())
      return lcov
    except IOError:
      return None

def test_filename(filename, relative_filename):
  return filename.replace("./", "").endswith(relative_filename)

def get_file_info(lcov_data):
  files = att
  # for fileInfo in lcov_data:
  #   name = fileInfo.file
  #   files[name] or=
  #     hit: 0
  #     total: 0
  #     covered: 0
  #     coverage: 0
  #     name: name
  #     lines: {}
  #   fdata = files[name]

  #   for detail in fileInfo.lines.details when detail.line
  #     unless fdata.lines[detail.line]
  #       fdata.total++
  #       total++

  #     fdata.lines[detail.line] or=
  #       hit: 0
  #       no: detail.line
  #       klass: 'lcov-info-no-coverage'
  #       range: [[detail.line - 1, 0], [detail.line - 1, 0]]
  #     line = fdata.lines[detail.line]

  #     if detail.hit > 0
  #       line.klass = 'lcov-info-has-coverage'
  #       unless line.hit
  #         fdata.covered++
  #         covered++
  #       line.hit += detail.hit
  #       fdata.hit += detail.hit
  #       hit += detail.hit

  #   fdata.coverage = (if fdata.total then fdata.covered/fdata.total else 0)*100

class ShowJsCoverageCommand(sublime_plugin.TextCommand):
  def init(self, view, project_root):
    # get name of currently opened file
    coverage_dir = os.path.join(project_root, getCoverageDir())
    coverage_filename = find_lcov_filename(coverage_dir)

    debug("project_root", project_root)
    debug("coverage_dir", coverage_dir)
    debug("coverage_filename", coverage_filename)

    if not coverage_filename:
      if view.window():
        sublime.status_message(
          "Can't find the coverage file in project root: " + str(project_root))
      return None

    # Clean up
    view.erase_status(REGION_KEY_COVERED)
    view.erase_regions(REGION_KEY_COVERED)

    lcov_data = read_lcov(
      os.path.join(coverage_dir, coverage_filename))

    report = parse_lcov(lcov_data)

    if report is None:
      if view.window():
        sublime.status_message(
          "Can't read coverage report from file: " + str(coverage_filename))
      return None

    return report

  """
    Highlight uncovered lines in the current file
    based on a previous coverage run.
  """
  def run(self, edit):
    view = self.view

    # get name of currently opened file
    filename = view.file_name()
    if not filename:
      return None
    project_root = find_project_root(filename)

    if not project_root:
      if view.window():
        sublime.status_message("Could not find coverage directory.")
      return None

    relative_filename = filename.replace(project_root + "/", "")

    outlines = {}
    report = self.init(view, project_root)

    if report is None:
      return

    debug("Found report for the following number of files: " + str(len(report)))

    if not report:
      view.set_status(REGION_KEY_COVERED, "UNCOVERED!")
      if view.window():
        sublime.status_message(
          "Can't find the coverage json file in project root: " + project_root)
      return

    for file_report in report:
      filename = file_report.file.replace("./", "")
      if not filename.endswith(relative_filename):
        continue

      debug("Found test report for file " + str(relative_filename))

      lines = file_report.lines

      if not lines:
        sublime.status_message("No lines found in coverage")
        return

      for line in lines.details:
        outlines[line.get("line")] = line.get("hit") > 0

    badOutlines = []
    goodOutlines = []

    for lineNumber in outlines:
      region = view.full_line(view.text_point(int(lineNumber) - 1, 0))

      if outlines[lineNumber]:
        goodOutlines.append(region)
      else:
        badOutlines.append(region)

    flags = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE if ST3 else sublime.HIDDEN
    if goodOutlines:
      view.add_regions(REGION_KEY_COVERED, goodOutlines,
        'markup.inserted.diff', 'dot', flags)

    if badOutlines:
      view.add_regions(REGION_KEY_UNCOVERED, badOutlines,
        'markup.deleted.diff', 'dot', flags)

class ClearJsCoverageCommand(sublime_plugin.TextCommand):

  """
    Remove highlights created by plugin.
  """

  def run(self, edit):
    view = self.view
    view.erase_regions(REGION_KEY_COVERED)
    view.erase_regions(REGION_KEY_UNCOVERED)
