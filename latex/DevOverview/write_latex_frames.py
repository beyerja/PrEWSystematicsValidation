def main():
  """ Create a file with latex code that produce frames with all the plots 
      from the deviation tests.
  """

  # Deviation directions that were testest
  dev_dir_list = [
    "center_only",
    "lower_edge_only",
    "upper_edge_only",
    "width_only" ]
  
  # Difermion sub-categories that were tested
  difermion_list = [
    "2f_mu_180to275_250_eLpR_costh_f_star",
    "2f_mu_180to275_250_eRpL_costh_f_star",
    "2f_mu_81to101_250_eLpR_costh_f_star",
    "2f_mu_81to101_250_eRpL_costh_f_star" ]
  
  # WW sub-categories that were tested
  ww_list = [
    "WW_muminus_250_eLpR_costh_Wminus_star",
    "WW_muminus_250_eLpR_costh_l_star",
    "WW_muminus_250_eLpR_phi_l_star",
    "WW_muminus_250_eRpL_costh_Wminus_star",
    "WW_muminus_250_eRpL_costh_l_star",
    "WW_muminus_250_eRpL_phi_l_star",
    "WW_muplus_250_eLpR_costh_Wminus_star",
    "WW_muplus_250_eLpR_costh_l_star",
    "WW_muplus_250_eLpR_phi_l_star",
    "WW_muplus_250_eRpL_costh_Wminus_star",
    "WW_muplus_250_eRpL_costh_l_star",
    "WW_muplus_250_eRpL_phi_l_star" ]
    
  # Open a latex file and write the frames
  latex_file = open("Frames.tex", "w+")
  
  for difermion_base in difermion_list:
    for dev_dir in dev_dir_list:
      latex_file.write("\\begin{frame}\n")
      latex_file.write("\\includegraphics[width=\\thirdfraction\\textwidth]{{\\DifermionPath/CutEffect/{}_CutEffect.pdf}}\n".format(difermion_base))
      latex_file.write("\\includegraphics[width=\\thirdfraction\\textwidth]{{\\DifermionPath/DevCutCut0/{}_DevCutCut0_{}.pdf}}\n".format(difermion_base,dev_dir))
      latex_file.write("\\includegraphics[width=\\thirdfraction\\textwidth]{{\\DifermionPath/DevParCut/{}_DevParCut_{}.pdf}}\n".format(difermion_base,dev_dir))
      latex_file.write("\\end{frame}\n\n")
  
  for ww_base in ww_list:
    for dev_dir in dev_dir_list:
      latex_file.write("\\begin{frame}\n")
      latex_file.write("\\includegraphics[width=\\thirdfraction\\textwidth]{{\\WWPath/CutEffect/{}_CutEffect.pdf}}\n".format(ww_base))
      latex_file.write("\\includegraphics[width=\\thirdfraction\\textwidth]{{\\WWPath/DevCutCut0/{}_DevCutCut0_{}.pdf}}\n".format(ww_base,dev_dir))
      latex_file.write("\\includegraphics[width=\\thirdfraction\\textwidth]{{\\WWPath/DevParCut/{}_DevParCut_{}.pdf}}\n".format(ww_base,dev_dir))
      latex_file.write("\\end{frame}\n\n")
  
  latex_file.close()
  
#-------------------------------------------------------------------------------
  
if __name__ == "__main__":
  main()