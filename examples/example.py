import pandas as pd
import os
import tempfile
from prettyresults import AnalysisContext

def main():
    # Read the data to analyze (standard Pandas)
    csv_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data.csv')
    df = pd.read_csv(csv_path)
    
    # Create an analysis context. This will keep track of results, and has methods to
    # generate the web page and the Word document.
    ctx = AnalysisContext()
    
    # Results have an ID and a name. The ID identifies the result, while the name is intended
    # to be read by humans. Results are organized hierarchically, in a tree-like structure.
    # The root of the tree has always an ID of 'root'. Results can be of several types: figures,
    # tables, containers (results that have children results)... The root result is a container.
    root_result = ctx.get_result('root')
    
    # Container results have several add_<result-type> methods, which create a result and add
    # it as a child of the container. You must pass at least the child result id and the child name.
    region_result = root_result.add_container('region', 'Region')
    channel_result = root_result.add_container('channel', 'Channel')
    region_channel_result = root_result.add_container('channel-by-region', 'Sales channel by region')

    # Analysis for Region
    df['Region'].value_counts().plot.bar()
    
    # add_figure will add a figure result, using the current active figure
    # (the bar plot, in our case)
    region_result.add_figure('bar', 'Frequency bar chart')
    
    # add_series_table will add a table result from a pandas Series object
    region_result.add_series_table('freqs',
                                   'Frequency table',
                                   df['Region'].value_counts())
    
    # Let's repeat the same analysis for another variable. Note that result IDs must only
    # be unique within the container they are placed in - there is no problem with the two bar
    # graphs to have the same 'bar' ID.
    df['Sales Channel'].value_counts().plot.bar()
    channel_result.add_figure('bar', 'Frequency bar chart')
    channel_result.add_series_table('freqs',
                                   'Frequency table',
                                   df['Sales Channel'].value_counts())
    

    # Analyze the interactions between the above variables.
    crosstab = pd.crosstab(df['Region'], [df['Sales Channel']])
    region_channel_result.add_dataframe_table('freq', 'Frequency table', crosstab)
    crosstab.plot.bar()
    region_channel_result.add_figure('bar', 'Bar chart')
    
    # We've added a bunch of results now. The result tree will look like this:
    # root
    #    root.region
    #       root.region.bar
    #       root.region.freq
    #    root.channel
    #       root.channel.bar
    #       root.channel.freq
    #    root.channel-by-region
    #       root.channel-by-region.freq
    #       root.channel-by-region.bar
    #
    # The generated web page and Word document will represent this layout.
    
    # Generate the web and open a browser tab to view it.
    web_directory = os.path.join(tempfile.gettempdir(), 'prettyresults_web')
    ctx.generate_web(web_directory, open_browser=True, overwrite=True)
    
    # Generate the Word document.
    word_path = os.path.join(tempfile.gettempdir(), 'results.docx')
    ctx.generate_word(word_path)

    # Generate another Word document only including region and channel results,
    # but not region-vs-channel.
    word_path_reduced = os.path.join(tempfile.gettempdir(), 'results_reduced.docx')
    ctx.generate_word(word_path_reduced, ['root.region', 'root.channel'])

if __name__ == '__main__':
    main()