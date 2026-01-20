import discord
import feedparser
import os
import asyncio

# --- CONFIGURATION ---
# Get these from GitHub Secrets later
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

# Your Feeds (Use RSS Bridge links for Insta/FB)
FEEDS = [
    {
        "name": "Youtube",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=YOUR_CHANNEL_ID",
        "platform": "YouTube"
    },
    # Add more feeds here
]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("Channel not found!")
        await client.close()
        return

    # 1. Get the last 10 messages from the bot to see what we posted last
    last_posted_links = []
    async for message in channel.history(limit=20):
        if message.author == client.user:
            last_posted_links.append(message.content)

    # 2. Check feeds
    for feed_config in FEEDS:
        try:
            feed = feedparser.parse(feed_config['url'])
            if not feed.entries:
                continue

            latest_entry = feed.entries[0]
            latest_link = latest_entry.link

            # 3. Check if we already posted this link
            already_posted = any(latest_link in content for content in last_posted_links)

            if not already_posted:
                print(f"New post found for {feed_config['name']}!")
                await channel.send(f"**New post on {feed_config['platform']}!**\n{latest_link}")
            else:
                print(f"No new updates for {feed_config['name']}.")

        except Exception as e:
            print(f"Error checking {feed_config['name']}: {e}")

    # 4. Close the bot (important for GitHub Actions!)
    await client.close()

client.run(DISCORD_TOKEN)
