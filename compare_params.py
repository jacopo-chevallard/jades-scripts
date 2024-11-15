from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm

# Function to read the required columns from a FITS file
def read_columns(file_name, columns):
    result = {}
    with fits.open(file_name) as hdul:
        for col in columns:
            found_column = False
            for hdu in hdul:
                if hdu.data is not None and isinstance(hdu.data, fits.FITS_rec):
                    col_names = hdu.columns.names
                    if col + '_median' in col_names:
                        for row in hdu.data:
                            id = row[col_names.index('ID')]
                            if id not in result:
                                result[id] = {}
                            row_result = {'median': row[col_names.index(col + '_median')]}
                            if col + '_68.00_low' in col_names and col + '_68.00_up' in col_names:
                                row_result['low'] = row[col_names.index(col + '_68.00_low')]
                                row_result['up'] = row[col_names.index(col + '_68.00_up')]
                            elif col + '_68.00' in col_names:
                                row_result['low'], row_result['up'] = row[col_names.index(col + '_68.00')]
                            else:
                                raise KeyError(f"Columns '{col}_68.00_low' and '{col}_68.00_up' not found in {file_name}.")
                            result[id][col] = row_result
                        found_column = True
                        break
            if not found_column:
                raise KeyError(f"Column '{col}' not found in any extension of {file_name}.")
        return result

def read_column(file_name, column_name):
    values = []
    with fits.open(file_name) as hdul:
        for hdu in hdul:
            if hdu.data is not None and isinstance(hdu.data, fits.FITS_rec):
                col_names = hdu.columns.names
                if column_name in col_names:
                    values.extend(hdu.data[column_name])
                    break
    return values

# Function to plot the data
import numpy as np

def plot_columns(file1, file2, columns, label1="", label2="", log_columns=[], alpha=0.6):
    data1 = read_columns(file1, columns)
    data2 = read_columns(file2, columns)
    
    for col in columns:
        x, y, xerr_low, xerr_up, yerr_low, yerr_up = [], [], [], [], [], []
        log_label = ""
        
        for id, values in data1.items():
            if id in data2:
                x_val = values[col]['median']
                y_val = data2[id][col]['median']
                x_low = values[col]['low']
                x_up = values[col]['up']
                y_low = data2[id][col]['low']
                y_up = data2[id][col]['up']

                # Apply log transformation if the column is in log_columns
                if col in log_columns:
                    log_label = "log10"
                    x_err_low = (x_val - x_low) / (np.log(10) * x_val)
                    x_err_up = (x_up - x_val) / (np.log(10) * x_val)
                    y_err_low = (y_val - y_low) / (np.log(10) * y_val)
                    y_err_up = (y_up - y_val) / (np.log(10) * y_val)
                    x_val = np.log10(x_val)
                    y_val = np.log10(y_val)
                else:
                    x_err_low = x_val - x_low
                    x_err_up = x_up - x_val
                    y_err_low = y_val - y_low
                    y_err_up = y_up - y_val

                x.append(x_val)
                y.append(y_val)
                xerr_low.append(x_err_low)
                xerr_up.append(x_err_up)
                yerr_low.append(y_err_low)
                yerr_up.append(y_err_up)
        
        xerr = [np.array(xerr_low), np.array(xerr_up)]
        yerr = [np.array(yerr_low), np.array(yerr_up)]
        
        plt.errorbar(x, y, xerr=xerr, yerr=yerr, fmt='o', label=col, alpha=alpha)

        # Robust linear regression
        X = sm.add_constant(x)  # Adds a constant term to the predictor
        model = sm.RLM(y, X)
        results = model.fit()

        # Plot the regression line
        plt.plot(x, results.fittedvalues, 'r-', label='Robust Regression Line')

        # Print the coefficients of the regressed line on the plot
        plt.text(0.05, 0.95, f'y = {results.params[1]:.2f}x + {results.params[0]:.2f}', 
                 transform=plt.gca().transAxes, verticalalignment='top')
        
        # Determine the common range for both axes
        common_min = min(min(x), min(y))
        common_max = max(max(x), max(y))

        # Calculate 5% of the range
        extension = 0.05 * (common_max - common_min)
        
        # Extend the limits by the calculated amount
        plt.xlim(common_min - extension, common_max + extension)
        plt.ylim(common_min - extension, common_max + extension)
        
        # Plot the diagonal line
        plt.plot([common_min, common_max], [common_min, common_max], 'k--')
        
        plt.xlabel(f'{log_label} {col} in {label1}')
        plt.ylabel(f'{log_label} {col} in {label2}')
        plt.legend()
        plt.savefig(f'{col}_plot.pdf', format='pdf')
        plt.show()

from scipy.stats import chi2

def plot_chi_square(file_name, chi_square_column, degrees_of_freedom, bins=1500, label=""):
    # Read chi-square values from file1
    chi_square_values_file1 = read_column(file_name, chi_square_column)

    # Plot histogram for file1
    plt.hist(chi_square_values_file1, bins=bins, density=True, alpha=0.5, label=label)

    # Plot theoretical chi-square distribution
    x = np.linspace(min(chi_square_values_file1),
                    max(chi_square_values_file1), 1000)
    y = chi2.pdf(x, degrees_of_freedom)

    plt.plot(x, y, label=f'Theoretical (N={degrees_of_freedom})')

    plt.xscale('log')

    plt.xlabel('Chi-Square Value')
    plt.ylabel('Density')
    plt.legend()
    plt.savefig(f'chi_square_plot{label}.pdf', format='pdf')
    plt.show()

# List of columns to plot
columns_to_plot = ["M_tot", "SFR", "logOH", "tauv_eff", "nebular_logu", "nebular_xi", "mass_w_age"]
log_columns=["M_tot", "SFR",  "mass_w_age", "tauv_eff"]

columns_to_plot = ["M_tot"]
log_columns=["M_tot"]

# Path to the FITS files
file_spec = '/Users/jchevall/JWST/JADES/results/DEEP_GOODS_S_R100_base_v3.0_mup100/pyp-beagle/data/BEAGLE_summary_catalogue.fits'
file_photom_spec = '/Users/jchevall/JWST/JADES/results/fit_R100_photom_poly/pyp-beagle/data/BEAGLE_summary_catalogue_reformatted_R100_v3p0_photom_poly.fits'

label1 = "R100"
label2 = "R100+photometry"

dof = 683
chi_sq_col = "MAP_chi_square"
#plot_chi_square(file_photom_spec, chi_square_column=chi_sq_col, degrees_of_freedom=dof, label=label2)

# Call the function to plot the data
plot_columns(file_spec, file_photom_spec, columns_to_plot, 
             label1=label1, label2=label2, log_columns=log_columns)