import cv2

from backend.image import Image


class ImageUtil:
    @staticmethod
    def resize(image, new_height=None, new_width=None):
        original_height, original_width = image.shape
        resize_ratio = new_width / original_width if new_width is not None else new_height / original_height
        size = (round(original_height * resize_ratio), round(original_width * resize_ratio))
        return cv2.resize(image, tuple(reversed(size)), interpolation=Image.interpolation)