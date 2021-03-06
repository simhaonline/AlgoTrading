from os import linesep
from typing import Sequence, Dict, Tuple
from datetime import datetime, timedelta
from FinancialAnalysis.analysis.smoothing import Smoother
from FinancialAnalysis.analysis.forecasting import Forecaster

import numpy as np
import plotly.graph_objs as go


def _plot_2d_lines(x_axes: Sequence[Sequence], y_axes: Sequence[Sequence],
                   plotting_params: Dict = None, figure: go.Figure = None,
                   show: bool = True):
    """
    A utility method for plotting multiple 2d lines on a joint figure, using the Plotly
    package.

    :param x_axes: An iterable object, where each element at index i,
     contains an appropriate x-axis values to plot as part of plot i.
    :param y_axes: An iterable object, where each element at index i,
     contains an appropriate y-axis values to plot as part of plot i.
    :param plotting_params: Meta parameters for the entire figure, i.e.:
     xlabel, ylable, title, legend, etc.
    :param figure: Plotly Figure object to plot on, if None generates new figure
    :param show: (bool) Whether to display the figure or not.

    :return: None
    """

    if len(x_axes) != len(y_axes):
        raise ValueError(
            f"'x_axes' and 'y_axes' must have exactly the same number of elements,"
            f" however len(x_axes) = {len(x_axes)} and len(y_axes) = {len(y_axes)}."
        )

    if figure is None:
        figure = go.Figure()

    # Add the traces
    [
        figure.add_trace(
            go.Scatter(
                x=x_axes[i],
                y=y_axes[i],
                mode=(
                    plotting_params['mode']
                    if 'mode' in plotting_params else 'lines+markers'
                ),
                name=(
                    plotting_params['legend'][i]
                    if 'legend' in plotting_params else f'trace {i}'
                ),
                text=(
                    plotting_params['meta_data'][i]
                    if 'meta_data' in plotting_params else ''
                ),
            )
        )
        for i in range(len(x_axes))
    ]

    figure.update_layout(
        title=(plotting_params['title']if 'title' in plotting_params else ''),
        xaxis={'title': plotting_params['xlabel']
        if 'xlabel' in plotting_params else 'X Label'},
        yaxis={'title': plotting_params['ylabel']
        if 'ylabel' in plotting_params else 'Y Label'},
    )

    if show:
        figure.show()


def plot_assets_list(assets_symbols: tuple, assets_data: list, dates: list,
                     assets_meta_data: list = None,
                     display_meta_paramets: Tuple[str, ...] = tuple(),
                     figure: go.Figure = None, show: bool = True):
    """
    A method for plotting a list of tradable equities

    :param assets_symbols: (list) A list of strings, denoting the listed symbols
    of the assets to be plotted
    :param assets_data: (list) A list of NumPy arrays, denoting the stocks to plot
    :param dates: (list) A list of strings, denoting the dates for which
    the quotes are given
    :param assets_meta_data: (list) A list of dicts containing the macro data for
    each asset to be plotted
    :param display_meta_paramets: (Tuple) A tuple of string, denoting the meta
    parameters to display for each asset.
    :param figure: Plotly Figure object to plot on, if None generates new figure
    :param show: (bool) Whether to display the figure or not.

    :return: None
    """

    names = []
    infos = []
    dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
    x_axes = []
    y_axes = []
    for i, asset in enumerate(assets_data):
        x_axes.append(dates[-len(asset):])
        y_axes.append(asset)

        names.append(f"{assets_symbols[i]}")

        if assets_meta_data is not None:
            meta_info = assets_meta_data[i]
            info = f'{linesep}'.join([f'{key}: {meta_info[key]}'
                                      for key in meta_info
                                      if key in display_meta_paramets])
            infos.append([info] * len(asset))

    xlabel = 'Date'
    ylabel = 'Price [USD]'
    plotting_params = {
        'xlabel': xlabel,
        'ylabel': ylabel,
        'legend': names,
        'title': "Equities Prices"
    }

    if len(infos):
        plotting_params['meta_data'] = infos

    _plot_2d_lines(x_axes=x_axes, y_axes=y_axes, plotting_params=plotting_params,
                   figure=figure, show=(True if figure is None else False))

    if show and figure is not None:
        figure.show()


