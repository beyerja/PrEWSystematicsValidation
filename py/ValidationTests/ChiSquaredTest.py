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
import DeltaHelp as VMDH

#-------------------------------------------------------------------------------

class DevDirection:
  """ Class defines one deviation direction.
  """
  def __init__(self,name,func):
    self.name = name
    self.func = np.vectorize(func,signature='(n)->()')

# Library of most relevant deviation directions 
# -> use lambda functions of delta = [delta-c, delta-w] to describe direction
dev_directions = (
  DevDirection("all points", lambda deltas: True),
  DevDirection("center only", lambda deltas: deltas[1] == 0),
  DevDirection("width only", lambda deltas: deltas[0] == 0),
  DevDirection("upper edge only", lambda deltas: deltas[0] - deltas[1]/2.0 == 0),
  DevDirection("lower edge only", lambda deltas: deltas[0] + deltas[1]/2.0 == 0)
)

#-------------------------------------------------------------------------------

def plot_chi_squared_test(file_path, output_formats=["pdf"]):
  # TODO TODO TODO DESCRIPTION
  
  # Read the input file
  log.debug("Reading file: {}".format(file_path))
  reader = IOR.Reader(file_path)
  
  # Output info
  output_dir = "{}/plots".format(os.path.dirname(file_path))
  base_name = os.path.basename(file_path).replace("_valdata.csv","")
  log.debug("Output will be written to: {}".format(output_dir))
  
  # Get the pandas dataframe for the cut histograms
  df = reader["Data"]
  n_bins = len(reader["BinCenters"])
  
  row_cut0 = df[(df["Delta-c"] == 0) & (df["Delta-w"] == 0)]
  N_cut_cut0 = np.array([row_cut0["C{}".format(b)].values[0] for b in range(n_bins)])
  
  # Get scale factor to normalise distribution to the (roughly) number of events
  # expected during the fit
  scale_factor = VMCC.TestLumi * reader["CrossSection"] / reader["NTotalMC"]
  N_cut_cut0 *= scale_factor
  
  # Find the deltas 
  deltas = IOPH.delta_pairs(df)
  delta_metrics = VMDH.delta_metric(deltas)
  
  # Maximum sqrt(dc**2 + dw**2) that should be included in chi-squared calc.
  # -> Don't use outermost test values, not bad if not exact fit there
  d_max = 2.0 * reader["Delta"]
  
  # Chi squared arrays for each dev dir
  chi_sq_pc = []
  chi_sq_c0 = []
  
  for dev_dir in dev_directions:
    log.debug("Looking at direction {}".format(dev_dir.name))
    
    # Get the rows for this direction which fulfill the d_max criterium
    dir_selection = dev_dir.func(deltas)
    d_max_selection = delta_metrics <= d_max
    selection = np.logical_and(dir_selection,d_max_selection)
    dir_rows = df[selection]
    dir_deltas = deltas[selection]
    n_dev_points = len(dir_deltas)
    
    N_cut = np.array([dir_rows["C{}".format(b)] for b in range(n_bins)]) * scale_factor
    N_par = np.array([dir_rows["P{}".format(b)] for b in range(n_bins)]) * scale_factor
    
    diff_pc_sq = (N_par - N_cut)**2
    diff_c0_sq = ((N_cut.transpose() - N_cut_cut0)**2).transpose()
    
    dir_chi_sq_pc = []
    dir_chi_sq_c0 = []
    
    # Calculate the chi-squared for each bin
    for d in range(n_dev_points):
      dev_chi_sq_pc = 0
      dev_chi_sq_c0 = 0
      diff_pc_sq_d = diff_pc_sq[:,d]
      diff_c0_sq_d = diff_c0_sq[:,d]
      N_cut_d = N_cut[:,d]
      
      for b in range(n_bins):
        if not N_cut_d[b] > 0:
          if abs(diff_pc_sq_d[b]) > 0:
            log.warning("Bin {} at deviation ({}) has 0 for cut and non-0 for parametrisation".format(b,dir_deltas[d]))
        elif np.all(N_cut[b] == N_cut_cut0[b]):
          # Skip bins that aren't affected by the cut
          continue
        else:
          dev_chi_sq_pc += diff_pc_sq_d[b] / N_cut_d[b]
          dev_chi_sq_c0 += diff_c0_sq_d[b] / N_cut_cut0[b]
    
      dir_chi_sq_pc.append(dev_chi_sq_pc)
      dir_chi_sq_c0.append(dev_chi_sq_c0)
      
    chi_sq_pc.append(dir_chi_sq_pc)
    chi_sq_c0.append(dir_chi_sq_c0)
    

  # --- Plotting ---------------------------------------------------------------

  # start with a rectangular Figure
  fig = plt.figure(figsize=(6, 6))
  title = "{} : {}{} @ {}fb$^{{-1}}$".format(reader["Name"],VTN.eM_chirality(reader["e-Chirality"]),VTN.eP_chirality(reader["e+Chirality"]),VMCC.TestLumi)
  fig.suptitle(title)#, fontsize=16)
  
  # definitions for the axes
  left, width = 0.18, 0.49
  bottom, height = 0.1, 0.49
  spacing = 0.005
  rect_scatter = [left, bottom, width, height]
  rect_histx = [left, bottom + height + spacing, width, 0.93 - (bottom + height + spacing)]
  rect_histy = [left + width + spacing, bottom, 0.93 - (left + width + spacing), height]
  leg_pos = [(width + spacing)/width, (height + spacing)/height]
  
  ax_scatter = plt.axes(rect_scatter)
  ax_scatter.tick_params(direction='in', top=True, right=True)
  ax_scatter.set_xlabel(r"$\chi_{shift}^{2} = \sum_{affected\, bins} (\frac{N_{cut}^{(\Delta c, \Delta w)} - N_{cut}^{0}}{\sqrt{N_{cut}^{0}}})^2$")
  ax_scatter.set_ylabel(r"$\chi_{par}^{2} = \sum_{affected\, bins} (\frac{N_{par}^{(\Delta c, \Delta w)} - N_{cut}^{(\Delta c, \Delta w)}}{\sqrt{N_{cut}^{(\Delta c, \Delta w)}}})^2$")
  ax_histx = plt.axes(rect_histx)
  ax_histx.tick_params(direction='in', labelbottom=False)
  ax_histx.set_ylabel("# $(\Delta c, \Delta w)$ points")
  ax_histy = plt.axes(rect_histy)
  ax_histy.tick_params(direction='in', labelleft=False)
  ax_histy.set_xlabel("# $(\Delta c, \Delta w)$ points")

  x_min = min([min(c) for c in chi_sq_c0])
  x_max = max([max(c) for c in chi_sq_c0])
  y_min = min([min(c) for c in chi_sq_pc])
  y_max = max([max(c) for c in chi_sq_pc])
  x_bin_edges = np.linspace(x_min, x_max, 21)
  y_bin_edges = np.linspace(y_min, y_max, 21)

  colors = PHC.ColorMap("nipy_spectral",len(dev_directions)+1)

  for i_dir in range(len(dev_directions)):
    x = chi_sq_c0[i_dir]
    y = chi_sq_pc[i_dir]
    color = colors[i_dir]
    scatter = ax_scatter.scatter(x, y, color='none', edgecolors=color, marker=PHM.markers[i_dir], label=dev_directions[i_dir].name)

    ax_histx.hist(x, bins=x_bin_edges, histtype='step',fill=False, ec=color)
    ax_histy.hist(y, bins=y_bin_edges, orientation='horizontal', histtype='step',fill=False, ec=color)

  ax_scatter.set_xlim(0,ax_scatter.get_xlim()[1])
  ax_scatter.set_ylim(0,ax_scatter.get_ylim()[1])
  ax_histx.set_xlim(ax_scatter.get_xlim())
  ax_histy.set_ylim(ax_scatter.get_ylim())
  
  legend_title = r"$\cos\theta_{{\mu}}^{{cut}}={}$,".format(reader["Coef|MuonAcc_CutValue"]) + "\n" + r"$\sqrt{{\Delta c^2 + \Delta w^2}} \leq {}\delta$".format(d_max/reader["Delta"])
  ax_scatter.legend(loc=leg_pos, title=legend_title)
  
  # Save the figure in all requested formats
  for format in output_formats:
    format_dir = "{}/{}/ChiSquared".format(output_dir,format)
    IOSH.create_dir(format_dir)
    fig.savefig("{}/{}_ChiSquared.{}".format(format_dir, base_name, format))
  
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
      plot_chi_squared_test(file_path)
      
#-------------------------------------------------------------------------------

if __name__ == "__main__":
  main()