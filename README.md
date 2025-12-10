# Replication Project Template

This is a GitHub template to use for replications projects in PSYCH 201a at UCSD. Create a new repo using this as a template in order to use it.

## Analysis
contains all the data analysis code in python.
### preprocessing.py 
clean raw data files to only contain columns that are of analysis interest
### mat_files.py
calculate the ten closest pairs using the data from the original paper
### outliers.py
check if there are outliers according to the 3SD rule
### plot_space.py
plot each participant's arrangement
### plot_word_isc.py
plot ISC for each word
### preprocessing_multiarrangement.py
preprocess the cleaned data files to generate matrix for the final data analysis
### data_analysis_multiarrangement.py
main analysis for calculating ISC for each word

## BehavioralSemanticDistanceMatrix

## cleaned
cleaned data files for eligible participants

## data
raw data

## explo_data
cleaned data files for eligible participants for the exploratory analysis

## figures
arrangement for each participant

## preprocessed
files for the final data analysis for calculating ISC

## processed_explo
files for the final data analysis for calculating ISC for the exploratory analysis

## results
results for t-test and plotting 

## results_explo
results for t-test and plotting for exploratory analysis