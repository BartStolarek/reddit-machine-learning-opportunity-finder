# Reddit ML Opportunity Finder

A Python script that scans Reddit for discussions about potential AI/ML applications. Using fuzzy matching, it identifies posts and comments where users express interest in AI/ML solutions, helping find potential development opportunities.

## Features

- Fuzzy text matching to identify AI/ML-related discussions
- Comprehensive subreddit coverage (400+ subreddits across various categories)
- Statistical analysis of match quality
- Separate tracking for posts and comments
- Rate limit compliance
- Results saved to timestamped CSV files

## Setup

### Prerequisites

- Python 3.x
- Reddit account
- Reddit API credentials

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

Required packages:
- praw
- python-dotenv
- pandas
- fuzzywuzzy
- python-Levenshtein (optional, for better performance)

3. Set up Reddit API credentials:
   - Visit https://www.reddit.com/prefs/apps/
   - Create a new application (script type)
   - Note your client ID and secret

4. Create a `.env` file with your credentials:
```plaintext
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
REDDIT_USER_AGENT="your user agent string"
```

## Usage

Run the script:
```bash
python script.py
```

The script will:
1. Verify environment variables
2. Initialize Reddit connection
3. Search each subreddit for:
   - Posts matching target phrases
   - Comments matching target phrases
4. Generate statistics about match quality
5. Save results to CSV files

### Target Phrases

Current target phrases (customizable in `get_target_phrases()`):
```python
[
    "would be cool to have an AI for that",
    "need a machine learning model for this",
    "could use AI to automate this"
]
```

### Fuzzy Matching

The script uses fuzzy string matching with:
- Partial ratio matching for substring matches
- Token sort ratio for word order variations
- Configurable threshold (default: 70%)

## Output Files

### Posts CSV (`ml_opportunities_posts_[subreddit]_[timestamp].csv`):
- `type`: Content type
- `title`: Post title
- `text`: Post content
- `url`: Reddit post URL
- `author`: Username
- `score`: Post score
- `created_utc`: Timestamp

### Comments CSV (`ml_opportunities_comments_[subreddit]_[timestamp].csv`):
- `type`: Content type
- `text`: Comment content
- `url`: Reddit comment URL
- `author`: Username
- `score`: Comment score
- `created_utc`: Timestamp

## Statistics

The script generates match quality statistics for both posts and comments:
- Average match ratio
- Maximum match ratio
- Minimum match ratio
- Standard deviation
- Total count

## Rate Limiting

The script includes built-in delays:
- 0.5 seconds between submissions
- 5 seconds between subreddits

## Subreddit Coverage

The script searches an extensive list of subreddits across categories including:
- Business/Entrepreneurship
- Technology
- General Interest
- Media/Entertainment
- Educational
- Specific Interest Communities

Full list available in the script's `subreddits` list.

## Error Handling

- Environment variable verification
- Connection status checking
- Individual subreddit failures don't stop entire script

## License

MIT License

## Contributing

Contributions welcome! Key areas for improvement:
- Additional target phrases
- Subreddit list refinement
- Match quality optimization
- Output format enhancements

---

### Development Notes

#### Modifying Search Criteria

To modify the search criteria, edit the `get_target_phrases()` function:

```python
def get_target_phrases():
    """Define phrases to look for"""
    return [
        "would be cool to have an AI for that",
        "need a machine learning model for this",
        "could use AI to automate this"
        # Add more phrases here
    ]
```

#### Adjusting Fuzzy Match Threshold

The default fuzzy match threshold is 70%. To adjust this, modify the `threshold` parameter in `is_similar_to_target()`:

```python
def is_similar_to_target(text, target_phrases, threshold=70):  # Adjust threshold here
```

#### Adding New Subreddits

To add new subreddits to scan, append to the `subreddits` list in the `main()` function:

```python
subreddits = [
    'SmallBusiness',
    'Entrepreneur',
    # Add more subreddits here
]
```