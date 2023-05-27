import discord
from  discord.ext import commands
import sqlite3
import json
import os

path = 'C:\\Users\\dr_mc\\Desktop\\Mario Superstar Baseball League\\baseball bot\\teams.db'
conn = sqlite3.connect(path)
cursor = conn.cursor()
TOKEN = ''
intents = discord.Intents.default()
intents.message_content = True

DRAFTCHANNEL = 725385443834593312
draftStarted = 0

client = commands.Bot(command_prefix='.', intents=intents)

cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        username TEXT,
        character TEXT
    )
''')
cursor.execute('''
    DROP TABLE game_data;
    '''
)
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
    DROP TABLE roster_data;
    '''
)
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

# Dictionary to keep track of drafted characters and their counts
drafted_characters = {}
teams = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user} and ready {draftStarted}')

# Start draft
@client.command()
async def startDraft(ctx):
    await ctx.send(f'The draft has begun')
    global draftStarted
    draftStarted = 1
    print(f'draftStarted: {draftStarted}')

# End draft
@client.command()
async def endDraft(ctx):
    await ctx.send(f'The draft is complete. Goodluck and happy baseball.')
    global draftStarted
    draftStarted = 2
    print(f'draftStarted: {draftStarted}')

@client.command()
async def draft(ctx, *, args):
    author = ctx.author
    mention = ctx.message.mentions
    target_user = mention[0] if mention else author

    if draftStarted == 1:
        characters_to_draft = args.split()
        if mention:
            characters_to_draft = [c for c in characters_to_draft if c != mention[0].mention]

        for character in characters_to_draft:
            print(f'{author} is attempting to draft {character}')
            if character not in characters:
                print(f'{character} is not a valid character.')
                await ctx.send(f'{character} is not a valid character')
                continue
            if character not in drafted_characters:
                drafted_characters[character] = 1
                teams.setdefault(target_user.id, []).append(character)

                # Insert the drafted character into the database
                conn = sqlite3.connect('teams.db')
                cursor = conn.cursor()
                insert_query = '''
                INSERT INTO teams (user_id, username, character)
                VALUES (?, ?, ?)
                '''
                cursor.execute(insert_query, (target_user.id, target_user.name, character))
                conn.commit()
                conn.close()

                print(f'{author} has successfully drafted {character}. There is ONE {character} left')
                await ctx.send(f'{author} has successfully drafted {character} onto {target_user.name}\'s team. There is ONE {character} left')
            elif drafted_characters[character] < 2:
                drafted_characters[character] += 1
                teams.setdefault(target_user.id, []).append(character)

                # Insert the drafted character into the database
                conn = sqlite3.connect('teams.db')
                cursor = conn.cursor()
                insert_query = '''
                INSERT INTO teams (user_id, username, character)
                VALUES (?, ?, ?)
                '''
                cursor.execute(insert_query, (target_user.id, target_user.name, character))
                conn.commit()
                conn.close()

                print(f'{author} has successfully drafted {character}. There are ZERO {character}s left')
                await ctx.send(f'{author} has successfully drafted {character} onto {target_user.name}\'s team. There are ZERO {character}s left')
            else:
                print(f'{character} has already been drafted twice.')
                await ctx.send(f'{character} has already been drafted twice.')
    elif draftStarted == 0:
        print(f'Draft has not started yet {draftStarted}')
        await ctx.send(f'Draft has not started yet.')
    elif draftStarted == 2:
        print(f'Draft is completed')
        await ctx.send(f'The draft is completed.')

@client.command()
async def undraft(ctx, mention, *, character):
    author = ctx.author
    guild = ctx.guild

    # Check if a mentioned user is present
    if mention:
        mentioned_user = ctx.message.mentions[0]
        user_id = mentioned_user.id
        author_name = mentioned_user.name
    else:
        mentioned_user = None
        user_id = author.id
        author_name = author.name

    # Check if the character has been drafted by the author or mentioned user
    if user_id in teams and character in teams[user_id]:
        conn = sqlite3.connect('teams.db')
        cursor = conn.cursor()

        # Find the row matching the user_id and character
        query = 'SELECT rowid FROM teams WHERE user_id = ? AND character = ? LIMIT 1'
        cursor.execute(query, (user_id, character))
        row = cursor.fetchone()

        if row:
            # Delete the row using the retrieved rowid
            delete_query = 'DELETE FROM teams WHERE rowid = ?'
            cursor.execute(delete_query, (row[0],))
            conn.commit()
            conn.close()

            # Remove one instance of the character from the author's or mentioned user's team in the teams dictionary
            if mentioned_user:
                teams[user_id].remove(character)
            else:
                teams[author.id].remove(character)

            # Decrement the count of drafted characters in the drafted_characters dictionary
            drafted_characters[character] -= 1

            # Get the count of available characters for drafting
            available_count = 2 - drafted_characters.get(character, 0)

            await ctx.send(f'{character} has been undrafted from {author_name}\'s team. '
                           f'There are {available_count} {character}(s) available for drafting.')
            return

    await ctx.send(f'{character} has not been drafted by {author_name}.')



