import pandas as pd
import numpy as np
from pathlib import Path
import os
import matplotlib.pyplot as plt
# plt.style.use('../../style/berkeley.mplstyle')
import textwrap
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import gaussian_kde
SEED = 1
rng = np.random.default_rng(seed=SEED)

COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']


## Plotting utilities

def label_bars(bars,ax,horz=False):
    for bar in bars:
        color = bar.get_facecolor()
        if horz:
            label = f"{100*bar.get_width():.0f}%"
            x = bar.get_width()+0.01
            y = bar.get_y() + bar.get_height()/2
            ha = 'left'
            va = 'center'
        else:
            label = f"{100*bar.get_height():.0f}%"
            x = bar.get_x() + bar.get_width()/2
            y = bar.get_height()+0.01
            ha = 'center'
            va = 'bottom'
        ax.text(
            x, y, label, ha=ha, va=va,
            fontsize=10, fontweight='bold', color=color
        )


## Question text processing utilities

def clear_questions():
    with open("out/questions.csv", '+w') as f:
        print(f"", file=f)         
    with open("out/questions_shortened.csv", '+w') as f:
        print(f"", file=f)         

def title_processor(question_pre,question_post,qtype='proficiency'):
    if qtype == 'proficiency':
        title = question_pre.replace("Please rate your level of proficiency in the following areas.", "")
    elif qtype == 'agree':
        title = question_pre.replace("Please select your level of agreement or disagreement with the following statement:", "")
        title = question_pre.replace("Please select your level of agreement or disagreement with the following statements:", "")
    else:
        title = question_pre
    title = title.lstrip(".").strip()
    title = textwrap.fill(title,width=60)
    return title

def write_shortened_question(col,data,qtype):
    if col in data.keys():
        question = question_pre = question_post = data[col][0]
    else:
        question_pre = data[f"{col}_pre"][0]
        question_post = data[f"{col}_post"][0]
    if isinstance(question_pre,str) and isinstance(question_post,str):
        question = title_processor(question_pre,question_post,qtype)
        with open("out/questions_shortened.csv", '+a') as f:
            print(f'"{question}"', file=f) 
    else:
        with open("out/questions_shortened.csv", '+a') as f:
            print('', file=f) 


def write_questions(col,data):
    if col in data.keys():
        question = data[col][0]
        with open("out/questions.csv", '+a') as f:
            print(f'{col}, "{question}"', file=f)   
    else:
        question_pre = data[f"{col}_pre"][0]
        question_post = data[f"{col}_post"][0]
        with open("out/questions.csv", '+a') as f:
            print(f'{col}, "{question_pre}", "{question_post}"', file=f)   


## Pre-post comparison utilities

