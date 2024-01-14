﻿from os import path
from json import load
from numpy import arange
import matplotlib.pyplot as plt

clusterDic = {}
with open("firstPass.dat") as dicFile:
    #load dictionary from LuminosityFunctions.py into code
    clusterDic = load(dicFile)
    
#hard-coded column name, start of slice, end of slice tuples for table III properties
DATA_FILE_COLUMNS = [
        ("radialVelocity", 13, 20), #this should have no correlation, good to check
        ("centralConcentration", 50, 55),
        ("coreObsRadiusArcMin", 60, 65), #in arcmin, need cluster distance
        ("luminosityDensity", 80, 87),
        ("velocityDispersion", 37, 42),
    ]

GENERATE_PLOTS = [ #code name, table header tuples
        ("radialVelocity", "Pulsar Count vs Heliocentric Radial Velocity", "Radial Velocity (km s^-1)"),
        ("centralConcentration", "Pulsar Count vs King-model Central Concentration", "Central Concentration"),
        ("luminosityDensity", "Pulsar Count vs Central Luminosity Density", "Luminosity Density (L_☉ pc^-3)"),
        ("coreRadiusPc", "Pulsar Count vs Core Radius", "Core Radius (pc)"),
        ("velocityDispersion", "Pulsar Count vs Central Velocity Dispersion", "Central Velocity Dispersion (km/s)"),
        ("metallicity", "Pulsar Count vs Cluster Metallicity", "Metallicity (Fe/H)")
    ]

MIN_OBSERVATIONS = 0 #adjust to eliminate low-data clusters
    
with open("clusterData.dat") as dataFile:
    #here we go. First, load into a list:
    dataFileMainList = dataFile.readlines()
    #Restrict to table III (velocities and structural parameters) and table I (positional data)
    dataFileTableIII = dataFileMainList[433:590]
    dataFileTableII = dataFileMainList[252:410]
    dataFileTableI = dataFileMainList[72:230]
    #Extract cluster names and validate cluster names in generated dictionary
    idListTableIII = [row[:12].strip() for row in dataFileTableIII]
    idListTableII = [row[:12].strip() for row in dataFileTableII]
    idListTableI = [row[:12].strip() for row in dataFileTableI]
    for clusterName in clusterDic.keys():
        if clusterName not in idListTableIII:
            raise ValueError(f"{clusterName} is invalid. Perhaps it has a different name?")
        #Retrieve cluster distance from table I
        rowNumI = idListTableI.index(clusterName)
        clusterDic[clusterName]["distanceKPc"] = float(dataFileTableI[rowNumI][68:73]) 
        rowNumMetal = idListTableII.index(clusterName)
        clusterDic[clusterName]["metallicity"] = float(dataFileTableII[rowNumMetal][14:19])
        #Go through desired properties defined in DATA_FILE_COLUMNS and add to clusterDic
        rowNum = idListTableIII.index(clusterName)
        for prop, start, end in DATA_FILE_COLUMNS:
            try:
                clusterDic[clusterName].update({
                        prop : float(dataFileTableIII[rowNum][start:end])
                    })
            except ValueError:
                clusterDic[clusterName].update({
                        prop: 0
                    })
        #set a core-collapsed boolean, just in case
        clusterDic[clusterName]["coreCollapsed"] = "c" in dataFileTableIII[rowNum][56:59]

#We've got our dictionary! Still needs some massaging though. Let's calculate physical radius of cluster cores first.
for clusterName in clusterDic.keys():
    clusterData = clusterDic[clusterName]
    d = clusterData["distanceKPc"] * 1000 #parsecs
    r_o = clusterData["coreObsRadiusArcMin"] * 0.000290888 #radians
    clusterData.update({
            "coreRadiusPc" : d*r_o #small-angle approximation is our friend
        })

    
for valueName, title, yLable in GENERATE_PLOTS:
    plt.clf()
    xValues = []
    yValues = []
    xErrorMin = []
    xErrorMax = []
    for clusterName in clusterDic.keys():
        xValues.append(clusterDic[clusterName]["probableCount"])
        yValues.append(clusterDic[clusterName][valueName])
        xErrorMin.append(clusterDic[clusterName]["95min"])
        xErrorMax.append(clusterDic[clusterName]["95max"])
    xError = [xErrorMin, xErrorMax]
    #plt.scatter(xValues, yValues)
    plt.yscale("log")
    #plt.xscale("log")
    plt.title(title)
    plt.ylabel("Most probable count of pulsars")
    plt.xlabel(yLable)
    plt.errorbar(yValues, xValues, yerr=xError, fmt='or', capsize=0) #swap the x and y axes the messy way
    plt.savefig(path.join(".","plots","properties",f"{valueName}.png"))