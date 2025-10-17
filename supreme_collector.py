#!/usr/bin/env python3
"""
Supreme StockTwits Collector - Target: 20K+ messages
Designed for web app with fresh data collection
"""

import json
import time
from datetime import datetime
from stocktwits_scraper import StockTwitsScraper
from collections import defaultdict
import sys


class SupremeCollector:
    """Collect 20K+ messages for comprehensive analysis"""
    
    def __init__(self, delay=1.0):
        self.scraper = StockTwitsScraper(delay=delay)
        self.all_messages = []
        self.collected_ids = set()
        self.start_time = time.time()
        
    def add_messages(self, messages):
        """Add messages, avoiding duplicates"""
        added = 0
        for msg in messages:
            msg_id = msg.get('message_id') if isinstance(msg, dict) and 'message_id' in msg else msg.get('id')
            if msg_id and msg_id not in self.collected_ids:
                # Add URL
                if msg.get('username') and msg_id:
                    msg['post_url'] = f"https://stocktwits.com/{msg['username']}/message/{msg_id}"
                self.all_messages.append(msg)
                self.collected_ids.add(msg_id)
                added += 1
        return added
    
    def collect_supreme(self, target=20000):
        """Collect messages until target reached"""
        
        print(f"Starting SUPREME collection - Target: {target:,} messages")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        strategies = [
            ("Trending Symbols", self.collect_trending, 50, 150),
            ("Popular Stocks", self.collect_popular, 150, 100),
            ("Active Users", self.collect_users, 600, 30),
            ("Extended Trending", self.collect_trending, 100, 100),
        ]
        
        for strategy_name, method, *args in strategies:
            if len(self.all_messages) >= target:
                break
                
            print(f"\n[Strategy: {strategy_name}]")
            before = len(self.all_messages)
            method(*args)
            added = len(self.all_messages) - before
            print(f"Added {added:,} messages | Total: {len(self.all_messages):,}")
            
            if len(self.all_messages) < target:
                print("Taking 30s break...")
                time.sleep(30)
        
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 80)
        print(f"Collection complete: {len(self.all_messages):,} messages in {elapsed/60:.1f} minutes")
        
        return self.all_messages
    
    def collect_trending(self, num_symbols, msgs_per):
        """Collect from trending symbols"""
        symbols = self.scraper.get_trending_symbols(limit=num_symbols)
        for i, symbol in enumerate(symbols[:num_symbols], 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(symbols[:num_symbols])}", end='\r')
            try:
                raw = self.scraper.get_symbol_stream(symbol, max_messages=msgs_per)
                parsed = [self.scraper.parse_message(m) for m in raw if self.scraper.parse_message(m)]
                self.add_messages(parsed)
            except:
                continue
        print()
    
    def collect_popular(self, num_stocks, msgs_per):
        """Collect from popular stocks"""
        stocks = [
            'SPY', 'QQQ', 'IWM', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA',
            'AMD', 'NFLX', 'CRM', 'INTC', 'COIN', 'MSTR', 'GME', 'AMC', 'PLTR',
            'TQQQ', 'SQQQ', 'UVXY', 'VXX', 'UPRO', 'SPXU', 'TNA', 'TZA',
            'XLF', 'XLE', 'XLK', 'XLV', 'GLD', 'SLV', 'VTI', 'VOO',
        ] * 5  # Repeat to get more messages
        
        for i, symbol in enumerate(stocks[:num_stocks], 1):
            if i % 20 == 0:
                print(f"  Progress: {i}/{min(len(stocks), num_stocks)}", end='\r')
            try:
                raw = self.scraper.get_symbol_stream(symbol, max_messages=msgs_per)
                parsed = [self.scraper.parse_message(m) for m in raw if self.scraper.parse_message(m)]
                self.add_messages(parsed)
            except:
                continue
        print()
    
    def collect_users(self, num_users, msgs_per):
        """Collect from active users"""
        user_counts = defaultdict(int)
        for msg in self.all_messages:
            if msg.get('username'):
                user_counts[msg['username']] += 1
        
        top_users = [u for u, _ in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:num_users]]
        
        for i, username in enumerate(top_users, 1):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(top_users)}", end='\r')
            try:
                url = f"{self.scraper.API_BASE}/streams/user/{username}.json"
                response = self.scraper.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    messages = data.get('messages', [])
                    parsed = [self.scraper.parse_message(m) for m in messages if self.scraper.parse_message(m)]
                    self.add_messages(parsed)
                self.scraper._rate_limit()
            except:
                continue
        print()


def main():
    collector = SupremeCollector(delay=1.0)
    messages = collector.collect_supreme(target=20000)
    
    # Save
    print("\nSaving data...")
    with open('stocktwits_supreme_24h.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    
    collector.scraper.save_to_csv(messages, 'stocktwits_supreme_24h.csv')
    
    summary = collector.scraper.generate_summary(messages)
    summary['collection_time'] = datetime.now().isoformat()
    with open('stocktwits_supreme_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSaved {len(messages):,} messages!")
    print("Files: stocktwits_supreme_24h.json, .csv, summary.json")


if __name__ == '__main__':
    main()

