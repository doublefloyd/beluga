# Beluga Dataset Generation

This repository contains scripts that generate two types of hypersonic vehicle trajectory datasets using Beluga.

The first type of dataset generates hypersonic trajectories that exibit vertical maneuvers. This type of dataset is called a "Planar Hypersonics Skip" dataset.

The second type of datasets generates hypersonic trajectories that exhibit vertical and horizontal maneuvers. This type of dataset is called a "Planar to 3 DOF" dataset.

## Generating a Planar Hypersonics Skip Dataset
1. Open `planarHypersonicsSkip.py` and navigate to the USER INPUTS section.
2. Change user inputs as necessary.
3. Run `planarHypersonicsSkip.py`: ```python planarHypersonicsSkip.py```. The outputs are a log file and a dataset file, which will be stored in the location specified by the variable `OUTPUT_DIR` in the USER INPUTS section of `planarHypersonicsSkip.py`. The log file will have a `.log` extension, and the dataset will have a `.beluga` extension. The dataset can be visualized from the `.beluga` file. It can also be converted to `.csv` files.
4. Open `plotresults_planarHypersonicsSkip.py` and navigate to the USER INPUTS section.
5. Change user inputs as necessary, making sure that the exact filepath to the `.beluga` dataset file that was just generated is provided to the variable `BELUGA_DATA_FILE`.
6. Run `plotresults_planarHypersonicsSkip.py`: ```python plotresults_planarHypersonicsSkip.py```. The outputs will be stored in the location specified by the variable `PLOT_DIR` in the USER INPUTS section of `plotresults_planarHypersonicsSkip`.
7. Open `writeresults_planarHypersonicsSkip.py` and navigate to the USER INPUTS section.
8. Change user inputs as necessary, making sure that the exact filepath to the `.beluga` dataset file that was just generated is provided to the variable `BELUGA_DATA_FILE`.
9. Run `writeresults_planarHypersonicsSkip.py`: ```python writeresults_planarHypersonicsSkip.py```. A `.csv` file will be produced for each trajectory in the dataset. The outputs will be stored in the location specified by the variable `CSV_DIR` in the USER INPUTS section of `writeresults_planarHypersonicsSkip.py`.