def multi_axis_barh(cols,labels,qtype,results,nrows=3,fig_title=None,barwidth=0.8):
    """
    Create a single multi-axis plot for all pre-post comparisons
    of a specific question type
    """
    width = barwidth
    fig,ax = plt.subplots(nrows,int(len(cols)//nrows), figsize=(12,8), constrained_layout=True)
    for i,col in enumerate(cols):
        max_x = 0
        axi = ax[i%nrows,i//nrows]
        for j,mode in enumerate(['pre','post']):
            data = results[f"{col}_{mode}"]
            # question = data[0]
            # importID = data[1]
            responses = data[2:].value_counts(normalize=True, dropna=True)
            bar_lengths = np.array([responses[label] if label in responses.keys() else 0 for label in labels])
            max_x = max(max_x, max(bar_lengths))
            y = -2*np.arange(len(bar_lengths))
            bars = axi.barh(y-(2*j-1)*width/2, bar_lengths, height=width, label=f"{mode.capitalize()}-Survey")
            label_bars(bars,axi,horz=True)
        question_pre = results[f"{col}_pre"][0]
        question_post = results[f"{col}_post"][0]
        title = title_processor(question_pre,question_post,qtype=qtype)
        axi.set_ylabel(title)
        if i//nrows==0:
            axi.set_yticks(y,labels=[str(l) for l in labels])
        else:
            axi.set_yticks([])
        axi.set_xlim((0,max_x*1.25))
        axi.set_xticks([])
    ax[-1,0].legend(loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5,-0.1))
    fig.suptitle(fig_title)
    return fig
      
def single_select_compare_tables(col,compare_data,labels,out_dirs,filters=None,filter_labels=None):
    """
    Pre-post comparison tables.
    Filters: list of QuestionIDs by which the results should be filtered
    """
    for mode in ['pre','post']:
        if filters is not None:
            col_data = compare_data[[f"{col}_{mode}"]+[f"{qid}_{mode}" for qid in filters]]

            filtered_tables = []
            for fil in filters:
                filtered_responses = col_data[2:].groupby(f"{fil}_{mode}")[f"{col}_{mode}"].value_counts(normalize=True, dropna=True)
                if filter_labels is not None and fil in filter_labels:
                    unique_filter_values = filter_labels[fil]
                else:
                    # use master labels if provided, otherwise fallback to data scan
                    unique_filter_values = pd.concat([
                        compare_data[f"{fil}_pre"][2:],
                        compare_data[f"{fil}_post"][2:]
                    ]).dropna().unique()
                full_index = pd.MultiIndex.from_product(
                    [unique_filter_values, labels], 
                    names=[f"{fil}_{mode}", f"{col}_{mode}"]
                )
                filtered_responses = filtered_responses.reindex(full_index, fill_value=0)
                filtered_responses = filtered_responses.unstack(level=1)
                filtered_responses = filtered_responses.reindex(columns=labels).dropna(how='all')
                # calculate and append N={N} to category row names
                counts = col_data[2:].groupby(f"{fil}_{mode}")[f"{col}_{mode}"].count()
                filtered_responses.index = [
                    f"{idx} (N={counts.get(idx, 0)})" if pd.notna(idx) else idx 
                    for idx in filtered_responses.index
                ]
                filtered_tables.append(filtered_responses)
            overall_counts = col_data[2:][f"{col}_{mode}"].value_counts(normalize=True)
            overall_counts = overall_counts.reindex(labels, fill_value=0)
            overall_counts.index = pd.MultiIndex.from_product(
                [['Overall'], labels], 
                names=["Overall", f"{col}_{mode}"]
            )
            overall_counts = overall_counts.unstack(level=1)
            # calculate and append N={N} to the "overall" row ---
            overall_n = col_data[2:][f"{col}_{mode}"].count()
            overall_counts.index = [f"Overall (N={overall_n})"]
            filtered_tables.append(overall_counts)
            responses = pd.concat(filtered_tables)
        else:
            col_data = compare_data[f"{col}_{mode}"]
            responses = col_data[2:].value_counts(normalize=True, dropna=True)
            responses = responses.reindex(labels, fill_value=0)
        responses_to_csv = responses.copy()
        if filters is None:
            # For unfiltered tables, rows are answer choices. Append total N to the header instead
            total_n = col_data[2:].count()
            responses_to_csv.index.name = f"{compare_data[f'{col}_{mode}'][0]} (N={total_n})"
        else:
            responses_to_csv.index.name = compare_data[f"{col}_{mode}"][0]
        responses_to_csv.index.name = compare_data[f"{col}_{mode}"][0]
        responses_to_csv = responses_to_csv.drop(index=np.nan, errors='ignore')
        responses_to_csv.to_csv(out_dirs[f"compare_{mode}"]/f"{col}.csv", index=True)

def single_select_compare_plots(col,compare_data,labels,out_dirs,width=0.8,colors=['#004AAE','#FFC31B']):
    """
    Pre-post comparison using vertical bar charts
    """
    fig,ax = plt.subplots(figsize=(6,4), constrained_layout=True)
    max_y = 0
    for i,mode in enumerate(['pre','post']):
        col_data = compare_data[f"{col}_{mode}"]
        responses = col_data[2:].value_counts(normalize=True, dropna=True)
        for label in labels:
            if label not in responses.keys():
                responses[label]=0
        responses = responses.reindex(labels)
        bar_heights = np.array([responses[label] for label in labels])
        max_y = max(max_y, max(bar_heights))          
        x = 2*np.arange(len(bar_heights))
        label = f"{mode.capitalize()}-Survey"
        bars = ax.bar(x+(2*i-1)*width/2, bar_heights, width=width, label=label, color=colors[i])
        label_bars(bars,ax)
    ax.set_ylim((0,max_y*1.1))
    ax.set_xticks(x,[str(l) for l in labels],rotation=45)
    ax.set_yticks([])
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.5), ncol=2, frameon=False)
    fig.savefig(out_dirs['comparison']/f"{col}.png", dpi=400, bbox_inches='tight')
    plt.close()

