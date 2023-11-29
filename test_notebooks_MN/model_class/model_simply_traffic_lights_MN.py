import random 


#################################################
###  Define Classes 
#################################################

class TrafficSimulation:
    # Class to handle the running of the model
    
    # Method run when initialising the class.
    def __init__(self, road_speed_limit_list, traffic_lights, density, car_slow_down_prob):
        # set the model on the data given
        self.road_length = len(road_speed_limit_list)
        self.density = density
        self.car_slow_down_prob = car_slow_down_prob

        # Compute number of car in model
        self.number_of_cars = int(self.road_length * density )
        self.roads = Roads(road_speed_limit_list, self.number_of_cars, self.car_slow_down_prob)    # make the class
        self.roads.initialise_traffic_lights(traffic_lights)
        self.roads.initialise_roads() 

        ## Model data for statistics 
        self.data_laps = 0 
        self.data_speeds_histogram = { }

    def update(self): 
        # method to update model for a time step
        self.roads.time_step_traffic_lights()
        new_position_and_speed = self.roads.get_new_positions_speed() 
        ## Get data from the model 
        new_position_and_speed =  self.update_statistics(new_position_and_speed)
        ## Clear all old and make now
        self.roads.reset()    # make the class
        self.roads.update(new_position_and_speed) 


    def update_statistics(self, position_speed):
        # Method to update data about the model regarding laps and speeds 
        self.data_speeds_histogram = { }                # Clear old data 
        new_position_and_speed = []
        for position, speed,car in position_speed: 
            # count laps 
            if position >= self.road_length: 
                self.data_laps += 1                     # Update lap tally 
                position = position % self.road_length  # periodic boundary conditions 
            # Count speeds 
            self.data_speeds_histogram[speed] = self.data_speeds_histogram.get(speed, 0) + 1
            new_position_and_speed.append( (position, speed, car))  # Append to list for return

        return new_position_and_speed

    def print_step(self):
        self.roads.print_roads()

    def print_speed_limits(self): 
        self.roads.print_road_header() 

    def print_traffic_lights(self):
        traffic_light_states = [ road.traffic_light.state if road.is_traffic_light() else road.empty_road_char for road in self.roads.roads ]
        print(" ".join("{:<1}".format(traffic_light_state) for traffic_light_state in traffic_light_states ))

    def get_heatmap(self):
        heatmap_list = [ road.empty_road_char if road.is_empty() else road.car.speed for road in self.roads.roads ]
        return heatmap_list
    
    def get_speed_limits(self):
        road_speed_lims = [ road.speed_limit for road in self.roads.roads ]
        return road_speed_lims
    
    def get_traffic_lights(self):
        traffic_light_states = [ road.traffic_light.state if road.is_traffic_light() else road.empty_road_char for road in self.roads.roads ]
        return traffic_light_states


    ### Test cases to verify models behaviour 
    # Test One
    ## Acceleration 
    def test_simple_acceleration(self,slow_down_prob):
        ### set paras for model
        road_length = 50 
        number_of_cars = 1 
        starting_speed = 0
        self.road_length = road_length 
        self.number_of_cars = number_of_cars 
        self.car_slow_down_prob = slow_down_prob 
        ###
        self.roads = Roads(road_length, number_of_cars, slow_down_prob) 
        self.roads.roads[0].add_car(starting_speed, slow_down_prob) 
    
    # Test two 
    ## deceleration 
    def test_simple_deceleration(self, starting_speed, stationary_position=4):
        self.road_length = 10 
        self.number_of_cars = 2 
        self.car_slow_down_prob = 0 
        ##
        self.roads = Roads(self.road_length, self.number_of_cars, self.car_slow_down_prob) 
        self.roads.roads[0].add_car(starting_speed, self.car_slow_down_prob) # Add the moving car 
        self.roads.roads[stationary_position].add_car(0, 1) # Add the stationary car 
        
    # test Three 
    ## Variable speed limits 
    def test_variable_speed_limits(self, speed_limit_B, speed_limit_C): 
        self.road_length = 60 
        self.number_of_cars = 1
        self.car_slow_down_prob = 0 
        self.roads = Roads(self.road_length, self.number_of_cars, self.car_slow_down_prob) 
        for i in range(self.road_length):
            if i > 10:
                self.roads.roads[i] = Road(speed_limit_B)
                
            if i > 30:
                self.roads.roads[i] = Road(speed_limit_C)
        self.roads.roads[0].add_car(5, self.car_slow_down_prob) # Add the moving car 


