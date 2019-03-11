import pandas as pd
import os
import tempfile
from analyzer import AnalysisContext

def row_identifier(row):
    return row['Order ID']

def main():
    # Where result files will be stored. Images, table data... will be stored here.
    result_directory = os.path.join(tempfile.gettempdir(), 'analyzer_example')
    
    # Read the data to analyze (standard Pandas)
    csv_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data.csv')
    df = pd.read_csv(csv_path)
    
    # Create an analysis context. This will keep track of results, and has methods to
    # store the results in disk, generating the web page and the Word document.
    ctx = AnalysisContext([], [], result_directory, row_identifier)
    
    # Results have an ID and a name. The ID identifies the result, while the name is intended
    # to be read by humans. Results are organized hierarchically, in a tree-like structure.
    # The root of the tree has always an ID of 'root'. Results can be of several types: figures,
    # tables, containers (results that have children results)... The root result is a container.
    root_result = ctx.get_result('root')
    
    # Container results have several add_<result-type> methods, which create a result and add
    # it as a child of the container. You must pass at least the child result id and the child name.
    singlevar_result = root_result.add_container('singlevar', 'Single variable descriptive analysis')
    interactions_result = root_result.add_container('inter', 'Interactions')
    
    # Let's do some basic descriptive analysis
    region_result = singlevar_result.add_container('region', 'Region')
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
    channel_result = singlevar_result.add_container('channel', 'Channel')
    df['Sales Channel'].value_counts().plot.bar()
    channel_result.add_figure('bar', 'Frequency bar chart')
    channel_result.add_series_table('freqs',
                                   'Frequency table',
                                   df['Sales Channel'].value_counts())
    

    # Analyze the interactions between the above variables.
    region_channel_result = interactions_result.add_container('channel-by-region', 'Sales channel by region')
    crosstab = pd.crosstab(df['Region'], [df['Sales Channel']])
    region_channel_result.add_dataframe_table('freq', 'Frequency table', crosstab)
    crosstab.plot.bar()
    region_channel_result.add_figure('bar', 'Bar chart')
    
    # We've added a bunch of results now. The result tree will look like this:
    # root
    #   root.singlevar
    #      root.singlevar.region
    #         root.singlevar.region.bar
    #         root.singlevar.region.freq
    #      root.singlevar.channel
    #         root.singlevar.channel.bar
    #         root.singlevar.channel.freq
    #   root.inter
    #      root.inter.channel-by-region
    #         root.inter.channel-by-region.freq
    #         root.inter.channel-by-region.bar
    #
    # The generated web page and Word document will represent this layout.
    
    # This will write the results to the result directory. It must be called before generating the web
    # or the word, as these rely on the result directory being written.
    ctx.dump_results()
    
    # This will copy the relevant files to generate the web and will open a browser tab
    # to view it.
    ctx.generate_web(open_browser=True)
    
    # Generate the Word document.
    ctx.generate_word(os.path.join(result_directory, 'results.docx'))


if __name__ == '__main__':
    main()