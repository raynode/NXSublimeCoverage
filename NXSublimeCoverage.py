import os
import sys
import json
import fnmatch

import sublime
import sublime_plugin

from .utils.lcovParse import walkFile

ST3 = int(sublime.version()) >= 3000

LCOV = 'LCOV_INFO'
COVERAGE = 'COVERAGE_JSON'

debug = lambda *args: sys.stdout.write("\n%s" % " ".join(map(str, args)))

REGION_KEY_BRANCH_COVERED = 'NXSublimeCoverageBranchCovered'
REGION_KEY_BRANCH_UNCOVERED = 'NXSublimeCoverageBranchUncovered'
REGION_KEY_COVERED = 'NXSublimeCoverageCovered'
REGION_KEY_UNCOVERED = 'NXSublimeCoverageUnCovered'


REGION_TEXT_FLAGS_COVERED = sublime.DRAW_NO_FILL
REGION_TEXT_FLAGS_UNCOVERED = sublime.DRAW_NO_FILL
REGION_LINE_FLAGS_COVERED = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
REGION_LINE_FLAGS_UNCOVERED = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
REGION_FLAGS_BRANCH_COVERED = sublime.DRAW_NO_FILL
REGION_FLAGS_BRANCH_UNCOVERED = sublime.DRAW_NO_FILL

REGION_TEXT_SCOPE_COVERED = 'markup.inserted'
REGION_TEXT_SCOPE_UNCOVERED = 'markup.deleted.diff'
REGION_LINE_SCOPE_COVERED = 'markup.inserted'
REGION_LINE_SCOPE_UNCOVERED = 'markup.deleted.diff'
REGION_SCOPE_BRANCH_COVERED = 'markup.inserted'
REGION_SCOPE_BRANCH_UNCOVERED = 'markup.changed.diff'

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

def find_file_in_dir(directory, file):
  """
    Returns latest file in specifed direcotry or None if cannot find it
  """
  files = []
  for root, dirnames, filenames in os.walk(directory):
    for filename in fnmatch.filter(filenames, file):
      files.append(os.path.join(root, filename))

  getmtime = lambda key: os.path.getmtime(os.path.join(directory, key))
  found_file = None

  if files:
    files.sort(key=getmtime, reverse=True)
    found_file = files.pop(0)

  return found_file

def read_file(file_path):
  debug("reading text file: " + file_path)
  with open(file_path, 'r', encoding='utf-8') as file:
    try:
      return file.read()
    except IOError:
      return None

def read_json(file_path):
  debug("reading json file:" + file_path)
  with open(file_path, 'r', encoding='utf-8') as file:
    try:
      return json.load(file)
    except IOError:
      return None

def parse_lcov(lcov_file):
  return walkFile(lcov_file)

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

def clear_coverage(view):
  view.erase_regions(REGION_KEY_COVERED)
  view.erase_regions(REGION_KEY_UNCOVERED)


