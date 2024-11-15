import numpy as np
from astropy.io import fits
from astropy.table import Table
import matplotlib.pyplot as plt
import argparse
import os
import sys

SPLIT_STRING = 'Final_products'

class Wavelength():
  prism_clear = np.array([6.0255e-07, 6.05154e-07, 6.0777e-07, 6.10441e-07, 6.13123e-07, 6.15862e-07, 6.18612e-07, 6.2142e-07, 6.24241e-07, 6.27119e-07, 6.30011e-07, 6.32962e-07, 6.35927e-07, 6.38951e-07, 6.41991e-07, 6.45091e-07, 6.48206e-07, 6.51383e-07, 6.54623e-07, 6.57879e-07, 6.61199e-07, 6.64535e-07, 6.67937e-07, 6.71404e-07, 6.74889e-07, 6.78441e-07, 6.82012e-07, 6.85651e-07, 6.89358e-07, 6.93085e-07, 6.96882e-07, 7.0075e-07, 7.04639e-07, 7.086e-07, 7.12634e-07, 7.1674e-07, 7.20871e-07, 7.25076e-07, 7.29356e-07, 7.33713e-07, 7.38095e-07, 7.42555e-07, 7.47093e-07, 7.5171e-07, 7.56406e-07, 7.61184e-07, 7.65991e-07, 7.7088e-07, 7.75852e-07, 7.80907e-07, 7.86047e-07, 7.91271e-07, 7.96581e-07, 8.01978e-07, 8.07462e-07, 8.13034e-07, 8.18695e-07, 8.24445e-07, 8.30286e-07, 8.36218e-07, 8.42242e-07, 8.48359e-07, 8.54569e-07, 8.60872e-07, 8.67319e-07, 8.73861e-07, 8.80499e-07, 8.87234e-07, 8.94066e-07, 9.01042e-07, 9.08116e-07, 9.1529e-07, 9.22606e-07, 9.30023e-07, 9.37541e-07, 9.452e-07, 9.52962e-07, 9.60826e-07, 9.6883e-07, 9.76937e-07, 9.85183e-07, 9.93533e-07, 1.00202e-06, 1.01061e-06, 1.01933e-06, 1.02816e-06, 1.03713e-06, 1.04622e-06, 1.05541e-06, 1.06474e-06, 1.07419e-06, 1.08374e-06, 1.09341e-06, 1.1032e-06, 1.11311e-06, 1.12313e-06, 1.13325e-06, 1.14349e-06, 1.15383e-06, 1.16428e-06, 1.17484e-06, 1.18549e-06, 1.19624e-06, 1.20708e-06, 1.21801e-06, 1.22903e-06, 1.24014e-06, 1.25132e-06, 1.26259e-06, 1.27393e-06, 1.28535e-06, 1.29684e-06, 1.30839e-06, 1.32001e-06, 1.33169e-06, 1.34342e-06, 1.35522e-06, 1.36706e-06, 1.37893e-06, 1.39085e-06, 1.40281e-06, 1.41481e-06, 1.42685e-06, 1.43889e-06, 1.45096e-06, 1.46306e-06, 1.47519e-06, 1.48734e-06, 1.49948e-06, 1.51163e-06, 1.52381e-06, 1.53599e-06, 1.54819e-06, 1.56036e-06, 1.57254e-06, 1.58472e-06, 1.5969e-06, 1.60909e-06, 1.62123e-06, 1.63337e-06, 1.64551e-06, 1.65764e-06, 1.66976e-06, 1.68183e-06, 1.69389e-06, 1.70594e-06, 1.71797e-06, 1.72999e-06, 1.74194e-06, 1.75388e-06, 1.7658e-06, 1.7777e-06, 1.78958e-06, 1.80144e-06, 1.81322e-06, 1.82498e-06, 1.83672e-06, 1.84843e-06, 1.86012e-06, 1.87177e-06, 1.8834e-06, 1.89496e-06, 1.90648e-06, 1.91797e-06, 1.92943e-06, 1.94086e-06, 1.95226e-06, 1.96362e-06, 1.97495e-06, 1.98625e-06, 1.99751e-06, 2.00874e-06, 2.01994e-06, 2.03109e-06, 2.04222e-06, 2.0533e-06, 2.06435e-06, 2.07536e-06, 2.08634e-06, 2.09728e-06, 2.10818e-06, 2.11904e-06, 2.12986e-06, 2.14065e-06, 2.15139e-06, 2.1621e-06, 2.17276e-06, 2.18339e-06, 2.19398e-06, 2.20453e-06, 2.21504e-06, 2.2255e-06, 2.23593e-06, 2.24632e-06, 2.25667e-06, 2.26702e-06, 2.27733e-06, 2.28759e-06, 2.29782e-06, 2.30801e-06, 2.31816e-06, 2.32826e-06, 2.33837e-06, 2.34844e-06, 2.35846e-06, 2.36845e-06, 2.37839e-06, 2.38829e-06, 2.39819e-06, 2.40805e-06, 2.41787e-06, 2.42765e-06, 2.43743e-06, 2.44717e-06, 2.45686e-06, 2.46652e-06, 2.47613e-06, 2.48574e-06, 2.49531e-06, 2.50484e-06, 2.51433e-06, 2.52382e-06, 2.53327e-06, 2.54267e-06, 2.55208e-06, 2.56144e-06, 2.57076e-06, 2.58004e-06, 2.58932e-06, 2.59856e-06, 2.60776e-06, 2.61695e-06, 2.6261e-06, 2.63522e-06, 2.64433e-06, 2.6534e-06, 2.66243e-06, 2.67145e-06, 2.68044e-06, 2.68942e-06, 2.69836e-06, 2.70727e-06, 2.71616e-06, 2.72502e-06, 2.73384e-06, 2.74266e-06, 2.75143e-06, 2.7602e-06, 2.76893e-06, 2.77763e-06, 2.78631e-06, 2.79496e-06, 2.8036e-06, 2.81221e-06, 2.82081e-06, 2.82937e-06, 2.83789e-06, 2.84641e-06, 2.85489e-06, 2.86336e-06, 2.87179e-06, 2.88022e-06, 2.88861e-06, 2.897e-06, 2.90534e-06, 2.91369e-06, 2.92199e-06, 2.93029e-06, 2.93855e-06, 2.9468e-06, 2.95502e-06, 2.96323e-06, 2.9714e-06, 2.97957e-06, 2.9877e-06, 2.99582e-06, 3.00391e-06, 3.01199e-06, 3.02004e-06, 3.02807e-06, 3.03607e-06, 3.04407e-06, 3.05203e-06, 3.05998e-06, 3.06793e-06, 3.07584e-06, 3.08374e-06, 3.0916e-06, 3.09946e-06, 3.10729e-06, 3.11511e-06, 3.12292e-06, 3.13069e-06, 3.13846e-06, 3.14619e-06, 3.15392e-06, 3.16161e-06, 3.1693e-06, 3.17697e-06, 3.18462e-06, 3.19225e-06, 3.19985e-06, 3.20745e-06, 3.21503e-06, 3.22259e-06, 3.23013e-06, 3.23767e-06, 3.24517e-06, 3.25267e-06, 3.26016e-06, 3.26761e-06, 3.27506e-06, 3.28248e-06, 3.28988e-06, 3.29728e-06, 3.30465e-06, 3.31201e-06, 3.31936e-06, 3.32668e-06, 3.33399e-06, 3.34129e-06, 3.34856e-06, 3.35583e-06, 3.36308e-06, 3.37031e-06, 3.37752e-06, 3.38473e-06, 3.39193e-06, 3.3991e-06, 3.40626e-06, 3.41341e-06, 3.42053e-06, 3.42765e-06, 3.43475e-06, 3.44182e-06, 3.44889e-06, 3.45595e-06, 3.463e-06, 3.47002e-06, 3.47703e-06, 3.48404e-06, 3.49101e-06, 3.49797e-06, 3.50493e-06, 3.51188e-06, 3.5188e-06, 3.52571e-06, 3.53261e-06, 3.53951e-06, 3.54637e-06, 3.55323e-06, 3.56008e-06, 3.56692e-06, 3.57373e-06, 3.58054e-06, 3.58733e-06, 3.59412e-06, 3.60088e-06, 3.60763e-06, 3.61437e-06, 3.62111e-06, 3.62783e-06, 3.63453e-06, 3.64122e-06, 3.6479e-06, 3.65458e-06, 3.66122e-06, 3.66786e-06, 3.67449e-06, 3.68111e-06, 3.68772e-06, 3.69431e-06, 3.70088e-06, 3.70745e-06, 3.71401e-06, 3.72056e-06, 3.72709e-06, 3.7336e-06, 3.74011e-06, 3.74661e-06, 3.75311e-06, 3.75959e-06, 3.76605e-06, 3.7725e-06, 3.77894e-06, 3.78537e-06, 3.7918e-06, 3.7982e-06, 3.80459e-06, 3.81097e-06, 3.81734e-06, 3.82371e-06, 3.83007e-06, 3.83642e-06, 3.84274e-06, 3.84906e-06, 3.85537e-06, 3.86167e-06, 3.86796e-06, 3.87424e-06, 3.88052e-06, 3.88677e-06, 3.89301e-06, 3.89924e-06, 3.90547e-06, 3.91169e-06, 3.9179e-06, 3.9241e-06, 3.93028e-06, 3.93645e-06, 3.94261e-06, 3.94876e-06, 3.9549e-06, 3.96104e-06, 3.96717e-06, 3.97329e-06, 3.97939e-06, 3.98548e-06, 3.99156e-06, 3.99763e-06, 4.00369e-06, 4.00975e-06, 4.0158e-06, 4.02184e-06, 4.02788e-06, 4.0339e-06, 4.0399e-06, 4.0459e-06, 4.05188e-06, 4.05786e-06, 4.06383e-06, 4.06979e-06, 4.07575e-06, 4.08169e-06, 4.08763e-06, 4.09356e-06, 4.09949e-06, 4.1054e-06, 4.11129e-06, 4.11718e-06, 4.12306e-06, 4.12892e-06, 4.13479e-06, 4.14064e-06, 4.14648e-06, 4.15232e-06, 4.15815e-06, 4.16397e-06, 4.16979e-06, 4.1756e-06, 4.1814e-06, 4.18719e-06, 4.19297e-06, 4.19875e-06, 4.20452e-06, 4.21027e-06, 4.216e-06, 4.22173e-06, 4.22746e-06, 4.23317e-06, 4.23888e-06, 4.24458e-06, 4.25028e-06, 4.25596e-06, 4.26164e-06, 4.26731e-06, 4.27297e-06, 4.27863e-06, 4.28428e-06, 4.28992e-06, 4.29555e-06, 4.30117e-06, 4.30679e-06, 4.3124e-06, 4.31801e-06, 4.3236e-06, 4.32919e-06, 4.33477e-06, 4.34034e-06, 4.34591e-06, 4.35147e-06, 4.35702e-06, 4.36256e-06, 4.3681e-06, 4.37363e-06, 4.37915e-06, 4.38466e-06, 4.39017e-06, 4.39567e-06, 4.40116e-06, 4.40665e-06, 4.41212e-06, 4.41759e-06, 4.42305e-06, 4.42851e-06, 4.43396e-06, 4.4394e-06, 4.44483e-06, 4.45026e-06, 4.45568e-06, 4.46109e-06, 4.46649e-06, 4.47189e-06, 4.47728e-06, 4.48266e-06, 4.48804e-06, 4.49341e-06, 4.49877e-06, 4.50412e-06, 4.50947e-06, 4.51481e-06, 4.52014e-06, 4.52546e-06, 4.53078e-06, 4.53609e-06, 4.54139e-06, 4.54669e-06, 4.55198e-06, 4.55726e-06, 4.56254e-06, 4.5678e-06, 4.57306e-06, 4.57832e-06, 4.58356e-06, 4.58882e-06, 4.59406e-06, 4.5993e-06, 4.60453e-06, 4.60976e-06, 4.61497e-06, 4.62018e-06, 4.62539e-06, 4.63058e-06, 4.63577e-06, 4.64095e-06, 4.64613e-06, 4.6513e-06, 4.65646e-06, 4.66161e-06, 4.66676e-06, 4.6719e-06, 4.67703e-06, 4.68217e-06, 4.6873e-06, 4.69243e-06, 4.69755e-06, 4.70266e-06, 4.70776e-06, 4.71286e-06, 4.71795e-06, 4.72303e-06, 4.72811e-06, 4.73318e-06, 4.73824e-06, 4.7433e-06, 4.74835e-06, 4.7534e-06, 4.75845e-06, 4.76349e-06, 4.76852e-06, 4.77355e-06, 4.77857e-06, 4.78358e-06, 4.78859e-06, 4.79359e-06, 4.79858e-06, 4.80357e-06, 4.80856e-06, 4.81355e-06, 4.81852e-06, 4.82349e-06, 4.82846e-06, 4.83342e-06, 4.83837e-06, 4.84331e-06, 4.84825e-06, 4.85318e-06, 4.85812e-06, 4.86305e-06, 4.86797e-06, 4.87288e-06, 4.87779e-06, 4.8827e-06, 4.88759e-06, 4.89248e-06, 4.89736e-06, 4.90224e-06, 4.90712e-06, 4.912e-06, 4.91686e-06, 4.92172e-06, 4.92658e-06, 4.93143e-06, 4.93627e-06, 4.9411e-06, 4.94594e-06, 4.95077e-06, 4.9556e-06, 4.96042e-06, 4.96523e-06, 4.97004e-06, 4.97484e-06, 4.97963e-06, 4.98443e-06, 4.98922e-06, 4.99401e-06, 4.99879e-06, 5.00356e-06, 5.00832e-06, 5.01308e-06, 5.01784e-06, 5.02259e-06, 5.02734e-06, 5.03209e-06, 5.03683e-06, 5.04156e-06, 5.04628e-06, 5.051e-06, 5.05573e-06, 5.06044e-06, 5.06515e-06, 5.06986e-06, 5.07455e-06, 5.07924e-06, 5.08393e-06, 5.08862e-06, 5.0933e-06, 5.09798e-06, 5.10265e-06, 5.10731e-06, 5.11197e-06, 5.11662e-06, 5.12127e-06, 5.12592e-06, 5.13056e-06, 5.1352e-06, 5.13983e-06, 5.14445e-06, 5.14908e-06, 5.1537e-06, 5.15832e-06, 5.16293e-06, 5.16753e-06, 5.17213e-06, 5.17673e-06, 5.18132e-06, 5.18591e-06, 5.19049e-06, 5.19507e-06, 5.19964e-06, 5.20421e-06, 5.20878e-06, 5.21334e-06, 5.21789e-06, 5.22244e-06, 5.22698e-06, 5.23153e-06, 5.23607e-06, 5.2406e-06, 5.24513e-06, 5.24965e-06, 5.25417e-06, 5.25869e-06, 5.2632e-06, 5.26771e-06, 5.27221e-06, 5.2767e-06, 5.2812e-06, 5.2857e-06, 5.29018e-06, 5.29466e-06, 5.29914e-06, 5.30361e-06, 5.30808e-06])