###### end Class TrafficSimulation 

class Roads:
    # A classes that can contain the different types of roads for the model. 
    def __init__(self, road_speed_limit_list, number_of_cars, car_slow_down_prob):
        ## initialise the road 
        self.length = len(road_speed_limit_list) 
        self.number_of_cars = number_of_cars
        self.car_slow_down_prob = car_slow_down_prob
        self.roads = [Road(speed_limit) for speed_limit in road_speed_limit_list] 

    def initialise_traffic_lights(self,traffic_lights):
        for position, green_time, red_time, starting_time, is_random in traffic_lights: 
            self.roads[position].add_traffic_light(green_time, red_time, starting_time, is_random) 

    
    def time_step_traffic_lights(self): 
        for road in self.roads: 
            if road.is_traffic_light():
                road.time_step_traffic_lights()

    def initialise_roads(self):
        # generate list of starting positions 
        random_car_positions = random.sample(range(self.length), self.number_of_cars)
        for position in random_car_positions: 
            self.roads[position].initialise_car(self.car_slow_down_prob) # initialise car, so random speed

    def get_new_positions_speed(self): 
        new_position_and_speed = [] 
        for position, road in enumerate(self.roads): 
            if not road.is_empty():
                distance_ahead = self.get_distance_ahead(position) 
                distance_speed, new_speed_limit = self.get_distance_speed_limit(position) 
                new_speed = road.update(distance_ahead, distance_speed, new_speed_limit)    # get new speed 
                new_position = (position + new_speed)      # compute new position 
                car = road.car                             # pass the car object 

                new_position_and_speed.append( (new_position, new_speed, car)) 

        return new_position_and_speed 

    def get_distance_ahead(self, position): 
        distance_ahead = 0
        while distance_ahead <= self.length: 
            distance_ahead += 1 
            if not self.roads[ (position + distance_ahead) % self.length  ].is_empty() or self.roads[(position +distance_ahead) %self.length ].check_traffic_light() :
                return distance_ahead 

    def get_distance_speed_limit(self, position):
        # get the next speed limit
        distance = 0 
        while distance <= self.length:
            new_speed_limit = self.roads[(position + distance) % self.length].speed_limit 
            if self.roads[position].speed_limit !=  new_speed_limit: 
                return distance, new_speed_limit
            distance += 1 
        
        return distance,  new_speed_limit
    
    def update(self, position_speed): 
        for position,speed,car in position_speed: 
            self.roads[position].move_car(car)
    
    def reset(self): 
        for road in self.roads: 
            road.car = None

    def print_road_header(self):
        road_speed_limits = [ road.speed_limit for road in self.roads ] 
        print(" ".join("{:<1}".format(speed_limit) for speed_limit in road_speed_limits ) )  

    def print_roads(self):
        road_speeds = [road.car.speed if road.car else road.empty_road_char for road in self.roads]
        print(" ".join("{:<1}".format(speed) for speed in road_speeds))
        
    
###### End of Class Roads

