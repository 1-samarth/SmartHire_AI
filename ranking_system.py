import pandas as pd

def rank_candidates(candidate_list):

    df = pd.DataFrame(candidate_list)

    df = df.sort_values(by="Score", ascending=False)

    df["Rank"] = range(1, len(df)+1)

    return df