parser = argparse.ArgumentParser()

parser.add_argument(
    '-s', '--spectrum-folder',
    help="folder containing 1D spectra",
    action="store",
    type=str,
    dest="spectrumFolder",
    required=True
)

parser.add_argument(
    '-scaling', '--scaling',
    help="text file containing noise scaling factor",
    action="store",
    type=str,
    default=None,
    dest="scalingFactor"
)

args = parser.parse_args()

args.spectrumFolder = os.path.abspath(args.spectrumFolder)
outputFolder = os.path.join(args.spectrumFolder, 'beagle_format')

#Make the output directory if it doesn't exist yet
if not os.path.exists(outputFolder):
  os.mkdir(outputFolder)
  
spectraList = os.listdir(args.spectrumFolder)

# If a redshift catalogue exists, use it to create the lists of objects with spec_z and photo_z
redshift_folder = os.path.join(args.spectrumFolder.split(SPLIT_STRING)[0], 'redshifts')
if os.path.exists(redshift_folder):
  for filename in os.listdir(redshift_folder):
    if filename.endswith('.fits'):
      # Open the FITS file
      with fits.open(os.path.join(redshift_folder, filename)) as hdul:
        # Assuming the data you want is in the first extension
        data = Table(hdul[1].data)
        if 'sample' in data.colnames:
          spec_z_IDs = [str(id) + '.fits' for id in data[data['sample'] == 'spec_z']['ID']]
          spec_phot_z_IDs = [str(id) + '.fits' for id in data[data['sample'] != '']['ID']]

          # Define the filename for the output file
          output_filename = 'spectra_spec_z.list'

          # Open the file in write mode ('w')
          with open(os.path.join(outputFolder, output_filename), 'w') as file:
            for id in spec_z_IDs:
              file.write(id + '\n')  # Write each ID on a new line

          # Define the filename for the output file
          output_filename = 'spectra_spec_phot_z.list'

          # Open the file in write mode ('w')
          with open(os.path.join(outputFolder, output_filename), 'w') as file:
            for id in spec_phot_z_IDs:
              file.write(id + '\n')  # Write each ID on a new line


