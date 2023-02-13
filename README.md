# Python Steam Store Recommendations Web Scraper

A simple Python web scraper that will construct and export a graph of Steam store recommendations.

The scraper randomly loads a set number of Steam store pages set by the user at runtime, also known as source nodes. The graph is created using the [NetworkX](https://networkx.org/documentation/stable/index.html) library for Python, and exported in [GEFX](https://gexf.net/) format.

Created for a semester research project in a network science course.

## Setup

To use, you should have an up-to-date version of Python 3 installed. (Python 3.10.5 is being used at time of most recent development.) A virtual environment is recommended, but not required. Please see the Python docs [here](https://docs.python.org/3/library/venv.html) for more information.

To install required libraries, simply navigate to the repository directory from a terminal and run:
```
pip install -r requirements.txt
```

The program may then be started with:
```
python ./scraper.py
```
## Usage
At startup you will receive this message and be prompted with, 
```
Welcome to Steam Recommendation Scraper v0.1.1
Add to existing graph? (y/n) 
```
Using an existing graph lets you create an expanded version of a graph created during a previous run. When prompted, enter your graph's filename, omitting the path, but including the file extension. Graphs follow the format:
```
steam{totalSourceNodes}_{recsPerSource}_{version}.fileExtension
```
Source nodes will automatically be incremented from previous value if using an existing graph.
```
Loading old graph...
Loaded graph with 3488 nodes
Use previous settings? (y/n) 
```
Once a graph is loaded, you will be asked if you would like to use previous setting. Currently this means using the same number of recommendations per source node.
```
How many new source nodes? 
```
This question will always be asked, and just means how many times a random Steam game should be requested. After this, execution will begin.
## Execution
Now what is left to do is wait. This can be timely based on internet speed and the numbers of requests being made. With base configuration, the user will be notified of overall progress every 10 source nodes, and every 100 the graph file will be saved. If the user sends `SIGINT` during during parsing, the program will catch the exception and allow the graph to be exported one final time.

As mentioned, graphs are exported in [GEFX](https://gexf.net/) format by default, though this can easily be changed to any of NetworkX's supported formats.

## Using Your Graphs
Generated graphs are output into the `.graphs` directory, and can be used from there or copied elsewhere. Graph files **MUST** be in the `.graphs` directory if you intend to import them as an existing graph.

There are multiple software options for analysis and visualization of graph files, though the software I am using is open-source option [Gephi](https://gephi.org/).

## Limitations/Caveats
There are a few things to note regarding the current state of this software.

First, the URL used to find source nodes, [http://store.steampowered.com/explore/random/](http://store.steampowered.com/explore/random/), does not provide a random game from all games on Steam. Obscene games that require login are omitted from this URL, as well as all recommendations. There may be other unknown constraints on how this URL operates.

The URL does seems to only recommends games themselves, not DLC, though the same cannot be said for the recommendations, which include DLC. There may be an option to filter these out and prevent them from being added to the graph in future versions.
