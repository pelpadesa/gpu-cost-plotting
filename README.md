# gpu-cost-plotting
Calculates and plots "Cost Per Frame" figures for GPUs using data scraped from Tom'sHardware, and provided .CSV pricing data.

Using .CSV data from `./pricing_data` (Formatted as `GPU,Price`), Cost-Per-Frame graphs are generated and saved to image files. Framerate data is scraped on-the-fly from the tables on TomsHardware's "GPU Hierarchy" page. For GPU data to be plotted, it has to be present in Main.py's `color_map` dictionary.

### Usage
Main.py contains an example of usage at the bottom. This repository also contains an example data file at `/pricing_data/US_Newegg.csv`, as well as an example output image at `/images/US_Newegg.png`. The default behavior of Main.py will use the US_Newegg.csv file to generate a new graph which is saved to US_Newegg.png

### Example Output:
![US_Newegg](https://user-images.githubusercontent.com/117033048/215795237-cb730f9b-785e-42b6-a295-a283f6a78a4c.png)
