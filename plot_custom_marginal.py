from astropy.io import fits
import os
from pyp_beagle.beagle_utils import prepare_violin_plot 
from matplotlib import pyplot as plt
from matplotlib.colors import colorConverter
from matplotlib.patches import Rectangle


import numpy as np
from getdist import plots, MCSamples

plt.rcParams['text.usetex'] = True

def main():

    results_folder = "/Users/jchevall/JWST/JADES/results/GS_3215/prism_clear_v3.1_base_mup300_variable_CO"
    results_file = "20096216_masked_JC_BEAGLE.fits.gz"

    fits_file = os.path.join(results_folder, results_file)

    hdulist = fits.open(fits_file)

    # Read the posterior probability
    probability = hdulist['posterior pdf'].data['probability']

    CIIId_flux = hdulist['HII emission'].data['C3_1907_flux'] + hdulist['HII emission'].data['C3_1910_flux']

    OIId_flux = hdulist['HII emission'].data['O2_3726_flux'] + hdulist['HII emission'].data['O2_3729_flux']

    NeIII_flux = hdulist['HII emission'].data['Ne3_3869_flux']

    CIVd_flux = hdulist['HII emission'].data['C4_1548_flux'] + hdulist['HII emission'].data['C4_1551_flux']

    OIIIUVd_flux = hdulist['HII emission'].data['O3_1661_flux'] + hdulist['HII emission'].data['O3_1666_flux']

    OIIId_flux = hdulist['HII emission'].data['O3_4959_flux'] + hdulist['HII emission'].data['O3_5007_flux']

    ratio = CIIId_flux / (OIId_flux+NeIII_flux)

    CIV_CIII_ratio = CIVd_flux / CIIId_flux

    OIII_CIII_ratio = OIIId_flux / CIIId_flux

    OIIIUV_CIII_ratio = OIIIUVd_flux / CIIId_flux

    print(np.sum(probability*OIII_CIII_ratio)/np.sum(probability))
    print(OIII_CIII_ratio[np.argmax(probability)])
    print(OIII_CIII_ratio[OIII_CIII_ratio < 0.])

    for r in [ratio, CIV_CIII_ratio, OIII_CIII_ratio, OIIIUV_CIII_ratio]:
        print()
        sort = np.argsort(r)
        cumulative_probability = np.cumsum(probability[sort])/np.sum(probability)
        low = np.interp(0.16, cumulative_probability, r[sort])
        high = np.interp(0.84, cumulative_probability, r[sort])
        print(low, high)
        low = np.interp(0.025, cumulative_probability, r[sort])
        high = np.interp(0.975, cumulative_probability, r[sort])
        print(low, high)

    kde_pdf, pdf_norm, median_flux, x_plot, y_plot = prepare_violin_plot(ratio, weights=probability) 

    fig = plt.figure(figsize=(12, 3))
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(x_plot, y_plot)

    fig.savefig("test.pdf")

    n_rows = len(probability)
    params_to_plot = [
        {"col":"tauV_eff", "label":"$\\hat{\\tau}_V$"},
        #{"col":"max_stellar_age"},
        {"ext":"HII emission", "col":"logU", "label": "$\\log(\\textnormal{U})$"},
        {"col":"nebular_xi", "label":"$\\xi_d$"},
        {"ext":"HII emission", "col":"logOH", "label": "$12+\\log(\\textnormal{O}/\\textnormal{H})$"}, 
        #{"col":"nebular_CO", "label":"$(\\textnormal{C}/\\textnormal{O})/(\\textnormal{C}/\\textnormal{O})_\\odot$"}
        {"col":"nebular_CO", "label":"$[\\textnormal{C}/\\textnormal{O}]$", "log" : True}
        ]
    
    nParamsToPlot = len(params_to_plot) + 1
    samps = np.zeros((n_rows, nParamsToPlot))
    names = list() ; labels = list()
    for j, param in enumerate(params_to_plot):
        ext = param["ext"] if "ext" in param else "POSTERIOR PDF"
        col = param["col"] if "col" in param else param
        samps[:,j] = np.log10(hdulist[ext].data[col]) if "log" in param and param["log"] else hdulist[ext].data[col]
        names.append(col)
        label = param['label']
        labels.append(label)

    #samps[:, -4] = OIIIUV_CIII_ratio
    #names.append("OIII]uv/CIII]")
    #names.append("(OIII]1661+OIII]1666)/(CIII]1907+CIII]1909)")

    samps[:, -1] = ratio
    #names.append("(CIII]1907+CIII]1909)/([OII]+[NeIII])")
    names.append("CIII]/([OII]+[NeIII])")
    labels.append("$\\textnormal{C}\\,\\textsc{iii]}/([\\textnormal{O}\\,\\textsc{ii}]+[\\textnormal{Ne}\,\\textsc{iii}])$")

    #samps[:, -2] = CIV_CIII_ratio
    #names.append("CIV/(CIII]1907+CIII]1909)")
    #names.append("CIV/CIII]")

    #samps[:, -1] = OIII_CIII_ratio
    #names.append("([OIII]4959+[OIII]5007)/(CIII]1907+CIII]1909)")
    #names.append("[OIII]opt/CIII]")

    settings = {
        "contours":[0.68, 0.95, 0.99], 
        "range_ND_contour":1, 
        "range_confidence":0.001,
        "fine_bins":400,
        "fine_bins_2d":150,
        "smooth_scale_1D":0.3,
        "smooth_scale_2D":0.5,
        "tight_gap_fraction":0.15
        }

    ranges = {"tauV_eff":[0., 0.8]}

    samples = MCSamples(samples=samps, names=names, ranges=ranges, labels=labels,
                weights=probability, settings=settings )

    g = plots.getSubplotPlotter()
    g.settings.num_plot_contours = 3
    g.settings.prob_y_ticks = True

    # Change the size of the labels 
    fontsize = 16
    g.settings.lab_fontsize = fontsize
    g.settings.axes_fontsize = fontsize

    line_args = {"lw":2, "color":colorConverter.to_rgb("#006FED") } 

    g.triangle_plot(samples, filled=True, line_args=line_args)

    g.fig.subplots_adjust(wspace=0.1, hspace=0.1)

    prune  = 'both'
    

    for i in range(len(names)):
            for i2 in range(i, len(names)):
                _ax = g._subplot(i, i2)
                _ax.xaxis.set_major_locator(plt.MaxNLocator(3, prune=prune))
                _ax.yaxis.set_major_locator(plt.MaxNLocator(3, prune=prune))

    # Add tick labels at top of diagonal panels
    for i, ax in enumerate([g.subplots[i,i] for i in range(nParamsToPlot)]):
        par_name = names[i]
        print(par_name)

        if i < nParamsToPlot-1: 
            ax.tick_params(which='both', labelbottom=False, 
                    top=True, labeltop=True, labelsize=fontsize*0.8, left=False, labelleft=False)
        else:
            ax.tick_params(which='both', labelbottom=True, 
                    top=True, labeltop=False, labelsize=fontsize*0.8, left=False, labelleft=False)

        # Add shaded region showing 1D 68% credible interval
        y0, y1 = ax.get_ylim()
        lev = samples.get1DDensity(par_name).getLimits(settings['contours'][0])
        print(par_name, lev)

        ax.add_patch(
                Rectangle((lev[0], y0), 
                lev[1]-lev[0], 
                y1-y0, 
                facecolor="grey", 
                alpha=0.5)
                )
        
    
    g.export(os.path.join(results_folder,
                          "Custom_triangle.pdf"))

if __name__ == '__main__':
    main()