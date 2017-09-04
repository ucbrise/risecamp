import boto3

rise_camp_bucket = "ampcamp-data"

def check_result_1(result):
    if result:
        if result == "hello world!":
            print("Correct!")
        else:
            print("Hmm...the result is not 'hello world!'")
    else:
        print("Hmm...the result is None, not 'hello world!'")

def check_result_2(result):
    if result:
        if result == "hello world!":
            print("Correct!")
        else:
            print("Hmm...the result is not 'hello world!'")
    else:
        print("Hmm...the result is None, not 'hello world!'")

def plot_pywren_execution(futures):
    from IPython import get_ipython
    get_ipython().run_line_magic('pylab', 'inline')
    import pylab
    import seaborn as sns
    import pandas as pd
    sns.set_style('whitegrid')
    import os
    import matplotlib.patches as mpatches
    import numpy as np

    def collect_execution_info(futures):
        results = [f.result() for f in futures]
        run_statuses = [f.run_status for f in futures]
        invoke_statuses = [f.invoke_status for f in futures]
        return {'results' : results,'run_statuses' : run_statuses, 'invoke_statuses' : invoke_statuses}

    info = collect_execution_info(futures)

        # visualization
    def visualize_execution(info):
        # preparing data
        run_df = pd.DataFrame(info['run_statuses'])
        invoke_df = pd.DataFrame(info['invoke_statuses'])
        info_df = pd.concat([run_df, invoke_df], axis=1)
        
        def remove_duplicate_columns(df):
            Cols = list(df.columns)
            for i,item in enumerate(df.columns):
                if item in df.columns[:i]: Cols[i] = "toDROP"
            df.columns = Cols
            return df.drop("toDROP",1)

        info_df = remove_duplicate_columns(info_df)
        
        total_tasks = len(info_df)
        y = np.arange(total_tasks)
            
        time_offset = np.min(info_df.host_submit_time)
        fields = [('host submit', info_df.host_submit_time - time_offset), 
                  ('task start', info_df.start_time - time_offset ), 
                  ('setup done', info_df.start_time + info_df.setup_time - time_offset), 
                  ('task done', info_df.end_time - time_offset), 
                  ('results returned', info_df.download_output_timestamp - time_offset)
                 ]

        # create plotting env
        fig = pylab.figure(figsize=(10, 6))
        ax = fig.add_subplot(1, 1, 1)

        # plotting
        patches = []
        palette = sns.color_palette("deep", 6)
        point_size = 20
        for f_i, (field_name, val) in enumerate(fields):
            ax.scatter(val, y, c=palette[f_i], edgecolor='none', s=point_size, alpha=1)
            patches.append(mpatches.Patch(color=palette[f_i], label=field_name))
        ax.set_xlabel('wallclock time (sec)')
        ax.set_ylabel('task')
        
        # legend
        legend = pylab.legend(handles=patches, 
                              loc='upper left', frameon=True)
        legend.get_frame().set_facecolor('#FFFFFF')

        # y ticks
        plot_step = 5
        y_ticks = np.arange(total_tasks//plot_step + 2) * plot_step
        ax.set_yticks(y_ticks)
        for y in y_ticks:
            ax.axhline(y, c='k', alpha=0.1, linewidth=1)
        
        # formatting
        ax.grid(False)
        fig.tight_layout()

    visualize_execution(info)


def pywren_read_data(bucket, key):
    s3client = boto3.client("s3")
    r = s3client.get_object(Bucket=bucket, Key=key)
    return r['Body'].read().decode()


def list_keys_with_prefix(bucket, prefix):
    """
    Return a list of keys for the given prefix.
    :param prefix: Prefix to filter object names.
    :return: List of keys in bucket that match the given prefix.
    :rtype: list of str
    """
    s3client = boto3.client("s3")
    paginator = s3client.get_paginator('list_objects_v2')
    operation_parameters = {'Bucket': bucket,
                            'Prefix': prefix}
    page_iterator = paginator.paginate(**operation_parameters)

    key_list = []
    for page in page_iterator:
        for item in page['Contents']:
            key_list.append(item['Key'])

    items_to_remove = [prefix, prefix+"/", prefix+"/part-00000", prefix+"part-00000"]

    return [item for item in key_list if item not in items_to_remove]
