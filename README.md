# Description

This repository contains a collection of scripts and jupyter notebooks to perform semi-automatic analysis of Vehicle Routing Problem Solver algorithm behavior.

# How to use

## Preconditions

* install python
* install jupyter notebook
* install dependencies from `requirements.txt`
* install/build [VRP solver](https://github.com/reinterpretcat/vrp)

## Prepare data

* create a new folder for experiment, e.g. `experiments/my_experiment`, with two subfolders:
    * `configs`: should contain algorithm configuration files
    * `problems`: should contain VRP definitions in [pragmatic](https://reinterpretcat.github.io/vrp/concepts/pragmatic/index.html) format
* run `runner.py` script and pass the following parameters:
    * path to vrp-cli executable
    * path to experiment folder
    * sample size: how many times each problem should be run with each config

Please note, that the solver uses routing matrix approximation via great-circle distances and constant speed. Check solver documentation to see how to configure that behaviour.

## Analyze results

* run `jupyter notebook`
* select one of available notebooks
* change path to test data
* run kernel
