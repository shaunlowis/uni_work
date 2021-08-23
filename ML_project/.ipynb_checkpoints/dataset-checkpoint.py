import os
from PIL import Image
from torch.utils.data import Dataset
import numpy as np
import matplotlib.pyplot as plt


def open_im(img):
    im = Image.open(img)
    return np.array(im)

def split_im(im, base_dir):
    """ This assumes im is a numpy array of the image. """
    M = im.shape[0]//8
    N = im.shape[1]//8
    tiles = [im[x:x+M,y:y+N] for x in range(0,im.shape[0],M) for y in range(0,im.shape[1],N)]
    
    for x in range(0, len(M)):
        print(f'{(x // len(M)) * 100}% done..')
        for y in range(0, len(N)):
            out = Image.fromarray(im[x, y])
            plt.imshow(out,cmap='gray')
            plt.axis('off')
            # save the image
            plt.savefig(f'split{x}_{y}.tif', transparent=True, dpi=300, bbox_inches="tight", pad_inches=0.0)


def main():
    im_path = r'D:\python\uni_work\ML_project\data_raw\lds-new-zealand-4layers-GTiff\nz-10m-satellite-imagery-2017\nz-10m-satellite-imagery-2017.tif'
    split_dir = r'D:\python\uni_work\ML_project\data_split'
    im = open_im(im_path)
    curr_year_fp = os.path.join(split_dir, '2017')
    print(curr_year_fp)

    if os.path.exists(curr_year_fp):
        split_im(im, curr_year_fp)
    else:
        target_dir = os.mkdir(curr_year_fp)
        split_im(im, target_dir)
    
if __name__ == "__main__":
    # Here the test returns the same size as the input, thereby passing.
    main()

# class RolleSton(Dataset):
#     def __init__(self, image_dir, mask_dir, transform=None):
#         super().__init__()

#         self.image_dir = image_dir
#         self.mask_dir = mask_dir
#         self.transform = transform
#         self.images = os.listdir(image_dir)

#     def __len(self):
#         return len(self.images)

#     def __getitem__(self, index):
#         img_path = os.path.join(self.image_dir, self.images[index])
#         mask_path = os.path.join(self.image_dir, self.images[index])
#         image = np.array(Image.open(img_path).convert("RGB"))
#         mask = np.array(Image.open(mask_path))