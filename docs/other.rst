FAQ and other topics
====================================

.. _copying_web:

Copying the web page around
---------------------------

The web page is completely stand-alone. You can copy it by copying the
directory you passed to :meth:`prettyresults.AnalysisContext.generate_web` and
open it in any computer using a web browser. Visualizing the web does NOT
need Inernet access.


.. _browser_compatibility:

Web page browser compatibility
------------------------------

The web page should be compatible with any major web browser. It has been
tested under Firefox 67 and Chrome 75.


.. _result_ids:

Result IDs: qualified and unqualified
-------------------------------------

Each result has an ID that uniquely identifies it. In this context, IDs can be of two types:

- **Unqualified ID**. An unqualified ID identifies a result in the context of its container.
  If a container result has three children, their unqualified IDs must be different. However,
  they may be the same as other container's children. Whenever you create a new result using
  :class:`prettyresults.results.ContainerResult` add_xxxxx methods, the ID you provide is an
  unqualified ID. An unqualified ID is similar to a relative path in a filesystem.
- **Qualified ID**. A qualified ID uniquely identifies a result within an AnalysisContext.
  It is the concatenation of all parent container unqualified IDs, separated by dots.
  It is similar to an absolute path in a filesystem.

In `this example <https://anarthal.github.io/prettyresults-example/>`_ (see :ref:`tutorial`
for snippets of the source code), we have the following results:

- :code:`root`. This is the root of the result tree. It is implicitly added when the AnalysisContext
  gets created.

    - :code:`region`. A ContainerResult with:

        - :code:`bar`. A FigureResult with a bar plot.
        - :code:`freqs`. A TableResult with a frequency table.

    - :code:`channel`. A ContainerResult with:

        - :code:`bar`. A FigureResult with a bar plot.
        - :code:`freqs`. A TableResult with a frequency table.

    - :code:`channel-by-region`. A ContainerResult with:

        - :code:`bar`. A FigureResult with a bar plot.
        - :code:`freqs`. A TableResult with a frequency table.

All the above IDs are unqualified. Note that :code:`bar` and :code:`freqs` are repeated,
which is not an issue because the results are under different containers. The above result structure
translates into the following qualified IDs:

- :code:`root`

    - :code:`root.region`

        - :code:`root.region.bar`
        - :code:`root.region.freqs`
    
    - :code:`root.channel`

        - :code:`root.channel.bar`
        - :code:`root.channel.freqs`

    - :code:`root.channel-by-region`

        - :code:`root.channel-by-region.bar`
        - :code:`root.channel-by-region.freqs`

Note that these are unique across the entire AnalysisContext. Qualified IDs are employed,
for example, to retrieve results in :meth:`prettyresults.AnalysisContext.get_result`.

.. warning::
    Unqualified IDs **must not contain the dot character**. Trying to create a result
    that fails to fulfill this condition will result in an exception.



.. _generating_word:

Generating a Word with a subset of the results
----------------------------------------------

If you have a large number of results, including all of them in a single Word
document may be impractical. You can use :meth:`prettyresults.AnalysisContext.generate_word`
second parameter to reduce the number of results that get included in your Word document.

Taking the example in the :ref:`tutorial`, to generate a Word document that includes region
and channel data, but not the cross table:

.. literalinclude:: ../examples/example.py
   :lines: 77-80
