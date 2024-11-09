import os
from dotenv import load_dotenv
import praw
import pandas as pd
from datetime import datetime
import time
from collections import defaultdict
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

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

def get_target_phrases():
    """Define phrases to look for"""
    return [
        "would be cool to have an AI for that",
        "need a machine learning model for this",
        "could use AI to automate this"
    ]
    
def is_similar_to_target(text, target_phrases, threshold=70):
    """Check if text is similar to any target phrase using fuzzy matching"""
    text = text.lower()
    max_partial_ratio = 0
    max_sort_ratio = 0
    
    for phrase in target_phrases:
        # Check for partial ratio to catch substring matches
        partial_ratio = fuzz.partial_ratio(text, phrase.lower())
        sort_ratio = fuzz.token_sort_ratio(text, phrase.lower())
        
        max_partial_ratio = max(max_partial_ratio, partial_ratio)
        max_sort_ratio = max(max_sort_ratio, sort_ratio)
        
        if partial_ratio >= threshold:
            return True, partial_ratio
        # Check for token sort ratio to catch word order variations
        if sort_ratio >= threshold:
            return True, sort_ratio
    
    # Return the maximum ratios found
    return False, max(max_partial_ratio, max_sort_ratio)

def search_subreddit(reddit, subreddit_name, target_phrases, time_filter='week'):
    """Search a specific subreddit for similar phrases"""
    opportunities = defaultdict(list)
    subreddit = reddit.subreddit(subreddit_name)
    post_ratios = []
    comment_ratios = []

    # Get recent submissions
    for submission in subreddit.new(limit=100):  # Adjust limit as needed
        # Check submission title and text
        title_success, title_ratio = is_similar_to_target(submission.title, target_phrases)
        text_success, text_ratio = is_similar_to_target(submission.selftext, target_phrases)
        
        if title_success or text_success:
            opportunities['posts'].append({
                'type': 'post',
                'title': submission.title,
                'text': submission.selftext,
                'url': f"https://reddit.com{submission.permalink}",
                'author': str(submission.author),
                'score': submission.score,
                'created_utc': datetime.fromtimestamp(submission.created_utc)
            })
            
        # Store the higher of the two ratios
        post_ratios.append(max(title_ratio, text_ratio))
            
        # Search comments
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            comment_success, comment_ratio = is_similar_to_target(comment.body, target_phrases)
            if comment_success:
                opportunities['comments'].append({
                    'type': 'comment',
                    'text': comment.body,
                    'url': f"https://reddit.com{comment.permalink}",
                    'author': str(comment.author),
                    'score': comment.score,
                    'created_utc': datetime.fromtimestamp(comment.created_utc)
                })
            comment_ratios.append(comment_ratio)
        
        time.sleep(0.5)  # Respect rate limits within submission

    if post_ratios:
        print("-------------------------------------------------------------")
        print(f"Post Title & Text Ratio Stats:")
        print(f"Average: {sum(post_ratios) / len(post_ratios):.2f}")
        print(f"Max: {max(post_ratios)}")
        print(f"Min: {min(post_ratios)}")
        print(f"Standard Deviation: {pd.Series(post_ratios).std():.2f}")
        print(f"Count: {len(post_ratios)}")
    
    if comment_ratios:
        print("-------------------------------------------------------------")
        print(f"Comment Ratio Stats:")
        print(f"Average: {sum(comment_ratios) / len(comment_ratios):.2f}")
        print(f"Max: {max(comment_ratios)}")
        print(f"Min: {min(comment_ratios)}")
        print(f"Standard Deviation: {pd.Series(comment_ratios).std():.2f}")
        print(f"Count: {len(comment_ratios)}")
        print("-------------------------------------------------------------")
    
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
        'SmallBusiness',
        'Entrepreneur',
        'AccountingDepartment',
        'Organization',
        'Startup',
        'Sales',
        'Marketing',
        'Business',
        'gifs', 'behindthegifs', 'gif', 'Cinemagraphs', 'WastedGifs', 'educationalgifs',
        'perfectloops', 'highqualitygifs', 'gifsound', 'combinedgifs', 'retiredgif', 
        'michaelbaygifs', 'gifrecipes', 'mechanical_gifs', 'bettereveryloop', 'gifextra',
        'slygifs', 'gifsthatkeepongiving', 'wholesomegifs', 'noisygifs', 'brokengifs',
        'loadingicon', 'splitdepthgifs', 'blackpeoplegifs', 'whitepeoplegifs', 'asianpeoplegifs',
        'scriptedasiangifs', 'reactiongifs', 'shittyreactiongifs', 'chemicalreactiongifs',
        'physicsgifs', 'babyelephantgifs', 'weathergifs', 'pics', 'PhotoshopBattles',
        'perfecttiming', 'itookapicture', 'Pareidolia', 'ExpectationVSReality', 'dogpictures',
        'misleadingthumbnails', 'FifthWorldPics', 'TheWayWeWere', 'pic', 'nocontextpics',
        'miniworlds', 'foundpaper', 'images', 'screenshots', 'mildlyinteresting', 'interestingasfuck',
        'damnthatsinteresting', 'beamazed', 'reallifeshinies', 'thatsinsane', 'playitagainsam',
        'gentlemanboners', 'prettygirls', 'hardbodies', 'girlsmirin', 'thinspo', 'goddesses',
        'shorthairedhotties', 'fitandnatural', 'wrestlewiththeplot', 'skinnywithabs', 'bois',
        'GentlemanBonersGifs', 'asiancuties', 'asiangirlsbeingcute', 'PhotoshopBattles',
        'ColorizedHistory', 'reallifedoodles', 'HybridAnimals', 'colorization', 'amiugly',
        'roastme', 'rateme', 'uglyduckling', 'prettygirlsuglyfaces', 'wallpapers', 'wallpaper',
        'Offensive_Wallpapers', 'videos', 'youtubehaiku', 'artisanvideos', 'DeepIntoYouTube',
        'nottimanderic', 'praisethecameraman', 'killthecameraman', 'perfectlycutscreams',
        'donthelpjustfilm', 'abruptchaos', 'ShowerThoughts', 'DoesAnybodyElse', 'changemyview',
        'crazyideas', 'howtonotgiveafuck', 'tipofmytongue', 'quotes', 'casualconversation',
        'makenewfriendshere', 'relationship_advice', 'raisedbynarcissists', 'legaladvice',
        'bestoflegaladvice', 'advice', 'amitheasshole', 'mechanicadvice', 'toastme', 'needadvice',
        'IAmA', 'ExplainlikeIAmA', 'AMA', 'casualiama', 'de_Iama', 'whowouldwin', 'wouldyourather',
        'scenesfromahat', 'AskOuija', 'themonkeyspaw', 'shittysuperpowers', 'godtiersuperpowers',
        'decreasinglyverbose', 'whatisthisthing', 'answers', 'NoStupidQuestions', 'amiugly',
        'whatsthisbug', 'samplesize', 'tooafraidtoask', 'whatsthisplant', 'isitbullshit',
        'questions', 'morbidquestions', 'AskReddit', 'ShittyAskScience', 'TrueAskReddit',
        'AskScienceFiction', 'AskOuija', 'AskScience', 'askhistorians', 'AskHistory',
        'askculinary', 'AskSocialScience', 'askengineers', 'askphilosophy', 'askdocs',
        'askwomen', 'askmen', 'askgaybros', 'askredditafterdark', 'asktransgender',
        'askmenover30', 'tifu', 'self', 'confession', 'fatpeoplestories', 'confessions',
        'storiesaboutkevin', 'talesfromtechsupport', 'talesfromretail', 'techsupportmacgyver',
        'idontworkherelady', 'TalesFromYourServer', 'KitchenConfidential', 'TalesFromThePizzaGuy',
        'TalesFromTheFrontDesk', 'talesfromthecustomer', 'talesfromcallcenters',
        'talesfromthesquadcar', 'talesfromthepharmacy', 'starbucks', 'pettyrevenge',
        'prorevenge', 'nuclearrevenge', 'nosleep', 'LetsNotMeet', 'Glitch_in_the_Matrix',
        'shortscarystories', 'thetruthishere', 'UnresolvedMysteries', 'UnsolvedMysteries',
        'depression', 'SuicideWatch', 'Anxiety', 'foreveralone', 'offmychest', 'socialanxiety',
        'trueoffmychest', 'unsentletters', 'rant', 'YouShouldKnow', 'everymanshouldknow',
        'LearnUselessTalents', 'changemyview', 'howto', 'Foodforthought', 'educationalgifs',
        'lectures', 'education', 'college', 'GetStudying', 'teachers', 'watchandlearn',
        'bulletjournal', 'applyingtocollege', 'lawschool', 'todayilearned', 'wikipedia',
        'OutOfTheLoop', 'IWantToLearn', 'explainlikeimfive', 'explainlikeIAmA',
        'ExplainLikeImCalvin', 'anthropology', 'Art', 'redditgetsdrawn', 'heavymind',
        'drawing', 'graffiti', 'retrofuturism', 'sketchdaily', 'ArtPorn', 'pixelart',
        'artfundamentals', 'learnart', 'specart', 'animation', 'wimmelbilder', 'illustration',
        'streetart', 'place', 'breadstapledtotrees', 'chairsunderwater', 'painting',
        'minipainting', 'gamedev', 'engineering', 'ubuntu', 'cscareerquestions',
        'EngineeringStudents', 'askengineers', 'learnprogramming', 'compsci', 'java',
        'javascript', 'coding', 'machinelearning', 'howtohack', 'cpp', 'artificial',
        'python', 'learnpython', 'Economics', 'business', 'entrepreneur', 'marketing',
        'BasicIncome', 'business', 'smallbusiness', 'stocks', 'wallstreetbets',
        'stockmarket', 'environment', 'zerowaste', 'history', 'AskHistorians', 'AskHistory',
        'ColorizedHistory', 'badhistory', '100yearsago', 'HistoryPorn', 'PropagandaPosters',
        'TheWayWeWere', 'historymemes', 'castles', 'linguistics', 'languagelearning',
        'learnjapanese', 'french', 'etymology', 'law', 'math', 'theydidthemath', 'medicalschool',
        'medizzy', 'psychology', 'JordanPeterson', 'Science', 'AskScience', 'cogsci',
        'medicine', 'everythingscience', 'geology', 'Space', 'SpacePorn', 'astronomy',
        'astrophotography', 'aliens', 'rockets', 'spacex', 'nasa', 'biology', 'Awwducational',
        'chemicalreactiongifs', 'chemistry', 'physics', 'entertainment', 'fantheories',
        'Disney', 'obscuremedia', 'anime', 'manga', 'anime_irl', 'awwnime', 'TsundereSharks',
        'animesuggest', 'animemes', 'animegifs', 'animewallpaper', 'wholesomeanimemes',
        'pokemon', 'onepiece', 'naruto', 'dbz', 'onepunchman', 'ShingekiNoKyojin', 'yugioh',
        'BokuNoHeroAcademia', 'DDLC', 'berserk', 'hunterxhunter', 'tokyoghoul',
        'shitpostcrusaders', 'Books', 'WritingPrompts', 'writing', 'literature',
        'booksuggestions', 'lifeofnorman', 'poetry', 'screenwriting', 'freeEbooks',
        'boottoobig', 'hfy', 'suggestmeabook', 'lovecraft', 'comics', 'comicbooks',
        'polandball', 'marvel', 'webcomics', 'bertstrips', 'marvelstudios', 'defenders',
        'marvelmemes', 'avengers', 'harrypotter', 'batman', 'calvinandhobbes', 'xkcd',
        'DCComics', 'arrow', 'unexpectedhogwarts', 'spiderman', 'deadpool', 'KingkillerChronicle',
        'asoiaf', 'gameofthrones', 'freefolk', 'jonwinsthethrone', 'gameofthronesmemes',
        'daeneryswinsthethrone', 'asongofmemesandrage', 'lotr', 'lotrmemes', 'tolkienfans',
        'celebs', 'celebhub', 'EmmaWatson', 'jessicanigri', 'kateupton', 'alisonbrie',
        'EmilyRatajkowski', 'jenniferlawrence', 'alexandradaddario', 'onetruegod', 'joerogan',
        'keanubeingawesome', 'crewscrew', 'donaldglover', 'elonmusk', 'cosplay', 'cosplaygirls',
        'lego', 'boardgames', 'rpg', 'chess', 'poker', 'jrpg', 'DnD', 'DnDGreentext',
        'DnDBehindTheScreen', 'dndnext', 'dungeonsanddragons', 'criticalrole', 'DMAcademy',
        'dndmemes', 'magicTCG', 'modernmagic', 'magicarena', 'zombies', 'cyberpunk',
        'fantasy', 'scifi', 'starwars', 'startrek', 'asksciencefiction', 'prequelmemes',
        'empiredidnothingwrong', 'SequelMemes', 'sciencefiction', 'InternetIsBeautiful',
        'facepalm', 'wikipedia', 'creepyPMs', 'web_design', 'google', 'KenM',
        'bannedfromclubpenguin', 'savedyouaclick', 'bestofworldstar', 'discordapp',
        'snaplenses', 'tronix', 'instagramreality', 'internetstars', 'robinhood',
        'shortcuts', 'scams', 'tiktokcringe', 'crackheadcraigslist', '4chan', 'Classic4chan',
        'greentext', 'facepalm', 'oldpeoplefacebook', 'facebookwins', 'indianpeoplefacebook',
        'terriblefacebookmemes', 'insanepeoplefacebook', 'Tinder', 'OkCupid', 'KotakuInAction',
        'wikileaks', 'shitcosmosays', 'twitch', 'livestreamfail', 'serialpodcast', 'podcasts',
        'tumblrinaction', 'tumblr', 'blackpeopletwitter', 'scottishpeopletwitter',
        'WhitePeopleTwitter', 'wholesomebpt', 'latinopeopletwitter', 'YoutubeHaiku',
        'youtube', 'youngpeopleyoutube', 'gamegrumps', 'h3h3productions', 'CGPGrey',
        'yogscast', 'jontron', 'Idubbbz', 'defranco', 'cynicalbrit', 'pyrocynical',
        'SovietWomble', 'RedLetterMedia', 'videogamedunkey', 'loltyler1', 'ksi', 'MiniLadd',
        'jacksepticeye', 'pewdiepiesubmissions', 'pewdiepie', 'roosterteeth', 'funhaus',
        'rwby', 'cowchop', 'movies', 'documentaries', 'fullmoviesonyoutube', 'truefilm',
        'bollywoodrealism', 'moviedetails', 'moviesinthemaking', 'fullmoviesonvimeo',
        'continuityporn', 'ghibli', 'cinematography', 'shittymoviedetails', 'moviescirclejerk',
        'starwars', 'harrypotter', 'lotr', 'lotrmemes', 'otmemes', 'marvelstudios',
        'batman', 'DC_Cinematic', 'thanosdidnothingwrong', 'inthesoulstone', 'music',
        'listentothis', 'WeAreTheMusicMakers', 'mashups', 'vinyl', 'futurebeats',
        'musictheory', 'guitarlessons', 'spotify', 'fakealbumcovers', 'ableton', 'kanye',
        'radiohead', 'KendrickLamar', 'gorillaz', 'frankocean', 'donaldglover', 'eminem',
        'brockhampton', 'beatles', 'deathgrips', 'pinkfloyd', 'classicalmusic', 'jazz',
        'trap', 'indieheads', 'gamemusic', 'outrun', 'vaporwave', 'dubstep',
        'electronicmusic', 'edmproduction', 'EDM', 'hiphopheads', 'hiphopimages',
        'Metal', 'Metalcore', 'spop', 'kpop', 'funkopop', 'popheads', 'guitar', 'piano',
        'bass', 'drums', 'sports', 'running', 'bicycling', 'golf', 'fishing', 'skiing'
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
    keywords = get_target_phrases()
    
    # Search each subreddit
    for subreddit_name in subreddits:
        print(f"Searching r/{subreddit_name}...")

        opportunities = search_subreddit(reddit, subreddit_name, keywords)
        save_opportunities(opportunities, subreddit_name)
        print(f"Found {len(opportunities['posts'])} posts and {len(opportunities['comments'])} comments in r/{subreddit_name}")

        
        # Respect Reddit's rate limits
        time.sleep(5)

if __name__ == "__main__":
    main()