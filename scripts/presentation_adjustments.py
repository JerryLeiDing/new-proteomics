import sys
sys.dont_write_bytecode = True  # Avoid caching problems

import matplotlib
import matplotlib.pyplot as plt

from constants import COLORS, LABEL_MAPPING
from format_results import *
from roc import *
from sample import *


def plot_example_roc_curves():
    # Set up font
    font = {'family' : 'normal',
            'weight' : 'normal',
            'size'   : 22}
    matplotlib.rc('font', **font)
    """ Generate panel 2 of figure 1 """
    colors = [
        COLORS['CyberT'],
        COLORS['Absolute fold change'],
        COLORS['Moderated T (1-sample)'],
        COLORS['t-test (1-sample)'],
        COLORS['t-test (2-sample)'],
        COLORS['Moderated T (2-sample)'],
    ]

    ctrl, exp, is_changed = sample_no_ctrl_gamma(10000, 1000, 0.4, nctrl=4, nexp=4)
    pvals = do_stat_tests(ctrl, exp, True)
    plot_both(is_changed, pvals.values.transpose(), list(pvals.columns), colors=colors)


def pvalue_multipanel(pvals_u=None, pvals_g=None):
    """ Generate panel comparing p-value distributions
    Compare uniform and inverse gamma

    Corresponds to Figure 2B of manuscript"""
    matplotlib.rc('font', size=12)
    f, axarr = plt.subplots(2, 7, sharex='col', sharey='row')

    if pvals_u is None:
        ctrl_u, exp_u, _ = sample_no_ctrl_gamma(10000, 0, 0)
        pvals_u = do_stat_tests(ctrl_u, exp_u, True)
        pvals_u['Moderated T \n(2-sample, robust)'] = \
                modT_2sample(ctrl_u, exp_u, True)['P.Value'].values
        pvals_u['Moderated T \n(1-sample, robust)'] = \
                modT(ctrl_u, exp_u, True)['P.Value'].values

    if pvals_g is None:
        ctrl_g, exp_g, _ = sample_no_ctrl_uniform(10000, 0, 0)
        pvals_g = do_stat_tests(ctrl_g, exp_g, True)
        pvals_g['Moderated T \n(2-sample, robust)'] = \
                modT_2sample(ctrl_g, exp_g, True)['P.Value'].values
        pvals_g['Moderated T \n(1-sample, robust)'] = \
                modT(ctrl_g, exp_g, True)['P.Value'].values

    plot_pvalue_dist(pvals_u, axarr[0])
    plot_pvalue_dist(pvals_g, axarr[1])

    for ax in axarr[0]:
        ax.set_xlabel('')
    for ax in axarr[1]:
        ax.set_title('')

    return f, (pvals_u, pvals_g)


def pvalue_multipanel_noise():
    """ Compare p-value distributions different noise distributions """
    f, axarr = plt.subplots(3, 5, sharex='col', sharey='row')

    DF = 3
    def t_dist(loc, scale, size=1):
        return np.random.standard_t(DF, size=size)*scale

    ctrl_n, exp_n, _ = sample_no_ctrl_gamma(10000, 0, 0, use_var=np.random.normal)
    plot_pvalue_dist(do_stat_tests(ctrl_n, exp_n, True), axarr[0])
    ctrl_l, exp_l, _ = sample_no_ctrl_gamma(10000, 0, 0, use_var=np.random.laplace)
    plot_pvalue_dist(do_stat_tests(ctrl_l, exp_l, True), axarr[1])
    ctrl_t, exp_t, _ = sample_no_ctrl_gamma(10000, 0, 0, use_var=t_dist)
    plot_pvalue_dist(do_stat_tests(ctrl_t, exp_t, True), axarr[2])

    for ax in axarr[0]:
        ax.set_xlabel('')
    for ax in axarr[1]:
        ax.set_xlabel('')
        ax.set_title('')
    for ax in axarr[2]:
        ax.set_title('')

    return f

