#!/usr/bin/env python3
"""
Enhanced Trading Behavior Analyzer

Features:
- Conversation pattern analysis
- Response engagement analysis
- Sentiment in discussions (adversarial vs collaborative)
- One-post-out vs discussion threads
- Enhanced fast-twitch trader identification
"""

import json
import os
import csv
import re
from collections import defaultdict, Counter
from datetime import datetime
from analyze_traders import TradingBehaviorAnalyzer


class EnhancedAnalyzer(TradingBehaviorAnalyzer):
    """Extended analyzer with conversation pattern analysis"""
    
    def __init__(self, data_file):
        super().__init__(data_file)
        self.data_file = data_file
        self.conversation_patterns = None
        self.sentiment_analysis = None
    
    def analyze_conversation_patterns(self):
        """Analyze how users engage in discussions"""
        
        print("\n" + "=" * 80)
        print("ANALYZING CONVERSATION PATTERNS")
        print("=" * 80)
        
        patterns = {
            'total_posts': 0,
            'total_comments': 0,
            'posts_with_replies': 0,
            'posts_without_replies': 0,
            'avg_replies_per_post': 0,
            'conversation_starters': [],  # Users who get lots of replies
            'engaged_responders': [],  # Users who reply a lot
            'one_post_out_users': [],  # Users who post but never reply
            'discussion_participants': [],  # Users who actively discuss
        }
        
        # Count posts vs comments
        posts = [m for m in self.messages if not m.get('is_comment')]
        comments = [m for m in self.messages if m.get('is_comment')]
        
        patterns['total_posts'] = len(posts)
        patterns['total_comments'] = len(comments)
        
        # Posts with/without replies
        for post in posts:
            if post.get('replies_count', 0) > 0:
                patterns['posts_with_replies'] += 1
            else:
                patterns['posts_without_replies'] += 1
        
        # Average replies
        total_replies = sum(p.get('replies_count', 0) for p in posts)
        patterns['avg_replies_per_post'] = total_replies / len(posts) if posts else 0
        
        # User engagement patterns
        user_posts = defaultdict(int)
        user_comments = defaultdict(int)
        user_replies_received = defaultdict(int)
        
        for msg in self.messages:
            username = msg.get('username')
            if not username:
                continue
            
            if msg.get('is_comment'):
                user_comments[username] += 1
            else:
                user_posts[username] += 1
                user_replies_received[username] += msg.get('replies_count', 0)
        
        # Identify conversation starters (high replies:posts ratio)
        conversation_starters = []
        for user, posts_count in user_posts.items():
            if posts_count >= 5:  # At least 5 posts
                replies = user_replies_received.get(user, 0)
                ratio = replies / posts_count
                if ratio >= 1.0:  # At least 1 reply per post on average
                    conversation_starters.append({
                        'username': user,
                        'posts': posts_count,
                        'replies_received': replies,
                        'ratio': ratio
                    })
        
        patterns['conversation_starters'] = sorted(
            conversation_starters,
            key=lambda x: x['ratio'],
            reverse=True
        )[:20]
        
        # Engaged responders (high comment:post ratio)
        engaged_responders = []
        for user in set(list(user_posts.keys()) + list(user_comments.keys())):
            posts_count = user_posts.get(user, 0)
            comments_count = user_comments.get(user, 0)
            
            if comments_count >= 5:  # At least 5 comments
                ratio = comments_count / max(posts_count, 1)
                engaged_responders.append({
                    'username': user,
                    'posts': posts_count,
                    'comments': comments_count,
                    'comment_ratio': ratio
                })
        
        patterns['engaged_responders'] = sorted(
            engaged_responders,
            key=lambda x: x['comment_ratio'],
            reverse=True
        )[:20]
        
        # One-post-out users (post but never comment)
        one_post_out = []
        for user, posts_count in user_posts.items():
            comments_count = user_comments.get(user, 0)
            if posts_count >= 10 and comments_count == 0:
                one_post_out.append({
                    'username': user,
                    'posts': posts_count,
                    'comments': 0,
                    'type': 'broadcaster'
                })
        
        patterns['one_post_out_users'] = sorted(
            one_post_out,
            key=lambda x: x['posts'],
            reverse=True
        )[:20]
        
        # Discussion participants (balance of posts and comments)
        discussion_users = []
        for user in set(list(user_posts.keys()) + list(user_comments.keys())):
            posts_count = user_posts.get(user, 0)
            comments_count = user_comments.get(user, 0)
            
            if posts_count >= 5 and comments_count >= 5:
                balance = min(posts_count, comments_count) / max(posts_count, comments_count)
                discussion_users.append({
                    'username': user,
                    'posts': posts_count,
                    'comments': comments_count,
                    'balance': balance,
                    'total_activity': posts_count + comments_count
                })
        
        patterns['discussion_participants'] = sorted(
            discussion_users,
            key=lambda x: x['total_activity'],
            reverse=True
        )[:20]
        
        # Calculate engagement ratio
        patterns['engagement_ratio'] = patterns['total_comments'] / patterns['total_posts'] if patterns['total_posts'] > 0 else 0
        patterns['reply_rate'] = patterns['posts_with_replies'] / patterns['total_posts'] if patterns['total_posts'] > 0 else 0
        
        self.conversation_patterns = patterns
        
        print(f"✓ Analyzed {len(self.messages):,} messages")
        print(f"  Posts: {patterns['total_posts']:,}")
        print(f"  Comments: {patterns['total_comments']:,}")
        print(f"  Engagement ratio: {patterns['engagement_ratio']:.2f} comments per post")
        print(f"  Reply rate: {patterns['reply_rate']*100:.1f}% of posts get replies")
        
        return patterns
    
    def analyze_sentiment_dynamics(self):
        """Analyze sentiment in discussions - adversarial vs collaborative"""
        
        print("\n" + "=" * 80)
        print("ANALYZING SENTIMENT DYNAMICS")
        print("=" * 80)
        
        # Keywords for different sentiment types
        ADVERSARIAL_KEYWORDS = [
            # Direct disagreement
            'wrong', 'disagree', 'nope', 'nah', 'no way', 'false',
            'incorrect', 'stupid', 'dumb', 'idiot', 'moron',
            # Mockery
            'lol', 'lmao', 'haha', 'joke', 'clown', '🤡',
            'delusional', 'cope', 'copium', 'salty',
            # Aggressive
            'shut up', 'stfu', 'gtfo', 'loser', 'baghold',
            'rekt', 'wrecked', 'dumping on', 'fade',
        ]
        
        COLLABORATIVE_KEYWORDS = [
            # Agreement
            'agree', 'exactly', 'yes', 'yup', 'same', 'this',
            'good point', 'nice call', 'great', 'love',
            # Supportive
            'thanks', 'thank you', 'helpful', 'appreciate',
            'gl', 'good luck', 'lfg', 'lets go',
            # Questions (genuine interest)
            'what do you think', 'thoughts', 'how', 'why',
            'can you explain', 'tell me more',
        ]
        
        NEUTRAL_KEYWORDS = [
            'maybe', 'possibly', 'could be', 'perhaps',
            'depends', 'not sure', 'idk', 'interesting',
        ]
        
        sentiment = {
            'adversarial_count': 0,
            'collaborative_count': 0,
            'neutral_count': 0,
            'no_clear_sentiment': 0,
            'adversarial_examples': [],
            'collaborative_examples': [],
            'mixed_sentiment': 0,
        }
        
        for msg in self.messages:
            content = msg.get('content', '').lower()
            
            if not content or len(content) < 5:
                sentiment['no_clear_sentiment'] += 1
                continue
            
            adv_score = sum(1 for kw in ADVERSARIAL_KEYWORDS if kw in content)
            collab_score = sum(1 for kw in COLLABORATIVE_KEYWORDS if kw in content)
            neutral_score = sum(1 for kw in NEUTRAL_KEYWORDS if kw in content)
            
            if adv_score > 0 and collab_score > 0:
                sentiment['mixed_sentiment'] += 1
            elif adv_score > collab_score and adv_score > neutral_score:
                sentiment['adversarial_count'] += 1
                if len(sentiment['adversarial_examples']) < 20:
                    sentiment['adversarial_examples'].append({
                        'username': msg.get('username'),
                        'content': msg.get('content')[:200],
                        'post_url': msg.get('post_url'),
                        'is_comment': msg.get('is_comment', False)
                    })
            elif collab_score > adv_score and collab_score > neutral_score:
                sentiment['collaborative_count'] += 1
                if len(sentiment['collaborative_examples']) < 20:
                    sentiment['collaborative_examples'].append({
                        'username': msg.get('username'),
                        'content': msg.get('content')[:200],
                        'post_url': msg.get('post_url'),
                        'is_comment': msg.get('is_comment', False)
                    })
            elif neutral_score > 0:
                sentiment['neutral_count'] += 1
            else:
                sentiment['no_clear_sentiment'] += 1
        
        # Calculate percentages
        total = len(self.messages)
        sentiment['adversarial_pct'] = (sentiment['adversarial_count'] / total * 100) if total > 0 else 0
        sentiment['collaborative_pct'] = (sentiment['collaborative_count'] / total * 100) if total > 0 else 0
        sentiment['neutral_pct'] = (sentiment['neutral_count'] / total * 100) if total > 0 else 0
        
        # Determine overall tone
        if sentiment['adversarial_pct'] > sentiment['collaborative_pct'] * 2:
            sentiment['overall_tone'] = 'ADVERSARIAL'
        elif sentiment['collaborative_pct'] > sentiment['adversarial_pct'] * 2:
            sentiment['overall_tone'] = 'COLLABORATIVE'
        elif sentiment['adversarial_pct'] > sentiment['collaborative_pct']:
            sentiment['overall_tone'] = 'MODERATELY_ADVERSARIAL'
        elif sentiment['collaborative_pct'] > sentiment['adversarial_pct']:
            sentiment['overall_tone'] = 'MODERATELY_COLLABORATIVE'
        else:
            sentiment['overall_tone'] = 'NEUTRAL'
        
        self.sentiment_analysis = sentiment
        
        print(f"✓ Analyzed sentiment in {total:,} messages")
        print(f"  Adversarial: {sentiment['adversarial_count']:,} ({sentiment['adversarial_pct']:.1f}%)")
        print(f"  Collaborative: {sentiment['collaborative_count']:,} ({sentiment['collaborative_pct']:.1f}%)")
        print(f"  Neutral: {sentiment['neutral_count']:,} ({sentiment['neutral_pct']:.1f}%)")
        print(f"  Overall tone: {sentiment['overall_tone']}")
        
        return sentiment
    
    def save_enhanced_report(self, filename='enhanced_trading_report.json'):
        """Save comprehensive analysis with conversation patterns"""
        
        # Load existing analysis if available, otherwise run basic analysis
        print("\nLoading base trading behavior analysis...")
        trading_behavior = self.analyze_trading_urgency_patterns()
        
        # Load existing fast-twitch traders if available
        fast_twitch_traders = []
        if os.path.exists('trading_behavior_report.json'):
            with open('trading_behavior_report.json') as f:
                existing = json.load(f)
                fast_twitch_traders = existing.get('fast_twitch_traders', [])
            print(f"✓ Loaded {len(fast_twitch_traders)} fast-twitch traders from existing analysis")
        else:
            # Just get most engaged posts as a proxy
            fast_twitch_traders = []
            print("  (Run analyze_traders.py first for detailed trader analysis)")
        
        # Add conversation analysis
        conversation_patterns = self.analyze_conversation_patterns()
        sentiment_analysis = self.analyze_sentiment_dynamics()
        
        report = {
            'dataset_info': {
                'total_messages': len(self.messages),
                'data_file': self.data_file,
                'analysis_time': datetime.now().isoformat()
            },
            'fast_twitch_traders': fast_twitch_traders,
            'trading_behavior': trading_behavior,
            'conversation_patterns': conversation_patterns,
            'sentiment_analysis': sentiment_analysis
        }
        
        # Save
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved enhanced report: {filename}")
        
        return report


