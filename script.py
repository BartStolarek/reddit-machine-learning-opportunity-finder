import os
from dotenv import load_dotenv
import praw
import pandas as pd
from datetime import datetime
import time
from collections import defaultdict

# Load environment variables
load_dotenv()

def initialize_reddit():
    """Initialize Reddit instance using environment variables"""
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT'),
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD')
    )

def get_relevant_keywords():
    """Define keywords to search for"""
    return [
        "need machine learning",
        "need ml model",
        "machine learning help",
        "ai model needed",
        "looking for ml",
        "need ai developer",
        "machine learning developer",
        "ai engineer needed",
        "ml engineer needed",
        "machine learning consultation",
        "ai consultation",
        "build ai model",
        "build ml model"
    ]

def search_subreddit(reddit, subreddit_name, keywords, time_filter='week'):
    """Search a specific subreddit for keywords"""
    opportunities = defaultdict(list)
    subreddit = reddit.subreddit(subreddit_name)
    
    for keyword in keywords:
        # Search in posts
        for submission in subreddit.search(keyword, time_filter=time_filter):
            opportunities['posts'].append({
                'type': 'post',
                'title': submission.title,
                'text': submission.selftext,
                'url': f"https://reddit.com{submission.permalink}",
                'author': str(submission.author),
                'score': submission.score,
                'created_utc': datetime.fromtimestamp(submission.created_utc),
                'keyword_matched': keyword
            })
            
            # Search in comments
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                if any(kw.lower() in comment.body.lower() for kw in keywords):
                    opportunities['comments'].append({
                        'type': 'comment',
                        'text': comment.body,
                        'url': f"https://reddit.com{comment.permalink}",
                        'author': str(comment.author),
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'keyword_matched': keyword
                    })
        
        # Respect Reddit's rate limits
        time.sleep(2)
    
    return opportunities

def save_opportunities(opportunities, subreddit_name):
    """Save opportunities to CSV files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save posts
    if opportunities['posts']:
        df_posts = pd.DataFrame(opportunities['posts'])
        df_posts.to_csv(f'ml_opportunities_posts_{subreddit_name}_{timestamp}.csv', index=False)
    
    # Save comments
    if opportunities['comments']:
        df_comments = pd.DataFrame(opportunities['comments'])
        df_comments.to_csv(f'ml_opportunities_comments_{subreddit_name}_{timestamp}.csv', index=False)

def main():
    
    # List of subreddits to search
    subreddits = [
        'startups',
        'entrepreneur',
        'smallbusiness',
        'SaaS',
        'dataanalysis',
        'datascience',
        'BusinessIntelligence',
        'analytics',
        'artificial',
        'MachineLearning'
    ]
    
    # Initialize Reddit instance
    reddit = initialize_reddit()
    
    print("Checking environment variables:")
    print(f"CLIENT_ID exists: {'REDDIT_CLIENT_ID' in os.environ}")
    print(f"CLIENT_SECRET exists: {'REDDIT_CLIENT_SECRET' in os.environ}")
    print(f"USERNAME exists: {'REDDIT_USERNAME' in os.environ}")
    print(f"PASSWORD exists: {'REDDIT_PASSWORD' in os.environ}")
    print(f"USER_AGENT exists: {'REDDIT_USER_AGENT' in os.environ}")
    
    # Get keywords
    keywords = get_relevant_keywords()
    
    # Search each subreddit
    for subreddit_name in subreddits:
        print(f"Searching r/{subreddit_name}...")
        try:
            opportunities = search_subreddit(reddit, subreddit_name, keywords)
            save_opportunities(opportunities, subreddit_name)
            print(f"Found {len(opportunities['posts'])} posts and {len(opportunities['comments'])} comments in r/{subreddit_name}")
        except Exception as e:
            print(f"Error searching r/{subreddit_name}: {str(e)}")
        
        # Respect Reddit's rate limits
        time.sleep(5)

if __name__ == "__main__":
    main()