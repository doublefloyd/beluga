# Beluga Dataset Generation

This repository contains scripts that generate two types of hypersonic vehicle trajectory datasets using Beluga.

The first type of dataset generates 250 hypersonic trajectories that exibit vertical maneuvers. This type of dataset is called a "Planar Hypersonics Skip" dataset.

The second type of datasets generates 1,681 hypersonic trajectories that exhibit vertical and horizontal maneuvers. This type of dataset is called a "Planar to 3 DOF" dataset.

## Generating a Planar Hypersonics Skip Dataset

### Key Steps:

```
$ python generate_dataset_planarHypersonicsSkip.py
$ python plot_results_planarHypersonicsSkip.py
$ python write_results_planarHypersonicsSkip.py
```

### Detailed Steps and Instructions to Change Inputs/Outputs:

1. Open `generate_dataset_planarHypersonicsSkip.py` and navigate to the USER INPUTS section.
2. Change user inputs as necessary.
3. Run `generate_dataset_planarHypersonicsSkip.py`: ```python generate_dataset_planarHypersonicsSkip.py```. The outputs are a log file and a dataset file, which will be stored in the location specified by the variable `OUTPUT_DIR` in the USER INPUTS section of `generate_dataset_planarHypersonicsSkip.py`. The log file will have a `.log` extension, and the dataset will have a `.beluga` extension. The dataset can be visualized from the `.beluga` file. It can also be converted to `.csv` files.
4. Open `plot_results_planarHypersonicsSkip.py` and navigate to the USER INPUTS section.
5. Change user inputs as necessary, making sure that the exact filepath to the `.beluga` dataset file that was just generated is provided to the variable `BELUGA_DATA_FILE`.
6. Run `plot_results_planarHypersonicsSkip.py`: ```python plot_results_planarHypersonicsSkip.py```. The outputs will be stored in the location specified by the variable `PLOT_DIR` in the USER INPUTS section of `plot_results_planarHypersonicsSkip`.
7. Open `write_results_planarHypersonicsSkip.py` and navigate to the USER INPUTS section.
8. Change user inputs as necessary, making sure that the exact filepath to the `.beluga` dataset file that was just generated is provided to the variable `BELUGA_DATA_FILE`.
9. Run `write_results_planarHypersonicsSkip.py`: ```python write_results_planarHypersonicsSkip.py```. A `.csv` file will be produced for each trajectory in the dataset. The outputs will be stored in the location specified by the variable `CSV_DIR` in the USER INPUTS section of `write_results_planarHypersonicsSkip.py`.

## Generating a Planar to 3 DOF Dataset

### Key Steps:

```
$ python generate_dataset_planarto3dof.py
$ python plot_results_planarto3dof.py
$ python write_results_planarto3dof.py
```

### Detailed Steps and Instructions to Change Inputs/Outputs:

1. Open `generate_dataset_planarto3dof.py` and navigate to the USER INPUTS section.
2. Change user inputs as necessary.
3. Run `generate_dataset_planarto3dof.py`: ```python generate_dataset_planarto3dof.py```. The outputs are multiple log files and dataset files, which correspond to different stages of computation. The final dataset file will be called `data_<DATA_NAME_SUFFIX>_stage_3_final_output.beluga`. All outputs will be stored in the location specified by the variable `OUTPUT_DIR` in the USER INPUTS section of `generate_dataset_planarto3dof.py`. The log files will have `.log` extensions, and the data files will have `.beluga` extensions. The dataset can be visualized from the `data_<DATA_NAME_SUFFIX>_stage_3_final_output.beluga` file. It can also be converted to `.csv` files.
4. Open `plot_results_planarto3dof.py` and navigate to the USER INPUTS section.
5. Change user inputs as necessary, making sure that the exact filepath to the `data_<DATA_NAME_SUFFIX>_stage_3_final_output.beluga` dataset file that was just generated is provided to the variable `BELUGA_DATA_FILE`.
6. Run `plot_results_planarto3dof.py`: ```python plot_results_planarto3dof.py```. The outputs will be stored in the location specified by the variable `PLOT_DIR` in the USER INPUTS section of `plot_results_planarto3dof`.
7. Open `write_results_planarto3dof.py` and navigate to the USER INPUTS section.
8. Change user inputs as necessary, making sure that the exact filepath to the `.beluga` dataset file that was just generated is provided to the variable `BELUGA_DATA_FILE`.
9. Run `write_results_planarto3dof.py`: ```python write_results_planarto3dof.py```. A `.csv` file will be produced for each trajectory in the dataset. The outputs will be stored in the location specified by the variable `CSV_DIR` in the USER INPUTS section of `write_results_planarto3dof.py`.