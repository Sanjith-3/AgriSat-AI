
# CropSense - Agricultural Satellite Analysis Tool

Welcome to **CropSense**, a simple Streamlit-based web app designed to turn satellite data into insights for farmers and learners! Whether you’re tending fields or just curious about crops from space, CropSense aims to make complex satellite imagery understandable and useful.

This tool processes multispectral satellite data (like from Sentinel-2), calculates vegetation indices, and uses AI (via Groq) to suggest farming tips. I’m no expert in the science myself, but I’ve built this to explore and learn—so let’s figure it out together!

---

## Table of Contents
- [What is CropSense?](#what-is-cropsense)
- [Understanding Satellite Imagery](#understanding-satellite-imagery)
- [What are Multispectral Images?](#what-are-multispectral-images)
- [How CropSense Works](#how-cropsense-works)
- [Calculated Indices](#calculated-indices)
- [Instruction Guide: Downloading Sentinel-2 Data](#instruction-guide-downloading-sentinel-2-data)
- [Potential Use Cases](#potential-use-cases)
- [A Quick Note on Experimental Nature](#a-quick-note-on-experimental-nature)
- [Installation and Usage](#installation-and-usage)
- [Contributing](#contributing)
- [License](#license)

---

## What is CropSense?

CropSense is an open-source project that takes satellite data (in TIFF format, often from Sentinel-2), processes it to calculate agricultural indices, and offers AI-powered farming advice. Built with Python, Streamlit, and libraries like Rasterio and EarthPy, it’s meant to be approachable and educational.

Upload a zip file with satellite band data, and CropSense will compute indices, show visualizations, and give practical tips. It’s a starting point for anyone—like me—trying to learn about agriculture and satellites!

---

## Understanding Satellite Imagery

<details>
<summary>Click to expand: What is Copernicus, Sentinel, and Satellite Imagery?</summary>

Let’s keep it simple! Satellite imagery is like a bird’s-eye view of Earth, captured by satellites floating way up there. These images use different light wavelengths to reveal things we can’t see with our eyes—like how healthy crops are.

### Copernicus Programme
Copernicus is an EU project that watches over Earth’s environment. It’s free, open, and helps with everything from climate tracking to farming. The data comes from satellites called **Sentinel**.

### Sentinel Satellites
The Sentinel family, especially **Sentinel-2**, is great for land and farming. Launched in 2015 and 2017, these satellites snap detailed pics every few days using 13 wavelength bands—think of them as super-cameras seeing visible and invisible light. That’s what powers CropSense!

### How It Ties to CropSense
CropSense uses Sentinel-2 TIFF files (bands like Blue, Red, or Near-Infrared). You upload them, and we turn numbers into insights. It’s a fun way to peek at fields from space!

</details>

---

## What are Multispectral Images?

<details>
<summary>Click to expand: Multispectral Images Explained</summary>

Multispectral images sound fancy, but they’re just pictures taken in different light “colors”—some we see, some we don’t. Here’s the scoop:

### What Are They?
Unlike a regular photo, multispectral images split light into bands (e.g., Blue, Red, Infrared). Each band tells us something unique about the land or plants.

### How Are They Captured?
Satellites like Sentinel-2 use sensors to catch light bouncing off Earth. For example:
- **Visible bands**: Blue (490 nm), Green (560 nm), Red (665 nm)—what we’d see.
- **Near-Infrared (NIR)**: Shows plant health (healthy crops glow in NIR!).
- **Shortwave Infrared (SWIR)**: Spots water or burn marks.

Each band becomes a TIFF file, which CropSense stacks and analyzes.

### How Are They Used?
Farmers use these to check crop health, water needs, or damage. It’s like a diagnostic tool for fields!

### How CropSense Uses Them
We take those TIFFs, calculate indices (like health scores), plot them in colors, and let AI suggest what to do. It’s my attempt to make sense of it all!

</details>

---

## How CropSense Works

CropSense is pretty straightforward:
1. **Upload**: Drop in a zip file with TIFF bands (e.g., Sentinel-2 B02, B04, B08).
2. **Process**: We stack the bands into a 3D array.
3. **Calculate**: Compute 13 indices using standard formulas.
4. **Visualize**: Pick an index to see it mapped out.
5. **Insights**: AI (Grok) gives farming tips based on the numbers.
6. **Cleanup**: Temporary files get deleted.

It’s all wrapped in Streamlit for an easy click-and-go experience!

---

## Calculated Indices

<details>
<summary>Click to expand: Indices Calculated by CropSense</summary>

CropSense calculates a bunch of indices to peek into your field’s story. I’ve included what they are, their formulas, and what they might mean—based on what I’ve pieced together!

### 1. NDVI (Normalized Difference Vegetation Index)
- **What**: Checks plant health.
- **Formula**: `(NIR - Red) / (NIR + Red)`
- **Range**: -1 to 1
- **Meaning**: < 0 = bare soil; > 0.6 = lush crops.

### 2. SAVI (Soil Adjusted Vegetation Index)
- **What**: Adjusts NDVI for soil.
- **Formula**: `((NIR - Red) / (NIR + Red + 0.5)) * 1.5`
- **Range**: -1 to 1
- **Meaning**: Similar to NDVI, better for sparse areas.

### 3. VARI (Visible Atmospherically Resistant Index)
- **What**: Spots stress using visible light.
- **Formula**: `(Green - Red) / (Green + Red - Blue)`
- **Range**: -1 to 1
- **Meaning**: < 0 = stressed; > 0.3 = healthy.

### 4. MNDWI (Modified Normalized Difference Water Index)
- **What**: Finds water or moisture.
- **Formula**: `(Green - Red) / (Green + Red)`
- **Range**: -1 to 1
- **Meaning**: > 0 = water; < -0.2 = plants.

### 5. NDMI (Normalized Difference Moisture Index)
- **What**: Checks plant water content.
- **Formula**: `(NIR - Red) / (NIR + Red)` (alt form)
- **Range**: -1 to 1
- **Meaning**: < 0 = dry; > 0.2 = moist.

### 6. CMR (Chlorophyll/Moisture Ratio)
- **What**: Looks at chlorophyll and moisture.
- **Formula**: `NIR / SWIR1`
- **Range**: Varies
- **Meaning**: Higher = healthier.

### 7. FMR (Floating Mat Recognition)
- **What**: Detects floating plants.
- **Formula**: `NIR / SWIR1`
- **Range**: Varies
- **Meaning**: Higher = floating vegetation.

### 8. EVI (Enhanced Vegetation Index)
- **What**: Better NDVI for thick canopies.
- **Formula**: `2.5 * (NIR - Red) / (NIR + 6 * Red - 7.5 * Blue + 1)`
- **Range**: -1 to 1
- **Meaning**: > 0.5 = dense growth.

### 9. NBR (Normalized Burn Ratio)
- **What**: Checks burn severity.
- **Formula**: `(NIR - SWIR2) / (NIR + SWIR2)`
- **Range**: -1 to 1
- **Meaning**: < -0.2 = burned; > 0.1 = healthy.

### 10. GCI (Green Chlorophyll Index)
- **What**: Measures chlorophyll.
- **Formula**: `(NIR / Green) - 1`
- **Range**: Varies
- **Meaning**: > 1 = healthy plants.

### 11. TCARI (Transformed Chlorophyll Absorption in Reflectance Index)
- **What**: Precise chlorophyll check.
- **Formula**: `3 * ((Red - Blue) - 0.2 * (Red - Green) * (Red / Blue))`
- **Range**: Varies
- **Meaning**: Lower = more chlorophyll.

### 12. BAI (Burn Area Index)
- **What**: Highlights burned spots.
- **Formula**: `1 / ((0.1 - Green)^2 + (0.06 - Red)^2)`
- **Range**: Varies
- **Meaning**: Higher = recent burns.

### 13. OSAVI (Optimized Soil-Adjusted Vegetation Index)
- **What**: NDVI with soil tweak.
- **Formula**: `(NIR - Red) / (NIR + Red + 0.16)`
- **Range**: -1 to 1
- **Meaning**: > 0.5 = dense crops.

These get plotted and sent to AI for advice. Explore them in the app!

</details>

---

## Instruction Guide: Downloading Sentinel-2 Data

<details>
<summary>Click to expand: How to Download Sentinel-2 Data for CropSense</summary>

Not sure how to get the right satellite data? Here’s a step-by-step guide to download Sentinel-2 images from the Sentinel Hub EO Browser in the format CropSense needs. It’s easier than it sounds!

### Step-by-Step Download Process
**Step 1: Open Copernicus Browser**
- Go to [Copernicus Browser]([https://apps.sentinel-hub.com/eo-browser/](https://browser.dataspace.copernicus.eu/)).
- Log in or sign up for a free account.

**Step 2: Search for Your Area**
- Use the search bar to enter your latitude/longitude (e.g., for your farm) or zoom in manually.
- Set the date (e.g., 2025-02-26 or your preferred date).
- Select **Sentinel-2 L2A** (it’s pre-corrected for atmosphere—perfect for us!).

**Step 3: Select Required Bands**
- Click “Custom” under “Create custom visualization.”
- Go to “Raw Data” and check these bands:
  - ✅ B02 (Blue)
  - ✅ B03 (Green)
  - ✅ B04 (Red)
  - ✅ B05 (Red Edge 1)
  - ✅ B06 (Red Edge 2)
  - ✅ B07 (Red Edge 3)
  - ✅ B08 (NIR)
  - ✅ B8A (Narrow NIR)
  - ✅ B11 (SWIR-1)
  - ✅ B12 (SWIR-2)

**Step 4: Download the ZIP File**
- Click “Download.”
- In the pop-up:
  - **Image format**: TIFF (32-bit float)
  - **Resolution**: Medium or High (your choice!)
  - **Coordinate System**: WGS 84 (EPSG:4326)
  - Check “Clip extra bands” to skip unneeded ones.
- Hit “Download” to grab your ZIP file.

### Next Steps After Download
- Extract the ZIP file on your computer.
- Upload it to CropSense (via `stream.py`) to process the TIFFs and compute indices.

### Final Summary
- **Bands to Download**: B02, B03, B04, B05, B06, B07, B08, B8A, B11, B12
- **Format**: TIFF (32-bit float)
- **Process**: Extract ZIP → Upload to CropSense → Get Insights

Now you’re ready to analyze your fields!

</details>

---

## Potential Use Cases

I’m no farming expert, but CropSense might be handy in a few ways—especially for Indian farmers! Here’s where it could possibly help, in a small, humble way:

- **Crop Health Check for Small Farmers**: In India, where many farmers work small plots, CropSense could use free Sentinel-2 data to show if crops like rice or wheat are doing okay. It might help decide when to add fertilizer or water.
- **Monsoon Monitoring**: With unpredictable rains, it could maybe track soil moisture (via MNDWI or NDMI) to see if fields are too dry or flooded—useful for planning in states like Maharashtra or Punjab.
- **Pest or Stress Alerts**: The VARI index might hint at stressed plants. For cotton farmers in Gujarat, this could flag trouble early, though I’m not sure how accurate it’d be!
- **Burn Recovery in Dry Seasons**: In places like Tamil Nadu, where stubble burning happens, NBR or BAI might show how fields recover—could be a simple way to check damage.
- **Learning Tool for Villages**: Extension workers or students in rural India could use it to practice with satellite data, maybe helping farmers understand their land better over time.

These are just ideas—I don’t know the full science, but I hope CropSense can spark some curiosity or small wins for Indian agriculture!

---

## A Quick Note on Experimental Nature

Just so you know, CropSense is an experimental project I built to learn and play with satellite data. The indices, values, and AI tips are based on standard methods, but I’m not certain they’re spot-on for real farming decisions. Think of it as a fun, educational tool rather than something to bet your harvest on. Let’s keep exploring together!

---

## Installation and Usage

Ready to give CropSense a whirl? Here’s how:

### Prerequisites
- Python 3.8+
- A Groq API key (get one at [Groq’s website](https://groq.com))



### Sample Data
Download Sentinel-2 data using the [Instruction Guide](#instruction-guide-downloading-sentinel-2-data) above!

---

## Contributing

Love CropSense? Want to tweak it? Fork the repo, make changes, and send a pull request. Ideas for Indian farming tweaks or better visuals? Share them in the issues tab—I’d love your input!

### Tags
#AgriTech #SatelliteImagery #RemoteSensing #AI #Sentinel2 #PrecisionAgriculture #CropMonitoring #VegetationIndices #SoilAnalysis #FarmAnalytics #SustainableFarming #IndianAgriculture #MonsoonFarming #RicePaddyMonitoring #SmallholderFarming #DroughtManagement #DataScience #MachineLearning #Python #Streamlit #GeospatialAnalysis #Copernicus #OpenSource #ClimateChange #DisasterRecovery #EducationalTool