if args.scalingFactor is not None:
  scaling = np.genfromtxt(args.scalingFactor, dtype=None, names=True)
else:
  scaling = None

grating_filter = os.path.basename(os.path.normpath(args.spectrumFolder))

for file in spectraList:
  if file.endswith('1D.fits'):
    outputFile = file.split('_' + grating_filter)[0] + ".fits"
    outputFile = os.path.join(outputFolder, outputFile)
    if os.path.isfile(outputFile):
      continue
    spectra = fits.open(os.path.join(args.spectrumFolder, file))
    hdr = fits.Header()
    #If you want to add the redshift to the header, do it here
    empty_primary = fits.PrimaryHDU(header=hdr)
    spec = spectra['DATA'].data
    if scaling is not None:
      #check length of scaling array and error array
      if len(spectra['ERR'].data) != len(scaling['scaling_factor']):
        print("check length of scaling factor array")
        sys.exit()
      print("applying scaling factor")
      err = spectra['ERR'].data/scaling['scaling_factor']
  #    plt.figure()
  #    plt.plot(np.sqrt(spectra['VAR'].data[i,:]))
  #    plt.plot(np.sqrt(spectra['VAR'].data[i,:])/scaling['scaling_factor'])
  #    plt.savefig("test.pdf")
  #    sys.exit()
    else:
      err = spectra['ERR'].data #Careful - the factor
    #     of 1.4 is suggested by Stefano to account for STD being too high
    maskIdx = np.where(np.isfinite(spec) == False)[0]
    spec[maskIdx] = 0
    err[maskIdx] = 0
    if 'WAVELENGTH' in spectra:
      wl = spectra['WAVELENGTH'].data
    else:
      wl = getattr(Wavelength, grating_filter, None)
    if wl is None:
      raise ValueError('Cannot determine the wavelength of the spectrum')
    col1 = fits.Column(name="wl", format='D', array=wl*1E10)
    col2 = fits.Column(name="flux", format='D', array=spec*1E-7)
    col3 = fits.Column(name="err", format='D', array=err*1E-7)
    mask = np.zeros_like(spec) + 1
    mask[maskIdx] = False
    col4 = fits.Column(name="mask", format='L', array=mask)
    cols = fits.ColDefs([col1,col2,col3,col4])
    hdu = fits.BinTableHDU.from_columns(cols)
    hdul = fits.HDUList([empty_primary,hdu])
    hdul.writeto(outputFile, overwrite=True)