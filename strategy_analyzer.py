#!/usr/bin/env python3
"""
Trading Strategy & Timeframe Analyzer

Implements precise methodology for classifying users by:
- Trading timeframe (ultra-short, short, medium, long)
- Trading strategy (scalper, day trader, swing, momentum, value, growth, income, contrarian)
- Conviction level (high, medium, low)
- Risk profile (aggressive, moderate, conservative)
"""

import json
import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import csv


class StrategyAnalyzer:
    """Analyzes trading strategy and timeframe from user posts"""
    
    # Timeframe Indicators
    ULTRA_SHORT_KEYWORDS = [
        r'\b0dte\b', r'\bsame day\b', r'\bintraday\b', r'\bscalp(ing)?\b',
        r'\bday trad(e|ing)\b', r'\bright now\b', r'\bquick flip\b',
        r'\bin and out\b', r'\b(1|5|15)m chart\b', r'\bvwap\b', r'\blevel 2\b'
    ]
    
    SHORT_TERM_KEYWORDS = [
        r'\bswing trad(e|ing)\b', r'\bfew days\b', r'\bshort term\b',
        r'\bweekly\b', r'\bthis week\b', r'\b(1|4)h chart\b',
        r'\bholding through (week|earnings)\b', r'\b3-day play\b'
    ]
    
    MEDIUM_TERM_KEYWORDS = [
        r'\bposition trad(e|ing)\b', r'\bmedium term\b', r'\bfew weeks\b',
        r'\bcouple months\b', r'\bmomentum play\b', r'\bbuilding position\b',
        r'\baccumulat(e|ing)\b', r'\bmonthly expiration\b', r'\bLEAPS?\b'
    ]
    
    LONG_TERM_KEYWORDS = [
        r'\blong term\b', r'\bholding\b', r'\binvestor\b', r'\bbuy and hold\b',
        r'\bretirement\b', r'\byears?\b', r'\bforever hold\b', r'\bcore holding\b',
        r'\bnever selling\b', r'\bthinking \d+ years\b', r'\bdividend\b'
    ]
    
    # Strategy Indicators
    SCALPER_KEYWORDS = [
        r'\bscalp(ing)?\b', r'\bquick flip\b', r'\bin and out\b', r'\bticks?\b',
        r'\blevel 2\b', r'\btape reading\b', r'\bseconds to minutes\b'
    ]
    
    DAY_TRADER_KEYWORDS = [
        r'\bday trad(e|ing)\b', r'\b0dte\b', r'\bintraday\b',
        r'\bend of day\b', r'\bno overnight risk\b', r'\bclose(s|d|ing) all positions\b'
    ]
    
    SWING_TRADER_KEYWORDS = [
        r'\bswing trad(e|ing)\b', r'\bswing\b', r'\bfew days\b',
        r'\bweekly setup\b', r'\bshort term play\b', r'\b(2|3|5)-day\b'
    ]
    
    MOMENTUM_KEYWORDS = [
        r'\bmomentum\b', r'\bbreakout\b', r'\btrending\b', r'\briding the wave\b',
        r'\bcatching the move\b', r'\bvolume surge\b', r'\bstrong move\b'
    ]
    
    VALUE_KEYWORDS = [
        r'\bundervalued\b', r'\bcheap\b', r'\bPE ratio\b', r'\bvalue\b',
        r'\bfundamentals\b', r'\bintrinsic value\b', r'\bmargin of safety\b',
        r'\bbuying the dip\b', r'\bdiscount\b'
    ]
    
    GROWTH_KEYWORDS = [
        r'\bgrowth stock\b', r'\brevenue growth\b', r'\bdisruptive\b',
        r'\binnovation\b', r'\bfuture potential\b', r'\bhigh growth\b',
        r'\bexpansion\b', r'\bscaling\b'
    ]
    
    INCOME_KEYWORDS = [
        r'\bdividend(s)?\b', r'\bincome\b', r'\bcovered call(s)?\b',
        r'\bselling premium\b', r'\btheta gang\b', r'\byield\b',
        r'\bmonthly income\b', r'\bcash flow\b'
    ]
    
    CONTRARIAN_KEYWORDS = [
        r'\bcontrarian\b', r'\bbuying the dip\b', r'\beveryone wrong\b',
        r'\bfade the move\b', r'\boversold\b', r'\boverbought\b',
        r'\bsentiment extreme\b', r'\bagainst the crowd\b'
    ]
    
    # Conviction Indicators
    HIGH_CONVICTION = [
        r'\ball in\b', r'\bbiggest position\b', r'\bno doubt\b',
        r'\bguaranteed\b', r'\b100%\b', r'\badding more\b',
        r'\bvery confident\b', r'\bheavy position\b', r'\bmax conviction\b'
    ]
    
    MEDIUM_CONVICTION = [
        r'\bgood setup\b', r'\bthink it goes\b', r'\bshould work\b',
        r'\bstarter position\b', r'\bmoderate size\b', r'\bwill add if\b'
    ]
    
    LOW_CONVICTION = [
        r'\blottery ticket\b', r'\bsmall spec\b', r'\bmight work\b',
        r'\bwe\'ll see\b', r'\brisky\b', r'\bjust ?\$?\d+\b', r'\bYOLO\b'
    ]
    
    # Risk Indicators
    AGGRESSIVE_SIGNALS = [
        r'\b0dte\b', r'\bTQQQ|SQQQ\b', r'\bleverage\b', r'\bmargin\b',
        r'\bYOLO\b', r'\ball in\b', r'\b3x ETF\b', r'\bhigh risk\b'
    ]
    
    CONSERVATIVE_SIGNALS = [
        r'\bdividend\b', r'\bblue chip\b', r'\bsafe\b', r'\bstable\b',
        r'\bcapital preservation\b', r'\blow risk\b', r'\bdefensive\b'
    ]
    
    def __init__(self, data_file: str):
        """Initialize analyzer with data file"""
        print(f"Loading data from {data_file}...")
        with open(data_file, 'r', encoding='utf-8') as f:
            self.messages = json.load(f)
        print(f"✓ Loaded {len(self.messages):,} messages")
        
        # Build user activity index
        self.user_activity = defaultdict(list)
        for msg in self.messages:
            username = msg.get('username')
            if username:
                self.user_activity[username].append(msg)
        
        print(f"✓ Indexed {len(self.user_activity):,} users")
    
    def count_pattern_matches(self, text: str, patterns: List[str]) -> Tuple[int, List[str]]:
        """Count how many patterns match and return evidence"""
        matches = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
        return len(matches), matches
    
    def analyze_timeframe(self, posts: List[Dict]) -> Dict:
        """Analyze user's trading timeframe"""
        combined_text = ' '.join([p.get('body', '') for p in posts])
        
        ultra_count, ultra_evidence = self.count_pattern_matches(combined_text, self.ULTRA_SHORT_KEYWORDS)
        short_count, short_evidence = self.count_pattern_matches(combined_text, self.SHORT_TERM_KEYWORDS)
        medium_count, medium_evidence = self.count_pattern_matches(combined_text, self.MEDIUM_TERM_KEYWORDS)
        long_count, long_evidence = self.count_pattern_matches(combined_text, self.LONG_TERM_KEYWORDS)
        
        scores = {
            'ultra_short_term': ultra_count,
            'short_term': short_count,
            'medium_term': medium_count,
            'long_term': long_count
        }
        
        if max(scores.values()) == 0:
            return {
                'primary': 'unknown',
                'confidence': 0,
                'evidence': [],
                'all_scores': scores
            }
        
        primary = max(scores, key=scores.get)
        primary_count = scores[primary]
        
        # Calculate confidence based on evidence strength
        confidence = min(100, primary_count * 25 + (len(posts) // 5) * 5)
        
        evidence_map = {
            'ultra_short_term': ultra_evidence,
            'short_term': short_evidence,
            'medium_term': medium_evidence,
            'long_term': long_evidence
        }
        
        return {
            'primary': primary,
            'confidence': confidence,
            'evidence': evidence_map[primary][:5],  # Top 5
            'all_scores': scores
        }
    
    def analyze_strategy(self, posts: List[Dict]) -> Dict:
        """Analyze user's trading strategy"""
        combined_text = ' '.join([p.get('body', '') for p in posts])
        
        strategies = {
            'scalper': (self.SCALPER_KEYWORDS, []),
            'day_trader': (self.DAY_TRADER_KEYWORDS, []),
            'swing_trader': (self.SWING_TRADER_KEYWORDS, []),
            'momentum_trader': (self.MOMENTUM_KEYWORDS, []),
            'value_investor': (self.VALUE_KEYWORDS, []),
            'growth_investor': (self.GROWTH_KEYWORDS, []),
            'income_trader': (self.INCOME_KEYWORDS, []),
            'contrarian': (self.CONTRARIAN_KEYWORDS, [])
        }
        
        scores = {}
        for strategy_name, (keywords, _) in strategies.items():
            count, evidence = self.count_pattern_matches(combined_text, keywords)
            scores[strategy_name] = count
            strategies[strategy_name] = (keywords, evidence)
        
        if max(scores.values()) == 0:
            return {
                'primary': 'unknown',
                'confidence': 0,
                'evidence': [],
                'secondary': None,
                'all_scores': scores
            }
        
        # Get primary and secondary
        sorted_strategies = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_strategies[0][0]
        primary_count = sorted_strategies[0][1]
        
        secondary = sorted_strategies[1][0] if len(sorted_strategies) > 1 and sorted_strategies[1][1] > 0 else None
        secondary_count = sorted_strategies[1][1] if secondary else 0
        
        # Calculate confidence
        primary_confidence = min(100, primary_count * 30 + (len(posts) // 5) * 5)
        secondary_confidence = min(80, secondary_count * 30) if secondary else 0
        
        return {
            'primary': primary,
            'confidence': primary_confidence,
            'evidence': strategies[primary][1][:5],
            'secondary': secondary,
            'secondary_confidence': secondary_confidence,
            'all_scores': scores
        }
    
    def analyze_conviction(self, posts: List[Dict]) -> Dict:
        """Analyze conviction level"""
        combined_text = ' '.join([p.get('body', '') for p in posts])
        
        high_count, high_evidence = self.count_pattern_matches(combined_text, self.HIGH_CONVICTION)
        medium_count, medium_evidence = self.count_pattern_matches(combined_text, self.MEDIUM_CONVICTION)
        low_count, low_evidence = self.count_pattern_matches(combined_text, self.LOW_CONVICTION)
        
        # Calculate weighted score
        score = (high_count * 100 + medium_count * 60 + low_count * 20) // max(1, len(posts))
        
        if score >= 80:
            level = 'high'
            evidence = high_evidence
        elif score >= 40:
            level = 'medium'
            evidence = medium_evidence
        else:
            level = 'low'
            evidence = low_evidence
        
        return {
            'level': level,
            'score': min(100, score),
            'evidence': evidence[:3]
        }
    
    def analyze_risk_profile(self, posts: List[Dict]) -> Dict:
        """Analyze risk profile"""
        combined_text = ' '.join([p.get('body', '') for p in posts])
        
        aggressive_count, aggressive_evidence = self.count_pattern_matches(combined_text, self.AGGRESSIVE_SIGNALS)
        conservative_count, conservative_evidence = self.count_pattern_matches(combined_text, self.CONSERVATIVE_SIGNALS)
        
        # Calculate score (0 = very conservative, 100 = very aggressive)
        if aggressive_count + conservative_count == 0:
            score = 50  # Neutral/unknown
            category = 'moderate'
            evidence = []
        else:
            score = int((aggressive_count / (aggressive_count + conservative_count)) * 100)
            if score >= 70:
                category = 'aggressive'
                evidence = aggressive_evidence
            elif score >= 30:
                category = 'moderate'
                evidence = aggressive_evidence + conservative_evidence
            else:
                category = 'conservative'
                evidence = conservative_evidence
        
        return {
            'category': category,
            'score': score,
            'evidence': evidence[:5]
        }
    
    def calculate_product_fit_score(self, profile: Dict) -> Tuple[int, str, List[str]]:
        """Calculate product fit score for in-app trading"""
        score = 0
        reasons = []
        features = []
        
        # Timeframe scoring (ultra-short = best fit)
        timeframe_scores = {
            'ultra_short_term': 30,
            'short_term': 25,
            'medium_term': 15,
            'long_term': 5
        }
        timeframe = profile['timeframe']['primary']
        score += timeframe_scores.get(timeframe, 0)
        if timeframe == 'ultra_short_term':
            reasons.append("Ultra-short timeframe (perfect for mobile trading)")
            features.extend(["Real-time quotes", "Quick execution", "0DTE options"])
        
        # Strategy scoring
        strategy_scores = {
            'day_trader': 25,
            'scalper': 25,
            'swing_trader': 20,
            'momentum_trader': 20,
            'contrarian': 15,
            'growth_investor': 10,
            'value_investor': 8,
            'income_trader': 5
        }
        strategy = profile['strategy']['primary']
        score += strategy_scores.get(strategy, 0)
        if strategy in ['day_trader', 'scalper']:
            reasons.append(f"Active {strategy.replace('_', ' ')} (high trade frequency)")
            features.extend(["Level 2 data", "Mobile alerts", "Paper trading"])
        
        # Conviction scoring
        conviction_scores = {'high': 15, 'medium': 10, 'low': 5}
        score += conviction_scores.get(profile['conviction']['level'], 0)
        
        # Risk profile scoring
        if profile['risk_profile']['category'] == 'aggressive':
            score += 20
            reasons.append("Aggressive risk profile (frequent trader)")
            features.extend(["Options chains", "Margin trading", "Advanced orders"])
        elif profile['risk_profile']['category'] == 'moderate':
            score += 10
        
        # Instruments bonus
        if profile.get('instruments', {}).get('primary') == 'options':
            score += 10
            reasons.append("Options trader (sophisticated user)")
            features.append("Options strategies builder")
        
        # Determine likelihood
        if score >= 80:
            likelihood = "very_high"
        elif score >= 60:
            likelihood = "high"
        elif score >= 40:
            likelihood = "medium"
        else:
            likelihood = "low"
        
        return min(100, score), likelihood, list(set(features))
    
    def analyze_user(self, username: str) -> Dict:
        """Complete analysis of a single user"""
        posts = self.user_activity[username]
        
        if len(posts) < 3:
            return None  # Insufficient data
        
        timeframe = self.analyze_timeframe(posts)
        strategy = self.analyze_strategy(posts)
        conviction = self.analyze_conviction(posts)
        risk_profile = self.analyze_risk_profile(posts)
        
        # Build profile
        profile = {
            'username': username,
            'total_posts': len(posts),
            'timeframe': timeframe,
            'strategy': strategy,
            'conviction': conviction,
            'risk_profile': risk_profile
        }
        
        # Calculate product fit
        product_fit_score, likelihood, features = self.calculate_product_fit_score(profile)
        profile['product_fit_score'] = product_fit_score
        profile['in_app_trading_likelihood'] = likelihood
        profile['recommended_features'] = features
        
        return profile
    
    def analyze_all_users(self, min_posts: int = 5) -> List[Dict]:
        """Analyze all users with sufficient data"""
        print(f"\nAnalyzing users with {min_posts}+ posts...")
        
        profiles = []
        for username, posts in self.user_activity.items():
            if len(posts) >= min_posts:
                profile = self.analyze_user(username)
                if profile:
                    profiles.append(profile)
        
        print(f"✓ Analyzed {len(profiles):,} users")
        return profiles
    
    def save_results(self, profiles: List[Dict], output_file: str = 'strategy_analysis.json'):
        """Save analysis results"""
        # Sort by product fit score
        profiles.sort(key=lambda x: x['product_fit_score'], reverse=True)
        
        # Generate summary stats
        summary = {
            'total_users_analyzed': len(profiles),
            'total_messages': len(self.messages),
            'timeframe_distribution': Counter([p['timeframe']['primary'] for p in profiles]),
            'strategy_distribution': Counter([p['strategy']['primary'] for p in profiles]),
            'conviction_distribution': Counter([p['conviction']['level'] for p in profiles]),
            'risk_distribution': Counter([p['risk_profile']['category'] for p in profiles]),
            'product_fit_distribution': {
                'very_high': len([p for p in profiles if p['product_fit_score'] >= 80]),
                'high': len([p for p in profiles if 60 <= p['product_fit_score'] < 80]),
                'medium': len([p for p in profiles if 40 <= p['product_fit_score'] < 60]),
                'low': len([p for p in profiles if p['product_fit_score'] < 40])
            }
        }
        
        output = {
            'summary': summary,
            'profiles': profiles[:500]  # Top 500 by product fit
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved results to {output_file}")
        
        # Also save top traders to CSV
        csv_file = output_file.replace('.json', '_top_traders.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'rank', 'username', 'product_fit_score', 'likelihood',
                'timeframe', 'timeframe_confidence',
                'strategy', 'strategy_confidence',
                'conviction', 'risk_profile',
                'posts', 'recommended_features'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, profile in enumerate(profiles[:100], 1):
                writer.writerow({
                    'rank': i,
                    'username': profile['username'],
                    'product_fit_score': profile['product_fit_score'],
                    'likelihood': profile['in_app_trading_likelihood'],
                    'timeframe': profile['timeframe']['primary'],
                    'timeframe_confidence': profile['timeframe']['confidence'],
                    'strategy': profile['strategy']['primary'],
                    'strategy_confidence': profile['strategy']['confidence'],
                    'conviction': profile['conviction']['level'],
                    'risk_profile': profile['risk_profile']['category'],
                    'posts': profile['total_posts'],
                    'recommended_features': ' | '.join(profile['recommended_features'][:3])
                })
        
        print(f"✓ Saved top 100 to {csv_file}")
        
        return summary


def main():
    print("=" * 80)
    print("TRADING STRATEGY & TIMEFRAME ANALYSIS")
    print("=" * 80)
    
    analyzer = StrategyAnalyzer('stocktwits_maximum_24h.json')
    
    profiles = analyzer.analyze_all_users(min_posts=5)
    
    summary = analyzer.save_results(profiles, 'strategy_analysis.json')
    
    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Users Analyzed: {summary['total_users_analyzed']:,}")
    
    print("\nTimeframe Distribution:")
    for timeframe, count in summary['timeframe_distribution'].most_common():
        pct = (count / summary['total_users_analyzed'] * 100)
        print(f"  {timeframe.replace('_', ' ').title():20s}: {count:4,} ({pct:5.1f}%)")
    
    print("\nStrategy Distribution:")
    for strategy, count in summary['strategy_distribution'].most_common():
        pct = (count / summary['total_users_analyzed'] * 100)
        print(f"  {strategy.replace('_', ' ').title():20s}: {count:4,} ({pct:5.1f}%)")
    
    print("\nProduct Fit Distribution:")
    for level, count in summary['product_fit_distribution'].items():
        pct = (count / summary['total_users_analyzed'] * 100)
        print(f"  {level.replace('_', ' ').title():20s}: {count:4,} ({pct:5.1f}%)")
    
    print("\n" + "=" * 80)
    print("✓ ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - strategy_analysis.json (Full results)")
    print("  - strategy_analysis_top_traders.csv (Top 100 by product fit)")
    print("=" * 80)


if __name__ == '__main__':
    main()

