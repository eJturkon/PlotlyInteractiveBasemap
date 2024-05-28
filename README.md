## **3D Interactive Basemap |** *Plotly*

#### Contents:
- [**Data Scrape**](./basemap_scrape.ipynb): Data obtained via [Earth Explorer](https://earthexplorer.usgs.gov/) an applet created by The United States Geological Survey.
- [**Map Build**](./basemap.ipynb): Bot build with Selenium.

<ins>Data Structure</ins>: Data is stored in 108 geotiff files scraped from [Earth Explorer](https://earthexplorer.usgs.gov/). Each file represents a 20x30 degree tile of the world map in in EPSG:4326 projection. 

Here, the z-axis(altitude) is exaggerated realative to x, y to emphasize changes in elevation, the realative numbers are correct. This can be easily corrected.

![img2](./images/2.png)
![img3](./images/3.png)
![img1](./images/1.png)


