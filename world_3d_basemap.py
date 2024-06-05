#basemap
import os
import re
import sys
import json
import shapely
import requests
import rasterio
import numpy as np
import pandas as pd
import datetime as dt
from cartopy import crs
import geopandas as gpd
import plotly.express as px
from rasterio.mask import mask
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from rasterio.transform import Affine
from shapely.geometry import mapping, Point

#scrape
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def scrape_basemap_data(
    downloads_directory,
    data_directory,
    ee_username,
    ee_password,
    maximize_window=True
):
    # create selenium istance
    website = "https://earthexplorer.usgs.gov/"
    driver = webdriver.Chrome()
    driver.maximize_window() if maximize_window else ''
    driver.get(website)

    # click data tab
    el = driver.find_element(By.XPATH, value='''//ul/li[@id="authMenuLink"]/a''')
    el.click()

    # input username
    el = driver.find_element(By.XPATH, value='''//div/input[@name="username"]''')
    el.send_keys(ee_username)

    # input password
    el = driver.find_element(By.XPATH, value='''//div/input[@name="password"]''')
    el.send_keys(ee_password)

    # click login button
    el = driver.find_element(By.XPATH, value='''//input[@id="loginButton"]''')
    el.click()

    # click data tab
    el = driver.find_element(By.XPATH, value='''//div/div[contains(text(), "Data Sets")]''')
    el.click()

    # click digital elevation drop down
    time.sleep(3)
    el = driver.find_element(By.XPATH, value='''//div/strong[contains(text(), "Digital Elevation")]''')
    el.click()

    # select GMTED2012
    el = driver.find_element(By.XPATH, value='''//div/label[contains(text(), "GMTED2010")]''')
    el.click()

    # click results
    time.sleep(3)
    el = driver.find_elements(By.XPATH, value='''//input[@title="Results"]''')
    el[1].click()

    # takes ~ 6min to scrape
    page_nums = 11
    for i in range(page_nums-1):

        scrape_page(driver)
        
        # go to next page
        el = driver.find_element(By.XPATH, value=f'''//div/a[@id="{i+2}_5e83a1f36d8572da"]''')
        el.click()
        time.sleep(1)

    driver.quit()

    # move files from downloads to data directory
    command = f'mv {downloads_directory}/GMTED2010* {data_directory}'
    subprocess.run(command, shell=True)

    command = f'find {data_directory} -type f -name "*.zip" -exec unzip {{}} -d {data_directory} \\;'
    subprocess.run(command, shell=True)


