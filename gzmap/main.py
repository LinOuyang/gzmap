from .utils import *
from shapefile import Reader
from warnings import warn
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.font_manager import FontProperties
import pandas as pd

def to_list(obj):
    if isinstance(obj , str):
        return [obj]
    elif np.iterable(obj):
        return list(obj)
    return None

class GZMap:

    def __init__(self, ax=None, extent=[113.8, 116.7, 24.4, 27.3], font=None):
        if ax is None:
            self.ax = plt.gca()
        else:
            self.ax = ax
        self.extent(*extent)
        self.font = font
        if isinstance(font, str):
            self.font = FontProperties(fname=font)

    def extent(self, *args):
        if len(args) > 1:
            self.ax.set_xlim(*args[:2])
        if len(args) > 3:
            self.ax.set_ylim(*args[2:4])

    def __get_default_cmap(self, vmin, vmax, vlen):
        cmap = plt.cm.RdYlBu_r
        v = np.array([(vmin + 8), (vmax + 8)])/vlen
        if (v[1] - v[0]) < 0.4:
            v += np.array([-0.2, 0.2])
        if v[0] < 0:
            v += (- v[0])
        if v[1] > 1:
            v -= (v[1] - 1)
        cmap = LinearSegmentedColormap.from_list("n", cmap(np.linspace(*v, 100)))
        return cmap

    def get_shape_dict(self):
        if hasattr(self, "shape_dict"):
            return
        df = read_file(shapefile_lev2, encoding=encoding)
        names, geometries = df[["NAME", "geometry"]].values.T
        self.shape_dict = dict()
        for name, geometry in zip(names, geometries):
            self.shape_dict[name] = np.stack(geometry.xy, 1)
        # func = lambda cls, nam : cls.get(most_similar(nam, cls.keys()))
        # setattr(self.shape_dict, "match", MethodType(func, self.shape_dict))
        # self.shape_dict["n_record"] = len(names)

    def title(self, content, x=114.9, y=26.9, horizontalalignment='center', fontsize=18, **kwargs):
        for key in kwargs.keys():
            if 'font' in key:
                break
        else:
            kwargs["font"] = self.font
        return self.ax.text(x, y, content, ha=horizontalalignment, fontsize=fontsize, **kwargs)

    def station_heat(self, names, values, substitude={"章贡":"赣县"}, fmt=".1f", cmap=None, vlen=49, ticks=None, label=None, title=None, font=None, undisplay_name=False, undisplay_value="章贡"):
        self.get_shape_dict()
        vmin, vmax = np.nanmin(values), np.nanmax(values)
        if cmap is None:
            cmap = self.__get_default_cmap(vmin, vmax, vlen)
        elif isinstance(cmap, str):
            cmap = plt.cm.get_cmap(cmap)
        extra_dict = dict()
        if font is not None:
            extra_dict["fontproperties"] = font
        elif self.font is not None:
            extra_dict["fontproperties"] = self.font
                      

        series = pd.Series(values.squeeze(), index=names)
        for raw_name, sub_name in substitude.items():
            if most_similar(raw_name, names) is None:
                series[raw_name] = series.loc[most_similar(sub_name, names)]
        names = series.index
        v = series.values.squeeze()
        scale = pd.Series((v - vmin)/(vmax - vmin), index=series.index)

        for i, (name, points) in enumerate(self.shape_dict.items()):
            matched_name = most_similar(name, names)
            skip = False
            if matched_name is None:
                warn(f"{name} not found in your data")
                skip = True

            if not skip:
                dat = series.loc[matched_name]
                dat = int(round(dat)) if "d" in fmt else dat
                ma = micro_adjust.get(matched_name, (0, 0))
                x, y = np.median(points, axis=0) + np.array(ma)
                disp_name = '\n' + matched_name
                disp_value = eval("'{:" + fmt + "}'.format(dat)")

                if isinstance(undisplay_name, (int, bool)):
                    disp_name = disp_name if not undisplay_name else ''
                elif isinstance(undisplay_name, (list, tuple, str)):
                    if len(most_similar(matched_name, to_list(undisplay_name), none_type='')) > 0:
                        disp_name = ''

                if isinstance(undisplay_value, (int, bool)):
                    disp_value = disp_value if not undisplay_value else ''
                elif isinstance(undisplay_value, (list, tuple, str)):
                    if len(most_similar(matched_name, to_list(undisplay_value), none_type='')) > 0:
                        disp_value = ''

                cont = disp_value + disp_name
                self.ax.text(x, y, cont, va='center', ha='center', **extra_dict)
            facecolor = cmap(scale.loc[matched_name]) if not skip else 'none'
            p = plt.Polygon(points, edgecolor='k', facecolor=facecolor)
            self.ax.add_patch(p)

        vmin, vmax = np.min(values), np.max(values)
        norm = Normalize(vmin, vmax)
        bounds = np.unique(np.round(np.linspace(vmin, vmax, 9)))
        if fmt.endswith("f"):
            number = fmt.split(".")[-1][:-1]
            bounds = np.unique(np.round(np.linspace(vmin, vmax, 9), int(number)))
        if ticks is not None:
            bounds = ticks
        cb = plt.colorbar(plt.cm.ScalarMappable(norm, cmap), orientation='vertical', ax=self.ax, pad=0.05)
        cb.set_ticks(bounds)
        if label is not None:
            cb.set_label(label, **extra_dict)
        if title is not None:
            self.ax.set_title(title, **extra_dict)

if __name__ == "__main__":
    import pandas as pd
    from matplotlib.font_manager import FontProperties
    m = GZMap()
    df = pd.read_excel("../data.xlsx", index_col=0, skiprows=1) + 20
    m.station_heat(df.index, df.values, font=FontProperties(fname="../simsun.ttc"), ticks=None, label=None, title="赣州温度分布图", substitude={"宁都":"于都"})
    plt.show()

