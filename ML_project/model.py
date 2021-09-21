import torch
import torch.nn as nn
import torchvision.transforms.functional as tf
import os
os.environ[r'C:\ProgramData\Miniconda3\Library\bin']

# This is a custom implementation of the UNET model.
# It is important to choose an input that is divisible by 16.
# The code does account for non divisible inputs, but may result in errors.

class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DoubleConv, self).__init__()
        # This is making the model a same convolution model;
        # a type of convolution where the output matrix is 
        # of the same dimension as the input matrix
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, 1, 1, bias=False),
            # BatchNorm just uses a convolving normalization kernel to standardize batches.
            # More on this here: https://machinelearningmastery.com/batch-normalization-for-training-of-deep-neural-networks/
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )
        
    def forward(self, x):
        return self.conv(x)

class UNET(nn.Module):
    def __init__(self, in_channels=3, out_channels=1,
                features=[64, 128, 256, 512]):
        super(UNET, self).__init__()
        self.ups = nn.ModuleList()
        self.downs = nn.ModuleList()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Down part, this iterates through all of the conv layers in the model.
        # Pooling layer used in forward method.
        # So does the left hand of the model structure
        for feature in features:
            self.downs.append(DoubleConv(in_channels, feature))
            in_channels = feature

        # Up part, this is doing a double conv, so for every up step, it does 2 convs.
        for feature in reversed(features):
            self.ups.append(nn.ConvTranspose2d(feature*2, feature, kernel_size=2, stride=2))
            self.ups.append(DoubleConv(feature*2, feature))

        # The multiplication is just to retain the correct sizes and scaling shown in the model diagram.
        self.bottleneck = DoubleConv(features[-1], features[-1]*2)
        self.final_conv = nn.Conv2d(features[0], out_channels, kernel_size=1)

    def forward(self, x):
        skip_connections = []

        for down in self.downs:
            x = down(x)
            skip_connections.append(x)
            x = self.pool(x)
        
        # This is for the lowest level in the model architecture.
        x = self.bottleneck(x)
        # reverse the skip connections list to be able to repeat the bottom layer
        skip_connections = skip_connections[::-1]

        for idx in range(0, len(self.ups), 2):
            x = self.ups[idx](x)
            # So this is to do the linear step, but in a step of 2, hence the division
            skip_connection = skip_connections[idx // 2]

            # This is if the input x is not divisible by 16, so if the above floors the input.
            if x.shape != skip_connection.shape:
                # Skip the batch size and number of channels, resize to same shapes.
                x = tf.resize(x, size=skip_connection.shape[2:])

            concat_skip = torch.cat((skip_connection, x), dim=1)
            x = self.ups[idx+1](concat_skip)

        return self.final_conv(x)


def test():
    x = torch.randn((3, 1, 160, 160))
    model = UNET(in_channels=1, out_channels=1)
    preds = model(x)
    print(preds.shape)
    print(x.shape)
    assert preds.shape == x.shape

if __name__ == "__main__":
    # Here the test returns the same size as the input, thereby passing.
    test()