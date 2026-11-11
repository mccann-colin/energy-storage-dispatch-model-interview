# energy-storage-dispatch-model-interview

A repo to build a small asset dispatch model for an interview.

Uses daily optimisation with a look forward window to ensure battery state considers next horizon. 

Current state covers:

* Single, hourly market optimisation
* upper and lower asset power bounds
* state of charge constraints

**Repo Structure**

market.py:

* Handles loading of prices

optimisation.py

* Handles the setup of the optimisation problem, such as adding constraints, bounds, and running the optimisation itself.

runner.py

* used to actually run the model from inputs and output results as a csv.
* Currently also used for some behaviours that should be moved from this file, such as logic to run a single days optimisation at once
* To update asset parameters, currently you need to manually change values in src\energy_storage_dispatch_model_interview\runner.py\`setup_optimisation_problem`

**Installation**

uv is required for this repo.

After cloning the repo, run:

```
uv sync
```

from the repo root. 

To run the model, run

```
uv run python -m energy_storage_dispatch_model_interview.runner
```

from the repo root. 

Output will be in energy-storage-dispatch-model-interview\output\dispatch_results.csv
