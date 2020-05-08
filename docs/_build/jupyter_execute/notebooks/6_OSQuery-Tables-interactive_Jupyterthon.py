# Untangling the Osquery❓ tables web🕸 using Jupyter Notebooks📓
## JOINing Osquery tables using graphing techniques
-----------------------------------------
* **Author:** Sevickson Kwidama 
    * [Twitter](https://twitter.com/SKwid345)
    * [LinkedIn](https://nl.linkedin.com/in/sevickson)
    * [GitHub Repo](https://github.com/sevickson/osquery_tables_graph)
* **Version:** 1.0_Jupyterthon

### Install and Upgrade `pip` packages if needed
I start by getting the needed dependencies if any, only need to be run once

!pip install --upgrade --user pip
!pip install --user pyvis

### Import modules in this Jupyter Notebook
Requirements:
- Python >= 3.6 (There are some changes in the open() function that will give error in older versions)  

Below I import the needed modules, each time I need a new module I add it to the list below.

# Standard modules to use and manipulate dataframes
import numpy as np
import pandas as pd
# Used to download from Osquery repository and unzip needed files
import requests, zipfile, io
# Used to be able to access locations on disk
import pathlib
# Regular expression based extracts and filtering
import re
# Module to copy same value in a dataframe, didn't find an easier way
from itertools import cycle
# Modules to create the graphs and computations on the graphs
import networkx as nx
#import matplotlib.pyplot as plt
from pyvis.network import Network
# For the dropdown box interactions
from ipywidgets import interact

# INGEST AND MANIPULATE DATA
-----------------------------------------

### Download the latest zip and extract only the tables folder
Below I wrote some code based on a [tweet](https://twitter.com/curi0usJack/status/1255702362225811457?s=20) I saw from @curi0usJack.  
In the code below I first download the complete zipped release, I iterate over the zipped file to extract only files from the `specs/` folder, this is the location for all the Osquery table definitions.

# Get the latest release from the API data of GitHub 
url_github_latest = "https://api.github.com/repos/osquery/osquery/releases/latest"
response = requests.get(url_github_latest).json() 
dir_tables = 'osquery-tables'
p = pathlib.Path(dir_tables)
  
# Response was in json and put in dict so can be called easily
url_github_dl = response['zipball_url']

# Get zipped content and unzip
github_content = requests.get(url_github_dl, stream=True)
zippedcontent = zipfile.ZipFile(io.BytesIO(github_content.content))
listOfFileNames = zippedcontent.namelist()

# Iterate over the file names
for fileName in listOfFileNames:
    # Check if file is located in the 'specs/' folder
    if 'specs/' in fileName:
       # Extract file from zip
        zippedcontent.extract(fileName, dir_tables)

### Extract table names and columns from the Osquery table files
Below is the function to check all the files with extension `.table` to extract the Table and Column names.  
I filter out `example.table` and the hidden Column names as they are used for internal Osquery accounting as far as I could see.  
Here I use a bit of a hack `list(zip(cycle))` to get both lists the same length.

def osquery_table_extract(dir_tables):
    table_columns = []
    for path in p.rglob("*.table"):
        if path.is_file() and 'example' not in path.stem:
            cf = open(path, "r", encoding="utf-8").read()
            tline = re.findall(r'table_name\(\"(\w+)\".*\)',cf)
            #below line is used to find all columns that do not have attribute hidden=True
            clines = re.findall(r'Column\(\"(\w+?)\".+?(\n)?.+? (?!hidden=True)\S+\),$',cf,re.M)
            #regex returns tuples because of the multiline matching so with list comprehesion turning it back in a list
            clines = [i[0] for i in clines]
            tcList =  list(zip(cycle(tline),clines))
        table_columns.append(tcList)
    return(table_columns)

Below I call the function above to iterate over the files I exported from the zip. All the data is than put in a DataFrame (DF).  
I also have some checks to make sure the data is correct.

extract = osquery_table_extract(dir_tables)
extract_df = pd.DataFrame([t for lst in extract for t in lst], columns = ['Table','Column'])

Check count of table names to be sure all have been processed.  
Check difference against Osquery website, I filtered out example.table as it is just an example table.

print('Tables', extract_df.Table.nunique())
extract_df

### Add OS into DataFrame based on cMakelists file
The `cMakelists.txt` contains all the Table/OS combinations, so I needed to do some regexing to parse out the Table/OS combination.

def osquery_table_os(tname):
    # For tables that are not present in cMakelists.txt
    tname_cmake = 0
    for path in p.rglob("cMakelists.txt"):
        with open(path, 'r') as read_obj:
            for line in read_obj:
                if tname in line:
                    if '/' in line:
                        #used to delete part of string that can give double matches bases on tables names that have same start or end.
                        tname_cmake = re.search( r'^.*/(.*)$', line, re.M|re.I).group(1)
                    else:
                        tname_cmake = line.strip()
    return(tname_cmake)

The function above is called from here and I iterate over each Table name and based on the result I append the OS and if receive `0` it means Table is not present in the file but if it is present but no OS combination it means it is for all OS platforms.

tname_list = []
for tname in extract_df['Table']:
    table_os = osquery_table_os(tname)
    if ':' in str(table_os):
        t_os = re.search(r'^.+?:(.+?)"$', table_os, re.M|re.I).group(1)
        tname_list.append(t_os)
    elif '0' in str(table_os):
        # Not in cMakeLists.txt file but on the website so later manually add the OS
        t_os = 'no_os'
        tname_list.append(t_os)
    else:
        t_os = 'linux,macos,freebsd,windows'
        tname_list.append(t_os)
    
extract_df_os = extract_df
extract_df_os['OS'] = tname_list 
extract_df_os

Workaround for issue that some tables did not get the correct OS assignment, fix this later in the re.search in the osquery_table_os function.  
Issue seems to be if another table contains a part of the name of one of the prior tables it takes the value from the last table, so matching is not specific enough.  

Tables that have `no_os` need manual assignment too.

extract_df_os.loc[extract_df_os.Table == 'crashes', 'OS'] = 'macos'
extract_df_os.loc[extract_df_os.Table == 'azure_instance_metadata', 'OS'] = 'linux,macos,freebsd,windows'
extract_df_os.loc[extract_df_os.Table == 'azure_instance_tags', 'OS'] = 'linux,macos,freebsd,windows'
extract_df_os.loc[extract_df_os.Table == 'wifi_survey', 'OS'] = 'macos'
extract_df_os.loc[extract_df_os.Table == 'processes', 'OS'] = 'linux,macos,freebsd,windows'
extract_df_os.loc[extract_df_os.Table == 'groups', 'OS'] = 'linux,macos,freebsd,windows'
extract_df_os.loc[extract_df_os.Table == 'hash', 'OS'] = 'linux,macos,freebsd,windows'
extract_df_os.loc[extract_df_os.Table == 'time', 'OS'] = 'linux,macos,freebsd,windows'
extract_df_os.loc[extract_df_os.Table == 'certificates', 'OS'] = 'macos,windows'

Check if all `no_os` have been assigned, if there is output below check the website to manually add OS based on osquery schema.

extract_df_os.loc[extract_df_os.OS == 'no_os']

Below is just some code that I do a quick check if a table has the correct association.

extract_df_os.loc[extract_df_os['Table'] == 'logon_sessions']

### Create separate DataFrames based on OS
Here I could have probably used a for loop with a list to get the same result.  
I check in the DataFrame `extract_df_os` for the OS name in the `OS` column and if present put that row in a new DataFrame.

#Windows
windows_df = extract_df_os.loc[pd.np.where(extract_df_os.OS.str.contains("windows"))]

#Linux
linux_df = extract_df_os.loc[pd.np.where(extract_df_os.OS.str.contains("linux"))]

#macOS
macos_df = extract_df_os.loc[pd.np.where(extract_df_os.OS.str.contains("macos"))]

#FreeBSD
freebsd_df = extract_df_os.loc[pd.np.where(extract_df_os.OS.str.contains("freebsd"))]

# GRAPHS 🕸
----------------------------

### Function to create the graph and all its properties
`create_OS_graph` function ingests a DF and creates the graph from this DF.  
I iterate twice over the graph to first remove Columns with only one connection as this implies it is only connected to one Table and after that iterate to remove orphaned Tables.  
I also assing different colors and sized dependent on the properties of each node.  
- Tables with only one connection are **ORANGE**
- Tables with more than one connection are **GREEN**
- Columns are **RED**

def create_OS_graph(df_OS):
    # Create nx node graph from DF
    G = nx.from_pandas_edgelist(df=df_OS, source='Table', target='Column')
    # Initiliaze lists to use for appending
    colors = []
    sizes = []
    selected_nodes_list = []
    selected_nodes_list_H = []
    
    # Calculate all degrees of separation for the nodes, so how many connection does each node have
    degree = nx.degree(G)

    # Iterate through nodes, if node is Table than check if node has connections, if so add to list, if no connections discard.
    # If node not a Table than it would be a Column and if it has more than 1 connection than add to list
    for node in G:
        if node in df_OS.Table.values:
            if (degree(node) > 0):
                selected_nodes_list.append(node)
        else: 
            # Column has always at least connection to it's own table that is why need to check for more than 1 connection
            if (degree(node) > 1):
                selected_nodes_list.append(node)

    # Create subgraph and degress based on filtering above
    H = G.subgraph(selected_nodes_list)
    degree_H = nx.degree(H)

    # Run the same logic as above to filter out Tables and Columns that were orphaned
    # Also add color and size to Table or Column dependent on how many connections
    for node in H:
        if node in df_OS.Table.values:
            if (degree_H(node) == 1):
                selected_nodes_list_H.append(node)
                colors.append("orange")
                sizes.append(300)
            elif (degree_H(node) > 1):
                selected_nodes_list_H.append(node)
                colors.append("green")
                sizes.append(H.degree(node) * 700)
        else: 
            if (degree_H(node) > 1):
                selected_nodes_list_H.append(node)
                colors.append("red")
                sizes.append(H.degree(node) * 1000)

    I = H.subgraph(selected_nodes_list_H)
    return(I, colors, sizes, selected_nodes_list_H)

### Column Filtering
Check the most common `Columns` to filter out common names that will not be able to JOIN.  
Used below to start creating the ignore_list, finished it visually by walking the graph.  
Each OS has a different `ignore_list` but the basis is from the information below.

column_count = extract_df['Column'].value_counts()
column_for_joins = column_count[column_count > 1]
column_for_joins.head(10)

Create a folder location to place the created graphs.

path_graphs = pathlib.Path.cwd() / 'graphs'

try:
    path_graphs.mkdir()
except:
    print ("Creation of the directory %s failed, location probably already exists" % path_graphs)
else:
    print ("Successfully created the directory %s " % path_graphs)

## All OS Graph
By using `pyvis.network` module I could create beautiful interactive graphs.  
The graph is created from the graph I created in the `create_OS_graph` function the colors and sizes are also taken from that function.  
`barnes_hut` is the type of visualization used.

# Get the needed data from the function
OS_graph, colors, sizes, nodelist = create_OS_graph(extract_df_os)

gr=Network(height=800, width=1200, notebook=True, bgcolor="#222222", font_color="white")
# First add the nodes with its properties to the graph
gr.add_nodes(nodelist, value=sizes, title=nodelist, color=colors)
gr.barnes_hut()
# Now connect the nodes based on the graph returned from the function
gr.from_nx(OS_graph)
gr.show("graphs/osquery_tables_OS_ALL_graph.html")

## Windows Graph
Filtering used is OS dependent. I noticed that filtering needs some more fine-tuning this will be in the next release of this Notebook.

ignore_list_w = ['name','path','type','version','size','version','description','status','state','label','class','source','device','mode','value','result','hardware_model','manufacturer','query','model','device_id','action','script_text','time','enabled',
               'date','caption','publisher','active','autoupdate','flags','comment','data','registry','author','directory','license','summary','permissions'] 
#maybe filter out key not the same meaning in all tables
#path can be used for some good joins but too noisy for now, example http://www.osdfcon.org/presentations/2016/Facebook-osquery.pdf

Below we create the Windows-only graph, we first filter down the OS DataFrame we created earlier with the `ignore_list_w`.

After that, we run the same code used to create the 'All OS Graph', we do the same for each OS.

windows_df_filtered = windows_df[~windows_df['Column'].isin(ignore_list_w)]
OS_graph, colors, sizes, nodelist = create_OS_graph(windows_df_filtered)

print('Nodes:', OS_graph.number_of_nodes(), 'Edges:', OS_graph.number_of_edges())

gr=Network(height=800, width=1200, notebook=True, bgcolor="#222222", font_color="white")
gr.add_nodes(nodelist, value=sizes, title=nodelist, color=colors)
gr.barnes_hut()
gr.from_nx(OS_graph)
gr.show("graphs/osquery_tables_OS_win_graph.html")

### Determine shortest path from table A to table B
Another part of this Notebook is to create a function to easily see connections between 2 different tables.  
I actually use the same code that is in `create_OS_graph` but a trimmed down version with an extra function, `shortest_path`, to retun the shortest path between Table A and B based on Dijkstra's algorithm.

def shortest_path(df_OS,s,t):
    P = nx.from_pandas_edgelist(df=df_OS, source='Table', target='Column')
    path_list = []
    colors_sp = []
    sizes_sp = []
    
    # If there is a path between Table A and B, return the list with the nodes.
    if nx.has_path(P, s, t):
        path_list = nx.shortest_path(P, source=s, target=t) 
    else:
        print('No path available.')
    
    # Create subgraph based on the shortest path.
    Q = P.subgraph(path_list)
    degree_Q = nx.degree(Q)
    
    # Below is used to add colors and sizes
    for node in path_list:
        if node in df_OS.Table.values:
            if (degree_Q(node) == 1):
                colors_sp.append("orange")
                sizes_sp.append(300)
            elif (degree_Q(node) > 1):
                colors_sp.append("green")
                sizes_sp.append(Q.degree(node) * 700)
        else: 
                colors_sp.append("red")
                sizes_sp.append(Q.degree(node) * 1000)

    return (Q, path_list, colors_sp, sizes_sp)

`@interact` is an easy way to create user interface controls for exploring data interactively.  
The definition of `corr_graph` automatically creates the controls. The dropdown box is based on unique values in the OS DataFrame.  

windows_df_filtered_tb = windows_df[~windows_df['Column'].isin(ignore_list_w)].sort_values('Table')

@interact
def corr_graph(Source=list(windows_df_filtered_tb.Table.unique()), Destination=list(windows_df_filtered_tb.Table.unique())):
    sp_graph, sp_list, sp_colors, sp_sizes = shortest_path(windows_df_filtered_tb,Source,Destination)  
    
    # Check if the sp_list returned is not NULL which means there is no path and if sp_list == 1 this means that the Table name in Source and Destination is the same
    if sp_list is not None and len(sp_list) > 1:
        sp_gr=Network(notebook=True, bgcolor="#222222", font_color="white")
        sp_gr.add_nodes(sp_list, value=sp_sizes, title=sp_list, color=sp_colors)
        sp_gr.barnes_hut()
        sp_gr.from_nx(sp_graph)
        return(sp_gr.show("graphs/shortest_path_graph.html"))

-----------------------------------------

#### Sources:
https://towardsdatascience.com/getting-started-with-graph-analysis-in-python-with-pandas-and-networkx-5e2d2f82f18e  
https://stackoverflow.com/questions/55342586/assign-color-to-networkx-node-based-on-column-name  
https://pyvis.readthedocs.io/en/latest/tutorial.html  
https://github.com/osquery/osquery  