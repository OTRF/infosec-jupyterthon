![](images/FirstSlide.PNG)

# ATT&CK - APT29 Evals Datasets

![](images/APT29.PNG)

![](images/WhatIsSpark.PNG)

![](images/CoreClasses.PNG)

![](images/CoreClassesToday.PNG)

### 1. Importing Python Libraries

* **pyspark** modules and classes

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql.types import *
import pyspark.sql.functions as func
from pyspark.sql.functions import length, concat ,concat_ws

* **Complementary** libraries

import pandas as pd, numpy as np, networkx as nx
import matplotlib.pyplot as plt
import requests

from openhunt import ossem, descriptiveStatistics as ds, visualizations as vis

import warnings
warnings.filterwarnings('ignore')

### 2. Initializing SparkSession

spark = SparkSession.builder.getOrCreate()
spark.conf.set("spark.sql.caseSensitive", "true")

### 3. Importing and Reading Datasets: Host and Network

* **Host** Data - **Day 1**

!unzip datasets/apt29_evals_day1_manual.zip

host_day1 = spark.read.json('datasets/apt29_evals_day1_manual_2020-05-01225525.json')

print(type(host_day1))
host_day1.select('@timestamp','Channel','EventID').show(5, truncate = False)

* **Host** Data - **Day 2**

!unzip datasets/apt29_evals_day2_manual.zip

host_day2 = spark.read.json('datasets/apt29_evals_day2_manual_2020-05-02035409.json')

print(type(host_day2))
host_day2.select('@timestamp','Channel','EventID').show(5, truncate = False)

* **Network** data - **Day 1**

zeekUrl_day1 = 'https://raw.githubusercontent.com/OTRF/detection-hackathon-apt29/master/datasets/day1/zeek/combined_zeek.log'
zeekLogs_day1 = requests.get(zeekUrl_day1)
zeekDf_day1 = pd.read_json(zeekLogs_day1.text, lines = True)

print(type(zeekDf_day1))
zeekDf_day1.head()

Let's convert this **pandas** dataframe into a **spark** dataframe.

columnsToChangeType_day1= zeekDf_day1.select_dtypes(include=[object]).columns.to_list()
dictionary_day1 = {i : 'str' for i in columnsToChangeType_day1}
zeekDf_day1 = zeekDf_day1.astype(dictionary_day1)

zeekSpark_day1 = spark.createDataFrame(zeekDf_day1)

print(type(zeekSpark_day1))
zeekSpark_day1.select('id_orig_h','id_orig_p','id_resp_h','id_resp_p').show(5, truncate = False)

* **Network** data - **Day 2**

zeekUrl_day2 = 'https://raw.githubusercontent.com/OTRF/detection-hackathon-apt29/master/datasets/day2/zeek/combined_zeek.log'
zeekLogs_day2 = requests.get(zeekUrl_day2)
zeekDf_day2 = pd.read_json(zeekLogs_day2.text, lines = True)

print(type(zeekDf_day2))
zeekDf_day2.head()

Let's convert this **pandas** dataframe into a **spark** dataframe.

columnsToChangeType_day2= zeekDf_day2.select_dtypes(include=[object]).columns.to_list()
dictionary_day2 = {i : 'str' for i in columnsToChangeType_day2}
zeekDf_day2 = zeekDf_day2.astype(dictionary_day2)

zeekSpark_day2 = spark.createDataFrame(zeekDf_day2)

print(type(zeekSpark_day2))
zeekSpark_day2.select('id_orig_h','id_orig_p','id_resp_h','id_resp_p').show(5, truncate = False)

### 4. Creating a Temporary SQL View

host_day1.createTempView("apt29HostDay1")
host_day2.createTempView("apt29HostDay2")

zeekSpark_day1.createTempView("apt29NetworkDay1")
zeekSpark_day2.createTempView("apt29NetworkDay2")

### 5. Now we are finally ready to start exploring our data!!

![](images/AreWeReady.PNG)

### Let's first check something really basic:

![](images/dataType1.PNG)

![](images/dataType2.PNG)

### a) What sources of data do we have for hosts on day 1?

Let's select all the data for event field **Channel**:

channel_host_day1 = spark.sql(
    '''
SELECT Channel
FROM apt29HostDay1
                          ''')
channel_host_day1.show(5, truncate = False)

This is a **Categorical** variable, so a **stack counting** operation would be helpful:

channel_host_day1 = spark.sql(
    '''
SELECT Channel, count(*) as count
FROM apt29HostDay1

GROUP BY Channel
ORDER BY count DESC
                          ''')
channel_host_day1.show(5, truncate = False)

If you are more a **visual** person :D

vis.barh_chart(channel_host_day1,'count','Channel','Frequency of Channel')

### b) What Sysmon logs do we have for hosts on day 1?

