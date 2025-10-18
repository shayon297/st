#!/usr/bin/env python3
"""
Mega Collector - Target 100K Messages
Aggressive collection strategy to maximize coverage
"""

import json
import time
from datetime import datetime
from stocktwits_scraper import StockTwitsScraper
from collections import defaultdict
import concurrent.futures
from threading import Lock
import sys


class MegaCollector100K:
    """Collect as close to 100K messages as possible"""
    
    def __init__(self, delay=0.3):  # Faster delay
        self.scraper = StockTwitsScraper(delay=delay)
        self.all_messages = []
        self.collected_ids = set()
        self.lock = Lock()
        self.start_time = time.time()
        
    def add_messages(self, messages):
        """Thread-safe message addition"""
        with self.lock:
            added = 0
            for msg in messages:
                msg_id = msg.get('message_id') or msg.get('id')
                if msg_id and msg_id not in self.collected_ids:
                    if msg.get('username') and msg_id:
                        msg['post_url'] = f"https://stocktwits.com/{msg['username']}/message/{msg_id}"
                    self.all_messages.append(msg)
                    self.collected_ids.add(msg_id)
                    added += 1
            return added
    
    def get_comprehensive_symbols(self):
        """Get maximum possible symbol list"""
        symbols = set()
        
        # Get trending multiple times (they change)
        for _ in range(3):
            trending = self.scraper.get_trending_symbols(limit=30)
            symbols.update(trending)
            time.sleep(2)
        
        # Major indices
        symbols.update(['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'AGG', 'TLT'])
        
        # Mega caps
        symbols.update(['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'NVDA', 'BRK.B', 'LLY'])
        symbols.update(['AVGO', 'JPM', 'V', 'UNH', 'WMT', 'XOM', 'MA', 'JNJ', 'PG', 'HD'])
        
        # Tech
        symbols.update(['AMD', 'NFLX', 'INTC', 'CSCO', 'ORCL', 'CRM', 'ADBE', 'QCOM', 'NOW', 'PANW'])
        symbols.update(['SHOP', 'SQ', 'PYPL', 'UBER', 'LYFT', 'SNOW', 'CRWD', 'ZS', 'DDOG', 'NET'])
        
        # Finance
        symbols.update(['BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB', 'PNC'])
        
        # Healthcare
        symbols.update(['PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'CVS', 'UNH', 'AMGN', 'GILD'])
        
        # Consumer
        symbols.update(['COST', 'NKE', 'SBUX', 'MCD', 'TGT', 'LOW', 'DIS', 'CMCSA', 'NFLX', 'CHTR'])
        
        # Energy
        symbols.update(['XLE', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'])
        
        # Crypto-related
        symbols.update(['COIN', 'MSTR', 'HOOD', 'RIOT', 'MARA', 'CLSK', 'CIFR', 'WULF', 'BITF', 'IREN'])
        symbols.update(['CORZ', 'BTC.X', 'ETH.X', 'DOGE.X', 'SOL.X', 'ADA.X', 'XRP.X', 'AVAX.X'])
        
        # Meme stocks
        symbols.update(['GME', 'AMC', 'BBBY', 'BB', 'NOK', 'PLTR', 'SOFI', 'WISH', 'CLOV', 'SPCE'])
        
        # Leveraged ETFs
        symbols.update(['TQQQ', 'SQQQ', 'UPRO', 'SPXU', 'TNA', 'TZA', 'UVXY', 'VXX', 'JNUG', 'JDST'])
        symbols.update(['LABU', 'LABD', 'SOXL', 'SOXS', 'TECL', 'TECS', 'FNGU', 'FNGD'])
        
        # Sectors
        symbols.update(['XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLB', 'XLU', 'XLRE'])
        
        # Gold/Silver
        symbols.update(['GLD', 'SLV', 'GDX', 'GDXJ', 'IAU', 'NUGT', 'DUST'])
        
        # International
        symbols.update(['EWJ', 'FXI', 'EWZ', 'INDA', 'EEM', 'VGK', 'EFA', 'KWEB'])
        
        # SPACs and Small Caps
        symbols.update(['ARKK', 'ARKW', 'ARKG', 'IWM', 'IJR', 'VB', 'VTWO'])
        
        print(f"Generated {len(symbols)} symbols to collect")
        return list(symbols)
    
    def collect_symbol_batch(self, symbols, msgs_per=250, max_workers=10):
        """Collect from symbols with high parallelization"""
        print(f"\nCollecting from {len(symbols)} symbols (parallel={max_workers})...")
        
        def collect_one(symbol):
            try:
                raw = self.scraper.get_symbol_stream(symbol, max_messages=msgs_per)
                parsed = [self.scraper.parse_message(m) for m in raw if self.scraper.parse_message(m)]
                return self.add_messages(parsed)
            except:
                return 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(collect_one, sym) for sym in symbols]
            
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                if completed % 50 == 0:
                    print(f"  {completed}/{len(symbols)} | Total: {len(self.all_messages):,} messages")
        
        print(f"  ✓ Phase complete: {len(self.all_messages):,} total")
    
    def collect_users_aggressive(self, num_users=2000):
        """Aggressively collect from active users"""
        print(f"\nCollecting from {num_users} most active users...")
        
        user_counts = defaultdict(int)
        for msg in self.all_messages:
            if msg.get('username'):
                user_counts[msg['username']] += 1
        
        top_users = [u for u, _ in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:num_users]]
        
        for i, username in enumerate(top_users, 1):
            if i % 200 == 0:
                print(f"  {i}/{num_users} | Total: {len(self.all_messages):,}")
            
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
        
        print(f"  ✓ Total: {len(self.all_messages):,}")
    
    def collect_mega(self, target=100000):
        """Execute mega collection"""
        print("=" * 80)
        print(f"MEGA COLLECTION - TARGET: {target:,} MESSAGES")
        print("=" * 80)
        
        # Phase 1: Comprehensive symbol sweep (high parallelization)
        symbols = self.get_comprehensive_symbols()
        batch_size = 100
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            self.collect_symbol_batch(batch, msgs_per=250, max_workers=10)
            if len(self.all_messages) >= target:
                break
            print(f"Progress: {len(self.all_messages):,}/{target:,}")
            time.sleep(10)
        
        # Phase 2: Active users
        if len(self.all_messages) < target:
            print("\n" + "=" * 80)
            self.collect_users_aggressive(num_users=2000)
        
        # Phase 3: Re-sweep trending (they change over time)
        if len(self.all_messages) < target:
            print("\n" + "=" * 80)
            print("Re-sweeping trending symbols...")
            trending = self.scraper.get_trending_symbols(limit=50)
            self.collect_symbol_batch(trending, msgs_per=300, max_workers=10)
        
        # Phase 4: Deep dive on high-volume symbols
        if len(self.all_messages) < target:
            print("\n" + "=" * 80)
            print("Deep dive on high-volume symbols...")
            high_volume = ['SPY', 'QQQ', 'TSLA', 'NVDA', 'AAPL', 'MSFT', 'COIN', 'MSTR']
            self.collect_symbol_batch(high_volume * 5, msgs_per=500, max_workers=8)
        
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 80)
        print(f"Collection Complete: {len(self.all_messages):,} messages in {elapsed/60:.1f} minutes")
        print(f"Target achievement: {len(self.all_messages)/target*100:.1f}%")
        print("=" * 80)
        
        return self.all_messages


def main():
    print("Starting MEGA COLLECTION (Target: 100K messages)")
    print("This will take 90-120 minutes with aggressive parallelization\n")
    
    collector = MegaCollector100K(delay=0.3)
    messages = collector.collect_mega(target=100000)
    
    # Save
    print("\nSaving data...")
    
    with open('stocktwits_mega100k_24h.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    
    # CSV
    import csv
    fieldnames = [
        'message_id', 'username', 'user_id', 'created_at', 'body',
        'sentiment', 'likes_count', 'replies_count', 'reshares_count',
        'symbols', 'followers', 'following', 'post_url', 'source'
    ]
    
    with open('stocktwits_mega100k_24h.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for msg in messages:
            msg_copy = msg.copy()
            if 'symbols' in msg_copy and isinstance(msg_copy['symbols'], list):
                msg_copy['symbols'] = ' '.join(msg_copy['symbols'])
            writer.writerow(msg_copy)
    
    # Summary
    unique_users = len(set(m.get('username') for m in messages if m.get('username')))
    coverage = (len(messages) / 100000) * 100
    
    summary = {
        'total_messages': len(messages),
        'unique_users': unique_users,
        'coverage_estimate_pct': round(coverage, 1),
        'collection_time': datetime.now().isoformat(),
        'collection_duration_minutes': round((time.time() - collector.start_time) / 60, 1)
    }
    
    with open('stocktwits_mega100k_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n" + "=" * 80)
    print("MEGA COLLECTION SUMMARY")
    print("=" * 80)
    print(f"Messages collected: {len(messages):,}")
    print(f"Unique users: {unique_users:,}")
    print(f"Estimated coverage: {coverage:.1f}% of daily volume")
    print(f"Duration: {summary['collection_duration_minutes']} minutes")
    print(f"\nFiles saved:")
    print(f"  - stocktwits_mega100k_24h.json")
    print(f"  - stocktwits_mega100k_24h.csv")
    print(f"  - stocktwits_mega100k_summary.json")
    print("=" * 80)


if __name__ == '__main__':
    main()

