# Trading Strategy & Timeframe Classification Methodology

## Executive Summary

This document defines a precise, multi-dimensional framework for classifying StockTwits users by their trading intent, strategy, and timeframe. Goes beyond simple instrument preference to understand **how** users trade, not just **what** they trade.

---

## Classification Dimensions

### 1. **Timeframe Classification**

#### 1.1 Ultra-Short Term (0-1 Day)
**Definition**: Intraday traders who open and close positions within the same trading session.

**Indicators**:
- **Explicit Keywords**: `0dte`, `0DTE`, `same day`, `intraday`, `scalp`, `scalping`, `day trade`, `day trading`
- **Timing Language**: `right now`, `immediately`, `ASAP`, `quick flip`, `in and out`
- **Position Updates**: Multiple posts about same symbol within hours showing entry/exit
- **Technical Indicators**: Mentions of minute charts (1m, 5m, 15m), VWAP, level 2
- **Options**: Same-day expiration contracts, 0DTE options

**Evidence Strength**:
- HIGH: 3+ indicators present
- MEDIUM: 2 indicators
- LOW: 1 indicator

**Example Posts**:
- "Scalping $SPY 0DTE calls, in at 580, out at 582"
- "Quick day trade on $TSLA, 5m chart showing breakout"
- "$QQQ puts for today's close, watching VWAP"

---

#### 1.2 Short Term (1-7 Days)
**Definition**: Swing traders who hold positions for several days to capture short-term price movements.

**Indicators**:
- **Explicit Keywords**: `swing trade`, `swing trading`, `few days`, `short term`, `weekly`, `this week`
- **Options**: Weekly expirations (explicit dates within 7 days)
- **Chart Timeframes**: 1-hour, 4-hour, daily charts
- **Entry/Exit Language**: "Taking profits tomorrow", "holding through week", "3-day play"
- **Technical Patterns**: Cup and handle, bull flags, short-term breakouts
- **Risk Management**: Stop losses, profit targets within days

**Evidence Strength**:
- HIGH: 3+ indicators present
- MEDIUM: 2 indicators
- LOW: 1 indicator

**Example Posts**:
- "$NVDA swing trade, holding through earnings next week"
- "Bought weekly calls expiring Friday"
- "Setting stop loss 5% below, targeting 15% gain in 3-5 days"

---

#### 1.3 Medium Term (1-12 Weeks)
**Definition**: Momentum/position traders holding for weeks to months to capture larger trends.

**Indicators**:
- **Explicit Keywords**: `position trading`, `medium term`, `few weeks`, `couple months`, `momentum play`
- **Options**: Monthly expirations (30-90 days out), LEAPS mentions
- **Catalysts**: Earnings plays, product launches, seasonal trends
- **Chart Timeframes**: Daily, weekly charts
- **Fundamental Mix**: Combination of technicals and fundamentals
- **Conviction Language**: "Building position", "accumulating", "adding on dips"

**Evidence Strength**:
- HIGH: 3+ indicators present
- MEDIUM: 2 indicators
- LOW: 1 indicator

**Example Posts**:
- "$AAPL position ahead of iPhone launch in 6 weeks"
- "Buying Feb calls, think this runs into earnings"
- "Accumulating $PLTR, building 500 share position over next month"

---

#### 1.4 Long Term (3+ Months)
**Definition**: Investors focused on long-term value appreciation and fundamentals.

**Indicators**:
- **Explicit Keywords**: `long term`, `holding`, `investor`, `buy and hold`, `retirement`, `years`, `forever hold`
- **Options**: LEAPS (6+ months), selling covered calls for income
- **Fundamental Focus**: PE ratios, revenue growth, DCF models, balance sheets
- **Dividend Mentions**: Income investing, dividend growth, DRIP
- **Conviction Language**: "Core holding", "never selling", "adding to retirement account"
- **Patience Indicators**: "Don't care about daily moves", "thinking 5 years out"

**Evidence Strength**:
- HIGH: 3+ indicators present
- MEDIUM: 2 indicators
- LOW: 1 indicator

**Example Posts**:
- "$MSFT core holding, adding every month for retirement"
- "Long term investor, these daily swings don't matter"
- "Selling covered calls on my 1000 share position"

---

### 2. **Trading Strategy Classification**

#### 2.1 Scalper
**Definition**: Extracts small profits from tiny price movements, many trades per day.

**Characteristics**:
- Multiple entries/exits same symbol same day
- Focus on bid-ask spread, level 2, order flow
- Very short holding periods (seconds to minutes)
- High volume, low profit per trade
- Mentions of "ticks", "cents", "quick profits"

**Keywords**: `scalp`, `scalping`, `quick flip`, `in and out`, `ticks`, `level 2`, `tape reading`

**Evidence Requirements**: 
- Multiple same-day updates on same symbol OR
- Explicit scalping language + technical indicators

---

#### 2.2 Day Trader
**Definition**: Opens and closes positions within same trading day based on intraday patterns.

