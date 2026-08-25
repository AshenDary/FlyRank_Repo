
# Explain It Like You Built It: The Market Data Pipeline

**Author:** Jared Noel

## The Concept
For my "Item Market Signals" project, I had to figure out how to track the changing economy of game items over time. Instead of just showing what an item is worth *today*, I wanted to analyze market trends and generate practical valuation signals. 

To do this, I built an automated data merger and snapshot system. 

## How It Works (In Plain English)
Imagine trying to track the price of a rare collectible. If you only look at the price today, you don't know if it's currently crashing or at an all-time high. Just like tracking real-world market yields, you need a history of data to make a smart call.

To solve this, I set up an automated daily schedule using GitHub Workflows, which acts like an invisible, recurring alarm clock. Every single day, this system wakes up and pulls live trading data from a public API—which is essentially a firehose of community trades continuously happening over on Discord. 

The script takes all that raw, messy text data and translates it into solid, comparable numerical values. It then stitches these fresh numbers together with a static "rulebook" I created (a JSON file) that holds the baseline facts about each item, like its rarity and tier category. 

Once the live prices and the static rules are merged, the system takes a "snapshot" and saves it. Day by day, it builds a historical archive. When you view the dashboard, it isn't just looking at today's price; it's flipping through all those saved daily snapshots to calculate the momentum and show you the actual trend.

## The Trickiest Part
The most confusing part of building this was the data acquisition itself. Extracting clean, usable information from a public API that relies on continuous, noisy Discord trades requires a lot of trial and error to get right. 

Additionally, calculating trends when the project first started was difficult. When you only have a few daily snapshots, trying to predict a market trend is like trying to guess a stock's long-term performance by looking at a five-minute chart. The trend mechanics were in place, but the analysis only becomes truly reliable once enough historical data accumulates over time.