def volcano_multipanel(background="U"):
    """ Generate panel comparing volcano plots
    Compare uniform and inverse gamma

    Corresponds to Figure 4B/G of manuscript
    """
    matplotlib.rc('font', size=16)
    f, axarr = plt.subplots(2, 5, sharex='col', sharey='row')

    if background == "U":
        sampler = sample_no_ctrl_uniform
    elif background == "G":
        sampler = sample_no_ctrl_gamma
    else:
        raise ValueError("Invalid specification for background")

    ctrl_u, exp_u, is_changed_u = sampler(10000, 1000, 0.5)
    pvals_u = do_stat_tests(ctrl_u, exp_u, True)

    pvals_c = pd.DataFrame.from_items([
        (col, multipletests(pvals_u[col], 0.05, method='fdr_bh')[1])
        for col in pvals_u.columns
    ])

    volcano_plots(pvals_u, ctrl_u, exp_u, is_changed_u, axarr[0])
    volcano_plots(pvals_c, ctrl_u, exp_u, is_changed_u, axarr[1])

    # Remove unnecessary labels
    for ax in axarr[0]:
        ax.set_xlabel('')
    for ax in axarr[1]:
        ax.set_title('')
    axarr[1][0].set_ylabel('$-\log_{10}$(Adjusted p-value)')

    return f


def barplot_multipanel(background='U'):
    f, axarr = plt.subplots(1, 2, sharey='row')

    if background == "U":
        sampler = sample_no_ctrl_uniform
    elif background == "G":
        sampler = sample_no_ctrl_gamma
    else:
        raise ValueError("Invalid specification for background")

    ctrl, exp, is_changed = sampler(10000, 1000, 0.5)
    pvals = do_stat_tests(ctrl, exp, True)

    pvals_a = pd.DataFrame.from_items([
        (col, multipletests(pvals[col], 0.05, method='fdr_bh')[1])
        for col in pvals.columns
    ])

    barplot_accuracy(pvals, is_changed, axarr[0])
    barplot_accuracy(pvals_a, is_changed, axarr[1])
    axarr[0].set_ylabel('Count')
    axarr[0].set_title('Raw p-values')
    axarr[1].set_title('BH adjusted')

    # Add legend
    # plt.legend((p1[0], p2[0]), ('Men', 'Women'))
    handles, labels = axarr[1].get_legend_handles_labels()
    # Map labels for pretty printing
    plt.figlegend(handles, labels, loc='upper center', ncol=2)

    return f

def plot_example_prc():
    """ Figure S1, example PRC curve """

    f, ax = plt.subplots()

    ctrl, exp, is_changed = sample_no_ctrl_gamma(10000, 1000, 0.5)
    pvals = do_stat_tests(ctrl, exp, True)
    labels = list(pvals.columns)

    colors = [
        COLORS['CyberT'],
        COLORS['Absolute fold change'],
        COLORS['Moderated T (1-sample)'],
        COLORS['t-test (1-sample)'],
        COLORS['t-test (2-sample)'],
        COLORS['Moderated T (2-sample)'],
    ]
    for i, label in enumerate(labels):
        c = colors[i]
        p_val = pvals[label]
        plot_prc(is_changed, p_val, ax=ax, label=label, is_pval=True, color=c)


def density_scatter():
    """
    Scatterplot of variance vs log2 mean intensity

    Figure 1B
    """
    matplotlib.rc('font', size=22)
    f, (ax1, ax2) = plt.subplots(1, 2)

    def do_plot(data, ax):
        x = np.mean(data.values, axis=1)
        y = np.var(data.values, axis=1)
        xy = np.vstack([x,y])

        z = gaussian_kde(xy)(xy)
        # Sort the points by density, so that the densest points are plotted last
        idx = z.argsort()
        x, y, z = x[idx], y[idx], z[idx]

        ax.scatter(x, y, c=z, s=10, edgecolor='')
        ax.set_ylim(bottom=0)

    ctrl_u, _, _ = sample_no_ctrl_uniform(10000, 0, 0)
    ctrl_g, _, _ = sample_no_ctrl_gamma(10000, 0, 0)
    do_plot(ctrl_u, ax1)
    do_plot(ctrl_g, ax2)

    ax1.set_title('Uniform')
    ax2.set_title('Inverse Gamma')
    ax1.set_ylabel('Peptide variance')
    ax1.set_xlabel('Mean $log2$ peptide intensity')
    ax1.set_xlabel('Mean $log2$ peptide intensity')


