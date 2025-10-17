#!/usr/bin/env python3
"""
Trading Behavior Analysis for StockTwits Data

Analyzes user behavior to identify:
1. Most engaged posts in last 24H
2. "Fast twitch" traders (likely to trade in-app vs use brokerages)
3. Trading activity patterns and instrument preferences
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import csv


class TradingBehaviorAnalyzer:
    """Analyze trading behavior patterns from StockTwits data"""
    
    # Keywords indicating fast-twitch trading behavior
    DAY_TRADING_KEYWORDS = [
        'scalp', 'scalping', 'day trade', 'intraday', 'momentum',
        'breakout', 'squeeze', 'gamma', 'short squeeze',
        '0dte', 'same day', 'quick trade', 'fast money'
    ]
    
    OPTIONS_KEYWORDS = [
        'call', 'calls', 'put', 'puts', 'option', 'options',
        'strike', 'expiry', 'expiration', 'theta', 'delta', 'vega',
        'iv', 'implied volatility', 'premium', 'otm', 'itm', 'atm'
    ]
    
    DERIVATIVES_KEYWORDS = [
        'future', 'futures', 'contract', 'leverage', 'leveraged',
        'margin', '3x', '2x', 'inverse', 'short etf'
    ]
    
    URGENT_KEYWORDS = [
        'now', 'right now', 'asap', 'quick', 'fast', 'immediate',
        'today', 'alert', 'breaking', 'just', 'buying now', 'selling now'
    ]
    
    TECHNICAL_KEYWORDS = [
        'rsi', 'macd', 'ema', 'sma', 'vwap', 'fibonacci', 'support',
        'resistance', 'channel', 'breakout', 'breakdown', 'pattern',
        'chart', 'technical', 'indicator'
    ]
    
    # Leveraged/derivative ETFs
    LEVERAGED_INSTRUMENTS = [
        'TQQQ', 'SQQQ', 'UVXY', 'SPXU', 'SPXL', 'TNA', 'TZA',
        'UPRO', 'SDOW', 'UDOW', 'LABU', 'LABD', 'NAIL', 'NUGT'
    ]
    
    def __init__(self, data_file: str):
        """Load StockTwits data for analysis"""
        with open(data_file, 'r') as f:
            self.messages = json.load(f)
        
        print(f"Loaded {len(self.messages):,} messages for analysis")
        
        self.user_activity = defaultdict(list)
        self._build_user_profiles()
    
    def _build_user_profiles(self):
        """Build activity profiles for each user"""
        for msg in self.messages:
            username = msg.get('username')
            if username:
                self.user_activity[username].append(msg)
    
    def get_most_engaged_posts(self, top_n: int = 50) -> List[Dict]:
        """
        Get posts with highest engagement in last 24H
        
        Args:
            top_n: Number of top posts to return
            
        Returns:
            List of posts sorted by engagement
        """
        posts = [m for m in self.messages if not m.get('is_comment')]
        
        # Calculate engagement score
        for post in posts:
            post['engagement_score'] = (
                post.get('likes_count', 0) * 1.0 +
                post.get('replies_count', 0) * 2.0 +  # Replies worth more
                post.get('reshares_count', 0) * 1.5
            )
        
        # Sort by engagement
        sorted_posts = sorted(posts, key=lambda x: x['engagement_score'], reverse=True)
        
        return sorted_posts[:top_n]
    
    def analyze_fast_twitch_score(self, username: str) -> Dict:
        """
        Calculate "fast twitch" score for a user
        
        Score based on:
        - Posting frequency
        - Use of urgent language
        - Options/derivatives mentions
        - Day trading terminology
        - Technical analysis focus
        - Leveraged instrument trading
        
        Returns:
            Dict with score and breakdown
        """
        user_msgs = self.user_activity.get(username, [])
        if not user_msgs:
            return {'score': 0, 'signals': {}}
        
        signals = {
            'posting_frequency': 0,
            'urgent_language': 0,
            'options_focus': 0,
            'derivatives_focus': 0,
            'day_trading_language': 0,
            'technical_analysis': 0,
            'leveraged_instruments': 0,
            'engagement_speed': 0,
        }
        
        total_text = ' '.join(m.get('body', '').lower() for m in user_msgs)
        
        # 1. Posting frequency (normalize to posts per day)
        if len(user_msgs) >= 10:
            signals['posting_frequency'] = 10
        elif len(user_msgs) >= 5:
            signals['posting_frequency'] = 7
        elif len(user_msgs) >= 3:
            signals['posting_frequency'] = 5
        elif len(user_msgs) >= 2:
            signals['posting_frequency'] = 3
        
        # 2. Urgent language
        urgent_count = sum(1 for kw in self.URGENT_KEYWORDS if kw in total_text)
        signals['urgent_language'] = min(urgent_count * 2, 10)
        
        # 3. Options focus
        options_count = sum(1 for kw in self.OPTIONS_KEYWORDS if kw in total_text)
        signals['options_focus'] = min(options_count * 1.5, 10)
        
        # 4. Derivatives focus
        deriv_count = sum(1 for kw in self.DERIVATIVES_KEYWORDS if kw in total_text)
        signals['derivatives_focus'] = min(deriv_count * 2, 10)
        
        # 5. Day trading language
        daytrade_count = sum(1 for kw in self.DAY_TRADING_KEYWORDS if kw in total_text)
        signals['day_trading_language'] = min(daytrade_count * 2, 10)
        
        # 6. Technical analysis
        tech_count = sum(1 for kw in self.TECHNICAL_KEYWORDS if kw in total_text)
        signals['technical_analysis'] = min(tech_count * 1, 10)
        
        # 7. Leveraged instruments
        all_symbols = []
        for msg in user_msgs:
            all_symbols.extend(msg.get('symbols', []))
        leveraged = [s for s in all_symbols if s in self.LEVERAGED_INSTRUMENTS]
        signals['leveraged_instruments'] = min(len(leveraged) * 3, 10)
        
        # 8. Engagement speed (comments vs posts ratio - high = fast twitch)
        comments = [m for m in user_msgs if m.get('is_comment')]
        if user_msgs:
            comment_ratio = len(comments) / len(user_msgs)
            signals['engagement_speed'] = min(comment_ratio * 15, 10)
        
        # Calculate total score (0-100)
        total_score = sum(signals.values())
        max_score = 80  # 8 signals * 10 max each
        normalized_score = min((total_score / max_score) * 100, 100)
        
        return {
            'username': username,
            'score': round(normalized_score, 1),
            'signals': signals,
            'total_posts': len(user_msgs),
            'followers': user_msgs[0].get('followers', 0) if user_msgs else 0,
            'classification': self._classify_trader(normalized_score)
        }
    
    def _classify_trader(self, score: float) -> str:
        """Classify trader type based on fast-twitch score"""
        if score >= 70:
            return "HYPER_ACTIVE_TRADER"
        elif score >= 50:
            return "ACTIVE_TRADER"
        elif score >= 30:
            return "MODERATE_TRADER"
        else:
            return "PASSIVE_INVESTOR"
    
    def analyze_trading_instruments(self, username: str = None) -> Dict:
        """
        Analyze what trading instruments users prefer
        
        Args:
            username: Specific user to analyze, or None for all users
            
        Returns:
            Dict with instrument preferences
        """
        msgs = self.user_activity.get(username, []) if username else self.messages
        
        instrument_signals = {
            'stocks_only': 0,
            'options_trader': 0,
            'futures_trader': 0,
            'leveraged_etf_trader': 0,
            'crypto_trader': 0,
        }
        
        for msg in msgs:
            body_lower = msg.get('body', '').lower()
            symbols = msg.get('symbols', [])
            
            # Check for options language
            if any(kw in body_lower for kw in self.OPTIONS_KEYWORDS):
                instrument_signals['options_trader'] += 1
            
            # Check for futures
            if any(kw in body_lower for kw in ['future', 'futures', '/es', '/nq', '/ym']):
                instrument_signals['futures_trader'] += 1
            
            # Check for leveraged ETFs
            if any(symbol in self.LEVERAGED_INSTRUMENTS for symbol in symbols):
                instrument_signals['leveraged_etf_trader'] += 1
            
            # Check for crypto
            if any(kw in body_lower for kw in ['btc', 'eth', 'crypto', 'bitcoin', 'ethereum']):
                instrument_signals['crypto_trader'] += 1
            
            # Stocks by default
            if symbols and not any([
                instrument_signals['options_trader'],
                instrument_signals['futures_trader'],
                instrument_signals['leveraged_etf_trader'],
            ]):
                instrument_signals['stocks_only'] += 1
        
        return instrument_signals
    
    def identify_in_app_trade_candidates(self, min_score: float = 50) -> List[Dict]:
        """
        Identify users most likely to trade in-app vs going to brokerage
        
        High scores = would love instant trading from the app
        Low scores = probably okay with going to brokerage
        
        Args:
            min_score: Minimum fast-twitch score threshold
            
        Returns:
            List of users with analysis
        """
        candidates = []
        
        for username in self.user_activity.keys():
            analysis = self.analyze_fast_twitch_score(username)
            
            if analysis['score'] >= min_score:
                # Add instrument preferences
                instruments = self.analyze_trading_instruments(username)
                analysis['instruments'] = instruments
                candidates.append(analysis)
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return candidates
    
    def analyze_trading_urgency_patterns(self) -> Dict:
        """
        Analyze when and how urgently people want to trade
        
        Returns:
            Analysis of timing and urgency patterns
        """
        # Time-based analysis
        time_patterns = defaultdict(int)
        urgent_posts = []
        
        for msg in self.messages:
            body_lower = msg.get('body', '').lower()
            
            # Check urgency
            is_urgent = any(kw in body_lower for kw in self.URGENT_KEYWORDS)
            
            if is_urgent:
                urgent_posts.append(msg)
            
            # Parse timestamp
            created_at = msg.get('created_at')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    hour = dt.hour
                    
                    # Categorize by time
                    if 7 <= hour < 9:
                        time_patterns['pre_market'] += 1
                    elif 9 <= hour < 16:
                        time_patterns['market_hours'] += 1
                    elif 16 <= hour < 20:
                        time_patterns['after_hours'] += 1
                    else:
                        time_patterns['off_hours'] += 1
                except:
                    pass
        
        return {
            'total_messages': len(self.messages),
            'urgent_messages': len(urgent_posts),
            'urgency_rate': round(len(urgent_posts) / len(self.messages) * 100, 2) if self.messages else 0,
            'time_distribution': dict(time_patterns),
            'most_active_period': max(time_patterns.items(), key=lambda x: x[1])[0] if time_patterns else None,
        }
    
    def generate_report(self, output_file: str = 'trading_behavior_report.json'):
        """Generate comprehensive trading behavior report"""
        
        print("=" * 70)
        print("TRADING BEHAVIOR ANALYSIS REPORT")
        print("=" * 70)
        
        # 1. Most engaged posts
        print("\n1. TOP ENGAGED POSTS (Last 24H)")
        print("-" * 70)
        top_posts = self.get_most_engaged_posts(20)
        
        for i, post in enumerate(top_posts[:10], 1):
            print(f"\n#{i} | Score: {post['engagement_score']:.1f}")
            print(f"   @{post['username']} ({post['followers']:,} followers)")
            print(f"   {post['body'][:100]}...")
            print(f"   💙 {post['likes_count']} likes | 💬 {post['replies_count']} replies")
            print(f"   Symbols: {', '.join(post['symbols'][:3])}")
        
        # 2. Fast-twitch traders
        print("\n\n2. FAST-TWITCH TRADER IDENTIFICATION")
        print("-" * 70)
        print("Users most likely to trade IN-APP vs going to brokerage:\n")
        
        candidates = self.identify_in_app_trade_candidates(min_score=40)
        
        for i, user in enumerate(candidates[:15], 1):
            print(f"\n#{i} | @{user['username']}")
            print(f"   Fast-Twitch Score: {user['score']:.1f}/100 ({user['classification']})")
            print(f"   Posts: {user['total_posts']} | Followers: {user['followers']:,}")
            print(f"   Signals:")
            top_signals = sorted(user['signals'].items(), key=lambda x: x[1], reverse=True)[:3]
            for signal, value in top_signals:
                print(f"     - {signal.replace('_', ' ').title()}: {value:.1f}/10")
        
        # 3. Trading urgency patterns
        print("\n\n3. TRADING URGENCY & TIMING PATTERNS")
        print("-" * 70)
        urgency = self.analyze_trading_urgency_patterns()
        
        print(f"\nTotal Messages: {urgency['total_messages']:,}")
        print(f"Urgent Messages: {urgency['urgent_messages']:,} ({urgency['urgency_rate']:.1f}%)")
        print(f"\nPosting Time Distribution:")
        for period, count in urgency['time_distribution'].items():
            pct = (count / urgency['total_messages'] * 100) if urgency['total_messages'] else 0
            print(f"  {period.replace('_', ' ').title()}: {count:,} ({pct:.1f}%)")
        print(f"\nMost Active Period: {urgency.get('most_active_period', 'N/A').replace('_', ' ').title()}")
        
        # 4. Instrument preferences
        print("\n\n4. TRADING INSTRUMENT PREFERENCES")
        print("-" * 70)
        all_instruments = self.analyze_trading_instruments()
        
        total_signals = sum(all_instruments.values())
        if total_signals > 0:
            for instrument, count in sorted(all_instruments.items(), key=lambda x: x[1], reverse=True):
                pct = (count / total_signals * 100)
                print(f"  {instrument.replace('_', ' ').title()}: {count:,} mentions ({pct:.1f}%)")
        
        # 5. Key insights
        print("\n\n5. KEY INSIGHTS FOR IN-APP TRADING PRODUCT")
        print("-" * 70)
        
        high_ft_users = len([u for u in candidates if u['score'] >= 60])
        med_ft_users = len([u for u in candidates if 40 <= u['score'] < 60])
        
        print(f"\n📊 User Segmentation:")
        print(f"   - {high_ft_users} HYPER-ACTIVE traders (60+ score)")
        print(f"   - {med_ft_users} ACTIVE traders (40-60 score)")
        print(f"   - Total addressable: {len(candidates)} users in dataset")
        
        print(f"\n⚡ Urgency Signals:")
        if urgency['urgency_rate'] > 20:
            print(f"   - HIGH urgency: {urgency['urgency_rate']:.1f}% of posts show urgent language")
            print(f"   - Strong candidate for instant in-app trading")
        elif urgency['urgency_rate'] > 10:
            print(f"   - MODERATE urgency: {urgency['urgency_rate']:.1f}% of posts show urgent language")
            print(f"   - In-app trading would be valuable")
        else:
            print(f"   - LOW urgency: {urgency['urgency_rate']:.1f}% of posts show urgent language")
            print(f"   - Users may be okay with brokerage flow")
        
        print(f"\n🎯 Optimal Trading Features:")
        if all_instruments.get('options_trader', 0) > 50:
            print(f"   - OPTIONS trading is critical")
        if all_instruments.get('leveraged_etf_trader', 0) > 30:
            print(f"   - Support leveraged ETFs")
        if urgency['time_distribution'].get('market_hours', 0) > urgency['total_messages'] * 0.5:
            print(f"   - Focus on market hours execution")
        else:
            print(f"   - Need extended hours trading support")
        
        # Save detailed report
        report = {
            'top_engaged_posts': top_posts,
            'fast_twitch_candidates': candidates,
            'urgency_analysis': urgency,
            'instrument_preferences': all_instruments,
            'summary': {
                'total_users_analyzed': len(self.user_activity),
                'high_fast_twitch_users': high_ft_users,
                'medium_fast_twitch_users': med_ft_users,
                'urgency_rate': urgency['urgency_rate'],
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n\n📄 Detailed report saved to: {output_file}")
        print("=" * 70)
        
        return report


def main():
    """Run trading behavior analysis"""
    
    # Load data - try ultra first, then mega, then comprehensive, then regular
    data_file = None
    if os.path.exists('stocktwits_ultra_24h.json'):
        data_file = 'stocktwits_ultra_24h.json'
        print("📊 Using ULTRA dataset (14K+ messages)")
    elif os.path.exists('stocktwits_mega_24h.json'):
        data_file = 'stocktwits_mega_24h.json'
        print("📊 Using MEGA dataset (40K+ messages)")
    elif os.path.exists('stocktwits_comprehensive_24h.json'):
        data_file = 'stocktwits_comprehensive_24h.json'
        print("📊 Using comprehensive dataset")
    elif os.path.exists('stocktwits_scraped_24h.json'):
        data_file = 'stocktwits_scraped_24h.json'
        print("📊 Using regular dataset")
    
    if not data_file:
        print("Error: No data file found!")
        print("Please run: python stocktwits_scraper.py")
        return
    
    # Load data
    try:
        analyzer = TradingBehaviorAnalyzer(data_file)
    except FileNotFoundError:
        print(f"Error: {data_file} not found!")
        return
    
    # Generate report
    analyzer.generate_report('trading_behavior_report.json')
    
    # Also save fast-twitch traders to CSV for easy viewing
    candidates = analyzer.identify_in_app_trade_candidates(min_score=30)
    
    with open('fast_twitch_traders.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'username', 'score', 'classification', 'total_posts', 'followers',
            'posting_frequency', 'urgent_language', 'options_focus',
            'day_trading_language', 'technical_analysis'
        ])
        writer.writeheader()
        
        for user in candidates:
            row = {
                'username': user['username'],
                'score': user['score'],
                'classification': user['classification'],
                'total_posts': user['total_posts'],
                'followers': user['followers'],
                'posting_frequency': user['signals']['posting_frequency'],
                'urgent_language': user['signals']['urgent_language'],
                'options_focus': user['signals']['options_focus'],
                'day_trading_language': user['signals']['day_trading_language'],
                'technical_analysis': user['signals']['technical_analysis'],
            }
            writer.writerow(row)
    
    print("\n📊 Fast-twitch traders also saved to: fast_twitch_traders.csv")


if __name__ == '__main__':
    main()

