## **3D Interactive Basemap |** *Plotly*
A customizable and user interactive backround for visualizing geospatial data within the Plotly Python library.

#### Contents:
- [**dev_notebooks**](./dev_notebooks)
  - [**basemap_scrape.ipynb**](./dev_notebooks/basemap_scrape.ipynb): Bot built with Selenium, data obtained via [Earth Explorer](https://earthexplorer.usgs.gov/) an applet created by The United States Geological Survey.
  - [**basemap.ipynb**](./dev_notebooks/basemap.ipynb): Plotly basemap build with tile geodesy correction.
- [**example_usage.ipynb**](./example_usage.ipynb): Using the automated `scrape_basemap_data` and `show_basemap` methods from [world_3d_basemap.py](./world_3d_basemap.py)
- [**world_3d_basemap.py**](./world_3d_basemap.py): Automated processes.

<ins>Data Structure</ins>: Data is stored in 108 geotiff files scraped from [Earth Explorer](https://earthexplorer.usgs.gov/). Each file represents a 20x30 degree tile of the world map in in EPSG:4326 projection. 

Here, the scale of the z-axis(altitude) is exaggerated realative to x, y to emphasize changes in elevation, the numbers are correct. This can be easily changed.

![img2](./images/2.png)
![img3](./images/3.png)
![img1](./images/1.png)