def main():
    """Run enhanced analysis"""
    
    # Load data - try ultra first, then mega, then comprehensive
    data_file = None
    if os.path.exists('stocktwits_ultra_24h.json'):
        data_file = 'stocktwits_ultra_24h.json'
        print("📊 Using ULTRA dataset (14K+ messages)")
    elif os.path.exists('stocktwits_mega_24h.json'):
        data_file = 'stocktwits_mega_24h.json'
        print("📊 Using MEGA dataset (9K+ messages)")
    elif os.path.exists('stocktwits_comprehensive_24h.json'):
        data_file = 'stocktwits_comprehensive_24h.json'
        print("📊 Using comprehensive dataset")
    elif os.path.exists('stocktwits_scraped_24h.json'):
        data_file = 'stocktwits_scraped_24h.json'
        print("📊 Using regular dataset")
    
    if not data_file:
        print("Error: No data file found!")
        print("Please run: python ultra_collector.py")
        return
    
    print(f"Loading data from {data_file}...")
    
    analyzer = EnhancedAnalyzer(data_file)
    report = analyzer.save_enhanced_report()
    
    # Print summary
    print("\n" + "=" * 80)
    print("ENHANCED ANALYSIS SUMMARY")
    print("=" * 80)
    
    print("\n📊 CONVERSATION PATTERNS:")
    cp = report['conversation_patterns']
    print(f"   Total Posts: {cp['total_posts']:,}")
    print(f"   Total Comments: {cp['total_comments']:,}")
    print(f"   Engagement Ratio: {cp['engagement_ratio']:.2f} comments per post")
    print(f"   Reply Rate: {cp['reply_rate']*100:.1f}% of posts get replies")
    
    print(f"\n   Top 5 Conversation Starters (get most replies):")
    for i, user in enumerate(cp['conversation_starters'][:5], 1):
        print(f"      {i}. @{user['username']}: {user['ratio']:.1f} replies per post ({user['posts']} posts)")
    
    print(f"\n   Top 5 Engaged Responders (comment a lot):")
    for i, user in enumerate(cp['engaged_responders'][:5], 1):
        print(f"      {i}. @{user['username']}: {user['comments']} comments, {user['posts']} posts (ratio: {user['comment_ratio']:.1f})")
    
    print(f"\n   Top 5 One-Post-Out Users (broadcast only):")
    for i, user in enumerate(cp['one_post_out_users'][:5], 1):
        print(f"      {i}. @{user['username']}: {user['posts']} posts, {user['comments']} comments")
    
    print(f"\n   Top 5 Discussion Participants (balanced engagement):")
    for i, user in enumerate(cp['discussion_participants'][:5], 1):
        print(f"      {i}. @{user['username']}: {user['posts']} posts, {user['comments']} comments")
    
    print("\n💬 SENTIMENT DYNAMICS:")
    sa = report['sentiment_analysis']
    print(f"   Overall Tone: {sa['overall_tone']}")
    print(f"   Adversarial: {sa['adversarial_count']:,} ({sa['adversarial_pct']:.1f}%)")
    print(f"   Collaborative: {sa['collaborative_count']:,} ({sa['collaborative_pct']:.1f}%)")
    print(f"   Neutral: {sa['neutral_count']:,} ({sa['neutral_pct']:.1f}%)")
    
    print("\n   Example Adversarial Messages:")
    for i, ex in enumerate(sa['adversarial_examples'][:3], 1):
        url_text = f" | {ex['post_url']}" if ex.get('post_url') else ""
        print(f"      {i}. @{ex['username']}: \"{ex['content'][:100]}...\"{url_text}")
    
    print("\n   Example Collaborative Messages:")
    for i, ex in enumerate(sa['collaborative_examples'][:3], 1):
        url_text = f" | {ex['post_url']}" if ex.get('post_url') else ""
        print(f"      {i}. @{ex['username']}: \"{ex['content'][:100]}...\"{url_text}")
    
    print("\n🎯 TRADING BEHAVIOR:")
    tb = report.get('trading_behavior', {})
    print(f"   Urgency Rate: {tb.get('urgency_rate', 0)*100:.1f}%")
    print(f"   Fast-Twitch Traders: {len(report.get('fast_twitch_traders', []))}")
    
    instruments = tb.get('instrument_preferences', {})
    print(f"\n   Instrument Preferences:")
    for key, count in sorted(instruments.items(), key=lambda x: x[1], reverse=True)[:5]:
        total = sum(instruments.values())
        pct = (count / total * 100) if total > 0 else 0
        print(f"      {key}: {count} ({pct:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ Enhanced analysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

