# Demo Production Planning

## Usage
- [Usage](#usage)
- [Demo Production Planning](#what-is-demo-production-planning)
- [Directory Structure](#directory-structure)
- [License](#license)
- [Installation](#installation)
- [Contributing](#contributing)
- [Code of conduct](#code-of-conduct)

## What is demo Production Planning

Taipy is a Python library for creating Business Applications. More information on our
[website](https://www.taipy.io).

[Demo Production Planning](https://github.com/Avaiga/demo-production-planning) is a full application showing how Taipy Core and Taipy Gui can work together to build a minimalist but powerful application.
This demo shows the fundamental mathematical optimization problem of “Production Planning”. The goal is to minimize costs while fulfilling product demand and satisfying capacity constraints.
Some of the constraints can be modified, resulting in different scenarios. For each scenario, different graphical representations are provided. 

### Demo Type
- **Level**: Advanced
- **Topic**: Taipy-GUI, Taipy-Core
- **Components/Controls**: 
  - Taipy GUI: selector, chart, toggle, slider, expandable, table
  - Taipy Core: datanode, pipeline, scenario, primary scenario, cycle

## How to run

This demo works with a Python version superior to 3.8. Install the dependencies of the *requirements.txt* and run the *main.py*.

## Introduction
Here, the problem consists of planning the production for two finished products: FPA (table) & FPB (stool). 

Each Finished Product is manufactured from two raw products: RPA (oak wood) and RPB (pine planks).

In this demo, the optimization algorithm (based on the PuLP open-source math solver) decides the optimal levels of production for FPA & FPB in order to minimize costs while satisfying a set of constraints (described below).
## Input Data visualization
After registering with a new account (name & password), the first page gets displayed. 
- The main chart plots the future demand for finished product A (FPA) and finished product B (FPB) over the next 11 months. The current month is month 0.

<p align="center">
  <img src="images/image9.png" alt="drawing" width="700"/>
</p>
  
- Just above, when clicking on “Expand here”, you can find a Taipy GUI “expandable” containing the initial production data at time 0 (current month): the stock & production levels, the incoming orders for the raw materials, and the demand (in a table).

## Optimizing and Playing with Scenarios
By clicking on the Scenario Manager icon (on the left panel) <img src="images/image17.png" alt="drawing" width="40"/>, you access the main page of the application. From this page, you can create a new scenario, change the scenario parameters (on the ‘Scenario Configuration’ side of the page), and re-submit the scenario i.e., re-optimize the scenario by taking into account the modified parameters).

<p align="center">
  <img src="images/image5.png" alt="drawing" width="700"/>
</p>

Let’s look at the different fields in more detail.

Initially, no scenario is available yet, and you can see that the Year/Month corresponds to the current month.

Below, the two indicators, “Cost of Back Orders’ and ‘Cost of Stocks’ are displayed. These correspond to the two costs that the ‘optimization’ Algorithm will optimize.

## Creating your first scenario

When clicking on the “NEW SCENARIO” button,
1. A new scenario gets created containing all the input data related to the scenario.
2. An Optimization algorithm is then launched which very quickly finds the optimal levels of production respecting the capacity constraints and optimizing the two costs.

The results are displayed either as time series or as pie charts.

You can select the different visuals by selecting the data to be displayed (costs, productions, etc.).


<p align="center">
  <img src="images/image13.png" alt="drawing" width="700"/>
  <img src="images/image10.png" alt="drawing" width="700"/>
</p>
  
## Modifying the Parameters
This panel allows you to modify some of the parameters; these are divided in three categories:

<p align="center">
  <img src="images/image12.png" alt="drawing" width="400"/>
</p>

1. When clicking on ‘Capacity Constraints’, you can modify the various capacity values for the different products (finished product and raw products). The capacity constraints relate to the product icon selected (by default, the table icon is selected).


<p align="center">
  <img src="images/image2.png" alt="drawing" width="200"/>
</p>

By selecting a different product icon, the corresponding capacity constraints will appear.

2. When clicking on “Objectives Weights’,  you can emphasize minimizing one specific cost (either cost of stock or cost of back ordering).
4. When clicking on ‘Initial Parameters’, other parameters can be modified.

## Playing with Scenarios
Once some of the parameters have been modified, two options are available to the user:

<p align="center">
  <img src="images/image6.png" alt="drawing" width="300"/>
</p> 
  
- Clicking on “New Scenario”  will create a second scenario that will optimize the costs based on the new set of parameters.
- Clicking on “Re-optimize” will re-optimize the current scenario, and the previous solution gets overwritten.

Should you create a second scenario, you can select one of the two scenarios to be ‘Primary’. By clicking on “Make Primary’. In such a case, a little flag will appear on the side of the scenario name.

<p align="center">
  <img src="images/image1.png" alt="drawing" width="400"/>
</p>
  
‘Primary’ is a Taipy Core concept that comes in handy when one of the many scenarios that users create needs to be identified as the ‘official’ scenario for the current cycle. In this demo, the cycle (another Taipy Core concept) is the month. 

See Taipy Core Concepts in the User Manual for more information:  https://docs.taipy.io/en/latest/manuals/core/concepts/cycle/

## Comparing scenarios
By clicking on the balance icon on the left panel, you will be able to compare 2 scenarios within the same month (same cycle). 

## Visualize the Performance over time

By clicking on the circle arrow icon on the left panel, you will be able to display the algorithm's performance over time. The program simply extracts the optimized costs from the ‘Primary’ scenario for each cycle (i.e., month) and displays them in a bar chart. Note that this demo already contains scenarios generated for the previous months.

<p align="center">
<img src="images/image18.png" alt="drawing" width="700"/>
</p>
  
## Databases
By clicking on <img src="images/image8.png" alt="drawing" width="40"/> icon, you can display the different tables (dataframes) for a given scenario. You can download as CSV file the result table by clicking on the ‘Download Table’ button.



## Directory Structure


- `src/`: Contains the demo source code.
  - `src/algos`: Contains the functions to be executed as tasks by Taipy.
  - `src/config`: Contains the configuration files.
  - `src/data`: Contains the application data files.
  - `src/login`: Contains the code for the login.
  - `src/images`: Contains the application image files.
  - `src/pages`: Contains the page definition files.
- `docs/`: contains the images for the documentation
- `CODE_OF_CONDUCT.md`: Code of conduct for members and contributors of _demo-production-planning_.
- `CONTRIBUTING.md`: Instructions to contribute to _demo-production-planning_.
- `INSTALLATION.md`: Instructions to install _demo-production-planning_.
- `LICENSE`: The Apache 2.0 License.
- `Pipfile`: File used by the Pipenv virtual environment to manage project dependencies.
- `README.md`: Current file.

## License
Copyright 2022 Avaiga Private Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at
[http://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

## Installation

Want to install _demo production planning_? Check out our [`INSTALLATION.md`](INSTALLATION.md) file.

## Contributing

Want to help build _demo production planning_? Check out our [`CONTRIBUTING.md`](CONTRIBUTING.md) file.

## Code of conduct

Want to be part of the _demo production planning_ community? Check out our [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) file.
