

def if_neutral_planet_available(state):
    return any(state.not_my_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def have_smallest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           <= sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def enemy_attacks(state):
	for planet in state.my_planets():
		for fleet in state.enemy_fleets():
			if fleet.destination_planet == planet.ID:
				if planet.num_ships + state.distance(planet.ID, fleet.source_planet)*planet.growth_rate < fleet.num_ships:
					return True

	return False