"""
Transform results of variance AUC dictionary to more readable/usable ones
"""
def transform_keys(frm):
    # Replace inv_gamma with invgam
    x1 = ['invgam' + k[9:] if k.startswith('inv_gamma') else k for k in frm]

    x2 = []
    # Now add 'norm' for Gaussian noise
    for k in x1:
        toks = k.split('_')
        if len(toks) == 2:
            x2.append('_'.join((toks[0], 'norm', toks[1])))
        else:
            x2.append(k)

    return x2

"""
Format the dataframe result of running continuous fold changes
"""
def format_multiple_fc_cont(df):
    labels = df['labels']
    true_label = pd.Series([x.split(': ')[1] for x in labels])
    model = pd.Series([x.split(': ')[0] for x in labels])

    model[model=='Uniform, all'] = 'Uniform'
    model[model=='Normal, all'] = 'Normal'

    # TODO
    # Drop everything between -0.2 and 0.2

    setting = df['setting']
    true_setting = [float(x.split('<')[0]) for x in setting]
    pass

def regenerate_dataframes():
    """
    Regenerate dataframes
    """
    fc_range_gam = np.load('peptide_fc_range_gam_FINAL.npy')[()]
    fc_range_uni = np.load('peptide_fc_range_uni_FINAL.npy')[()]
    nexp = np.load('peptide_nexp_modtfix_FINAL.npy')[()]
    nexp_imba = np.load('peptide_nexp_imba_modtfix_FINAL.npy')[()]
    var = np.load('peptide_variances_FINAL.npy')[()]
    ds_size = np.load('peptide_ds_size_FINAL.npy')[()]

    fdr_fc_gam = np.load('peptide_fdr_fc_gam_FINAL.npy')[()]
    fdr_fc_uni = np.load('peptide_fdr_fc_uni_FINAL.npy')[()]

    # fix nexp_imba keys
    nexp_imba = {(('(%d,%d)' % k) if k != '_labels' else k):v for
            k,v in nexp_imba.iteritems()}
    # Fix ds_size keys
    ds_size = {(('%d: %d' % k) if k != '_labels' else k):v for
            k,v in ds_size.iteritems()}

    # Remove fold change from fdr labels
    fdr_fc_gam['_labels'] = list(fdr_fc_gam['_labels'])
    fdr_fc_gam['_labels'].remove('fold change')
    fdr_fc_uni['_labels'] = list(fdr_fc_uni['_labels'])
    fdr_fc_uni['_labels'].remove('fold change')

    write_result_dict_to_df(fc_range_gam, None).to_csv(
            'df_peptide_fc_range_gam_FINAL.csv')
    write_result_dict_to_df(fc_range_uni, None).to_csv(
            'df_peptide_fc_range_uni_FINAL.csv')
    write_result_dict_to_df(nexp, None).to_csv(
            'df_peptide_nexp_modtfix_FINAL.csv')
    write_result_dict_to_df(nexp_imba, None).to_csv(
            'df_peptide_nexp_imba_modtfix_FINAL.csv')
    write_result_dict_to_df(var, None).to_csv(
            'df_peptide_variances_FINAL.csv')
    write_result_dict_to_df(ds_size, None).to_csv(
            'df_peptide_dataset_size_FINAL.csv')

    write_result_dict_to_df(fdr_fc_gam, None, fdr=True).to_csv(
            'df_peptide_fdr_fc_gam_FINAL.csv')
    write_result_dict_to_df(fdr_fc_uni, None, fdr=True).to_csv(
            'df_peptide_fdr_fc_uni_FINAL.csv')



