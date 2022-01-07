import logging as log
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from tqdm import tqdm

# Local modules
import Naming as VTN
sys.path.append("../IO")
import PandasHelper as IOPH
import Reader as IOR
import SysHelpers as IOSH
sys.path.append("../PlottingHelp")
import Colors as PHC
import DefaultFormat as PHDF
import Markers as PHM
sys.path.append("../ValidityMeasures")
import CommonConfig as VMCC
import DeltaHelp as VMDH

#-------------------------------------------------------------------------------

class DevDirection:
  """ Class defines one deviation direction.
  """
  def __init__(self,name,coord,func):
    self.name = name
    self.coord = coord
    self.func = func
    
# Library of most relevant deviation directions 
# -> use lambda functions of delta = [delta-c, delta-w] to describe direction
dev_directions = {
  DevDirection("center", "c", lambda deltas: deltas[:,1] == 0),
  DevDirection("width", "w", lambda deltas: deltas[:,0] == 0),
  DevDirection("upper edge", "x_{{up}}", lambda deltas: deltas[:,0] - deltas[:,1]/2.0 == 0),
  DevDirection("lower edge", "x_{{low}}", lambda deltas: deltas[:,0] + deltas[:,1]/2.0 == 0)
}

def delta_in_dir(dir_name, deltas):
  """ Calculate the deviation in the given direction.
  """
  if dir_name == "center":
    return deltas[:,0]
  elif dir_name == "width":
    return deltas[:,1]
  elif dir_name == "upper edge":
    return deltas[:,0] + deltas[:,1]/2.0
  elif dir_name == "lower edge":
    return deltas[:,0] - deltas[:,1]/2.0
  else:
    raise Exception("Unknown dir name ", dir_name)

