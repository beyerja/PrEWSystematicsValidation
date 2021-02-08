## PrEWSystematicsValidation

Code to validate the systematics parametrisation for the PrEW analysis.
The relevant validation data files are produced in [`PrEWSampleProduction`](https://github.com/beyerja/PrEWSampleProduction).

### Running the code


#### Loading the environment

A modern python version is needed together with range of modules.
If not installed locally, the provided macro can be used to load a python environment from CVMFS:
```bash
cd py && source load_env.sh
```

#### Running the plotting code

The code to create the validation plots is in the `py/ValidationTests` directory.

```bash
cd py/ValidationTests
python CutEffect.py # Find the absolute effect of the base cut on the distribution
python DeviationTest.py # Effects of changes in the cut
```

#### Creating overview pdfs

Some latex code is provided in `latex` to create single-pdf overview.