import cv2
import numpy as np
import matplotlib.pyplot as plt

def gaussian_low_pass_filter(shape, D0):
    P, Q = shape
    u = np.arange(P)
    v = np.arange(Q)
    V, U = np.meshgrid(v, u)
    D = np.sqrt((U - P/2)**2 + (V - Q/2)**2)
    H = np.exp(-(D**2) / (2 * D0**2))
    return H

# ---------- 自动生成一张测试图片 ----------
img = np.zeros((256, 256), dtype=np.uint8)
cv2.circle(img, (128, 128), 60, 255, -1)

# FFT
f = np.fft.fft2(img)
fshift = np.fft.fftshift(f)

# Filter
H = gaussian_low_pass_filter(img.shape, 30)

# Apply filter
G = fshift * H

# IFFT
g = np.fft.ifftshift(G)
out = np.abs(np.fft.ifft2(g))

# Show result
plt.figure(figsize=(10, 5))
plt.subplot(121); plt.title("Original"); plt.imshow(img, cmap='gray')
plt.subplot(122); plt.title("Gaussian LPF"); plt.imshow(out, cmap='gray')
plt.show()
