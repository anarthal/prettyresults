.. _tutorial:

Tutorial
====================================



Welcome to prettyresults tutorial! In this example we will analyze some sales data,
generating some descriptive graphics and tables. We will learn how to tell prettyresults about
them so it can generate a web page and a Word document with them. The example full code
and data is accessible in the project's git repository (https://github.com/anarthal/prettyresults), under
the examples/ directory. The resulting web page is accessible online
`here <https://anarthal.github.io/prettyresults-example/>`_.

The FooBar company sells their BarBaz product brand around the world. We have a CSV with data
about their shipments, telling where they ship and which channel did they use (online/offline).
We will do some basic descriptive analytics using standard Python Pandas/Matplotlib,
and will make prettyresults generate a web with them.

We first load the CSV using standard Pandas:

.. literalinclude:: ../examples/example.py
   :lines: 8,9

We now create an :class:`prettyresults.AnalysisContext` object.
This is the heart of prettyresults: it will accumulate
the results of our analysis to generate the web and Word afterwards:

.. literalinclude:: ../examples/example.py
   :lines: 13
   
The AnalysisContext stores results hierarchically, in a tree. Results may be of the following types:

- Figures. These are matplotlib graphs.
- Tables. The name speaks by itself.
- Containers. These are intermediate nodes in the tree, and contain further results.
  They are shown as folders in the web page, and as headings in the Word document.
  Container results are represented by the :class:`prettyresults.results.ContainerResult` class,
  and have methods to add other results as children. This is the preferred way to
  add new results.
  
Results have a unique ID (more info :ref:`here <result_ids>`) and a human-friendly display name.
By default, the AnalysisContext creates a single container result, of ID :code:`root`.
We may retrieve any result by ID using :meth:`prettyresults.AnalysisContext.get_result`:

.. literalinclude:: ../examples/example.py
   :lines: 19

We are going to analyze channel and region data, as well as the interaction between the two.
We create one container result for each one, using :meth:`prettyresults.results.ContainerResult.add_container`.
We need to provide an ID, unique within the current container, and a display name:

.. literalinclude:: ../examples/example.py
   :lines: 21-25

Let's create a bar plot for the Region variable. We use :meth:`prettyresults.results.ContainerResult.add_figure`
to add it to our tree:

.. literalinclude:: ../examples/example.py
   :lines: 28-32

We are also going to add a frequency table for Region. ContainerResult has several method
for adding tables. As value counts will be stored in a pandas.Series, we will use
:meth:`prettyresults.results.ContainerResult.add_series_table`:

.. literalinclude:: ../examples/example.py
   :lines: 34-37

We will perform similar operations for Channel and Region-Channel, omitted here for brevity.
The next step is to generate the web page:

.. literalinclude:: ../examples/example.py
   :lines: 55-71
   
Finally, we will also generate a Word document with all the tables and figures:

.. literalinclude:: ../examples/example.py
   :lines: 74-75
   
That concludes prettyresults's tutorial! You can check the aspect of the generated web page
`here <https://anarthal.github.io/prettyresults-example/>`_.
