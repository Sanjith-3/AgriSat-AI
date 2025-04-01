import streamlit as st
import zipfile
import os
from glob import glob
import numpy as np
import earthpy.spatial as es
import rasterio as rio
from datetime import datetime
from groq import Groq
import matplotlib.pyplot as plt
import earthpy.plot as ep
import warnings
import base64
from io import BytesIO
warnings.filterwarnings('ignore')
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def load_bands_and_compute_indices(data_folder):
    """
    Load Sentinel bands from TIFF files and stack them.
    Returns stacked array of bands or None if error occurs.
    """
    try:
        # Find all band files
        sentinel_bands = glob(os.path.join(data_folder, "*B?*.tiff"))
        if not sentinel_bands:
            st.error("No band files found in the uploaded data")
            return None
        
        # Sort bands to ensure consistent order
        sentinel_bands.sort()
        
        # Load each band
        band_list = []
        for band_file in sentinel_bands:
            with rio.open(band_file, 'r') as src:
                band_data = src.read(1)
                # Replace potential infinity or invalid values with nan
                band_data = np.where(np.isfinite(band_data), band_data, np.nan)
                band_list.append(band_data)
        
        # Stack bands into 3D array
        if band_list:
            arr_st = np.stack(band_list)
            return arr_st
        else:
            st.error("No valid band data found")
            return None
            
    except Exception as e:
        st.error(f"Error loading satellite bands: {str(e)}")
        return None

def get_farmer_insights(analysis_summary):
    """Generate farming insights using Groq AI."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"""
You are an agricultural expert helping farmers understand their field conditions based on satellite data.
Please analyze this data and provide practical advice in simple, non-technical language. Additionally, give a detailed technical analysis.

{analysis_summary}

Please format your response as follows:
1. Simple Summary
2. Key Actions
3. Timing
4. Warnings
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gemma2-9b-it",
            temperature=0.7,
            max_tokens=1000
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating insights: {str(e)}"
    



def plot_index_with_interpretation(index, title, cmap="RdYlGn", vmin=-1, vmax=1):
    """Plot the selected index with appropriate coloring and title."""
    try:
        fig, ax = plt.subplots(figsize=(10, 14))
        ep.plot_bands(index, cmap=cmap, cols=1, vmin=vmin, vmax=vmax, ax=ax)
        plt.title(title)
        st.pyplot(fig)
        plt.close()
    except Exception as e:
        st.error(f"Error plotting index: {str(e)}")



def normalize_band(band):
    """Normalize band data to 0-1 range."""
    band_min = np.nanmin(band)
    band_max = np.nanmax(band)
    if band_max > band_min:
        return (band - band_min) / (band_max - band_min)
    return band