def plot_smooth_assets_list(
        assets_symbols: tuple, assets_data: list, dates: list,
        smoothers: (Smoother, ...), assets_meta_data: list = None,
        display_meta_paramets: Tuple[str, ...] = tuple(),
        figure: go.Figure = None, show: bool = True):
    """
    A method for plotting a list of tradable equities after smoothening.

    :param assets_symbols: (list) A list of strings, denoting the listed symbols
    of the assets to be plotted
    :param assets_data: (list) A list of NumPy arrays, denoting the stocks to plot
    :param dates: (list) A list of strings, denoting the dates for which
    the quotes are given
    :param assets_meta_data: (list) A list of dicts containing the macro data for
    each asset to be plotted
    :param display_meta_paramets: (Tuple) A tuple of string, denoting the meta
    parameters to display for each asset.
    :param smoothers: (list) A list of Smoother class instances. Each smoother will be
    applied to all assets and plotted together.
    :param figure: Plotly Figure object to plot on, if None generates new figure
    :param show: (bool) Whether to display the figure or not.

    :return: None
    """

    # Plot the assets as is
    figure = figure if figure is not None else go.Figure()

    plot_assets_list(
        assets_symbols=assets_symbols,
        assets_data=assets_data,
        dates=dates,
        assets_meta_data=assets_meta_data,
        display_meta_paramets=display_meta_paramets,
        figure=figure,
        show=False,
    )

    names = []
    x_axes = []
    y_axes = []
    for i, asset in enumerate(assets_data):
        # Plot smoothed data
        for s, smoother in enumerate(smoothers):
            smoothed_asset = smoother(asset)
            x_axes.append(dates[-len(smoothed_asset):])
            y_axes.append(smoothed_asset)
            names.append(
                f"{assets_symbols[i]} - {smoother.description}"
            )

    plotting_params = {
        'legend': names,
    }

    _plot_2d_lines(x_axes=x_axes, y_axes=y_axes, plotting_params=plotting_params,
                   figure=figure, show=False)

    if show:
        figure.show()


def plot_forecasts(periods: (np.ndarray, ...), smoother: Smoother,
                   forecaster: Forecaster, asset_symbol: str,
                   dates: list, asset_meta_data: dict,
                   display_meta_paramets: Tuple[str, ...] = tuple(),
                   figure: go.Figure = None, show: bool = True):
    """
    A method for plotting forecasts for a list of tradable equity after smoothening.

    :param periods: (Tuple) tuple of NumPy arrays, each denoting a period to perform
    forecasting on, should be of length of at least 2 periods.
    :param smoother: (Smoother) A smoother object to use on each period
    :param forecaster: (Forecaster) A forecaster object to calculate the forecast over
    the period
    :param asset_symbol: (str) A string denoting the symbol
    of the asset to be plotted
    :param dates: (list) A list of strings, denoting the dates for which
    the quotes are given
    :param asset_meta_data: (dict) A dict containing the macro data for
    the asset to be plotted
    :param display_meta_paramets: (Tuple) A tuple of string, denoting the meta
    parameters to display for each asset.
    :param figure: Plotly Figure object to plot on, if None generates new figure
    :param show: (bool) Whether to display the figure or not.

    :return: None
    """

    figure = figure if figure is not None else go.Figure()
    plot_smooth_assets_list(
        assets_symbols=tuple(f"{asset_symbol}: Forecast period {i}"
                             for i in range(len(periods))),
        assets_data=periods,
        dates=dates,
        assets_meta_data=None,
        smoothers=(smoother, ),
        display_meta_paramets=display_meta_paramets,
        figure=figure,
        show=False,
    )

    x_axes = []
    y_axes = []
    names = []
    # Add the dates for the final forecast period
    dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
    new_dates = [(dates[-1] + timedelta(days=1)), ]
    for f in range((len(periods[-1]) - 1)):
        new_dates.append((new_dates[-1] + timedelta(days=1)))

    dates.extend(new_dates)

    for i, period in enumerate(periods[1:]):
        period = np.concatenate(periods[:i + 1])
        smoothed = smoother(period)

        forecaster.smoother = smoother
        forecaster.arima_model = None
        forecast = forecaster(smoothed)

        x_axes.append(new_dates[-len(forecast):])
        y_axes.append(forecast)
        names.append(f"{forecaster.description}")


    # Plot all forecasts
    plotting_params = {
        'legend': names,
    }
    _plot_2d_lines(x_axes=x_axes, y_axes=y_axes, plotting_params=plotting_params,
                   figure=figure, show=False)

    if show:
        figure.show()

