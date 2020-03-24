# -- Disclaimer --

I started this project with zero knowledge of Python, or even OOP. It was meant to be a learning experience which would also serve as a tool supporting my thesis. It grew to be a bit bigger, but it is very clumsy, and practically unapprochable because of its architecture. 
Still, I leave it here as a memento.

# Comparator
\- comparison of numerical integration schemes -

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

1. Clone the repo to your local machine
1. Run Comparator.ipynb on a local kernel
1. Follow the instructions therein

## Required packages
The underlying source code is written in Python 3. It makes use of several packages; some that might not be included in every python distribution are:

1. ipywidgets
1. pandas
1. numpy
1. bokeh
1. astroquery from astropy
1. scipy
1. matplotlib
