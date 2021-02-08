import logging as log
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Local modules
import Naming as VTN
sys.path.append("../IO")
import PandasHelper as IOPH
import Reader as IOR
import SysHelpers as IOSH
sys.path.append("../PlottingHelp")
import Colors as PHC
import Markers as PHM
sys.path.append("../ValidityMeasures")
import CommonConfig as VMCC

#-------------------------------------------------------------------------------

class DevDirection:
  """ Class defines one deviation direction.
  """
  def __init__(self,name,func):
    self.name = name
    self.func = np.vectorize(func,signature='(n)->()')

# Library of most relevant deviation directions 
# -> use lambda functions of delta = [delta-c, delta-w] to describe direction
dev_directions = {
  DevDirection("center only", lambda deltas: deltas[1] == 0),
  DevDirection("width only", lambda deltas: deltas[0] == 0),
  DevDirection("upper edge only", lambda deltas: deltas[0] - deltas[1]/2.0 == 0),
  DevDirection("lower edge only", lambda deltas: deltas[0] + deltas[1]/2.0 == 0)
}

#-------------------------------------------------------------------------------

def plot_deviation_test(file_path, output_formats=["pdf"]):
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
  scale_factor = VMCC.TestLumi * reader["CrossSection"] / reader["NTotalMC"]

  bin_centers = reader["BinCenters"]
  n_bins = len(bin_centers)
  n_dims = len(reader["CoordName"])
  
  row_cut0 = df[(df["Delta-c"] == 0) & (df["Delta-w"] == 0)]
  N_cut_cut0 = np.array([row_cut0["C{}".format(b)] for b in range(n_bins)])
  N_par_cut0 = np.array([row_cut0["P{}".format(b)] for b in range(n_bins)])
  
  # Find the bin edges for each dimension
  bin_edges = [np.linspace(reader["CoordMin"][d],reader["CoordMax"][d],reader["CoordNBins"][d]+1) for d in range(n_dims)]
  
  deltas = IOPH.delta_pairs(df)
  for dev_dir in dev_directions:
    log.debug("Looking at direction {}".format(dev_dir.name))
    dir_selection = dev_dir.func(deltas)
    dir_rows = df[dir_selection]
    dir_deltas = deltas[dir_selection]
    
    N_cut = np.array([dir_rows["C{}".format(b)] for b in range(n_bins)])
    N_par = np.array([dir_rows["P{}".format(b)] for b in range(n_bins)])
    
    diff_c0 = (N_cut - N_cut_cut0)*scale_factor
    diff_pc = (N_par - N_cut)*scale_factor
    
    for d in range(n_dims):
      x = bin_centers[:,d]
      title = "{} : {}{} @ {}fb$^{{-1}}$ - Shift: {}".format(reader["Name"],VTN.eM_chirality(reader["e-Chirality"]),VTN.eP_chirality(reader["e+Chirality"]),VMCC.TestLumi,dev_dir.name)
      
      #--- Plot N_cut - N_cut0 -------------------------------------------------
      
      # start with a rectangular Figure
      fig = plt.figure(figsize=(6, 6))
      fig.suptitle(title)#, fontsize=16)
      
      # definitions for the axes
      left, width = 0.15, 0.49
      bottom, height = 0.1, 0.49
      spacing = 0.005
      rect_scatter = [left, bottom, width, height]
      rect_histx = [left, bottom + height + spacing, width, 0.93 - (bottom + height + spacing)]
      rect_histy = [left + width + spacing, bottom, 0.93 - (left + width + spacing), height]
      leg_pos = [(width + spacing)/width, (height + spacing)/height]
      
      ax_scatter = plt.axes(rect_scatter)
      ax_scatter.tick_params(direction='in', top=True, right=True)
      ax_scatter.set_xlabel(reader["CoordName"][d])
      ax_scatter.set_ylabel(r"$N_{cut}^{(\Delta c,\Delta w)} - N_{cut}^{0}$")
      ax_histx = plt.axes(rect_histx)
      ax_histx.tick_params(direction='in', labelbottom=False)
      ax_histx.set_ylabel("Cumulative")
      ax_histy = plt.axes(rect_histy)
      ax_histy.tick_params(direction='in', labelleft=False)
      ax_histy.set_xlabel("#bins")

      y_bin_edges = np.linspace(np.amin(diff_c0), np.amax(diff_c0), 20)

      colors = PHC.ColorMap("plasma",len(dir_deltas))

      # the scatter plot:
      for row in range(len(dir_deltas)):
        y = diff_c0[:,row]
        color = colors[row]
        scatter = ax_scatter.scatter(x, y, color='none', edgecolors=color, marker=PHM.markers[row], label=r"$({} \delta, {} \delta)$".format(dir_deltas[row][0]/reader["Delta"],dir_deltas[row][1]/reader["Delta"]))

        ax_histx.hist(x, bins=bin_edges[d], weights=y, histtype='step',fill=False, ec=color)
        ax_histy.hist(y, bins=y_bin_edges, orientation='horizontal', histtype='step',fill=False, ec=color)

      ax_histx.set_xlim(ax_scatter.get_xlim())
      ax_histy.set_ylim(ax_scatter.get_ylim())
      
      ax_scatter.legend(loc=leg_pos, title=r"$(\Delta c, \Delta w), \delta={}$".format(reader["Delta"]))
      
      # Save the figure in all requested formats
      for format in output_formats:
        format_dir = "{}/{}/DevCutCut0".format(output_dir,format)
        IOSH.create_dir(format_dir)
        dev_dir_name = dev_dir.name.replace(" ", "_")
        fig.savefig("{}/{}_{}_DevCutCut0_{}.{}".format(format_dir, base_name, reader["CoordName"][d], dev_dir_name, format))
      
      plt.close(fig)
      
      #--- Plot N_par - N_cut --------------------------------------------------
      
      # start with a rectangular Figure
      fig = plt.figure(figsize=(6, 6))
      fig.suptitle(title)#, fontsize=16)
      
      # definitions for the axes
      left, width = 0.15, 0.49
      bottom, height = 0.1, 0.49
      spacing = 0.005
      rect_scatter = [left, bottom, width, height]
      rect_histx = [left, bottom + height + spacing, width, 0.93 - (bottom + height + spacing)]
      rect_histy = [left + width + spacing, bottom, 0.93 - (left + width + spacing), height]
      leg_pos = [(width + spacing)/width, (height + spacing)/height]
      
      ax_scatter = plt.axes(rect_scatter)
      ax_scatter.tick_params(direction='in', top=True, right=True)
      ax_scatter.set_xlabel(reader["CoordName"][d])
      ax_scatter.set_ylabel(r"$N_{par}^{(\Delta c,\Delta w)} - N_{cut}^{(\Delta c,\Delta w)}$")
      ax_histx = plt.axes(rect_histx)
      ax_histx.tick_params(direction='in', labelbottom=False)
      ax_histx.set_ylabel("Cumulative")
      ax_histy = plt.axes(rect_histy)
      ax_histy.tick_params(direction='in', labelleft=False)
      ax_histy.set_xlabel("#bins")

      y_bin_edges = np.linspace(np.amin(diff_pc), np.amax(diff_pc), 20)

      colors = PHC.ColorMap("plasma",len(dir_deltas))

      # the scatter plot:
      for row in range(len(dir_deltas)):
        y = diff_pc[:,row]
        color = colors[row]
        scatter = ax_scatter.scatter(x, y, color='none', edgecolors=color, marker=PHM.markers[row], label=r"$({} \delta, {} \delta)$".format(dir_deltas[row][0]/reader["Delta"],dir_deltas[row][1]/reader["Delta"]))

        ax_histx.hist(x, bins=bin_edges[d], weights=y, histtype='step',fill=False, ec=color)
        ax_histy.hist(y, bins=y_bin_edges, orientation='horizontal', histtype='step',fill=False, ec=color)

      ax_histx.set_xlim(ax_scatter.get_xlim())
      ax_histy.set_ylim(ax_scatter.get_ylim())
      
      ax_scatter.legend(loc=leg_pos, title=r"$(\Delta c, \Delta w), \delta={}$".format(reader["Delta"]))
      
      # Save the figure in all requested formats
      for format in output_formats:
        format_dir = "{}/{}/DevParCut".format(output_dir,format)
        IOSH.create_dir(format_dir)
        dev_dir_name = dev_dir.name.replace(" ", "_")
        fig.savefig("{}/{}_{}_DevParCut_{}.{}".format(format_dir, base_name, reader["CoordName"][d], dev_dir_name, format))
      
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
      plot_deviation_test(file_path)
      
#-------------------------------------------------------------------------------

if __name__ == "__main__":
  main()