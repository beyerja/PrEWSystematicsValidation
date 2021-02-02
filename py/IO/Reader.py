import logging as log
import pandas as pd

# Local modules
import CSVMetadataReader as CMR

# ------------------------------------------------------------------------------

class Reader:
  """ Class to read / interpret a validation data file.
  """
  
  # --- Constructor ------------------------------------------------------------
  
  def __init__(self,file_path):
    self.data = {}
    self.interpret(file_path)
    
  # --- Access functions -------------------------------------------------------
    
  def __getitem__(self,index):
    """ Define what happens when the [] operator is applied (only reading).
    """
    return self.data[index]
    
  # --- Internal functions -----------------------------------------------------
    
  def interpret(self,file_path):
    """ Read and interpret the input file.
    """
    # Find and use the metadata
    mr = CMR.CSVMetadataReader(file_path)
    self.data = mr.metadata
    
    # Find the distribution data
    self.data["Data"] = pd.read_csv(file_path, header=mr.get_data_header_line())
    
# ------------------------------------------------------------------------------

def test():
  """ Test the reader.
  """
  log.basicConfig(level=log.DEBUG) # Set logging level
  test_file = "/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/NewMCProduction/2f_Z_l/PrEWInput/validation/2f_mu_180to275_250_eLpR_valdata.csv"
  reader = Reader(test_file)
  log.debug(reader.data)

if __name__ == "__main__":
  """ If this script is called directly perform the test function.
  """
  test()

# ------------------------------------------------------------------------------
