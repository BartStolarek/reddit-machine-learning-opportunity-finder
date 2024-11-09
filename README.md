# Reddit ML Opportunity Finder

A Python script that searches Reddit for posts and comments from people looking for machine learning or AI development help. The script searches multiple relevant subreddits and saves the results to CSV files for easy review.

## Features

- Searches multiple tech and business subreddits
- Looks for both posts and comments mentioning ML/AI needs
- Saves results to timestamped CSV files
- Respects Reddit's rate limits
- Configurable search keywords and subreddits

## Setup

### Prerequisites

- Python 3.10+
- A Reddit account
- Reddit API credentials (instructions below)

### Installation

1. Clone this repository:
```bash
git clone [your-repo-url]
cd reddit-ml-opportunity-finder
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a Reddit application:
   - Go to https://www.reddit.com/prefs/apps/
   - Click "create another app" or "create application"
   - Select "script"
   - Fill in any name you like
   - Set the redirect URI to `http://localhost:8080`
   - Click "create app"

4. Create a `.env` file in the project root with your Reddit credentials:
```
REDDIT_CLIENT_ID=your_client_id          # The string under your app name
REDDIT_CLIENT_SECRET=your_client_secret  # The string labeled 'secret'
REDDIT_USERNAME=your_username            # Your Reddit username
REDDIT_PASSWORD=your_password            # Your Reddit password
REDDIT_USER_AGENT="redditdev scraper by u/your_username"
```

## Usage

Run the script:
```bash
python script.py
```

The script will:
1. Search each configured subreddit
2. Look for posts and comments matching ML/AI keywords
3. Save results to CSV files named:
   - `ml_opportunities_posts_[subreddit]_[timestamp].csv`
   - `ml_opportunities_comments_[subreddit]_[timestamp].csv`

## Customization

### Modify Subreddits
Edit the `subreddits` list in `main()` to add or remove subreddits to search:
```python
subreddits = [
    'startups',
    'entrepreneur',
    'smallbusiness',
    # Add more subreddits here
]
```

### Modify Search Keywords
Edit the `get_relevant_keywords()` function to modify what terms to search for:
```python
return [
    "need machine learning",
    "need ml model",
    # Add more keywords here
]
```

## Output Format

The script generates two types of CSV files:

### Posts CSV
- type: Type of content
- title: Post title
- text: Post content
- url: Link to the post
- author: Reddit username
- score: Post score
- created_utc: Timestamp
- keyword_matched: Which keyword triggered this match

### Comments CSV
- type: Type of content
- text: Comment content
- url: Link to the comment
- author: Reddit username
- score: Comment score
- created_utc: Timestamp
- keyword_matched: Which keyword triggered this match

## Notes

- The script respects Reddit's rate limits with built-in delays
- Results are saved with timestamps to prevent overwriting
- Errors for individual subreddits won't stop the entire script
- Set up a `.gitignore` file to prevent committing your `.env` file

## License

MIT License# reddit-machine-learning-opportunity-finder
# reddit-machine-learning-opportunity-finder