def show_basemap(
    file_directory,
    pix_per_tile=250
):
    # med= median elevation across 30 arc seconds
    files = [file for file in os.listdir(file_directory) if file.endswith('med300.tif')]

    # create visualization
    fig = go.Figure()

    world_gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world_gdf = world_gdf.set_geometry('geometry')   # set the active geometry
    world_gdf['geometry'].crs = 'EPSG:4326'

    # pixles per tile
    n = pix_per_tile
    global_min_elevation = 0
    global_max_elevation = 8848 # meters

    # Set geographic bounds
    min_lon, max_lon = -180, 180
    min_lat, max_lat = -90, 90

    # calculate x, y, z and to add each file to figure as its own trace
    for file in files:

        with rasterio.open(file_directory + '/' + file) as src:
            img = src.read(1)  # Read first band
            meta = src.meta  # metadata to calculate lat and lon

        transform = meta['transform']
        width, height = meta['width'], meta['height']

        # defined above
        row_start, row_end, col_start, col_end = calculate_indices(transform, width, height, min_lon, max_lon, min_lat, max_lat)

        n_lat = n_lon = n
        if row_end - row_start != height or col_end - col_start != width:
            n_lat = max(int(n * (row_end - row_start) / height), 1)
            n_lon = max(int(n * (col_end - col_start) / width), 1)
        
        # Generate longitude and latitude arrays within the bounds
        lon = np.linspace(transform.c + col_start * transform.a, transform.c + col_end * transform.a, n_lon)
        lat = np.linspace(transform.f + row_start * transform.e, transform.f + row_end * transform.e, n_lat)
        lon, lat = np.meshgrid(lon, lat)

        # Select data within bounds
        row_indices = np.linspace(row_start, row_end - 1, n_lat, dtype=int)
        col_indices = np.linspace(col_start, col_end - 1, n_lon, dtype=int)
        row_indices = np.clip(row_indices, 0, height - 1)
        col_indices = np.clip(col_indices, 0, width - 1)
        z_data = img[np.ix_(row_indices, col_indices)]

        # Add to plot
        fig.add_trace(go.Surface(
            z=z_data, x=lon, y=lat, 
            colorscale='IceFire',
            cmin=global_min_elevation,
            cmax=global_max_elevation/1.5,
            colorbar=dict(title='elevation(m)'),
            showlegend=False
        ))
    # set initial camera view
    camera = dict(
        up=dict(x=0, y=0, z=1),  # "up" direction
        center=dict(x=-0.2, y=-0.2, z=-.02),  # R3 location
        eye=dict(x=-0.3, y=-0.45, z=.5)  # position of the camera
    )
    # make it look nice
    fig.update_layout(
        title='Earth Terrain Basemap',
        showlegend=False,
        scene=dict(
            aspectmode='manual',
            aspectratio=dict(x=1.5, y=1, z=1),
            xaxis = dict(
                range=[min_lon, max_lon], title='Latitude',
                backgroundcolor="rgb(0,0,0)",
                gridcolor="grey",
                showbackground=True,
                zerolinecolor="grey"),
            yaxis = dict(
                range=[min_lat, max_lat], title='Longitude',
                backgroundcolor="rgb(0,0,0)",
                gridcolor="grey",
                showbackground=True,
                zerolinecolor="grey"),
            zaxis = dict(
                range=[0.0000001, 300000], title='Altitude',
                gridcolor="grey",
                showbackground=True,
                zerolinecolor="black",),
        ),
        # figure size
        width=1250,  # figure width
        height=900,  # figure height
        autosize=False,
        scene_camera=camera
    )
    coord_list = []

    # non-topo world outline
    for shapely_object in world_gdf['geometry']:
        
        if shapely_object.geom_type == 'Polygon':
            coords = list(shapely_object.exterior.coords)
            coord_list.extend(coords)
            coord_list.append([None,None])
        elif shapely_object.geom_type == 'MultiPolygon':
            for polygon in shapely_object.geoms:
                coords = list(polygon.exterior.coords)
                coord_list.extend(coords)
                coord_list.append([None,None])

    lon, lat = zip(*coord_list)
    z = 2 * np.ones(len(lon)) # altitude(2 here)
    fig.add_scatter3d(x=lon, y=lat, z=z, mode='lines', line_color="rgb(70, 70, 70)", line_width=3, showlegend=False)
    fig.show()

def adjust_longitude(lon):
    # Adjust longitude from [0,360] to [-180, 180]
    if lon > 180:
        return lon - 360
        
    return lon


# Calculate indices based on realative to geographic bounds
def calculate_indices(
    transform,
    width,
    height,
    min_lon,
    max_lon,
    min_lat,
    max_lat
):
    # lon & lat for each pixel
    lon_per_pixel = transform.a
    lat_per_pixel = transform.e
    start_lon = transform.c
    start_lat = transform.f

    # indices
    col_start = max(int((start_lat - max_lat) / lon_per_pixel), 0)
    col_end = min(int((start_lat - min_lat) / lon_per_pixel), width)
    row_start = max(int((min_lon - start_lon) / abs(lat_per_pixel)), 0)
    row_end = min(int((max_lon - start_lon) / abs(lat_per_pixel)), height)

    return row_start, row_end, col_start, col_end

def scrape_page(driver):
    time.sleep(2)
    result_table = driver.find_elements(By.XPATH, value='''//table[@class="resultPageTable"]/tbody/tr''')
    for element in result_table:

        time.sleep(1)
        after = element.find_element(By.XPATH, value='''./td[@class="resultRowContent"]/ul/li/div[@class="iconContainer"]/a[@class="download"]''')
        after.click()

        time.sleep(2.5)
        el = driver.find_elements(By.XPATH, value='''//div[@id="optionsContainer"]/div/div[@class="downloadButtons"]''')
        try: el[2].click()
        except: driver.quit()

        time.sleep(1)
        el = driver.find_elements(By.XPATH, value='''//div/button[@title="Close"]''')
        el[2].click()