def single_select_pc(col,data,qtype,out_dirs,color='#004AAE'):
    """
    Pre-post comparison using parallel categories plots
    """
    question_pre = data[f"{col}_pre"][0]
    question_post = data[f"{col}_post"][0]
    fig = go.Figure(go.Parcats(
                            dimensions=[
                                {
                                    'label': 'Pre-Survey',
                                    'values': data.loc[2:,f"{col}_pre"],
                                },
                                {
                                    'label': 'Post-Survey',
                                    'values': data.loc[2:,f"{col}_post"],
                                }
                            ],
                            labelfont={'size':14,'family':'Arial'},
                            tickfont={'size':14,'family':'Arial'})
                    )
    fig.update_traces(line=dict(
        color=color
    ))
    title = title_processor(question_pre,question_post,qtype=qtype)
    title = title.replace("-\n","<br>")
    title = title.replace("\n","<br>")
    fig.update_layout(title={'text':f"{title}<br><br>",
                                'x':0.5,
                                'xanchor':'center',
                                'y':0.95,
                                'yanchor':'middle',
                                'font':{'family':'Arial'}},
                      margin=dict(l=100,r=100,t=100,b=20))
    fig.write_html(out_dirs['comparison']/f"{col}_pc.html")
    fig.write_image(out_dirs['comparison']/f"{col}_pc.png")

def multi_select_compare_tables(col,compare_data,labels,out_dirs,filters=None,filter_labels=None):
    for mode in ['pre','post']:
        col_name = f"{col}_{mode}"

        if filters is not None:
            filter_cols = [f"{qid}_{mode}" for qid in filters]
            col_data = compare_data[[col_name] + filter_cols].iloc[2:].copy()

            filtered_tables = []

            for fil in filters:
                fil_name = f"{fil}_{mode}"

                responses_exploded = col_data[[col_name, fil_name]].copy()
                responses_exploded[col_name] = (responses_exploded[col_name]
                                                .str.replace(', ', ': ', regex=False)
                                                .str.split(','))
                responses_exploded = responses_exploded.explode(col_name)

                # number of unique respondents in filtered group
                fil_counts = col_data[fil_name].value_counts()

                # number in each filter, response group
                counts = responses_exploded.groupby([fil_name, col_name]).size()

                responses_normalized = counts.div(fil_counts, level=fil_name)

                if filter_labels is not None and fil in filter_labels:
                    unique_filter_values = filter_labels[fil]
                else:
                    unique_filter_values = pd.concat([
                        compare_data[f"{fil}_pre"].iloc[2:],
                        compare_data[f"{fil}_post"].iloc[2:]
                    ]).dropna().unique()
                full_index = pd.MultiIndex.from_product(
                    [unique_filter_values, labels], 
                    names=[fil_name, col_name]
                )
                filtered_responses = responses_normalized.reindex(full_index, fill_value=0)
                filtered_responses = filtered_responses.unstack(level=1)
                filtered_responses = filtered_responses.reindex(columns=labels).dropna(how='all')
                # calculate and append N={N} to category row names
                filtered_responses.index = [
                    f"{idx} (N={int(fil_counts.get(idx, 0))})" if pd.notna(idx) else idx 
                    for idx in filtered_responses.index
                ]
                filtered_tables.append(filtered_responses)
            overall_n = len(col_data[col_name].dropna())
            overall_exploded = col_data[col_name].str.split(',').explode()
            if overall_n > 0:
                overall_counts = overall_exploded.value_counts() / overall_n
            else:
                overall_counts = pd.Series(0, index=labels)
            overall_counts = overall_counts.reindex(labels, fill_value=0).to_frame().T
            # append N={N} to Overall row
            overall_counts.index = [f'Overall (N={overall_n})']
            filtered_tables.append(overall_counts)
            responses_to_csv = pd.concat(filtered_tables)
        else:
            responses = compare_data[col_name].iloc[2:].dropna()
            n_responses = len(responses)
            exploded = responses.str.replace(', ', ': ', regex=False).str.split(',').explode()
            responses_to_csv = (exploded.value_counts() / n_responses).reindex(labels, fill_value=0)

        responses_to_csv = responses_to_csv.drop(index=np.nan, errors='ignore')

        if isinstance(responses_to_csv, pd.Series):
            responses_to_csv = responses_to_csv.reset_index()

        # handle index header naming based on filter status ---
        if filters is None:
            total_n = len(compare_data[col_name].iloc[2:].dropna())
            responses_to_csv.index.name = f"{compare_data[f'{col}_{mode}'][0]} (N={total_n})"
        else:
            responses_to_csv.index.name = compare_data[f"{col}_{mode}"][0]
        responses_to_csv.to_csv(out_dirs[f"compare_{mode}"]/f"{col}.csv", index=True)



