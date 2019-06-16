# prettyresults - Present data analysis results in Web or Docx format

Prettyresults is a Python package to display data analysis results in different formats.
In short: you run your data analysis using your preferred Python tools, generate
a set of results (figures, tables...) and tell prettyresults about them.
Prettyresults will generate a neat, friendly web page with your results.

Suppose you are analyzing some social or medical data, using pandas and scipy.stats.
You've created several matplotlib figures with descriptive data, some frequency tables,
some inference analysis... Visualizing all this information at once in a notebook may
not be practical. Prettyresults will display these results you've already created in
a webpage, allowing you to visualize them without problems. It can also create
a web document for you, with a subset of the obtained results.

Prettyresults is a Python library. It implements a result system to add and manipulate
results (such as figures or tables). Results are hierarchical, forming a tree.
Results can then be used to generate a web page or a Word document.

## Installation and requirements

From pypi:

```pip install prettyresults```

Required Python 3.4+. Tested with Python 3.6.7.

Prettyresults employs Pandas and Matplotlib.
