import logging as log
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Local modules
import Naming as VTN
sys.path.append("../IO")
import Reader as IOR
import SysHelpers as IOSH
sys.path.append("../ValidityMeasures")
import CommonConfig as VMCC

#-------------------------------------------------------------------------------

def plot_cut_effect(file_path, output_formats=["pdf"]):
  """ Plot the (absolute) effect of the cos(theta) cut on the distributions.
  """
  # Read the input file
  log.debug("Reading file: {}".format(file_path))
  reader = IOR.Reader(file_path)
  
  # Output info
  output_dir = "{}/plots".format(os.path.dirname(file_path))
  base_name = os.path.basename(file_path).replace("_valdata.csv","")
  log.debug("Output will be written to: {}".format(output_dir))
  
  # Get the pandas dataframe for the cut histograms
  df = reader["Data"]
  row_cut0 = df[(df["Delta-c"] == 0) & (df["Delta-w"] == 0)]

  bin_centers = reader["BinCenters"]
  n_bins = len(bin_centers)
  n_dims = len(reader["CoordName"])

  # Find the MC event histograms
  y_nocut = reader["NoCutData"]
  y_cut = []
  y_par = []
  for b in range(n_bins):
    y_cut.append(row_cut0["C{}".format(b)])
    y_par.append(row_cut0["P{}".format(b)])
  y_cut = np.array(y_cut)
  y_par = np.array(y_par)
  
  # Correctly normalise the MC event histograms
  scale_factor = VMCC.TestLumi * reader["CrossSection"] / reader["NTotalMC"]
  y_nocut *= scale_factor
  y_cut *= scale_factor
  y_par *= scale_factor
  
  # Create the test histograms
  for d in range(n_dims):
    # Find the binning x range and the relevant x bin center of each bin
    x_edges = np.linspace(reader["CoordMin"][d],reader["CoordMax"][d],reader["CoordNBins"][d]+1)
    x_vals = bin_centers[:,d]
    
    # Create the figure
    fig, ax = plt.subplots(tight_layout=True)
    title = "{} : {}{}".format(reader["Name"],VTN.eM_chirality(reader["e-Chirality"]),VTN.eP_chirality(reader["e+Chirality"]))
    ax.set_title(title)
    
    # Create the plots (no cut, actual cut, parametrised cut)
    hist_nocut = plt.hist(x_vals, bins=x_edges, weights=y_nocut, label="No cut", ec='black', fill=False)
    hist_cut = plt.hist(x_vals, bins=x_edges, weights=y_cut, label="True cut", ec='#CC3311', fill=False, hatch="//")
    hist_par = plt.hist(x_vals, bins=x_edges, weights=y_par, label="Param. cut", ec='#009988', fill=False, hatch="\\\\")
    
    # Some nicer plotting
    ax.set_xlabel(reader["CoordName"][d])
    ax.set_ylabel("#Events")
    ax.set_ylim([0,1.1*np.amax(hist_nocut[0])])
    ax.legend(title=r"{}fb$^{{-1}}$, $\cos\theta_{{\mu}}^{{cut}}={}$".format(VMCC.TestLumi,reader["Coef|MuonAcc_CutValue"]))
    
    # Save the figure in all requested formats
    for format in output_formats:
      format_dir = "{}/{}/CutEffect".format(output_dir,format)
      IOSH.create_dir(format_dir)
      fig.savefig("{}/{}_{}_CutEffect.{}".format(format_dir, base_name, reader["CoordName"][d], format))
      
    plt.close(fig)

#-------------------------------------------------------------------------------

def main():
  """ Run the cut effect plotting for each relevant file.
  """
  log.basicConfig(level=log.WARNING) # Set logging level

  input_dirs = [
    "/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_l/PrEWInput/validation",
    "/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/NewMCProduction/4f_WW_sl/PrEWInput/validation"
  ]
  
  for input_dir in input_dirs:
    for file_path in IOSH.find_files(input_dir, ".csv"):
      log.debug("Found file: {}".format(file_path))
      plot_cut_effect(file_path)
      
#-------------------------------------------------------------------------------

if __name__ == "__main__":
  main()