## Pre or post-only utilities

def single_select_tables(col, data, labels, out_dir, filters=None, filter_labels=None):
    """
    Pre or post-only tables with optional filtering and sample size reporting.
    Expects `data` to be the full DataFrame where rows 0 and 1 contain metadata/titles.
    """
    if filters is not None:
        filtered_tables = []
        for fil in filters:
            # Use master labels if provided, otherwise fallback to active data categories
            if filter_labels is not None and fil in filter_labels:
                unique_filter_values = filter_labels[fil]
            else:
                unique_filter_values = data[fil].iloc[2:].dropna().unique()
            
            # Calculate proportions within the filtered slices
            filtered_responses = data.iloc[2:].groupby(fil)[col].value_counts(normalize=True, dropna=True)
            
            # Build the complete matrix framework
            full_index = pd.MultiIndex.from_product(
                [unique_filter_values, labels], 
                names=[fil, col]
            )
            filtered_responses = filtered_responses.reindex(full_index, fill_value=0)
            filtered_responses = filtered_responses.unstack(level=1)
            filtered_responses = filtered_responses.reindex(columns=labels).dropna(how='all')
            
            # Calculate and append N={N} to category row names
            counts = data.iloc[2:].groupby(fil)[col].count()
            filtered_responses.index = [
                f"{idx} (N={counts.get(idx, 0)})" if pd.notna(idx) else idx 
                for idx in filtered_responses.index
            ]
            filtered_tables.append(filtered_responses)
            
        # Calculate and append the Overall summary metrics row
        overall_n = data[col].iloc[2:].count()
        overall_counts = data[col].iloc[2:].value_counts(normalize=True).reindex(labels, fill_value=0)
        overall_counts = overall_counts.to_frame().T
        overall_counts.columns = labels
        overall_counts.index = [f"Overall (N={overall_n})"]
        
        filtered_tables.append(overall_counts)
        responses_to_csv = pd.concat(filtered_tables)
        
        # Set the main header question string and reset index for output
        responses_to_csv.index.name = data[col].iloc[0]
        responses_to_csv = responses_to_csv.reset_index()
    else:
        # Standard unfiltered branch (adjusted to read from the DataFrame)
        responses = data[col].iloc[2:].value_counts(normalize=True, dropna=True)
        for label in labels:
            if label not in responses.keys():
                responses[label] = 0
        responses = responses.reindex(labels)
        responses_to_csv = responses.copy()
        
        total_n = data[col].iloc[2:].count()
        responses_to_csv.index.name = f"{data[col].iloc[0]} (N={total_n})"
        responses_to_csv = responses_to_csv.reset_index(name=col)
        
    responses_to_csv.to_csv(out_dir / f"{col}.csv", index=False)

def single_select_plots(col,data,labels,width=0.8,color='#004AAE'):
    """
    Pre or post-only bar charts
    """
    fig,ax = plt.subplots(figsize=(6,4), constrained_layout=True)
    responses = data[2:].value_counts(normalize=True, dropna=True)
    for label in labels:
        if label not in responses.keys():
            responses[label]=0
    responses = responses.reindex(labels)
    bar_heights = np.array([responses[label] for label in labels])
    max_y = max(bar_heights)  
    x = np.arange(len(bar_heights))
    bars = ax.bar(x, bar_heights, width=width, label=label, color=color)
    label_bars(bars,ax)
    ax.set_ylim((0,max_y*1.1))
    ax.set_xticks(x,[str(l) for l in labels],rotation=45)
    ax.set_yticks([])
    return fig

