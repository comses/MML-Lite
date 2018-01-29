# MML-Lite
The "lite" version of the MedLanD Modeling Laboratory

---

It contains three separate versions of an agro-pastoral village pseudo-ABM.

__r.agropast.nonadaptive__ Implements a static farming and grazing plan that does not change over time. Human population size and location of farming and grazing impacts are set at the start and do not vary from year to year.

__r.agropastoral.semiadaptive__ Implements a static quota for a farming and grazing plan with fixed goals (ratios of farming and grazing), but with adaptive localization of impacts (field and grazing sites move around from year to year). Human population size does not vary and land is not tenured.

__r.agropastoral.adaptive__ Implements a dynamic quota for a farming and grazing plan that with fixed goals (ratios of farming and grazing), but with adaptive localization of impacts (field and grazing sites move around from year to year). Human population sizes vary based on the success of the farming and grazing plan, and the plan is updated yearly to meet new population sizes. Farming can be optionally implemented with multiple types of land tenure.


### Dependencies

All three of these scripts depend upon r.landscape.evol, which can be installed via the official GRASS addons repository.

### Installation

Copy scripts to the GRASS_ADDONS_PATH (usually ~/.grass7/scripts). Ensure scripts are allowed to be executed.
