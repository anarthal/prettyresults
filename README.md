# analyzer - Present data analysis results in Web or Docx format

analyzer is a Python project to present data analysis results in different formats.
The core idea behind analyzer is to allow the user generate and display thousands of
analysis results in a neat, friendly way.

Suppose you are analyzing some social or medical data, using pandas and scipy.stats.
You've created several matplotlib figures with descriptive data, some frequency tables,
some inference analysis... Visualizing all this information at once in a notebook may
not be practical. analyzer will display these results you've already created in
a webpage, allowing you to visualize them without problems. It can also create
a web document for you, with a subset of the obtained results.

analyzer is a Python library. It implements a result system to add and manipulate
results (such as figures or tables). Results are hierarchical, forming a tree.
Results can then be used to generate a web page or a Word document.

## Installation and requirements

analyzer is not yet in pypy. Clone this repository and add it to the PYTHONPATH to use it.

Required Python packages: python-pandas, matplotlib, docx
