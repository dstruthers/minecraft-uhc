import math, mc, time

class Player:
    def __init__(self):
        self.ready = False

server = mc.MinecraftServer('minecraft/server.jar', directory='minecraft')
server.match_started = False
server.players = {}

@server.on_start
def on_start():
    server.set_difficulty(mc.PEACEFUL)
    server.set_game_rule('naturalRegeneration', False)
    server.set_world_spawn(0, 0, 0)

    # Display health in tab list
    server.send('/scoreboard objectives add health health\n')
    server.send('/scoreboard objectives setdisplay list health\n')

@server.on_login
def on_login(event):
    """Perform necessary actions on players as they log in."""

    if not server.match_started:
        server.set_game_mode(mc.SURVIVAL_MODE, event.player)

        server.apply_effect(event.player, 'blindness', 3600, 128)
        server.apply_effect(event.player, 'slowness', 3600, 128)
        server.apply_effect(event.player, 'mining_fatigue', 3600, 128)
        server.apply_effect(event.player, 'jump_boost', 3600, -128)
        server.apply_effect(event.player, 'invisibility', 3600)
        server.apply_effect(event.player, 'regeneration', 3600, 128)
        server.apply_effect(event.player, 'resistance', 3600, 128)
        server.apply_effect(event.player, 'water_breathing', 3600)
        server.apply_effect(event.player, 'fire_resistance', 3600, 128)

        server.tell_raw(event.player, '{"text": "Welcome to UHC!", "color": "yellow"}')
        server.tell_raw(event.player, '{"color": "yellow", "text": "Say ", "extra": [{"color": "green", "text": ".ready"}, " when you are ready to begin."]}')
        
        server.players[event.player] = Player()
    else:
        if event.player not in server.players:
            server.set_game_mode(mc.SPECTATOR_MODE, event.player)

@server.on_logout
def on_logout(event):
    if not server.match_started:
        del server.players[event.player]
            
@server.on_death
def on_death(event):
    """Drop player's head and switch them to game mode 3 upon death."""
    
    if server.match_started:
        player_head = '{Item: {id: "minecraft:skull", Damage: 3, Count: 1, tag: {SkullOwner: %s }}}' % event.player
        server.summon_at_player(event.player, 'Item', player_head)
        server.set_game_mode(mc.SPECTATOR_MODE, event.player)

@server.on_chat(pattern='\.ready')
def on_ready(event):
    server.players[event.player].ready = True
    server.say('%s is ready!' % event.player)
        
@server.on_chat(pattern='\.unready')
def on_unready(event):
    server.players[event.player].ready = False
    server.say('%s is not ready!' % event.player)

@server.on_chat(pattern='\.start')
def on_start(event):
    unready_players = [k for k, v in server.players.items() if not v.ready]

    if len(unready_players):
        server.say('Still waiting on the following players: ' + ', '.join(unready_players))
    else:
        server.match_started = True
        spread_distance = 250
        world_diameter = spread_distance * 2 + 50
        server.send('/worldborder set %d\n' % world_diameter)
        server.spread_players(0, 0, spread_distance, spread_distance + 1, True)
        server.set_time(0)
        server.set_difficulty(mc.HARD)
        server.send('/title @a times 5 200 0\n')
        server.send('/title @a title {"text": "Get Ready...", "bold": "true"}\n')
        for sec in range(5, 0, -1):
            server.send('/title @a subtitle {"text": "%s", "color": "gray"}\n' % sec)
            server.play_sound('block.note.harp', 'ambient', '@a', 0, 0, 0, 1, 1, 1)
            time.sleep(1)
        server.send('/title @a subtitle {"text": ""}\n')
        server.send('/title @a times 5 40 5\n')
        server.send('/title @a title {"text": "Go!", "bold": "true", "color": "green"}\n')
        server.play_sound('entity.wither.spawn', 'ambient', '@a', 0, 0, 0, 1, 1, 1)
        server.clear_inventory('@a')
        server.take_achievement('@a', '*')
        server.apply_effect('@a', 'clear')
        server.send('/worldborder set 100 5400\n')
    
server.start()