Let's use the **WHERE** operator to **filter** our dataset:

sysmon_host_day1 = spark.sql(
    '''
SELECT EventID, count(*) as count
FROM apt29HostDay1
WHERE Channel = 'Microsoft-Windows-Sysmon/Operational'

GROUP BY EventID
ORDER BY count DESC
                          ''')

vis.barh_chart(spark.createDataFrame(sysmon_host_day1.head(8)),'count','EventID','Frequency of Sysmon Logs')

### c) Let's analyze information of Sysmon 1: Process Creation

What are the event fields for **Sysmon 1**? Let's get this information from OSSEM :D

ossem.getEventDf(platform = 'windows', provider = 'sysmon', event = 'event-1')

Now that we know the fields' names of **Sysmon 1**, let's query its info:

sysmon1 = spark.sql(
    '''
SELECT User, LogonId, ProcessId, Image, CommandLine, ParentProcessId, ParentImage, ParentCommandLine 
FROM apt29HostDay1
WHERE Channel = "Microsoft-Windows-Sysmon/Operational"
    AND EventID = 1
                          ''')
sysmon1.show(1, truncate = False, vertical = True)

All the fields contain **categorical data**, so we can continue doing stack counting operations. Let's try something different: Let's calculate the **length of characters** of the **CommandLine** field.

sysmon1 = spark.sql(
    '''
SELECT User, LogonId, ProcessId, Image, CommandLine, ParentProcessId, ParentImage, ParentCommandLine,
        length(CommandLine) as CommandLineLength
FROM apt29HostDay1
WHERE Channel = "Microsoft-Windows-Sysmon/Operational"
    AND EventID = 1
                          ''')
sysmon1.show(1,truncate = False, vertical = True)

Now we have a **Numerical** variable in our dataframe. What do we know about this new variable?

* Before we continue with our analysis, let's review two basic but important concepts: **Mean** and **Standard Deviation**:

![](images/average.PNG)

![](images/average2.PNG)

![](images/average3.PNG)

We can use **descriptive** method to calculate basic statistics

sysmon1.select('CommandLineLength').describe().show()

We can also use **numStats** method from openhunt to calculate more basic statistics

ds.numStats(sysmon1,'CommandLineLength')

Can we do this statistical analysis in a more **visual** way? Let's check a couple of visualizations :D

A **histogram**

vis.histogram(sysmon1,'CommandLineLength')

A **Boxplot***

vis.box_plot(sysmon1,'CommandLineLength')

How can we improve our graphs? Let's add more contex to our SQL query:

sysmon1 = spark.sql(
    '''
SELECT User, LogonId, ProcessId, Image, CommandLine, ParentProcessId, ParentImage, ParentCommandLine,
        length(CommandLine) as CommandLineLength
FROM apt29HostDay1
WHERE Channel = "Microsoft-Windows-Sysmon/Operational"
    AND EventID = 1
    AND length(CommandLine) <1000
                          ''')

Let's graph our **Histogram** again!!

vis.histogram(sysmon1,'CommandLineLength')

And our **Boxplot** also!!

vis.box_plot(sysmon1,'CommandLineLength')

And what about the **atipic** values or outliers for the CommandLine lenght? Let's filter the one  :D

sysmon1 = spark.sql(
    '''
SELECT User, LogonId, ProcessId, Image, CommandLine, ParentProcessId, ParentImage, ParentCommandLine,
        length(CommandLine) as CommandLineLength
FROM apt29HostDay1
WHERE Channel = "Microsoft-Windows-Sysmon/Operational"
    AND EventID = 1
    AND length(CommandLine) > 7000
                          ''')
print('We have ', sysmon1.count(), ' records')
sysmon1.show(truncate = False, vertical = True)

This event might represent the **potential execution** of a **PowerSheel script** **:O**

Let's get all the **Sysmon** events related to its **ProcessId 8704** as a Child

process8704 = spark.sql(
    '''
SELECT EventID , count(*) as count
FROM apt29HostDay1
WHERE ProcessId = 8704

GROUP BY EventID
ORDER BY count DESC
                          ''')
process8704.show(truncate = False)

It is common to start looking for **PowerShell** events because it is a tool that **enables** a lot of other **techiques**. We should also focus on the events related to this process to identify other behaviors and techniques.
* Notes: 12 (Registry creation and deletion), 7 (Image Loaded), 11 (File Creation), 23 (File Delete), 17 (Pipe Created), 13 (Registry Modification), 1 (Process Creation), 10 (Process Access), 18 (Pipe Connected), 5 (Process Terminated)


### d) Let's now analyze information of Sysmon 3: Network Connection

Let's query the info for this event and calculate the **most frequent** pair or IPs (Source -> Destination):

