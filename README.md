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
We can also configure your where the plugin is going to look for coverage the information. Just go to Preferences > Package Settings > JS Coverage > Settings - User. The configuration should look something like:

{
    "coverageDir": "my_custom_coverage_dir"
}


Karma configuration
===================

You may need to install coverage plugin
```
npm install karma-coverage --save-dev
```

Karama should be configured to put coverage report to coverage directory, e.g:

```javascript
reporters: ['coverage'],
...

plugins : [
...
  'karma-coverage'
...
];

...

preprocessors: {
  // source files, that you wanna generate coverage for
  // do not include tests or libraries
  // (these files will be instrumented by Istanbul)
  'public/js/*.js': ['coverage']
},

...

//configure the reporter
coverageReporter: {
  type : 'json',
  dir : 'coverage/'
}
```

Screenshots
===========

![screen shot 2013-10-02 at 8 44 25 am](https://f.cloud.github.com/assets/72428/1254702/b1d6f232-2b79-11e3-8882-6ad66a287bdf.png)

