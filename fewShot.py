import json
import pandas as pd

class FewShotPost:
    def __init__(self):
        self.df= None
        self.unique_tags = None
        self.load_posts(r"data\pre_processed_data.json")
    
    def load_posts(self, file_path):
        with open(file_path, encoding = "utf-8") as file:
            posts = json.load(file)
            self.df = pd.json_normalize(posts)
            self.df['length'] = self.df['line_count'].apply(self.categorize_legnth)
            #self.df = df
            all_tags = self.df['tags'].apply(lambda x: x).sum()
            self.unique_tags = list(set(all_tags))
            return self.df
        
    def categorize_legnth(self, line_cnt):
        if line_cnt<=5: 
            return "Short"
        elif line_cnt>5 and line_cnt<=10:
            return "Medium"
        else: return "Long"

    def get_filtered_posts(self, length, language, tag):
        df_filtered = self.df[
            (self.df['tags'].apply(lambda tags : tag in tags)) &  # Tags contain 'Influencer'
            (self.df['language'] == language) &  # Language is 'English'
            (self.df['length'] == length)  # Line count is less than 5
        ]
        return df_filtered.to_dict(orient='records')
    
    def get_tags(self):
        return self.unique_tags
if __name__ == "__main__":
    fsp = FewShotPost()
    df=fsp.load_posts(r"D:\LLMs\groc\data\pre_processed_data.json")
    print(df)
    print(fsp.get_filtered_posts("Short",'English',"Career"))

