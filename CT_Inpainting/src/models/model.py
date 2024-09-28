import torch.nn as nn
import torch

# Define the U-Net model
class UNet(nn.Module):
    def __init__(self, in_channels=4, out_channels=1):
        super(UNet, self).__init__()
        # Encoder
        self.enc_conv0 = self.conv_block(in_channels, 64)
        self.pool0 = nn.MaxPool2d(kernel_size=2)

        self.enc_conv1 = self.conv_block(64, 128)
        self.pool1 = nn.MaxPool2d(kernel_size=2)

        self.enc_conv2 = self.conv_block(128, 256)
        self.pool2 = nn.MaxPool2d(kernel_size=2)

        self.enc_conv3 = self.conv_block(256, 512)
        self.pool3 = nn.MaxPool2d(kernel_size=2)

        self.enc_conv4 = self.conv_block(512, 1024)

        # Decoder
        self.upconv3 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec_conv3 = self.conv_block(1024, 512)

        self.upconv2 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec_conv2 = self.conv_block(512, 256)

        self.upconv1 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec_conv1 = self.conv_block(256, 128)

        self.upconv0 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec_conv0 = self.conv_block(128, 64)

        self.final_conv = nn.Conv2d(64, out_channels, kernel_size=1)

    def conv_block(self, in_channels, out_channels):
        block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(out_channels),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(out_channels),
        )
        return block

    def forward(self, x):
        # Encoder
        enc0 = self.enc_conv0(x)
        enc0_pool = self.pool0(enc0)

        enc1 = self.enc_conv1(enc0_pool)
        enc1_pool = self.pool1(enc1)

        enc2 = self.enc_conv2(enc1_pool)
        enc2_pool = self.pool2(enc2)

        enc3 = self.enc_conv3(enc2_pool)
        enc3_pool = self.pool3(enc3)

        bottleneck = self.enc_conv4(enc3_pool)

        # Decoder
        dec3 = self.upconv3(bottleneck)
        dec3 = torch.cat((dec3, enc3), dim=1)
        dec3 = self.dec_conv3(dec3)

        dec2 = self.upconv2(dec3)
        dec2 = torch.cat((dec2, enc2), dim=1)
        dec2 = self.dec_conv2(dec2)

        dec1 = self.upconv1(dec2)
        dec1 = torch.cat((dec1, enc1), dim=1)
        dec1 = self.dec_conv1(dec1)

        dec0 = self.upconv0(dec1)
        dec0 = torch.cat((dec0, enc0), dim=1)
        dec0 = self.dec_conv0(dec0)

        out = self.final_conv(dec0)
        return out