@client.command()
async def drafted(ctx):
    print('Displaying drafted characters')
    output = 'Drafted Characters: \n'
    for character, count in drafted_characters.items():
        output += f'{character}: {count}\n'

    await ctx.send(output)

@client.command()
async def getTeam(ctx, *, character=None):
    if character is None:
        await ctx.send("Please provide a character name.")
        return

    # Convert the character name to lowercase
    character = character.lower()

    # Check if the lowercase character name is in the characters list
    if character not in (c.lower() for c in characters):
        await ctx.send(f"{character} is not a valid character.")
        return

    # Establish a database connection
    conn = sqlite3.connect('teams.db')
    cursor = conn.cursor()

    query = "SELECT username FROM teams WHERE LOWER(character) = ?"
    cursor.execute(query, (character,))
    result = cursor.fetchone()

    # Close the database connection
    conn.close()

    if result:
        username = result[0]
        await ctx.send(f'{character.capitalize()} has been drafted by {username}.')
    else:
        await ctx.send(f'{character.capitalize()} has not been drafted.')

@client.command()
async def listUndrafted(ctx):
    undrafted_characters = [character for character in characters if character not in drafted_characters]
    if undrafted_characters:
        output = "Undrafted Characters:\n"
        line_length = 0
        line = ""

        for character in undrafted_characters:
            if line_length + len(character) + 2 <= 100:
                line += character + ", "
                line_length += len(character) + 2
            else:
                output += line[:-2] + "\n"  # Remove the trailing comma and space
                line = character + ", "
                line_length = len(character) + 2

        if line:
            output += line[:-2] + "\n"  # Remove the trailing comma and space

        await ctx.send(output)
    else:
        await ctx.send("All characters have been drafted.")

@client.command()
async def getUserTeam(ctx, *, username):
    if ctx.message.mentions:
        username = ctx.message.mentions[0].name

    # Fetch the drafted characters for the user from the database
    conn = sqlite3.connect('teams.db')
    cursor = conn.cursor()
    query = '''
    SELECT character FROM teams
    WHERE username = ?
    '''
    cursor.execute(query, (username,))
    result = cursor.fetchall()
    conn.close()

    if result:
        characters = [row[0] for row in result]
        await ctx.send(f"The team drafted by {username}: {', '.join(characters)}")
    else:
        await ctx.send(f"{username} has not drafted any characters.")

client.remove_command('help')

@client.command()
async def help(ctx):
    await ctx.send(f'Please only use me in #bot-spam. \nCommands are: \n\t .startDraft to begin a draft. \n\t .draft Character to draft a character. There is capitalization and spelling, Matt was too lazy to sanitize inputs.\n\t .undraft Character to remove a character from a team\n\t Note: characters may be drafted onto other player\'s teams by doing .draft @user Character. This is purely for convenience, don\'t draft characters onto other player\'s teams please.  \n\t .drafted to see what characters have been drafted. \n\t .getTeam Character to see the team a character was drafted onto. \n\t .getUserTeam username to get another perons\'s team. \n\t .listUndrafted to get a list of all undrafted characters \n\t .endDraft to complete the draft')

@client.command()
async def wipeDatabase(ctx):
    conn = sqlite3.connect('teams.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM teams;') 
    cursor.execute('DELETE FROM game_data;')
    cursor.execute('DELETE FROM roster_data;')
    conn.commit()
    conn.close()
    await ctx.send('The database has been wiped.')

    # Clear the drafted characters and teams dictionaries
    drafted_characters.clear()
    teams.clear()

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
            era = round((earned_runs/outs_pitched) * 9, 2)
            whip = round((batters_walked + batters_hit + hits_allowed)/(outs_pitched/3), 2)
            hits_per_9 = round((hits_allowed/outs_pitched) * 9, 2)
            hrs_per_9 = round((hrs_allowed/outs_pitched)  * 9, 2)
            bb_per_9 = round((batters_walked/outs_pitched) * 9, 2)
            so_per_9 = round((strikeouts_pitching/outs_pitched) * 9, 2)
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
            batting_average = round(hits/at_bats, 2)
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