pyheatmap
=========

Python library, provides various utilities for rendering heat maps:

Input data format of all tools is the same "x,y[,weight]":
<pre><code>0.1,0.3,3.0
0.5,0.6,6.0
0.12,0.74       # weight defaults to 1.0
...</code></pre>

 * __mapcoords.py__

    Receives file or stream of points and normalizes points coordinates given their bounding rectangle. Output points X,Y coordinates fall in range [0, 1].

    Usage example:
    <pre><code>python mapcoords.py \
      --area=0,0,100,100 \
      my_points.csv > my_points_normalized.csv</code></pre>

 * __heataccum.py__

    Receives file or stream of points and outputs accumulated values. It uses quad tree space partitioning and collapses points within specified threshold into single point, accumulating the weights. This allows to feed it very large set of points and receive an accumulated summary that can be used for final rendering.

    Usage example:
    <pre><code>python heataccum.py \
      --error=0.01 \
      my_points_normalized.csv > heat.csv</code></pre>

 * __heatmap.py__

   Renders heat map points on top of the background image. Input is points in format "x,y,weight":
    <pre><code>0.1,0.3,1.0
    0.5,0.6,1.0
    ...</code></pre>

    Weight parameter is optional (defaults to 1.0). Coordinates expected to be normalized in image space and fall into [0, 1] range.

    Usage example:
    <pre><code>python heatmap.py \
      --palette=resources/palette.png \
      --bg=resources/usa.jpg \
      --dot=50 \
      --opacity=0.8 \
      resources/heat.csv</code></pre>

And of course you can pipe everything together!

Dependencies
------------
 * Python 2.7.x
 * PIL (make sure to install with libjpeg support etc.)