def compute_indices(arr_st):
    """
    Compute various vegetation and environmental indices from satellite bands.
    Returns tuple of computed indices.
    """
    try:
        if arr_st is None or len(arr_st) < 8:
            raise ValueError("Insufficient band data for index computation")

        # Normalize bands for consistent calculations
        bands_normalized = [normalize_band(band) for band in arr_st]

        # Calculate indices with error handling
        def safe_normalized_diff(band1, band2):
            """Safely compute normalized difference with error handling."""
            try:
                return es.normalized_diff(band1, band2)
            except Exception as e:
                st.warning(f"Error computing normalized difference: {str(e)}")
                return np.full_like(band1, np.nan)

        # Basic indices
        ndvi = safe_normalized_diff(arr_st[7], arr_st[3])
        
        # Soil Adjusted Vegetation Index
        L = 0.5
        try:
            savi = ((arr_st[7] - arr_st[3]) / (arr_st[7] + arr_st[3] + L)) * (1 + L)
        except:
            savi = np.full_like(arr_st[7], np.nan)
        
        # Visible Atmospherically Resistant Index
        try:
            vari = (arr_st[2] - arr_st[3]) / (arr_st[2] + arr_st[3] - arr_st[1])
        except:
            vari = np.full_like(arr_st[2], np.nan)
        
        # Modified Normalized Difference Water Index
        mndwi = safe_normalized_diff(arr_st[1], arr_st[3])
        
        # Normalized Difference Moisture Index
        ndmi_alt = safe_normalized_diff(arr_st[7], arr_st[3])
        
        # Chlorophyll/Moisture Ratio
        try:
            cmr_alt = np.divide(arr_st[7], arr_st[5])
        except:
            cmr_alt = np.full_like(arr_st[7], np.nan)
        
        # Floating Mat Recognition
        try:
            fmr_alt = np.divide(arr_st[7], arr_st[5])
        except:
            fmr_alt = np.full_like(arr_st[7], np.nan)
        
        # Enhanced Vegetation Index
        try:
            evi = 2.5 * (arr_st[7] - arr_st[3]) / (arr_st[7] + 6 * arr_st[3] - 7.5 * arr_st[1] + 1)
        except:
            evi = np.full_like(arr_st[7], np.nan)
        
        # Normalized Burn Ratio
        nbr = safe_normalized_diff(arr_st[7], arr_st[6])
        
        # Green Chlorophyll Index
        try:
            gci = (arr_st[7] / arr_st[1]) - 1
        except:
            gci = np.full_like(arr_st[7], np.nan)
        
        # Transformed Chlorophyll Absorption in Reflectance Index
        try:
            tcari = 3 * ((arr_st[3] - arr_st[1]) - 0.2 * (arr_st[3] - arr_st[2]) * (arr_st[3] / arr_st[1]))
        except:
            tcari = np.full_like(arr_st[3], np.nan)
        
        # Burn Area Index
        try:
            bai = 1 / ((0.1 - arr_st[2])**2 + (0.06 - arr_st[3])**2)
        except:
            bai = np.full_like(arr_st[2], np.nan)
        
        # Optimized Soil-Adjusted Vegetation Index
        try:
            osavi = (arr_st[7] - arr_st[3]) / (arr_st[7] + arr_st[3] + 0.16)
        except:
            osavi = np.full_like(arr_st[7], np.nan)

        return ndvi, savi, vari, mndwi, ndmi_alt, cmr_alt, fmr_alt, evi, nbr, gci, tcari, bai, osavi

    except Exception as e:
        st.error(f"Error computing indices: {str(e)}")
        return tuple([None] * 13)

def format_analysis_summary(ndvi, savi, vari, mndwi, evi, nbr, gci, tcari, bai, osavi, moisture="high", valid_pixels=48.0):
    """Format analysis results into a readable summary."""
    try:
        # Ensure all required indices are provided and calculated
        indices = [ndvi, savi, vari, mndwi, evi, nbr, gci, tcari, bai, osavi]
        if any(index is None for index in indices):
            raise ValueError("Missing required index data")

        # Calculate mean values for each index
        ndvi_mean = np.nanmean(ndvi)
        savi_mean = np.nanmean(savi)
        vari_mean = np.nanmean(vari)
        mndwi_mean = np.nanmean(mndwi)
        evi_mean = np.nanmean(evi)
        nbr_mean = np.nanmean(nbr)
        gci_mean = np.nanmean(gci)
        tcari_mean = np.nanmean(tcari)
        bai_mean = np.nanmean(bai)
        osavi_mean = np.nanmean(osavi)

        # Assessments for readability
        vegetation_status = "good" if ndvi_mean > 0.3 else "poor"
        stress_level = "high" if vari_mean < 0 else "low"
        water_presence = "high" if mndwi_mean > 0 else "low"
        burn_severity = "high" if nbr_mean < -0.1 else "low"
        chlorophyll_content = "high" if gci_mean > 0 else "low"
        burn_area_risk = "high" if bai_mean > 0.1 else "low"
        soil_adjusted_status = "healthy" if osavi_mean > 0.16 else "stressed"

        # Formatted summary
        return f"""
SATELLITE ANALYSIS SUMMARY:
1. Vegetation Health (NDVI): {ndvi_mean:.3f} - {vegetation_status} vegetation density
2. Soil Impact (SAVI): {savi_mean:.3f} - Significant soil influence detected
3. Plant Stress (VARI): {vari_mean:.3f} - {stress_level} vegetation stress
4. Water Presence (MNDWI): {mndwi_mean:.3f} - {water_presence} water content in soil
5. Enhanced Vegetation Index (EVI): {evi_mean:.3f} - Vegetation enhancement index
6. Burn Severity (NBR): {nbr_mean:.3f} - {burn_severity} burn severity risk
7. Green Chlorophyll Index (GCI): {gci_mean:.3f} - {chlorophyll_content} chlorophyll content in plants
8. Chlorophyll Absorption (TCARI): {tcari_mean:.3f} - Chlorophyll absorption rate
9. Burn Area Index (BAI): {bai_mean:.3f} - {burn_area_risk} burn area risk
10. Soil-Adjusted Vegetation (OSAVI): {osavi_mean:.3f} - {soil_adjusted_status} vegetation
11. Moisture Content: {moisture}
12. Data Quality: {valid_pixels}% valid measurements
"""
    except Exception as e:
        return f"Error formatting analysis summary: {str(e)}"


