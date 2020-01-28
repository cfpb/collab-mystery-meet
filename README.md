# Mystery Meet

[![Build Status](https://travis-ci.org/cfpb/collab-mystery-meet.svg?branch=master)](https://travis-ci.org/cfpb/collab-mystery-meet)

*Mystery Meet* is a social app to meet people randomly at an organization for [Collab](https://github.com/cfpb/collab).


## Screenshot

![index page](screenshots/main.png "Index Page")

## Installation

To use this application you will need to first have [Collab](https://github.com/cfpb/collab) installed.

Then, once you clone this repo, you can install the application using setuptools:

`python setup.py install`

Or, if you are developing with this app, you can add it to your search path like:

```
cd collab
ln -s ../mystery-meet/mystery .
```

Once the application is installed, add it to core collab's `INSTALLED_APPS` in your `local_settings.py` file:

```
INSTALLED_APPS += ( 'mystery', )
```

## Contributing

Please read the [contributing guide](./CONTRIBUTING.md).
