# UpRite Analysis

#### Motivation

The study of gait (a person's manner of walking) is greatly studied to be used for signs of deterioration (signs showing high risk of fall and early signs of dementia). The main medical systems utilized for gait analysis either are too expensive being at $2,000+ or don't integrate specific study analysis into the system. The new product will be made from ground up, starting with purchasing an off the shelf bluetooth capable, integrated accelerometer and gyroscope. Using the off-the-shelf product, a data analysis software will be built to record the gait parameters of a person wearing the sensor. This product is called the UpRite sensor.

#### Data Acquisition

In order to produce a robust algorithm, data is needed to be produced to affirm the data analysis algorithm's validity. Therefore, the data acquisition was tagged onto an ongoing research study being conducted at SFSU under Kate Hamel, PhD. She is studying the gait of the elderly through a pre-existing product, Zeno Walkway. This pre-exisiting product's data is used to confirm and calibrate the new UpRite sensor. 

The relevant recorded data from the Zeno Walkway is the toe-off and heel-strike data from each step and the velocity data. The relevant recorded data from the UpRite Sensor will be the sampling time, 3-dimensional acceleration, and 3-dimensional angular velocity. This data aquisition will be used to calculate the gait parameters.

#### Project Description
This is a robust codebase for extracting gait parameter data from [MetaSensor](https://mbientlab.com/product/clip-sensor-research-kit/). 

## Installation

To install UpRite Analysis from source, first clone repository and then run:  `python setup.py install`  
Actually, you just need to run:  `pipenv install`  

## Deployment

Open a virtual environment from root of repository:  `pipenv shell`  
Open up the scripts folder and run script: `pythonw python_structure.py`  
Note: read README.md in scripts folder to understand what is happening.  

## Results  

All results are within the docs folder.

## Production Summary

- A python script to parse raw data
- Analysis of UR data to provide gait parameters
- Comparison of data with a reference system
- Display results
- Adjust analysis algorithm if results are not satisfactory

## Authors

Main Contributor: Abhay Gupta || Host Company: Theranova

Project Members:
- CEO/Founder: Dan Burnett, MD
- Vice President of R\&D: Michael Jaasma, PhD
- Sr. Software Engineer: George Chen
- Software Intern: Abhay Gupta 


## License

This project is restricted to Theranova, LLC property.

## Acknowledgements

- George Chen for initial gait study program and assisting brainstorming.
- Michael Jaasma for initiating the project, completing initial research and analysis, and assisting brainstorming.
- Carl Ketchem and Kate Hamel in conducting and providing clinical data at SFSU.