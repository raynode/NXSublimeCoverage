NX Coverage
=================

Combined code from [JS Coverage
 Plugin](https://packagecontrol.io/packages/JS%20Coverage) with [Atom lcov-info](https://atom.io/packages/lcov-info) to build this plugin.

Highlights uncovered lines in the current file based on a previous coverage run.

Display highlights: Super + Shift + C

Remove highlights: Super + Shift + C + X

Plugin tries to find the latest coverage report in a closest "coverage" directory.

Configuration
=================
We can also configure your where the plugin is going to look for coverage the information.
Just go to Preferences > Package Settings > NX Coverage > Settings - User.
The configuration should look something like:

```json
{
    "coverageDir": "my_custom_coverage_dir"
}
```


Jest configuration
===================

Jest has a coverage tool integrated, it is just hidden behind a flag
```bash
$ jest --coverage
```

Jest configuration should output to the coverage directory, the following configuration has typescript support as well

```javascript
module.exports = {
  testEnvironment: 'node',
  transform: {
    '.(ts|tsx)': '<rootDir>/node_modules/ts-jest/preprocessor.js'
  },
  clearMocks: true,
  bail: true,
  mapCoverage: true,
  modulePaths: [
    "src",
    "node_modules"
  ],
  moduleDirectories: [
    "node_modules",
    "<rootDir>/src"
  ],
  moduleFileExtensions: [
    'ts',
    'tsx',
    'js',
    'jsx'
  ],
  testRegex: '/src/.*\.spec\.[tj]sx?$',
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'lib/**/*.{ts,tsx,js,jsx}'
  ],
}

```

Screenshots
===========

![screen shot 2013-10-02 at 8 44 25 am](https://f.cloud.github.com/assets/72428/1254702/b1d6f232-2b79-11e3-8882-6ad66a287bdf.png)