class ShowNxCoverageCommand(sublime_plugin.TextCommand):
  def message(self, message):
    if self.view.window():
      sublime.status_message(message)

  def readLcovReport(self, coverage_dir, file):
    report = parse_lcov(read_file(os.path.join(coverage_dir, file)))

    if report:
      return [LCOV, report]

    debug("Can't read coverage report from file: " + str(file))

    return None


  def readCoverageReport(self, coverage_dir, file):
    report = read_json(os.path.join(coverage_dir, file))

    if report:
      return [COVERAGE, report]

    debug("Can't read coverage report from file: " + str(file))

    return None


  def findReports(self, project_root):
    # get name of currently opened file
    coverage_dir = os.path.join(project_root, getCoverageDir())

    coverage_file = find_file_in_dir(coverage_dir, 'coverage-final.json')
    lcov_info = find_file_in_dir(coverage_dir, 'lcov.info')

    debug("project_root", project_root)
    debug("coverage_dir", coverage_dir)
    debug("coverage_file", coverage_file)
    debug("lcov_info", lcov_info)

    if coverage_file:
      return self.readCoverageReport(coverage_dir, coverage_file)

    if lcov_info:
      return self.readLcovReport(coverage_dir, lcov_info)

    debug("Can't find any coverage files in project root: " + str(project_root))

    return None

  """
    Highlight uncovered lines in the current file
    based on a previous coverage run.
  """
  def run(self, edit):
    clear_coverage(self.view)

    # get name of currently opened file
    filename = self.view.file_name()
    if not filename:
      self.message("Could not show coverage, no filename associated with this view.")
      return None

    project_root = find_project_root(filename)

    if not project_root:
      self.message("Could not find coverage directory.")
      return None

    relative_filename = filename.replace(project_root + "/", "")

    reports = self.findReports(project_root)

    if reports is None:
      self.message("No Reports available")
      return

    [reportType, reportData] = reports

    debug("Found: ", reportType)

    if reportType is COVERAGE:
      return self.parseCoverageReport(relative_filename, reportData)

    if reportType is LCOV:
      return self.parseLcovReport(relative_filename, reportData)

  def parseLcovReport(self, relative_filename, reports):
    outlines = {}
    view = self.view

    debug("Found reports for the following number of files: " + str(len(reports)))

    if not reports:
      view.set_status(REGION_KEY_COVERED, "UNCOVERED!")
      self.message("Can't find the coverage json file in project root: " + project_root)
      return

    for file_report in reports:
      filename = file_report.file.replace("./", "")
      if not filename.endswith(relative_filename):
        continue

      debug("Found test reports for file " + str(relative_filename))

      lines = file_report.lines

      if not lines:
        self.message("No lines found in coverage")
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
      view.add_regions(REGION_KEY_COVERED, goodOutlines, REGION_LINE_SCOPE_COVERED, "dot", REGION_LINE_FLAGS_COVERED)
    if badOutlines:
      view.add_regions(REGION_KEY_UNCOVERED, badOutlines, REGION_LINE_SCOPE_UNCOVERED, "dot", REGION_LINE_FLAGS_UNCOVERED)

  def createRegion(self, row1, col1, row2, col2):
    point1 = self.view.text_point(int(row1) - 1, col1)
    point2 = self.view.text_point(int(row2) - 1, col2)
    return sublime.Region(point1, point2)

  def startEndRegion(self, item):
    start = item['start']
    end = item['end']
    return self.createRegion(start['line'], start['column'], end['line'], end['column'])


  def parseCoverageReport(self, relative_filename, reports):
    outlines = {}
    view = self.view

    debug("Found reports for the following number of files: " + str(len(reports)))

    report = None

    for report_filename in reports:
      filename = report_filename.replace("./", "")
      if not filename.endswith(relative_filename):
        continue
      report = reports[report_filename]
      break

    if report is None:
      self.message("No report found for " + relative_filename)
      return None

    # the following might need to be done for branches as well

    statementMap = report['statementMap']
    branchMap = report['branchMap']

    # statements
    good_statements = []
    bad_statements = []
    statements = report['s']

    for statement_index in statements:
      statement = statementMap[statement_index]
      region = self.startEndRegion(statement)

      if statements[statement_index]:
        good_statements.append(region)
      else:
        bad_statements.append(region)

    good_branches = []
    bad_branches = []
    branches = report['b']

    for branch_index in branches:
      branch = branchMap[branch_index]
      locations = branch['locations']

      debug('------')

      for index, count in enumerate(branches[branch_index]):
        debug(locations[index])
        region = self.startEndRegion(locations[index])
        if count:
          good_branches.append(region)
        else:
          bad_branches.append(region)

      # debug(statement_index, statement_count)

    # debug(relative_filename)
    # debug(report)

    if good_statements:
      view.add_regions(REGION_KEY_COVERED, good_statements, REGION_LINE_SCOPE_COVERED, 'dot', REGION_LINE_FLAGS_COVERED)
    if bad_statements:
      view.add_regions(REGION_KEY_UNCOVERED, bad_statements, REGION_TEXT_SCOPE_UNCOVERED, '', REGION_TEXT_FLAGS_UNCOVERED)

    if good_branches:
      view.add_regions(REGION_KEY_BRANCH_COVERED, good_branches, REGION_SCOPE_BRANCH_COVERED, '', REGION_FLAGS_BRANCH_COVERED)
    if bad_branches:
      view.add_regions(REGION_KEY_BRANCH_UNCOVERED, bad_branches, REGION_SCOPE_BRANCH_UNCOVERED, '', REGION_FLAGS_BRANCH_UNCOVERED)

class ClearNxCoverageCommand(sublime_plugin.TextCommand):

  """
    Remove highlights created by plugin.
  """

  def run(self, edit):
    clear_coverage(self.view)
