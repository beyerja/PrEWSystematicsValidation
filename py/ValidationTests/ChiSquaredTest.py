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
  def __init__(self,name,func):
    self.name = name
    self.func = np.vectorize(func,signature='(n)->()')

# Library of most relevant deviation directions 
# -> use lambda functions of delta = [delta-c, delta-w] to describe direction
dev_directions = (
  DevDirection("center", lambda deltas: deltas[1] == 0),
  DevDirection("width", lambda deltas: deltas[0] == 0),
  DevDirection("upper edge", lambda deltas: deltas[0] - deltas[1]/2.0 == 0),
  DevDirection("lower edge", lambda deltas: deltas[0] + deltas[1]/2.0 == 0),
  DevDirection("combinations", 
    lambda deltas: not ((deltas[1] == 0) or 
                        (deltas[0] == 0) or 
                        (deltas[0] - deltas[1]/2.0 == 0) or 
                        (deltas[0] + deltas[1]/2.0 == 0)))
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
          # Their contribution to each chi^2 is zero anyway
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
  fig = plt.figure(figsize=(7.5, 6), tight_layout=True)
  
  ax_scatter = plt.gca()
  title = "{}, ${}$ab$^{{-1}}$".format(VTN.metadata_to_process(reader),VMCC.TestLumi/1000)
  ax_scatter.set_title(title)
  ax_scatter.set_xlabel(r"$\chi_{shift}^{2} = \sum_{bins} \left(\frac{N_{cut}^{(\Delta c, \Delta w)} - N_{cut}^{0}}{\sqrt{N_{cut}^{0}}}\right)^2$")
  ax_scatter.set_ylabel(r"$\chi_{par}^{2} = \sum_{bins} \left(\frac{N_{par}^{(\Delta c, \Delta w)} - N_{cut}^{(\Delta c, \Delta w)}}{\sqrt{N_{cut}^{(\Delta c, \Delta w)}}}\right)^2$")
  
  # Set logarithmic axes 
  x_min = min([min(c) for c in chi_sq_c0])
  x_max = max([max(c) for c in chi_sq_c0])
  y_min = min([min(c) for c in chi_sq_pc])
  y_max = max([max(c) for c in chi_sq_pc])
  edge_min = 0.5 * y_min
  edge_max = 1.5 * max(x_max,y_max)
  log_edge_min = np.log10(edge_min)
  log_edge_max = np.log10(edge_max)
  edges = np.logspace(log_edge_min, log_edge_max, 16)
  ax_scatter.set_yscale('log')
  ax_scatter.set_xscale('log')
  ax_scatter.set_ylim(edge_min,edge_max)
  ax_scatter.set_xlim(edge_min,edge_max)

  # Draw diagonal axis line, everything below that line is fine
  ax_scatter.fill_between(edges,edges,edge_max*np.ones(16),color='red',alpha=0.5)
  ax_scatter.axline((edge_min, edge_min), (edge_max, edge_max), ls='--', color='black')

  colors =  plt.rcParams['axes.prop_cycle'].by_key()['color']

  for i_dir in range(len(dev_directions)):
    scatter = ax_scatter.scatter(chi_sq_c0[i_dir], chi_sq_pc[i_dir], 
                color='none', ec=colors[i_dir], lw=2, s=10**2, 
                marker=PHM.markers[i_dir], label=dev_directions[i_dir].name)

  legend_title = r"$\cos\theta_{{\mu}}^{{cut}}={}$,".format(reader["Coef|MuonAcc_CutValue"]) + "\n" + r"$\sqrt{{\Delta c^2 + \Delta w^2}} \leq {}\delta$".format(d_max/reader["Delta"])
  ax_scatter.legend(title=legend_title, loc="upper left")
  
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
  PHDF.set_default_mpl_format()

  input_dirs = [
    "/home/jakob/DESY/MountPoints/DUST/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_l/PrEWInput/MuAcc_costheta_0.9925/validation",
    "/home/jakob/DESY/MountPoints/DUST/TGCAnalysis/SampleProduction/NewMCProduction/4f_WW_sl/PrEWInput/validation"
  ]
  
  # Set a useful font size
  plt.rcParams.update({'font.size': 17})
  
  for input_dir in tqdm(input_dirs, desc="Input dirs"):
    for file_path in tqdm(IOSH.find_files(input_dir, ".csv"), desc="Files", leave=False):
      log.debug("Found file: {}".format(file_path))
      plot_chi_squared_test(file_path)
      
#-------------------------------------------------------------------------------

if __name__ == "__main__":
  main()