def plot_index_with_interpretation(index, title, cmap="RdYlGn", vmin=-1, vmax=1):
    """Plot the selected index with appropriate coloring and title and return it as HTML."""
    try:
        fig, ax = plt.subplots(figsize=(10, 14))
        ep.plot_bands(index, cmap=cmap, cols=1, vmin=vmin, vmax=vmax, ax=ax)
        plt.title(title)
        
        # Save plot to a temporary buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.close()
        buf.seek(0)
        
        # Encode the image as base64
        image_base64 = base64.b64encode(buf.getvalue()).decode()
        
        # Create HTML for the image with a button to open in new tab
        html = f'''
            <div style="text-align: center;">
                <img src="data:image/png;base64,{image_base64}" style="max-width: 100%; height: auto;">
                <br>
                <a href="data:image/png;base64,{image_base64}" target="_blank">
                    <button style="margin-top: 10px; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        Open Plot in New Tab
                    </button>
                </a>
            </div>
        '''
        st.markdown(html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error plotting index: {str(e)}")

def get_index_interpretation(index_name):
    """Return the interpretation guide for the selected index."""
    interpretations = {
        "NDVI (Normalized Difference Vegetation Index)": """
        - Range: -1 to 1
        - Used for: Measuring vegetation health and density
        - < 0: Water, bare soil, or clouds
        - 0-0.2: Barren areas, rock, sand, or snow
        - 0.2-0.4: Shrubs and grassland
        - 0.4-0.6: Moderate vegetation
        - > 0.6: Dense vegetation, crops at peak growth
        
        This index is particularly useful for monitoring crop health throughout the growing season.
        """,
        
        "SAVI (Soil Adjusted Vegetation Index)": """
        - Range: -1 to 1
        - Used for: Vegetation analysis in areas with high soil exposure
        - < 0: Water, bare soil, or clouds
        - 0-0.2: Very sparse vegetation
        - 0.2-0.4: Sparse vegetation
        - 0.4-0.6: Moderate vegetation
        - > 0.6: Dense vegetation
        
        SAVI is particularly useful in areas where soil exposure might affect NDVI readings.
        """,
        
        "VARI (Visible Atmospherically Resistant Index)": """
        - Range: Generally -1 to 1
        - Used for: Vegetation analysis using only visible light bands
        - < 0: Stressed or senescent vegetation
        - 0-0.1: Bare soil or very sparse vegetation
        - 0.1-0.3: Moderate vegetation health
        - > 0.3: Healthy vegetation
        
        VARI is particularly useful for analyzing vegetation in RGB imagery and is less sensitive to atmospheric effects.
        """,
        
        "MNDWI (Modified Normalized Difference Water Index)": """
        - Range: -1 to 1
        - Used for: Detecting water bodies and moisture content
        - > 0: Water bodies
        - 0 to -0.2: Built-up areas and bare soil
        - < -0.2: Vegetation
        
        MNDWI is excellent for distinguishing water features and assessing soil moisture conditions.
        """,
        
        "NDMI (Normalized Difference Moisture Index)": """
        - Range: -1 to 1
        - Used for: Vegetation water content assessment
        - < 0: Water stress or low moisture content
        - 0-0.2: Moderate moisture content
        - > 0.2: High moisture content
        
        NDMI is particularly useful for monitoring drought conditions and irrigation needs.
        """,
        
        "CMR (Chlorophyll/Moisture Ratio)": """
        - Used for: Assessing both chlorophyll content and moisture stress
        - Higher values indicate better plant health
        - Lower values may indicate stress conditions
        
        CMR combines information about chlorophyll content and moisture stress in vegetation.
        """,
        
        "FMR (Floating Mat Recognition)": """
        - Used for: Detecting floating vegetation in water bodies
        - Higher values indicate presence of floating vegetation
        - Lower values indicate clear water or other surfaces
        
        FMR is particularly useful for monitoring aquatic vegetation and water quality.
        """,
        
        "EVI (Enhanced Vegetation Index)": """
        - Range: -1 to 1
        - Used for: Improved vegetation monitoring
        - < 0: Non-vegetated areas
        - 0-0.2: Sparse vegetation
        - 0.2-0.5: Moderate vegetation
        - > 0.5: Dense vegetation
        
        EVI improves upon NDVI by being more sensitive to canopy structural variations.
        """,
        
        "NBR (Normalized Burn Ratio)": """
        - Range: -1 to 1
        - Used for: Identifying burned areas and severity
        - < -0.2: High severity burn
        - -0.2 to -0.1: Moderate severity burn
        - -0.1 to 0.1: Low severity or unburned
        - > 0.1: Healthy vegetation
        
        NBR is particularly useful for post-fire monitoring and recovery assessment.
        """,
        
        "GCI (Green Chlorophyll Index)": """
        - Used for: Estimating chlorophyll content
        - < 0: Stressed vegetation
        - 0-1: Moderate chlorophyll content
        - > 1: High chlorophyll content, healthy vegetation
        
        GCI is particularly useful for monitoring crop nutrition and health status.
        """,
        
        "TCARI (Transformed Chlorophyll Absorption in Reflectance Index)": """
        - Used for: Precise chlorophyll content estimation
        - Higher values: Lower chlorophyll content
        - Lower values: Higher chlorophyll content
        
        TCARI is less sensitive to leaf layering effects than other chlorophyll indices.
        """,
        
        "BAI (Burn Area Index)": """
        - Used for: Highlighting recently burned areas
        - Higher values: Recently burned areas
        - Lower values: Unburned vegetation or other surfaces
        
        BAI is particularly useful for fire damage assessment and monitoring.
        """,
        
        "OSAVI (Optimized Soil-Adjusted Vegetation Index)": """
        - Range: -1 to 1
        - Used for: Vegetation monitoring with soil brightness correction
        - < 0.2: Bare soil or very sparse vegetation
        - 0.2-0.5: Moderate vegetation coverage
        - > 0.5: Dense vegetation
        
        OSAVI optimizes the soil adjustment factor for most agricultural conditions.
        """
    }
    return interpretations.get(index_name, """
    Interpretation not available for this index. 
    Please select another index from the dropdown menu.
    """)


def main():
    """Main application function."""
    st.set_page_config(page_title="Agricultural Satellite Analysis", layout="wide")
    
    st.title("Advanced Satellite Analysis for Agricultural Insights")
    st.write("Upload satellite data to analyze vegetation indices and get agricultural insights")

    uploaded_file = st.file_uploader("Upload a zip file containing satellite data", type="zip")
    
    if uploaded_file:
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                data_folder = "extracted_data"
                if os.path.exists(data_folder):
                    for file in glob(os.path.join(data_folder, "*")):
                        os.remove(file)
                else:
                    os.makedirs(data_folder)
                zip_ref.extractall(data_folder)

            st.write("Processing satellite data...")
            arr_st = load_bands_and_compute_indices(data_folder)
            
            if arr_st is not None:
                # Compute all indices
                indices = compute_indices(arr_st)
                
                # Updated index names with descriptions
                index_names = [
                    "NDVI (Normalized Difference Vegetation Index)",
                    "SAVI (Soil Adjusted Vegetation Index)",
                    "VARI (Visible Atmospherically Resistant Index)",
                    "MNDWI (Modified Normalized Difference Water Index)",
                    "NDMI (Normalized Difference Moisture Index)",
                    "CMR (Chlorophyll/Moisture Ratio)",
                    "FMR (Floating Mat Recognition)",
                    "EVI (Enhanced Vegetation Index)",
                    "NBR (Normalized Burn Ratio)",
                    "GCI (Green Chlorophyll Index)",
                    "TCARI (Transformed Chlorophyll Absorption in Reflectance Index)",
                    "BAI (Burn Area Index)",
                    "OSAVI (Optimized Soil-Adjusted Vegetation Index)"
                ]
                
                # Visualization section
                st.header("Visualization Tools")
                
                # Index selection with improved dropdown
                selected_index = st.selectbox(
                    "Select an index to visualize",
                    index_names,
                    help="Choose which vegetation index to display"
                )
                
                # Get index data (map full names to short names for data access)
                short_names = ["NDVI", "SAVI", "VARI", "MNDWI", "NDMI", "CMR", "FMR", 
                             "EVI", "NBR", "GCI", "TCARI", "BAI", "OSAVI"]
                index_dict = dict(zip(index_names, indices))
                selected_data = index_dict[selected_index]
                
                if selected_data is not None:
                    # Display plot and interpretation
                    st.subheader(f"{selected_index} Visualization")
                    plot_index_with_interpretation(selected_data, selected_index)
                    
                    # Show interpretation
                    st.write("### How to Interpret This Index")
                    interpretation = get_index_interpretation(selected_index)
                    st.markdown(interpretation)
                    
                    # Statistics for selected index
                    st.write("### Statistical Analysis")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Mean Value", f"{np.nanmean(selected_data):.3f}")
                    with col2:
                        st.metric("Min Value", f"{np.nanmin(selected_data):.3f}")
                    with col3:
                        st.metric("Max Value", f"{np.nanmax(selected_data):.3f}")
                    
                    # Generate comprehensive analysis
                analysis_summary = format_analysis_summary(
                                        indices[0],  # NAVI 
                                        indices[1],  # SAVI
                                        indices[2],  # VARI
                                        indices[3],  # MNDWI
                                        indices[4],  # EVI
                                        indices[5],  # NBR
                                        indices[6],  # GCI
                                        indices[7],  # TCARI
                                        indices[8],  # BAI
                                        indices[9]   # OSAVI
                                        )
                
                print(analysis_summary)
                    
                    # Get insights from Groq
            st.header("AI-Powered Agricultural Insights")
            insights = get_farmer_insights(analysis_summary)
            st.write(insights)
            
            # Cleanup
            for file in glob(os.path.join(data_folder, "*")):
                os.remove(file)
            if os.path.exists(data_folder):
                os.rmdir(data_folder)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            # Ensure cleanup happens even if there's an error
            if os.path.exists(data_folder):
                for file in glob(os.path.join(data_folder, "*")):
                    os.remove(file)
                os.rmdir(data_folder)
    else:
        st.write("Please upload a zip file containing your satellite data.")



if __name__ == "__main__":
    main()
