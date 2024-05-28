## **3D Interactive Basemap |** *Plotly*

#### Contents:
- [**Data Scrape**](./basemap_scrape.ipynb): Bot built with Selenium, data obtained via [Earth Explorer](https://earthexplorer.usgs.gov/) an applet created by The United States Geological Survey.
- [**Map Build**](./basemap.ipynb): Plotly basemap build with tile geodesy correction.

<ins>Data Structure</ins>: Data is stored in 108 geotiff files scraped from [Earth Explorer](https://earthexplorer.usgs.gov/). Each file represents a 20x30 degree tile of the world map in in EPSG:4326 projection. 

Here, the scale of the z-axis(altitude) is exaggerated realative to x, y to emphasize changes in elevation, the numbers are correct. This can be easily changed.

![img2](./images/2.png)
![img3](./images/3.png)
![img1](./images/1.png)
