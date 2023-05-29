import discord
from  discord.ext import commands
import sqlite3
import json
import os
from dotenv import load_dotenv

load_dotenv()
path = os.getenv("DB_PATH")
conn = sqlite3.connect(path)
cursor = conn.cursor()
TOKEN = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

DRAFTCHANNEL = 725385443834593312
draftStarted = 0

client = commands.Bot(command_prefix='.', intents=intents)

cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY,
        team_name TEXT
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_members (
        member_id INEGER primary KEY,
        team_id INTEGER,
        character_id TEXT,
        FOREIGN KEY (team_id) REFERENCES teams (team_id)
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS discord_users (
        user_id INTEGER PRIMARY KEY,
        discord_username TEXT,
        team_id INTEGER,
        FOREIGN KEY (team_id) REFERENCES teams (team_id)
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_data (
        game_id TEXT PRIMARY KEY,
        game_date TEXT,
        stadium_id TEXT,
        away_player TEXT,
        home_player TEXT,
        away_score INTEGER,
        home_score INTEGER,
        innings_selected INTEGER,
        innings_played INTEGER,
        quitter_team TEXT,
        average_ping INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS roster_data (
    roster_id INTEGER PRIMARY KEY,
    game_id INTEGER,
    team TEXT,
    roster_id_game INTEGER,
    character_id TEXT,
    superstar INTEGER,
    captain INTEGER,
    fielding_hand TEXT,
    batting_hand TEXT,
    stamina INTEGER,
    was_pitcher INTEGER,
    strikeouts_pitching INTEGER,
    strikeouts_batting INTEGER,
    star_pitches_thrown INTEGER,
    big_plays INTEGER,
    outs_pitched INTEGER,
    at_bats INTEGER,
    hits INTEGER,
    singles INTEGER,
    doubles INTEGER,
    triples INTEGER,
    home_runs INTEGER,
    successful_bunts INTEGER,
    sac_flys INTEGER,
    walks_four_balls INTEGER,
    walks_hit INTEGER,
    rbi INTEGER,
    bases_stolen INTEGER,
    star_hits INTEGER,
    batting_average REAL,
    hits_per_at_bats REAL,
    slg REAL,
    obp REAL,
    ops REAL,
    batters_faced INTEGER,
    runs_allowed INTEGER,
    earned_runs INTEGER,
    batters_walked INTEGER,
    batters_hit INTEGER,
    hits_allowed INTEGER,
    hrs_allowed INTEGER,
    pitches_thrown INTEGER,
    era REAL,
    innings_pitched REAL,    
    whip REAL,
    hits_per_9 REAL,
    hrs_per_9 REAL,
    bb_per_9 REAL,
    so_per_9 REAL,
    so_bb_ratio REAL,
    FOREIGN KEY (game_id) REFERENCES game_data (game_id)
)
''')

#cursor.execute(table_query)

conn.commit()
conn.close()

# List of characters available for drafting
characters = [
    "Mario", "Luigi", "Peach", "Daisy", "Yoshi", "Birdo", "Wario", "Waluigi",
    "Donkey Kong", "Diddy Kong", "Bowser", "Bowser Jr.", "Boo", "Petey Piranha",
    "Dixie Kong", "Grey Dry Bones", "Toadsworth", "Toadette", "Baby Mario", "Baby Luigi",
    "Red Toad", "Blue Toad", "Yellow Toad", "Green Toad", "Purple Toad", "Green Koopa Troopa",
    "Red Koopa Troopa", "Red Shy Guy", "Blue Shy Guy", "Yellow Shy Guy", "Green Shy Guy", "Black Shy Guy",
    "Goomba", "Blue Magikoopa", "Red Magikoopa", "Green Magikoopa", "Yellow Magikoopa", "Green Koopa Paratroopa",
    "Green Dry Bones", "Red Dry Bones", "Blue Dry Bones", "Blue Noki", "Red Noki", "Green Noki", "Red Koopa Paratroopa",
    "Paragoomba", "Monty Mole", "King Boo", "Blue Pianta", "Red Pianta", "Yellow Pianta", "Hammer Bro", "Boomerang Bro", "Fire Bro"
]

@client.event
async def on_ready():
    print(f'Logged in as {client.user} and ready {draftStarted}')

@client.command()
async def wipeDatabase(ctx):
    conn = sqlite3.connect('teams.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM teams;') 
    cursor.execute('DELETE FROM game_data;')
    cursor.execute('DELETE FROM roster_data;')
    cursor.execute('DELETE FROM team_members;')
    cursor.execute('DELETE FROM discord_users;')
    conn.commit()
    conn.close()
    await ctx.send('The database has been wiped.')

@client.command()
async def parseJSON(ctx):
    if len(ctx.message.attachments) == 0:
        await ctx.send("No file attached. Please upload a JSON file.")
        return

    attachment = ctx.message.attachments[0]

    if not attachment.filename.endswith('.json'):
        await ctx.send("Invalid file format. Please upload a JSON file.")
        return

    try:
        await attachment.save(attachment.filename)
    except Exception as e:
        await ctx.send(f"Error saving the file: {str(e)}")
        return

    try:
        with open(attachment.filename, 'r') as file:
            data = json.load(file)
    except Exception as e:
        await ctx.send(f"Error parsing the JSON file: {str(e)}")
        return

    conn = sqlite3.connect('teams.db')
    cursor = conn.cursor()

    # Extract game details
    game_id = data.get('GameID')
    cursor.execute('SELECT game_id FROM game_data WHERE game_id = ?', (game_id,))
    
    if cursor.fetchone() is not None:
            await ctx.send(f"Game with GameID {game_id} already exists. Thanks for submitting.")
            conn.close()
            os.remove(attachment.filename)
            return

    game_date = data.get('Date - Start')
    stadium_id = data.get('StadiumID')
    away_player = data.get('Away Player')
    home_player = data.get('Home Player')
    away_score = data.get('Away Score')
    home_score = data.get('Home Score')
    innings_selected = data.get('Innings Selected')
    innings_played = data.get('Innings Played')
    quitter_team = data.get('Quitter Team')
    average_ping = data.get('Average Ping')
    version = data.get('Version')

    cursor.execute('''
        INSERT INTO game_data (
            game_id, game_date, stadium_id, away_player, home_player,
            away_score, home_score, innings_selected, innings_played, quitter_team, average_ping    
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (game_id, game_date, stadium_id, away_player, home_player, away_score,
        home_score, innings_selected, innings_played, quitter_team, average_ping))

    # Extract roster details and insert into roster_data table
    roster_data = data.get('Character Game Stats', {})
    for roster_key, roster_entry in roster_data.items():
        team = roster_entry.get('Team')
        roster_id_game = roster_entry.get('RosterID')
        character_id = roster_entry.get('CharID')
        superstar = roster_entry.get('Superstar')
        captain = roster_entry.get('Captain')
        fielding_hand = roster_entry.get('Fielding Hand')
        batting_hand = roster_entry.get('Batting Hand')

        # Defensive Stats
        defensive_stats = roster_entry['Defensive Stats']
        batters_faced = defensive_stats.get('Batters Faced')
        runs_allowed = defensive_stats.get('Runs Allowed')
        earned_runs = defensive_stats.get('Earned Runs')
        batters_walked = defensive_stats.get('Batters Walked')
        batters_hit = defensive_stats.get('Batters Hit')
        hits_allowed = defensive_stats.get('Hits Allowed')
        hrs_allowed = defensive_stats.get('HRs Allowed')
        pitches_thrown = defensive_stats.get('Pitches Thrown')
        outs_pitched = defensive_stats.get('Outs Pitched')
        was_pitcher = defensive_stats.get('Was Pitcher')
        strikeouts_pitching = defensive_stats.get('Strikeouts')
        star_pitches_thrown = defensive_stats.get('Star Pitches Thrown')
        big_plays = defensive_stats.get('Big Plays')
        stamina = defensive_stats.get('Stamina')

        # Calculated Defensive Stats

        if pitches_thrown != 0 and outs_pitched != 0:
            innings_pitched = round(outs_pitched/3, 2)
            era = round(earned_runs/(innings_pitched) * 9, 2)
            whip = round((batters_walked + batters_hit + hits_allowed)/(innings_pitched), 2)
            hits_per_9 = round((hits_allowed/innings_pitched) * 9, 2)
            hrs_per_9 = round((hrs_allowed/innings_pitched)  * 9, 2)
            bb_per_9 = round(((batters_walked + batters_hit)/innings_pitched) * 9, 2)
            so_per_9 = round((strikeouts_pitching/innings_pitched) * 9, 2)
            if batters_walked or batters_hit != 0:
                so_bb_ratio = round(strikeouts_pitching/(batters_walked + batters_hit))
        else:
            innings_pitched = 0
            era = 0
            whip = 0
            hits_per_9 = 0
            hrs_per_9 = 0
            bb_per_9 = 0
            so_per_9 = 0
            so_bb_ratio = 0
    

        # Offensive stats
        offensive_stats = roster_entry.get('Offensive Stats', {})
        at_bats = offensive_stats.get('At Bats')
        hits = offensive_stats.get('Hits')
        singles = offensive_stats.get('Singles')
        doubles = offensive_stats.get('Doubles')
        triples = offensive_stats.get('Triples')
        home_runs = offensive_stats.get('Homeruns')
        successful_bunts = offensive_stats.get('Successful Bunts')
        sac_flys = offensive_stats.get('Sac Flys')
        strikeouts_batting = offensive_stats.get('Strikeouts')
        walks_four_balls = offensive_stats.get('Walks (4 Balls)')
        walks_hit = offensive_stats.get('Walks (Hit)')
        rbi = offensive_stats.get('RBI')
        bases_stolen = offensive_stats.get('Bases Stolen')
        star_hits = offensive_stats.get('Star Hits')
        
        # Caculated Offensive Stats
        if at_bats != 0:
            batting_average = "%.03f" % round(hits/at_bats, 3)
        else:
            batting_average = 0

        if at_bats != 0:
            hits_per_at_bats = round(hits/at_bats, 2)
        else:
            hits_per_at_bats = 0        
        if at_bats != 0:
            slg = round((singles + 2 * doubles + 3 * triples + 4 * home_runs) / at_bats, 2)
        else:
            slg = 0
        obp = round((hits + walks_four_balls + walks_hit) / (at_bats + walks_four_balls + walks_hit + sac_flys), 2)
        ops = round(obp + slg, 2)

        cursor.execute(
            '''
            INSERT INTO roster_data (
                game_id, team, roster_id_game, character_id, superstar, captain, fielding_hand,
                batting_hand, stamina, was_pitcher, strikeouts_pitching, star_pitches_thrown,
                big_plays, outs_pitched, at_bats, hits, singles, doubles, triples, home_runs,
                successful_bunts, sac_flys, strikeouts_batting, walks_four_balls, walks_hit,
                rbi, bases_stolen, star_hits, batting_average, hits_per_at_bats, slg, obp, ops,
                batters_faced, runs_allowed, earned_runs, batters_walked, batters_hit, hits_allowed,
                hrs_allowed, pitches_thrown, era, whip, hits_per_9, hrs_per_9, bb_per_9, so_per_9, so_bb_ratio, 
                innings_pitched
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                game_id, team, roster_id_game, character_id, superstar, captain, fielding_hand,
                batting_hand, stamina, was_pitcher, strikeouts_pitching, star_pitches_thrown,
                big_plays, outs_pitched, at_bats, hits, singles, doubles, triples, home_runs,
                successful_bunts, sac_flys, strikeouts_batting, walks_four_balls, walks_hit,
                rbi, bases_stolen, star_hits, batting_average, hits_per_at_bats, slg, obp, ops,
                batters_faced, runs_allowed, earned_runs, batters_walked, batters_hit, hits_allowed,
                hrs_allowed, pitches_thrown, era, whip, hits_per_9, hrs_per_9, bb_per_9, so_per_9, so_bb_ratio,
                innings_pitched
            ),
        )

    conn.commit()
    conn.close()

    if 'GameID' in data:
        await ctx.send(f"GameID: {data['GameID']}")
    else:
        await ctx.send("JSON file does not contain a 'GameID' key.")

    os.remove(attachment.filename)

client.run(TOKEN)