sysmon3 = spark.sql(
    '''
SELECT concat_ws(' <--> ',SourceIp,DestinationIp) as SourceDestinationIP, count(*) as count
FROM apt29HostDay1
WHERE Channel = "Microsoft-Windows-Sysmon/Operational"
    AND EventID = 3
    AND NOT SourceIp = DestinationIp
    AND (SourceIp = "10.0.1.4" OR SourceIp = "10.0.1.5" OR SourceIp = "10.0.1.6")
    
GROUP BY concat_ws(' <--> ',SourceIp,DestinationIp)
ORDER BY count DESC
                          ''')
sysmon3.show(truncate = False)

### e) So, Is this all the potential of PySpark.SQL?... "JOIN" me in learning more about it :D

Let's take a look at the **Lateral Movement** tactic accomplished during Day 1:

![](images/lateral1.PNG)

![](images/lateral2.PNG)

Let's query the host data for day 1 using **Security 4624 (Account Successfully Logged On)** event as a reference:

lateralMovement = spark.sql(
    '''
    SELECT
        o.Hostname, o.EventID, o.SubjectUserName, o.SubjectLogonId,
        a.TargetUserName, a.TargetLogonId, a.IpAddress
    FROM apt29HostDay1 o
    INNER JOIN (
        SELECT Hostname, TargetUserName, TargetLogonId, IpAddress
        FROM apt29HostDay1
        WHERE LOWER(Channel) = 'security'
            AND EventID = 4624
            AND LogonType = 3
            AND NOT IpAddress LIKE "%-%"
            AND NOT TargetUserName LIKE "%$"          
        ) a
    ON o.SubjectLogonId = a.TargetLogonId
    WHERE LOWER(o.Channel) = 'security'
    ''')

print("There are ", lateralMovement.count(), ' records.')
lateralMovement.show(truncate = False)

Let's take a look at **Security 5145 (A network share object was checked)** event:

lateralMovement = spark.sql(
    '''
    SELECT
        o.Hostname, o.EventID, o.SubjectUserName, o.SubjectLogonId, o.ShareName, o.ShareLocalPath, o.RelativeTargetName,
        a.TargetUserName, a.TargetLogonId, a.IpAddress
    FROM apt29HostDay1 o
    INNER JOIN (
        SELECT Hostname, TargetUserName, TargetLogonId, IpAddress
        FROM apt29HostDay1
        WHERE LOWER(Channel) = 'security'
            AND EventID = 4624
            AND LogonType = 3
            AND NOT IpAddress LIKE "%-%"
            AND NOT TargetUserName LIKE "%$"          
        ) a
    ON o.SubjectLogonId = a.TargetLogonId
    WHERE LOWER(o.Channel) = 'security'
        AND EventID = 5145
    ''')

print("There are ", lateralMovement.count(), ' records.')
lateralMovement.show(45, truncate = False)

Now we have **more context** to add in our data model :D

![](images/lateral3.PNG)

### f) Finally... let's check some network data!! :D

How many byters were transferred from hosts on days 1?

bytes_from_host_day1 = spark.sql(
    '''
SELECT orig_bytes
FROM apt29NetworkDay1
                          ''')

ds.numStats(bytes_from_host_day1,'orig_bytes')

Let's analyze the results in a more graphical way!! :)

vis.histogram(bytes_from_host_day1.dropna(),'orig_bytes')

vis.box_plot(bytes_from_host_day1.dropna(),'orig_bytes')

Yeah, you are right... We need to filter our data!! 

bytes_from_host_day1 = spark.sql(
    '''
SELECT orig_bytes
FROM apt29NetworkDay1
WHERE orig_bytes <= 1500
                          ''')

vis.histogram(bytes_from_host_day1.dropna(),'orig_bytes')

vis.box_plot(bytes_from_host_day1.dropna(),'orig_bytes')

Let's take a look at the **atipic** values for **bytes transfered**

bytes_from_host_day1 = spark.sql(
    '''
SELECT id_orig_h,id_orig_p,id_resp_h,id_resp_p, orig_bytes
FROM apt29NetworkDay1
WHERE (orig_bytes >= 1500 AND NOT orig_bytes LIKE 'NaN')

ORDER BY orig_bytes DESC
                          ''')
print(bytes_from_host_day1.count())
bytes_from_host_day1.show(truncate = False)

How can we **correlate** **network** and **host** data?

sysmon3_host_day1 = spark.sql(
    '''
SELECT ProcessId, User, Image, SourcePort, DestinationPort
FROM apt29HostDay1
WHERE Channel = 'Microsoft-Windows-Sysmon/Operational'
    AND EventID = 3
    AND SourceIp LIKE "%10.0.1.4%"
    AND DestinationIp LIKE "%192.168.0.4%"
                          ''')
print(sysmon3_host_day1.count())
sysmon3_host_day1.show(truncate = False)

# Thank you !!!