def multi_select_tables(col, data, labels, out_dir, filters=None, filter_labels=None):
    """
    Pre or post-only multi-select tables with optional filtering and sample size reporting.
    Expects `data` to be the full DataFrame where rows 0 and 1 contain metadata/titles.
    """
    if filters is not None:
        col_data = data[[col] + filters].iloc[2:].copy()
        filtered_tables = []
        
        for fil in filters:
            responses_exploded = col_data[[col, fil]].copy()
            responses_exploded[col] = (responses_exploded[col]
                                            .str.replace(', ', ': ', regex=False)
                                            .str.split(','))
            responses_exploded = responses_exploded.explode(col)
            
            # Count the total unique respondents in each filtered category group
            fil_counts = col_data[fil].value_counts()
            counts = responses_exploded.groupby([fil, col]).size()
            responses_normalized = counts.div(fil_counts, level=fil)
            
            # Determine master category row lists
            if filter_labels is not None and fil in filter_labels:
                unique_filter_values = filter_labels[fil]
            else:
                unique_filter_values = col_data[fil].dropna().unique()
                
            full_index = pd.MultiIndex.from_product(
                [unique_filter_values, labels], 
                names=[fil, col]
            )
            filtered_responses = responses_normalized.reindex(full_index, fill_value=0)
            filtered_responses = filtered_responses.unstack(level=1)
            filtered_responses = filtered_responses.reindex(columns=labels).dropna(how='all')
            
            # Append N={N} to categories based on group respondent counts
            filtered_responses.index = [
                f"{idx} (N={int(fil_counts.get(idx, 0))})" if pd.notna(idx) else idx 
                for idx in filtered_responses.index
            ]
            filtered_tables.append(filtered_responses)
            
        # Calculate Overall statistics for multi-select options
        overall_n = len(col_data[col].dropna())
        overall_exploded = col_data[col].str.split(',').explode()
        if overall_n > 0:
            overall_counts = overall_exploded.value_counts() / overall_n
        else:
            overall_counts = pd.Series(0, index=labels)
            
        overall_counts = overall_counts.reindex(labels, fill_value=0).to_frame().T
        overall_counts.index = [f'Overall (N={overall_n})']
        filtered_tables.append(overall_counts)
        
        responses_to_csv = pd.concat(filtered_tables)
        responses_to_csv.index.name = data[col].iloc[0]
        responses_to_csv = responses_to_csv.reset_index()
    else:
        # Standard unfiltered multi-select branch (adjusted to read from the DataFrame)
        responses = [r.replace(', ', ': ') for r in data[col].iloc[2:] if pd.notna(r)]
        n_responses = len(responses)
        
        if n_responses > 0:
            responses_concat = ','.join(responses).split(',')
            responses_concat = [r.replace(': ', ', ') for r in responses_concat]
            responses_count = pd.Series(responses_concat).value_counts() / n_responses
        else:
            responses_count = pd.Series(0, index=labels)
            
        for label in labels:
            if label not in responses_count:
                responses_count[label] = 0
                
        responses_count = responses_count.reindex(labels)
        responses_to_csv = responses_count.copy()
        
        responses_to_csv.index.name = f"{data[col].iloc[0]} (N={n_responses})"
        responses_to_csv = responses_to_csv.reset_index(name=col)
        
    responses_to_csv.to_csv(out_dir / f"{col}.csv", index=False)

def slider_tables(col,data,out_dir):
    question = data[0]
    responses = [float(r) for r in data[2:] if r is not np.nan]
    responses_to_csv = pd.Series(responses)
    responses_to_csv.index.name = question.rstrip("\n")
    responses_to_csv.to_csv(out_dir/f"{col}.csv")