class Road: 
    empty_road_char = '-'

    def __init__(self, road_speed_limit):
        self.speed_limit = road_speed_limit
        self.car = None   # set space to add a car 
        self.traffic_light = None
    
    def initialise_car(self, car_slow_down_prob): 
        random_initial_speed = int(random.sample(range(0, self.speed_limit+1), 1)[0])
        self.car = Car( random_initial_speed, car_slow_down_prob) 

    def add_car(self, speed, car_slow_down_prob): 
        self.car = Car(speed,car_slow_down_prob)

    def move_car(self, car): 
        self.car = car 

    def update(self, distance_ahead, distance_speed, new_speed_limit): 
        if self.car is None: 
            return 
        self.car.accelerate(self.speed_limit, distance_ahead, distance_speed, new_speed_limit) 
        self.car.deceleration( distance_ahead, distance_speed, new_speed_limit) 
        self.car.randomise_speed()
        return self.car.speed 

    def is_empty(self):
        return self.car is None

    def is_traffic_light(self):
        return not self.traffic_light is None

    def check_traffic_light(self):
        if self.is_traffic_light():
            return self.traffic_light.state == 'r' 
        else: 
            return False
    
    def add_traffic_light(self, green_time, red_time, starting_time, is_random):
        self.traffic_light = Traffic_light(green_time, red_time, starting_time, is_random)


    def time_step_traffic_lights(self): 
        self.traffic_light.step_time()

###### End of Class Roads

class Car: 
    def __init__(self, speed, car_slow_down_prob):
        self.slow_down_prob = car_slow_down_prob 
        self.speed = speed
        self.laps  = 0

    def accelerate(self, speed_limit, distance_ahead, distance_speed, new_speed_limit):
        if self.speed < speed_limit:
            if self.speed +1 < distance_ahead:
                if self.speed+1 <= new_speed_limit or self.speed +1 < distance_speed:
                    self.speed += 1
        if self.speed > speed_limit: 
            self.speed = speed_limit
                    

    def deceleration(self, distance_ahead, distance_speed, new_speed_limit):
        #print(f'S:{self.speed} d: {distance_speed} ,s-d: {self.speed - distance_speed}, ns {new_speed_limit}')
        if distance_speed <= self.speed  and self.speed > new_speed_limit:
            self.speed = distance_speed if distance_speed > new_speed_limit else new_speed_limit 
#            self.speed = self.speed - ( distance_speed // 2)  if distance_speed >1 else new_speed_limit 
            #self.speed = self.speed- (self.speed -(distance_speed)) if distance_speed >0 else new_speed_limit   
        if distance_ahead <= self.speed: 
            self.speed = distance_ahead - 1 if distance_ahead > 0 else 0 
            return

    def randomise_speed(self):
        if random.random() < self.slow_down_prob: 
            self.speed = max(self.speed -1 , 0)

    
###### End of Class car

class Traffic_light:
    def __init__(self, green_time, red_time, starting_time, is_random): 
        self.random  = is_random   ## set bool logic (true/ false) 

        if self.random: # is random 
            self.green_time = red_time + random.randint(5,30)
        else:
            self.green_time = green_time 

        self.red_time   = red_time 
        self.time       = starting_time 
        self.state      = 'g' if self.time > self.red_time else 'r' 

    def step_time(self): 
        self.time -= 1 
        self.state = 'g' if self.time > self.red_time else 'r' 

        # random case 
        if self.random: 
            self.green_time = self.red_time + random.randint(5,30) if self.time <= 0 else self.green_time 

        self.time = self.green_time if self.time <= 0 else self.time 

###### End of Class Traffic Light

if __name__ == "__main__":
    road_speed_limit_list = ([8]*10 ) + ([2]*10) #+ ( [3]*2) + ([9]*8)
    traffic_light_list = [(10,6,3,6), ( 15, 8,3,8)]
    density = 0.1
    car_slow_down_prob = 0.0
    sim1 = TrafficSimulation(road_speed_limit_list, traffic_light_list, density, car_slow_down_prob) 
#    print(sim1.number_of_cars)
#    sim1.test_simple_deceleration(0)
#    sim1.test_simple_acceleration(0)
#    sim1.test_variable_speed_limits(1, 9)
    sim1.print_speed_limits()
    for _ in range(20):
        sim1.print_traffic_lights()
        sim1.print_step() 
        sim1.update() 
#
#    print( sim1.data_laps, sim1.data_laps / 120 ) 
#    print( sim1.data_speeds_histogram )