**Characteristics**:
- Closes all positions by end of day
- Uses technical analysis, chart patterns
- Mentions of 0DTE options
- Focus on high-probability setups
- Risk management per trade

**Keywords**: `day trade`, `day trading`, `0DTE`, `intraday`, `end of day`, `no overnight risk`

**Evidence Requirements**: 
- Explicit day trading language OR
- 0DTE options + same-day timing language

---

#### 2.3 Swing Trader
**Definition**: Captures price "swings" over several days using technical and fundamental catalysts.

**Characteristics**:
- Holds 2-10 days typically
- Uses daily charts, support/resistance
- Catalyst-aware (earnings, news)
- Clear entry/exit rules
- Risk/reward ratios

**Keywords**: `swing trade`, `swing`, `few days`, `weekly setup`, `short term play`

**Evidence Requirements**: 
- Swing trading language + timeframe indicators OR
- Weekly options + technical analysis mentions

---

#### 2.4 Momentum Trader
**Definition**: Follows trending stocks with strong price momentum and volume.

**Characteristics**:
- Rides trends (days to weeks)
- Volume confirmation
- Momentum indicators (RSI, MACD)
- Trend following strategies
- "Buy high, sell higher" mentality

**Keywords**: `momentum`, `breakout`, `trending`, `riding the wave`, `catching the move`, `volume surge`

**Evidence Requirements**: 
- Momentum language + volume mentions OR
- Breakout patterns + continuation language

---

#### 2.5 Value Investor
**Definition**: Buys undervalued stocks based on fundamental analysis for long-term appreciation.

**Characteristics**:
- Fundamental analysis focus
- PE ratios, book value, intrinsic value
- Contrarian often (buying dips)
- Long holding periods
- Margin of safety concept

**Keywords**: `undervalued`, `cheap`, `PE ratio`, `value`, `fundamentals`, `intrinsic value`, `margin of safety`

**Evidence Requirements**: 
- Value language + fundamental metrics OR
- Long-term language + contrarian positioning

---

#### 2.6 Growth Investor
**Definition**: Invests in companies with strong growth potential, willing to pay premium valuations.

**Characteristics**:
- Revenue/earnings growth focus
- Future potential over current profits
- Technology, innovation focus
- Higher risk tolerance
- Long-term conviction

**Keywords**: `growth stock`, `revenue growth`, `disruptive`, `innovation`, `future potential`, `high growth`

**Evidence Requirements**: 
- Growth language + future-focused OR
- High-multiple stocks + conviction language

---

#### 2.7 Income Trader
**Definition**: Generates income through dividends, covered calls, or premium selling.

**Characteristics**:
- Dividend yield focus
- Covered calls, cash-secured puts
- Theta gang strategies
- Monthly income goals
- Lower risk tolerance

**Keywords**: `dividend`, `income`, `covered calls`, `selling premium`, `theta gang`, `yield`, `monthly income`

**Evidence Requirements**: 
- Income language + dividend/premium mentions OR
- Option selling + income strategy language

---

#### 2.8 Contrarian
**Definition**: Takes positions opposite to market sentiment, buying fear and selling greed.

**Characteristics**:
- Counter-trend positioning
- Sentiment indicators
- "Be fearful when greedy"
- Dip buying, short-term reversals
- Fade the crowd mentality

**Keywords**: `contrarian`, `buying the dip`, `everyone wrong`, `fade the move`, `oversold`, `overbought`, `sentiment extreme`

**Evidence Requirements**: 
- Contrarian language + opposite positioning OR
- Sentiment analysis + counter-trend trades

---

### 3. **Conviction Level Classification**

#### 3.1 High Conviction (80-100%)
**Indicators**:
- Large position sizes mentioned ("all in", "biggest position")
- Multiple posts about same position
- Detailed research/analysis shared
- Strong opinion language ("guaranteed", "no doubt", "100%")
- Defending position against skeptics
- Adding on dips

**Example**: "This is my largest position, been researching for months, adding more today"

---

#### 3.2 Medium Conviction (40-79%)
**Indicators**:
- Moderate position sizing
- Balanced language ("think it goes higher", "good setup")
- Some analysis but not exhaustive
- Open to other views
- Standard risk management

**Example**: "Looks like a good setup, took a starter position, will add if confirms"

---

#### 3.3 Low Conviction (1-39%)
**Indicators**:
- Small position sizes ("lottery ticket", "small spec")
- Hedging language ("might work", "we'll see", "risky")
- Entertainment/gambling framing
- Quick to exit
- No strong opinion

**Example**: "Threw $100 at this as a lottery ticket, 0DTE calls"

---

### 4. **Risk Profile Classification**

#### 4.1 Aggressive
**Characteristics**:
- Leveraged instruments (options, 3x ETFs)
- Short-term expiries
- All-or-nothing positioning
- High beta stocks
- Margin trading

**Indicators**: Options, TQQQ/SQQQ, 0DTE, "YOLO", leverage mentions

---

