# Comparator
\- comparison of numerical integration schemes -

PLEASE NOTE: This readme is only a stub. This is a work in progress and most instructions will appear in more detail on the GitHub repo at:
https://github.com/scolear/Comparator

This work was done as part of my MSc Thesis in Astronomy: the most detailed instructions can (as of now) only be found written in Hungarian in my Thesis. Sorry.

This software was designed to showcase certain aspects of different numerical integration algorithms used in celestial mechanics (and many other fields dealing with dynamical systems). The methods implemented as of now:

1. Three fixed-timestep methods:
  * Euler's method
  * Verlet's symplectic method
  * "Classical" Runge-Kutta 4th order method
2. One adaptive method:
  * Runge-Kutta Dormand-Prince 5(4)

# How-to

The user is meant to interact with the Jupyter Notebook called Comparator.ipynb. Since it calls local files using linemagics, the **surrounding folders must be present** on the users local machine.

To run the software as it is intended:

1. Have the entire folder-system present on your local machine
2. Run Comparator.ipynb on a local kernel
3. Follow the instructions therein

## Required packages
The underlying source code is written in Python 3. It makes use of several packages; some that might not be included in every python distribution are:

1. ipywidgets
2. pandas
3. numpy
4. bokeh
5. astroquery

*Hint:* The easiest way is to handle all of these through the Anaconda distribution.

