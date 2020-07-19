from PIL import Image
from PIL import ImageFilter
import app
import requests

from PIL.ImageFilter import (
    BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE,
    EMBOSS, FIND_EDGES, SMOOTH, SMOOTH_MORE, SHARPEN, GaussianBlur, UnsharpMask
    )


img = Image.open("images/courtyard.bmp")

filterTypes = ["BLUR", "GAUSSIAN_BLUR", "CONTOUR", "UNSHARP_MASK", "DETAIL", "EDGE_ENHANCE", "EDGE_ENHANCE_MORE", "EMBOSS", "FIND_EDGES", "SMOOTH", "SMOOTH_MORE", "SHARPEN"]

filterDict = {"BLUR": BLUR, "GAUSSIAN_BLUR" : GaussianBlur(radius=10), "UNSHARP_MASK": UnsharpMask(radius=2, percent=150, threshold=3), "CONTOUR": CONTOUR, "DETAIL": DETAIL, "EDGE_ENHANCE": EDGE_ENHANCE, "EDGE_ENHANCE_MORE": EDGE_ENHANCE_MORE, "EMBOSS": EMBOSS, "FIND_EDGES": FIND_EDGES, "SMOOTH": SMOOTH, "SMOOTH_MORE": SMOOTH_MORE, "SHARPEN": SHARPEN}

def applyFilter (image, filter): #image <- the filepath of the image, #filter <- a string showing which filter.
    if filter in filterTypes:
        filterActual = filterDict[filter]
    else:
        return "Not a valid filter"
    img = Image.open(requests.get(image, stream=True).raw)
    img = img.convert("RGB")
    img = img.filter(filterActual)
    return img
"""
imageToApply = "https://i.imgur.com/EqjbndL.png"
whereToSave = "image.png"
filterToApply = "GAUSSIAN_BLUR"
applyFilter(imageToApply, filterToApply).save(whereToSave)
"""
