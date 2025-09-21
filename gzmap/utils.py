import numpy as np
from .config import micro_adjust, shapefile_lev1, shapefile_lev2, encoding
from geopandas import read_file

def similarity(x : str, y : str, p=False):
    s1, s2 = set(x), set(y)
    common = s1.intersection(s2)
    n_len = len(s1.union(s2))
    return len(common)/n_len

def most_similar(x : str, values : list[str], none_type=None):
    similarity_list = [similarity(x, value) for value in values]
    ind = np.argmax(similarity_list)
    similar_score = similarity_list[ind]
    if similar_score > 0.55 :
        return values[ind]
    return none_type