def ratio(a,b,default=0.0):
  """ Calculate ratio between two arrays, if denominator point is 0 set default.
  """
  return np.where(np.abs(b)>0.00000001,a/b,default)

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
  
  # Find the deltas and the minimum and maximum deviations
  deltas = IOPH.delta_pairs(df)
  delta_metrics = VMDH.delta_metric(deltas)
  colors = PHC.ColorSpectrum("turbo",-1.1*np.amax(delta_metrics),1.1*np.amax(delta_metrics))
  
  for dev_dir in tqdm(dev_directions, desc="Dev. dir. loop", leave=False):
    log.debug("Looking at direction {}".format(dev_dir.name))
    dir_selection = dev_dir.func(deltas)
    dir_rows = df[dir_selection]
    dir_deltas = deltas[dir_selection]
    deltas_in_dir = delta_in_dir(dev_dir.name, dir_deltas)
    
    N_cut = np.array([dir_rows["C{}".format(b)] for b in range(n_bins)])
    N_par = np.array([dir_rows["P{}".format(b)] for b in range(n_bins)])
    
    diff_c0 = np.sqrt(scale_factor) * ratio(N_cut - N_cut_cut0, np.sqrt(N_cut_cut0)) 
    diff_p0 = np.sqrt(scale_factor) * ratio(N_par - N_cut_cut0, np.sqrt(N_cut_cut0)) 
    diff_pc = np.sqrt(scale_factor) * ratio(N_par - N_cut, np.sqrt(N_cut)) 
    
    title = "{}, ${}$ab$^{{-1}}$".format(VTN.metadata_to_process(reader),VMCC.TestLumi/1000)
    legend_title = "Shift {}\n$\Delta {}$ $[\delta={}]$".format(dev_dir.name,dev_dir.coord, reader["Delta"])
    
    for d in tqdm(range(n_dims), desc="Dim. loop", leave=False):
      x = bin_centers[:,d]
      x_min, x_max = bin_edges[d][0], bin_edges[d][-1]
      coord_name = "${}$".format(VTN.name_to_coord(reader["CoordName"][d]))
      
      # definitions for the axes
      figsize = (12,10)
      left, width = 0.17, 0.49
      bottom, height = 0.12, 0.49
      spacing = 0.005
      rect_scatter = [left, bottom, width, height]
      rect_histx = [left, bottom + height + spacing, width, 0.93 - (bottom + height + spacing)]
      rect_histy = [left + width + spacing, bottom, 0.93 - (left + width + spacing), height]
      leg_pos = [(width + spacing)/width, (height + spacing)/height]
      
      # Common plotting arguments
      common_sc_kwargs = { "color":'none', "linewidths": 2 , "s": 10**2}
      common_hist_kwargs = { "histtype":'step', "fill": False, "lw" : 2 }
      
      #--- Plot N_cut - N_cut0 -------------------------------------------------
      
      # start with a rectangular Figure
      fig = plt.figure(figsize=figsize)
      fig.suptitle(title)#, fontsize=16)
      
      ax_scatter = plt.axes(rect_scatter)
      ax_scatter.tick_params(direction='in', top=True, right=True)
      ax_scatter.set_xlabel(coord_name)
      ax_scatter.set_ylabel(r"$\left(N_{cut}^{(\Delta c,\Delta w)} - N_{cut}^{0}\right)/\sqrt{N_{cut}^{0}}$")
      ax_histx = plt.axes(rect_histx)
      ax_histx.tick_params(direction='in', labelbottom=False)
      ax_histx.set_ylabel("$\sum_{bins} y^2$")
      ax_histy = plt.axes(rect_histy)
      ax_histy.tick_params(direction='in', labelleft=False)
      ax_histy.set_xlabel("#bins")

      y_bin_edges = np.linspace(np.amin(diff_c0), np.amax(diff_c0), 20)

      for row in range(len(dir_deltas)):
        y = diff_c0[:,row]
        color = colors[deltas_in_dir[row]]
        scatter = ax_scatter.scatter(x, y, edgecolors=color, marker=PHM.markers[row], label=r"${}$".format(deltas_in_dir[row]/reader["Delta"]), **common_sc_kwargs)

        ax_histx.hist(x, bins=bin_edges[d], weights=y**2, ec=color, **common_hist_kwargs)
        ax_histy.hist(y, bins=y_bin_edges, orientation='horizontal', ec=color, **common_hist_kwargs)

      ax_scatter.set_xlim((x_min, x_max))
      ax_histx.set_xlim(ax_scatter.get_xlim())
      ax_histy.set_ylim(ax_scatter.get_ylim())
      
      ax_scatter.legend(loc=leg_pos, title=legend_title, ncol=2)
      
      # Save the figure in all requested formats
      for format in output_formats:
        format_dir = "{}/{}/DevCutCut0".format(output_dir,format)
        IOSH.create_dir(format_dir)
        dev_dir_name = dev_dir.name.replace(" ", "_")
        fig.savefig("{}/{}_{}_DevCutCut0_{}.{}".format(format_dir, base_name, reader["CoordName"][d], dev_dir_name, format))
      
      plt.close(fig)
      
      #--- Plot N_par - N_cut0 -------------------------------------------------
      
      # start with a rectangular Figure
      fig = plt.figure(figsize=figsize)
      fig.suptitle(title)#, fontsize=16)
      
      ax_scatter = plt.axes(rect_scatter)
      ax_scatter.tick_params(direction='in', top=True, right=True)
      ax_scatter.set_xlabel(coord_name)
      ax_scatter.set_ylabel(r"$\left(N_{par}^{(\Delta c,\Delta w)} - N_{cut}^{0}\right)/\sqrt{N_{cut}^{0}}$")
      ax_histx = plt.axes(rect_histx)
      ax_histx.tick_params(direction='in', labelbottom=False)
      ax_histx.set_ylabel("$\sum_{bins} y^2$")
      ax_histy = plt.axes(rect_histy)
      ax_histy.tick_params(direction='in', labelleft=False)
      ax_histy.set_xlabel("#bins")

      y_bin_edges = np.linspace(np.amin(diff_p0), np.amax(diff_p0), 20)

      for row in range(len(dir_deltas)):
        y = diff_p0[:,row]
        color = colors[deltas_in_dir[row]]
        scatter = ax_scatter.scatter(x, y, edgecolors=color, marker=PHM.markers[row], label=r"${}$".format(deltas_in_dir[row]/reader["Delta"]), **common_sc_kwargs)

        ax_histx.hist(x, bins=bin_edges[d], weights=y**2, ec=color, **common_hist_kwargs)
        ax_histy.hist(y, bins=y_bin_edges, orientation='horizontal', ec=color, **common_hist_kwargs)

      ax_scatter.set_xlim((x_min, x_max))
      ax_histx.set_xlim(ax_scatter.get_xlim())
      ax_histy.set_ylim(ax_scatter.get_ylim())
      
      ax_scatter.legend(loc=leg_pos, title=legend_title, ncol=2)
      
      # Save the figure in all requested formats
      for format in output_formats:
        format_dir = "{}/{}/DevParCut0".format(output_dir,format)
        IOSH.create_dir(format_dir)
        dev_dir_name = dev_dir.name.replace(" ", "_")
        fig.savefig("{}/{}_{}_DevParCut0_{}.{}".format(format_dir, base_name, reader["CoordName"][d], dev_dir_name, format))
      
      plt.close(fig)
      
      #--- Plot N_par - N_cut --------------------------------------------------
      
      # start with a rectangular Figure
      fig = plt.figure(figsize=figsize)
      fig.suptitle(title)#, fontsize=16)
      
      ax_scatter = plt.axes(rect_scatter)
      ax_scatter.tick_params(direction='in', top=True, right=True)
      ax_scatter.set_xlabel(coord_name)
      ax_scatter.set_ylabel(r"$\left(N_{par}^{(\Delta c,\Delta w)} - N_{cut}^{(\Delta c,\Delta w)}\right)/\sqrt{N_{cut}^{(\Delta c,\Delta w)}}$")
      ax_histx = plt.axes(rect_histx)
      ax_histx.tick_params(direction='in', labelbottom=False)
      ax_histx.set_ylabel("$\sum_{bins} y^2$")
      ax_histy = plt.axes(rect_histy)
      ax_histy.tick_params(direction='in', labelleft=False)
      ax_histy.set_xlabel("#bins")

      y_bin_edges = np.linspace(np.amin(diff_pc), np.amax(diff_pc), 20)

      for row in range(len(dir_deltas)):
        y = diff_pc[:,row]
        color = colors[deltas_in_dir[row]]
        scatter = ax_scatter.scatter(x, y, edgecolors=color, marker=PHM.markers[row], label=r"${}$".format(deltas_in_dir[row]/reader["Delta"]), **common_sc_kwargs)

        ax_histx.hist(x, bins=bin_edges[d], weights=y**2, ec=color, **common_hist_kwargs)
        ax_histy.hist(y, bins=y_bin_edges, orientation='horizontal', ec=color, **common_hist_kwargs)

      ax_scatter.set_xlim((x_min, x_max))
      ax_histx.set_xlim(ax_scatter.get_xlim())
      ax_histy.set_ylim(ax_scatter.get_ylim())
      
      ax_scatter.legend(loc=leg_pos, title=legend_title, ncol=2)
      
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
  PHDF.set_default_mpl_format()

  input_dirs = [
    "/home/jakob/DESY/MountPoints/DUST/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_l/PrEWInput/MuAcc_costheta_0.9925/validation",
    "/home/jakob/DESY/MountPoints/DUST/TGCAnalysis/SampleProduction/NewMCProduction/4f_WW_sl/PrEWInput/validation"
  ]
  
  for input_dir in tqdm(input_dirs, desc="Input dir loop"):
    for file_path in tqdm(IOSH.find_files(input_dir, ".csv"), desc="File loop", leave=False):
      log.debug("Found file: {}".format(file_path))
      plot_deviation_test(file_path)
      
#-------------------------------------------------------------------------------

if __name__ == "__main__":
  main()