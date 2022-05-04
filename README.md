# MRZ detector
## Algorithm 
- Resize current frame to `600` pixels heigh (to make image processing faster).
- Gaussian blurring is then used to reduce high frequency noise (like glares of the sun, muds).
- Then first blackhat operator is used to detect dark/light regions. (after gaussian function, there are only light text and light passport details on the image, others are quite darker).
- Sobel operator is followed then to compute gradients over horizontal ax. (Scharr gradient needs to find not only significant diff between light and dark, but also contains vertical changes in the gradient, such as the MRZ text region).
- Second operator is then used to detect MRZ lines. (rectangular kernel, which is usefull for MRZ chars in lines).
- Third operator needs to connect MRZ lines with each other. (square kernel -- reduce gaps between lines).
- To remedy problem with border, it is set 5% of the left and right borders of the image to zero (i.e., black).
- Finally, contours are found to get cropped image with only MRZ characters.
- This cropped image as the input then processed by Google Tessaract, which outputs string of MRZ.
![Alt text](images/ocr_flow.png?raw=true "Title")


