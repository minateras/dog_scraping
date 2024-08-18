# README

Dog Scraping is a repository containing a number of scripts for scraping dog-related data. The data mined by these scrips is used by this website: [Svenska Arbetande Rhodesian Ridgebacks](https://www.ridgerunner.se/workingridge_app "Svenska Arbetande Rhodesian Ridgebacks").

To run the scrips, you must set up a database (preferable MySQL). Run the file called _create.sql_ to set up the required tables in the database. Create a file named _.env_ in the root of this repository, where you provide the configuration details for the database.

## polar_plot

### \_\_init\_\_.py

This script creates polar plots for two types of Swedish mentality tests: _Behavior and Personality Assessment (BPH)_, as well as _Mentality Description (MH)_. Update the values in _ideal_bph.json_ and _ideal_mh.json_ inside the _input_ folder to match your ideal result. Inside this same folder, create a JSON file and paste your dog's results inside of an array. Then run the script and choose the type of plot you want to generate (i.e., _BPH_ or _MH_). Afterwards, you enter the name of the file you just created. The plot will then be generated and the result will be saved to the _output_ folder.

## skk

### skk_avelsdata

#### search_kennel_names.py

This script retrieves all rhodesian ridgeback kennel names that have at least one litter registered.

### skk_hunddata

#### search_competitions.py

This script retrieves rhodesian ridgeback's competition results in dog sports since 1993. At the moment obedience, working dog trials, and blood tracking are supported. Besides single competition results, it also retrieves titles and thus complements _search_titles.py_.

#### search_titles.py

This script retrieves rhodesian ridgeback's dog sport titles since 2006. All titles from sports recognized by _The Swedish Kennel Club_ are supported.

## srrs

### mentality_index.py

This script retrieves mentality indexes from _The Swedish Rhodesian Ridgeback Club (SRRS)_. Specify which dogs' mentality indexes to retrieve by passing their kennel names as arguments to the script. For example:
`py PATH_TO_REPOSITORY/srrs/mentality_index.py "Kadamo I Am Bagheera" "Lejonessa Air Of Happiness"`

__Note:__ This script requires that the database has a table named dog, and that the dogs for which you are retrieving mentality indexes for have already been saved to the database.
