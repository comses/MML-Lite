# MML-Lite
The "lite" version of the MedLanD Modeling Laboratory
Please use the following DOI to cite this code: [![DOI](https://zenodo.org/badge/119421478.svg)](https://zenodo.org/badge/latestdoi/119421478)

Authors are Isaac I. Ullah, C. Michael Barton, Grant Snitker, Nicholas P. Gauthier, and Sean M. Bergin.

---

**Transition to GRASS 8 is underway and will BREAK backwards compatibility! So far, only r.agropast.adaptive and r.lanscape.evol are updated. To see how the new version of r.landscape.evol works, please see [this page](https://github.com/OSGeo/grass-addons/blob/grass8/src/raster/r.landscape.evol/r.landscape.evol.md). For now, the older GRASS 7 version of r.landscape.evol is provided here as r.landscape.evol.old. You will have to remove the ".old" part of the name after downloading it in order for it to work with any of the yet-to-be updated scripts.**

---

It contains three separate versions of an agro-pastoral village pseudo-ABM.

__r.agropast.nonadaptive__ Implements a static farming and grazing plan that does not change over time. Human population size and location of farming and grazing impacts are set at the start and do not vary from year to year.

__r.agropastoral.semiadaptive__ Implements a static quota for a farming and grazing plan with fixed goals (ratios of farming and grazing), but with adaptive localization of impacts (field and grazing sites move around from year to year). Human population size does not vary and land is not tenured.

__r.agropastoral.adaptive__ Implements a dynamic quota for a farming and grazing plan that with fixed goals (ratios of farming and grazing), but with adaptive localization of impacts (field and grazing sites move around from year to year). Human population sizes vary based on the success of the farming and grazing plan, and the plan is updated yearly to meet new population sizes. Farming can be optionally implemented with multiple types of land tenure.


### Dependencies

All three of these scripts depend upon r.landscape.evol, which can be installed via the official GRASS addons repository.

### Installation

Copy scripts to the GRASS_ADDONS_PATH (usually ~/.grass7/scripts). Ensure scripts are allowed to be executed.