#### 4.2 Moderate
**Characteristics**:
- Mix of stocks and options
- Defined risk management
- Diversified positions
- Standard timeframes
- Stop losses used

**Indicators**: Risk/reward ratios, stops mentioned, position sizing, diversification

---

#### 4.3 Conservative
**Characteristics**:
- Stock-only or long-dated options
- Dividend focus
- Large-cap stocks
- Long timeframes
- Capital preservation

**Indicators**: Blue chips, dividends, long-term language, safety focus

---

## Implementation Scoring System

### Confidence Scores

Each classification receives a confidence score (0-100):

**90-100**: Extremely High Confidence
- 4+ explicit indicators
- Consistent behavior across multiple posts
- Detailed evidence

**70-89**: High Confidence
- 3 explicit indicators
- Mostly consistent behavior
- Good evidence

**50-69**: Medium Confidence
- 2 indicators
- Some consistency
- Adequate evidence

**30-49**: Low Confidence
- 1-2 weak indicators
- Limited posts
- Circumstantial evidence

**0-29**: Very Low Confidence
- Insufficient data
- Contradictory signals
- Need more observation

---

## Multi-Dimensional User Profile

Each user gets scored across all dimensions:

```json
{
  "username": "example_trader",
  "total_posts": 45,
  "analysis_period": "24h",
  
  "timeframe": {
    "primary": "ultra_short_term",
    "confidence": 95,
    "evidence": ["0DTE", "scalping", "same day", "5m charts"],
    "secondary": null
  },
  
  "strategy": {
    "primary": "day_trader",
    "confidence": 90,
    "evidence": ["explicit day trading language", "0DTE options", "no overnight"],
    "secondary": "scalper",
    "secondary_confidence": 60
  },
  
  "conviction": {
    "level": "medium",
    "score": 65,
    "evidence": ["moderate position sizing", "balanced language"]
  },
  
  "risk_profile": {
    "category": "aggressive",
    "score": 85,
    "evidence": ["0DTE options", "leveraged ETFs", "high frequency"]
  },
  
  "instruments": {
    "primary": "options",
    "types": ["calls", "puts", "spreads"],
    "confidence": 100
  },
  
  "product_fit_score": 92,
  "in_app_trading_likelihood": "very_high",
  "recommended_features": [
    "0DTE options",
    "real-time quotes",
    "quick execution",
    "mobile-first",
    "paper trading mode"
  ]
}
```

---

## Validation & Quality Checks

### Minimum Requirements for Classification:
- At least 5 posts in analysis period
- At least 2 dimensions have medium+ confidence
- No contradictory signals (e.g., "day trader" + "holding forever")

### Edge Cases:
- **Multi-strategy traders**: Assign primary and secondary
- **Transitioning traders**: Weight recent posts higher
- **Inconsistent signals**: Flag as "mixed" with lower confidence
- **Limited data**: Mark as "insufficient_data"

---

## Usage Examples

### Example 1: Clear Day Trader
**Posts**:
1. "Scalping $SPY 0DTE calls"
2. "$QQQ day trade, in at 480, out at 482"
3. "Love 0DTE, no overnight risk"

**Classification**:
- Timeframe: Ultra-short (100% confidence)
- Strategy: Day Trader (95% confidence)
- Risk: Aggressive (90% confidence)
- Instruments: Options (100% confidence)

---

### Example 2: Long-Term Investor
**Posts**:
1. "$AAPL core holding, never selling"
2. "Added to $MSFT for retirement"
3. "Don't care about daily noise, thinking years out"

**Classification**:
- Timeframe: Long-term (100% confidence)
- Strategy: Growth Investor (80% confidence)
- Risk: Conservative (85% confidence)
- Instruments: Stocks Only (100% confidence)

---

### Example 3: Mixed Signals (Lower Confidence)
**Posts**:
1. "$TSLA swing trade"
2. "$SPY holding long term"

**Classification**:
- Timeframe: Mixed (50% confidence) - need more data
- Strategy: Unclear (40% confidence) - insufficient evidence
- Flag: Needs more observation

---

## Product Development Implications

### For In-App Trading:

**Ultra-Short Term Traders** (0-1 day):
- Real-time quotes essential
- Mobile-first design
- Quick execution (< 1 second)
- Level 2 data
- Options chains
- Paper trading mode

**Short Term Traders** (1-7 days):
- Good charting tools
- Alerts/notifications
- Options strategies
- Risk management tools

**Medium/Long Term** (1+ weeks):
- Research integration
- Fundamental data
- Portfolio analytics
- Tax optimization

### Revenue Potential by Segment:
- **Ultra-Short**: Highest volume, highest revenue
- **Short-Term**: High volume, good revenue
- **Medium-Term**: Medium volume, steady revenue
- **Long-Term**: Low volume, but high AUM

---

## Next Steps

1. Implement this methodology in Python
2. Run on full 30K message dataset
3. Generate user profiles
4. Validate with sample review
5. Create product recommendation matrix
6. Build dashboard visualization

