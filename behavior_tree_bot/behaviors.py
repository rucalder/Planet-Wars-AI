import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

# attack - from aggressive_bot
def attack_weakest_enemy_planet(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    enemy_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(enemy_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return

# spread - from spread_bot
def spread_to_weakest_neutral_planet(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    neutral_planets = [planet for planet in state.neutral_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    neutral_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(neutral_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        target_to_distance = {}             #Dictionary mapping targets to closest distance
        ally_to_target = {}                 #Dictionary mapping allies to their closest targets
        for ally in state.my_planets():
            closest_distance = 99999
            for target in state.not_my_planets():
                ally_to_target_distance = state.distance(ally.ID,target.ID)
                if ally not in ally_to_target or ally_to_target_distance < closest_distance:
                    ally_to_target[ally] = target
                    closest_distance = ally_to_target_distance

        target_planet = ally_to_target[my_planet]       
        while True:
            required_ships = target_planet.num_ships + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return

# spread_production - from production_bot
def spread_production(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))

    target_planets = [planet for planet in state.not_my_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    target_planets_fallback = iter(sorted(target_planets, key=lambda p: p.num_ships))

    try:
        my_planet = next(my_planets)
        #target_planet = next(target_planets)
        target_to_distance = {}             #Dictionary mapping targets to closest distance
        ally_to_target = {}                 #Dictionary mapping allies to their closest targets
        print("Target planets:" + str(target_planets))
        for ally in state.my_planets():
            closest_distance = 99999
            for target in target_planets:
                ally_to_target_distance = state.distance(ally.ID,target.ID)
                if ally not in ally_to_target or ally_to_target_distance < closest_distance:
                    ally_to_target[ally] = target
                    closest_distance = ally_to_target_distance

        if my_planet in ally_to_target:
            target_planet = ally_to_target[my_planet]   
        else:
            target_planet = next(target_planets_fallback)    
        while True:
            if target_planet.owner == 0:
                required_ships = target_planet.num_ships + 1
            else:
                required_ships = target_planet.num_ships + \
                                 state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships: #and not any(fleet.destination_planet == my_planet.ID for fleet in state.enemy_fleets()):
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                #target_planet = next(target_planets)
            else:
                #target_planet = next(target_planets)
                break

    except StopIteration:
        return

# defend - from densive_bot        
def defend(state):
    my_planets = [planet for planet in state.my_planets()]
    if not my_planets:
        return

    def strength(p):
        return p.num_ships \
               + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    avg = sum(strength(planet) for planet in my_planets) / len(my_planets)

    weak_planets = [planet for planet in my_planets if strength(planet) < avg]
    strong_planets = [planet for planet in my_planets if strength(planet) > avg]

    if (not weak_planets) or (not strong_planets):
        return

    weak_planets = iter(sorted(weak_planets, key=strength))
    strong_planets = iter(sorted(strong_planets, key=strength, reverse=True))

    try:
        weak_planet = next(weak_planets)
        strong_planet = next(strong_planets)
        while True:
            need = int(avg - strength(weak_planet))
            have = int(strength(strong_planet) - avg)

            if have >= need > 0:
                issue_order(state, strong_planet.ID, weak_planet.ID, need)
                weak_planet = next(weak_planets)
            elif have > 0:
                issue_order(state, strong_planet.ID, weak_planet.ID, have)
                strong_planet = next(strong_planets)
            else:
                strong_planet = next(strong_planets)

    except StopIteration:
        return
        
def defend2(state):
    my_planets = [planet for planet in state.my_planets()]
    if not my_planets:
        return

    for planet in my_planets:
        for fleet in state.enemy_fleets():
            if fleet.destination_planet == planet.ID:
                if planet.num_ships + state.distance(planet.ID, fleet.source_planet)*planet.growth_rate < fleet.num_ships:
                    closest_ally = None
                    distance = 99999
                    for close in my_planets:
                        if state.distance(close.ID, planet.ID) < distance:
                            distance = state.distance(close.ID, planet.ID)
                            closest_ally = close
                    issue_order(state, closest_ally.ID, planet.ID, closest_ally.num_ships / 2)

    return