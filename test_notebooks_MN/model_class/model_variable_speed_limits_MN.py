import random 


#################################################
###  Define Classes 
#################################################

class TrafficSimulation:
    # Class to handle the running of the model
    
    # Method run when initialising the class.
    def __init__(self, road_speed_limit_list, density, car_slow_down_prob):
        # set the model on the data given
        self.road_length = len(road_speed_limit_list)
        self.density = density
        self.car_slow_down_prob = car_slow_down_prob

        # Compute number of car in model
        self.number_of_cars = int(self.road_length * density )
        self.roads = Roads(road_speed_limit_list, self.number_of_cars, self.car_slow_down_prob)    # make the class
        self.roads.initialise_roads() 

        ## Model data for statistics 
        self.data_laps = 0 
        self.data_speeds_histogram = { }

    def update(self): 
        # method to update model for a time step
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
        
    def get_road_header(self):  # edit: made a function to extract the speed limits per site
        speed_limit_list = [ road.speed_limit for road in self.roads ] 
        return speed_limit_list
                  
    def get_heatmap(self):  # edit: made function to extract iterations as lists
        heatmap_list = [ road.empty_road_char if road.is_empty() else road.car.speed for road in self.roads.roads ]
        return heatmap_list


    ### Test cases to verify models behaviour 
    # Test One
    ## Acceleration 
    def test_simple_acceleration(self,slow_down_prob):
        ### set paras for model
        road_length = 5020 
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
            if not self.roads[ (position + distance_ahead) % self.length  ].is_empty():
                return distance_ahead 

    def get_distance_speed_limit(self, position):
        # get the next speed limit
        distance = 0 
        while distance <= self.length:
            distance += 1 
            if self.roads[position].speed_limit !=  self.roads[ (position + distance ) % self.length ].speed_limit: 
                return distance, self.roads[ (position + distance) % self.length ].speed_limit 
    
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
            


###### End of Class Roads

class Car: 
    def __init__(self, speed, car_slow_down_prob):
        self.slow_down_prob = car_slow_down_prob 
        self.speed = speed
        self.laps  = 0

    def accelerate(self, speed_limit, distance_ahead, distance_speed, new_speed_limit):
        if self.speed < speed_limit:
            if self.speed +1 < distance_ahead:
                if self.speed < new_speed_limit or self.speed +1 < distance_speed:
                    self.speed += 1
                    

    def deceleration(self, distance_ahead, distance_speed, new_speed_limit):
        # case 1: more important 
        if distance_ahead <= self.speed: 
            self.speed = distance_ahead - 1 if distance_ahead > 0 else 0 
            return
        # case 2: 
        if distance_speed <= self.speed and self.speed > new_speed_limit:
            self.speed = max( distance_speed - 1, new_speed_limit) 

    def randomise_speed(self):
        if random.random() < self.slow_down_prob: 
            self.speed = max(self.speed -1 , 0)

    
###### End of Class car



if __name__ == "__main__":
    road_speed_limit_list = ([2]*30 ) + ([5]*30) + ( [9]*10) + ([5]*30)
    density = 0.2
    car_slow_down_prob = 0.05
    sim1 = TrafficSimulation(road_speed_limit_list, density, car_slow_down_prob) 
#    print(sim1.number_of_cars)
#    sim1.test_simple_deceleration(0)
#    sim1.test_simple_acceleration(0)
#    sim1.test_variable_speed_limits(1, 9)
    sim1.print_speed_limits()
    for _ in range(60):
        sim1.print_step() 
        sim1.update() 
#
#    print( sim1.data_laps, sim1.data_laps / 120 ) 
#    print( sim1.data_speeds_histogram )