def slider_kde(col,data,kde=False):
    responses = [float(r) for r in data[2:] if r is not np.nan]
    kernel = gaussian_kde(responses)
    xs = np.linspace(0,100,1000)
    fig,ax = plt.subplots(figsize=(6,0.75), constrained_layout=True)
    ax.plot(xs,np.zeros(1000),color='#004AAE')
    if kde:
        ys = kernel(xs)
        ax.plot(xs,ys)
        ax.fill_between(xs,ys, color='#004AAE', alpha=0.3, zorder=1)
    ax.scatter(responses+rng.random(len(responses)),np.zeros(len(responses)), s=80, alpha=0.5, edgecolors='#004AAE', c='#004AAE')
    ax.set_xlim(-5,120)
    ax.set_ylim(bottom=-0.004,top=0.004)
    ax.set_xticks([0,100],['Discovery\nResearch Hub','Traditional Graduate\nResearch Structure'])
    ax.set_yticks([])
    return fig

def string_tables(col,data,out_dir):
    question = data[0]
    responses = [r for r in data[2:] if r is not np.nan]
    responses_to_csv = pd.Series(responses)
    responses_to_csv.index.name = question.rstrip("\n")
    responses_to_csv.to_csv(out_dir/f"{col}.csv")

def rank_tables(cols,data,qtype,labels,out_dir):
    ranking = {}
    question = data[cols[0]][0].replace("\n"," ").split(" - ")[0]
    for i,col in enumerate(cols):
        data = data[f"{col}"]
        _,col_name = data[0].rstrip("\n").replace("\n"," ").split(" - ")
        assert col_name==labels[qtype][i]
        ranks = [int(r) for r in data[2:] if r is not np.nan]
        ranking[col_name] = sum(ranks)
    responses_to_csv = pd.Series(ranking).sort_values()/len(ranks)
    responses_to_csv.index.name = question
    responses_to_csv.to_csv(out_dir/f"{col}.csv")

def rank_plots(cols,data,qtype,labels,n_ranks,out_dir):
    ranking = {}
    for i,col in enumerate(cols):
        data = data[f"{col}"]
        _,col_name = data[0].rstrip("\n").replace("\n"," ").split(" - ")
        assert col_name==labels[qtype][i]
        ranks = [int(r) for r in data[2:] if r is not np.nan]
        ranking[col_name] = sum(ranks)
    fig,ax = plt.subplots(figsize=(4.9,5.5), constrained_layout=True)
    ax.plot([0,0],[-1,-n_ranks],color=COLORS[1])
    # For the plot, there can be multiple items at the same rank.
    # Reverse the dictionary to allow sets of items.
    # Also, get the average ranking by dividing by number of responses.
    n_responses = len(ranks)
    ranking_to_plot = {rank/n_responses:set() for rank in ranking.values()}
    for item,rank in ranking.items():
        if item=='Research Symposium':
            item='Research symposium'
        ranking_to_plot[rank/n_responses].add(f"{item} ({rank/n_responses:.1f})")
    for rank,items in ranking_to_plot.items():
        ax.scatter(0,-rank,c=COLORS[1],alpha=0.5)
        ax.plot([-0.3,0.3],[-rank,-rank], c=COLORS[1])
        annotation = "\n".join(reversed(list(items)))
        if len(annotation)>58:
            annotation = textwrap.fill(annotation,50)
        ax.annotate(annotation,
                    xy=(0,-rank),
                    xytext=(0.4,-rank),
                    va='center',
                    fontweight="bold" if rank==min(ranking_to_plot.keys()) else None)
    if qtype == 'rank_format':
        ax.text(0.1,-1, '(most preferred)', va='center')
        ax.text(0.1,-n_ranks, '(least preferred)', va='center')
    else:
        ax.text(0.1,-1, '(most rewarding)', va='center')
        ax.text(0.1,-n_ranks, '(least rewarding)', va='center')
    ax.set_xticks([])
    ax.set_yticks(ticks=[-1,-n_ranks], labels=[1,n_ranks])
    ax.set_ylabel(f"Average Ranking") # (1: Highest; {n_ranks}: Lowest)")
    ax.set_xlim(-0.1,3)
    fig.savefig(out_dir/f"{col}.png", transparent=True, dpi=300)
    plt.close()
    



