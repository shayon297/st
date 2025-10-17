#!/usr/bin/env python3
"""
StockTwits Web Scraper

Collects posts, comments, and engagement data from StockTwits using:
1. Public API endpoints (no auth required)
2. Web scraping as fallback

Note: This respects rate limits and ToS. For large-scale data collection,
consider using the official Firehose API.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import csv
from bs4 import BeautifulSoup
import re
from collections import defaultdict


class StockTwitsScraper:
    """Scraper for StockTwits public data"""
    
    API_BASE = "https://api.stocktwits.com/api/2"
    WEB_BASE = "https://stocktwits.com"
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize scraper
        
        Args:
            delay: Delay between requests in seconds (be respectful!)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.collected_message_ids: Set[int] = set()
        
    def _rate_limit(self):
        """Respectful rate limiting"""
        time.sleep(self.delay)
    
    def get_trending_symbols(self, limit: int = 30) -> List[str]:
        """
        Get trending stock symbols
        
        Args:
            limit: Number of symbols to fetch
            
        Returns:
            List of trending symbols
        """
        try:
            print("Fetching trending symbols...")
            url = f"{self.API_BASE}/trending/symbols.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            symbols = [s['symbol'] for s in data.get('symbols', [])[:limit]]
            print(f"Found {len(symbols)} trending symbols: {', '.join(symbols[:10])}...")
            return symbols
            
        except Exception as e:
            print(f"Error fetching trending symbols: {e}")
            # Fallback to popular symbols
            return ['SPY', 'AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'AMD', 'NFLX']
    
    def get_symbol_stream(self, symbol: str, max_messages: int = 30) -> List[Dict]:
        """
        Get recent messages for a symbol using public API
        
        Args:
            symbol: Stock symbol
            max_messages: Maximum messages to fetch
            
        Returns:
            List of messages
        """
        messages = []
        
        try:
            print(f"Fetching messages for ${symbol}...", end=' ')
            url = f"{self.API_BASE}/streams/symbol/{symbol}.json"
            params = {'limit': 30}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            msgs = data.get('messages', [])
            
            for msg in msgs[:max_messages]:
                if msg and msg.get('id') and msg['id'] not in self.collected_message_ids:
                    messages.append(msg)
                    self.collected_message_ids.add(msg['id'])
            
            print(f"Got {len(messages)} new messages")
            self._rate_limit()
            
        except Exception as e:
            print(f"Error: {e}")
        
        return messages
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get detailed user information
        
        Args:
            username: StockTwits username
            
        Returns:
            User information dict
        """
        try:
            url = f"{self.API_BASE}/streams/user/{username}.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('user', {})
            
        except Exception as e:
            print(f"Error fetching user {username}: {e}")
            return None
    
    def get_message_conversation(self, message_id: int) -> List[Dict]:
        """
        Get conversation/replies for a message
        
        Args:
            message_id: Message ID
            
        Returns:
            List of reply messages
        """
        try:
            url = f"{self.API_BASE}/messages/conversation/{message_id}.json"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            replies = data.get('messages', [])
            self._rate_limit()
            return replies
            
        except Exception as e:
            # Conversation endpoint might not be public
            return []
    
    def scrape_web_trending(self) -> List[Dict]:
        """
        Scrape trending messages from web interface
        
        Returns:
            List of messages from trending page
        """
        messages = []
        
        try:
            print("Scraping trending page...")
            url = f"{self.WEB_BASE}/streams/trending"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for embedded JSON data
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    # Extract messages from the JSON structure
                    self._extract_messages_from_json(data, messages)
                except:
                    continue
            
            print(f"Scraped {len(messages)} messages from trending")
            self._rate_limit()
            
        except Exception as e:
            print(f"Error scraping trending: {e}")
        
        return messages
    
    def _extract_messages_from_json(self, data: any, messages: List[Dict]):
        """Recursively extract messages from nested JSON"""
        if isinstance(data, dict):
            if 'id' in data and 'body' in data and 'user' in data:
                if data['id'] not in self.collected_message_ids:
                    messages.append(data)
                    self.collected_message_ids.add(data['id'])
            for value in data.values():
                self._extract_messages_from_json(value, messages)
        elif isinstance(data, list):
            for item in data:
                self._extract_messages_from_json(item, messages)
    
    def parse_message(self, message: Dict) -> Optional[Dict]:
        """
        Parse message data into standardized format
        
        Args:
            message: Raw message dict
            
        Returns:
            Parsed message or None if invalid
        """
        if not message:
            return None
            
        user = message.get('user', {})
        if not user:
            return None
        
        # Extract engagement metrics
        likes = message.get('likes', {})
        if isinstance(likes, dict):
            likes_count = likes.get('total', 0)
        else:
            likes_count = likes if likes else 0
        
        reshares = message.get('reshares', {})
        if isinstance(reshares, dict):
            reshares_count = reshares.get('reshare_count', 0)
        else:
            reshares_count = 0
        
        # Handle both 'conversation' and 'discussion' fields
        conversation = message.get('conversation') or message.get('discussion')
        replies_count = conversation.get('replies', 0) if conversation else 0
        parent_id = conversation.get('parent_message_id') or conversation.get('parent_id') if conversation else None
        
        # Extract symbols
        symbols = []
        if 'symbols' in message:
            symbols = [s.get('symbol', '') for s in message.get('symbols', [])]
        
        # Extract sentiment
        sentiment = None
        entities = message.get('entities', {})
        if entities and 'sentiment' in entities:
            sentiment_data = entities.get('sentiment')
            if sentiment_data and isinstance(sentiment_data, dict):
                sentiment = sentiment_data.get('basic')
        
        parsed = {
            'message_id': message.get('id'),
            'created_at': message.get('created_at'),
            'body': message.get('body', ''),
            'user_id': user.get('id'),
            'username': user.get('username'),
            'name': user.get('name', ''),
            'followers': user.get('followers', 0),
            'following': user.get('following', 0),
            'ideas': user.get('ideas', 0),  # Total posts by user
            'watchlist_stocks_count': user.get('watchlist_stocks_count', 0),
            'likes_count': likes_count,
            'reshares_count': reshares_count,
            'replies_count': replies_count,
            'is_comment': parent_id is not None,
            'parent_message_id': parent_id,
            'symbols': symbols,
            'sentiment': sentiment,
            'source': message.get('source', {}).get('title', ''),
        }
        
        return parsed
    
    def is_within_24h(self, timestamp: str) -> bool:
        """Check if timestamp is within last 24 hours"""
        try:
            # Parse ISO format timestamp
            msg_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(msg_time.tzinfo)
            return (now - msg_time) <= timedelta(hours=24)
        except:
            return True  # Include if we can't parse
    
    def collect_24h_data(self, 
                        num_symbols: int = 50,
                        messages_per_symbol: int = 30,
                        include_trending: bool = True) -> List[Dict]:
        """
        Collect data from past 24 hours
        
        Args:
            num_symbols: Number of symbols to fetch
            messages_per_symbol: Messages to fetch per symbol
            include_trending: Whether to scrape trending page
            
        Returns:
            List of parsed messages
        """
        all_messages = []
        
        print("\n" + "=" * 70)
        print("StockTwits Data Collection (Public API + Web Scraping)")
        print("=" * 70)
        
        # Get trending symbols
        symbols = self.get_trending_symbols(limit=num_symbols)
        
        # Collect messages for each symbol
        print(f"\nFetching messages for {len(symbols)} symbols...")
        print("-" * 70)
        
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] ", end='')
            messages = self.get_symbol_stream(symbol, max_messages=messages_per_symbol)
            
            for msg in messages:
                parsed = self.parse_message(msg)
                # Filter to last 24 hours
                if parsed and parsed.get('created_at') and self.is_within_24h(parsed['created_at']):
                    all_messages.append(parsed)
        
        # Optionally scrape trending page
        if include_trending:
            print("\n" + "-" * 70)
            trending_messages = self.scrape_web_trending()
            for msg in trending_messages:
                parsed = self.parse_message(msg)
                if parsed and parsed.get('created_at') and self.is_within_24h(parsed['created_at']):
                    all_messages.append(parsed)
        
        # Try to get conversations for top messages
        print("\n" + "-" * 70)
        print("Fetching conversations for top messages...")
        top_messages = sorted(all_messages, key=lambda x: x['replies_count'], reverse=True)[:20]
        
        for i, msg in enumerate(top_messages, 1):
            if msg['replies_count'] > 0:
                print(f"Getting replies for message {msg['message_id']} ({msg['replies_count']} replies)...", end=' ')
                replies = self.get_message_conversation(msg['message_id'])
                
                for reply in replies:
                    parsed = self.parse_message(reply)
                    if parsed and parsed.get('message_id') not in self.collected_message_ids:
                        all_messages.append(parsed)
                        self.collected_message_ids.add(parsed['message_id'])
                
                print(f"Got {len(replies)} replies")
        
        # Remove duplicates
        seen_ids = set()
        unique_messages = []
        for msg in all_messages:
            if msg['message_id'] not in seen_ids:
                seen_ids.add(msg['message_id'])
                unique_messages.append(msg)
        
        print("\n" + "=" * 70)
        print(f"Total messages collected: {len(unique_messages)}")
        print("=" * 70)
        
        return unique_messages
    
    def save_to_csv(self, messages: List[Dict], filename: str = 'stocktwits_scraped_data.csv'):
        """Save messages to CSV"""
        if not messages:
            print("No messages to save")
            return
        
        fieldnames = [
            'message_id', 'created_at', 'body', 'user_id', 'username', 'name',
            'followers', 'following', 'ideas', 'watchlist_stocks_count',
            'likes_count', 'reshares_count', 'replies_count',
            'is_comment', 'parent_message_id', 'symbols', 'sentiment', 'source'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for msg in messages:
                msg_copy = msg.copy()
                if isinstance(msg_copy.get('symbols'), list):
                    msg_copy['symbols'] = ','.join(msg_copy['symbols'])
                writer.writerow(msg_copy)
        
        print(f"Data saved to {filename}")
    
    def save_to_json(self, messages: List[Dict], filename: str = 'stocktwits_scraped_data.json'):
        """Save messages to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    
    def generate_summary(self, messages: List[Dict]) -> Dict:
        """Generate summary statistics"""
        if not messages:
            return {}
        
        posts = [m for m in messages if not m.get('is_comment')]
        comments = [m for m in messages if m.get('is_comment')]
        
        total_likes = sum(m.get('likes_count', 0) for m in messages)
        total_reshares = sum(m.get('reshares_count', 0) for m in messages)
        total_replies = sum(m.get('replies_count', 0) for m in messages)
        
        unique_users = len(set(m.get('user_id') for m in messages if m.get('user_id')))
        
        # Symbol analysis
        symbol_counts = defaultdict(int)
        for msg in messages:
            for symbol in msg.get('symbols', []):
                if symbol:
                    symbol_counts[symbol] += 1
        
        top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Sentiment analysis
        sentiments = [m.get('sentiment') for m in messages if m.get('sentiment')]
        bullish = sentiments.count('bullish')
        bearish = sentiments.count('bearish')
        
        summary = {
            'total_messages': len(messages),
            'total_posts': len(posts),
            'total_comments': len(comments),
            'total_likes': total_likes,
            'total_reshares': total_reshares,
            'total_replies': total_replies,
            'total_engagements': total_likes + total_reshares + total_replies,
            'unique_users': unique_users,
            'top_symbols': dict(top_symbols),
            'sentiment_bullish': bullish,
            'sentiment_bearish': bearish,
            'sentiment_neutral': len(sentiments) - bullish - bearish,
        }
        
        return summary


def main():
    """Main execution"""
    
    print("=" * 70)
    print("StockTwits Web Scraper")
    print("=" * 70)
    print("\nThis tool uses public API endpoints and web scraping.")
    print("Rate limited to be respectful to StockTwits servers.")
    print("=" * 70)
    
    # Initialize scraper with 1 second delay between requests
    scraper = StockTwitsScraper(delay=1.0)
    
    # Collect data
    # Adjust parameters based on how much data you want
    messages = scraper.collect_24h_data(
        num_symbols=50,           # Number of symbols to check
        messages_per_symbol=30,   # Messages per symbol
        include_trending=True     # Include trending page
    )
    
    if messages:
        # Generate and display summary
        summary = scraper.generate_summary(messages)
        
        print("\n" + "=" * 70)
        print("SUMMARY STATISTICS")
        print("=" * 70)
        print(f"Total Messages: {summary['total_messages']:,}")
        print(f"Posts: {summary['total_posts']:,}")
        print(f"Comments: {summary['total_comments']:,}")
        print(f"Unique Users: {summary['unique_users']:,}")
        print(f"\nEngagement:")
        print(f"  Total Likes: {summary['total_likes']:,}")
        print(f"  Total Reshares: {summary['total_reshares']:,}")
        print(f"  Total Replies: {summary['total_replies']:,}")
        print(f"  Total Engagements: {summary['total_engagements']:,}")
        print(f"\nSentiment:")
        print(f"  Bullish: {summary['sentiment_bullish']:,}")
        print(f"  Bearish: {summary['sentiment_bearish']:,}")
        print(f"  Neutral: {summary['sentiment_neutral']:,}")
        
        if summary['top_symbols']:
            print(f"\nTop Symbols:")
            for symbol, count in list(summary['top_symbols'].items())[:10]:
                print(f"  ${symbol}: {count} messages")
        
        # Save data
        print("\n" + "=" * 70)
        print("SAVING DATA")
        print("=" * 70)
        scraper.save_to_csv(messages, 'stocktwits_scraped_24h.csv')
        scraper.save_to_json(messages, 'stocktwits_scraped_24h.json')
        
        # Save summary
        with open('stocktwits_scraped_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        print("Summary saved to stocktwits_scraped_summary.json")
        
        print("\n" + "=" * 70)
        print("COMPLETE!")
        print("=" * 70)
    else:
        print("\nNo data collected.")


if __name__ == '__main__':
    main()

