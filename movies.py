# Your name: Sarah Nyaanga
# Your student id: 3324 2694
# Your email: snyaanga@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.  
# e.g.: I used AI to help me debug my code for update_cache and filer_movies_by_year



import requests
import json
import unittest
import os

#TO DO: 
# assign this variable to your API key
# if you are doing the extra credit, assign API_KEY to the return value of your get_api_key function


def get_json_content(filename):
    '''
    ARGUMENTS: 
        filename: name of file to be opened

    RETURNS: 
        json dictionary OR an empty dict if the file could not be opened 
    '''
    try:
        with open(filename, 'r', encoding = "utf-8") as file:
            data = json.load(file)
            return data
    except:    
        return {}

def save_cache(dict, filename):
    '''
    ARGUMENTS: 
        filename: the name of the file to write a cache to
        dict: cache dictionary

    RETURNS: 
        None
    '''
    with open(filename, 'w', encoding = "utf-8") as file:
        file.write(json.dumps(dict))
            


def search_movie(movie):
    '''
    ARGUMENTS: 
        title: title of the movie you're searching for 

    RETURNS: 
        tuple with the response text and url OR None if the 
        request was unsuccesful
    '''
    #API_KEY = "19865bf7"
    #formatted_movie = movie.replace(" ", "+")
    movie_dict = {"apikey":API_KEY, "t": movie }
    movie_url = "http://www.omdbapi.com"
    resp = requests.get(movie_url, movie_dict) # get the url

    #check the if the status is valid 200 means it is okay 
    if resp.status_code == 200:
        #get the data content of the movie
        data = resp.json()
        if data.get("Response") == "False":
            return None 
        return (data,resp.url)

    #if the url is invalid
    return None
    
def update_cache(movies, cache_file):
    '''
    ARGUMENTS: 
        movies: a list of movies to get data for 
        cache_file: the file that has cached data 

    RETURNS: 
        A string saying the percentage of movies we succesfully got data for 
    '''
    movies_added = 0

    cache = get_json_content(cache_file)
    for movie in movies:
        if search_movie(movie) != None:
            movie_url = "http://www.omdbapi.com/?t=" + movie
            if movie_url not in cache:
                cache[movie_url] = search_movie(movie)[0]
                movies_added += 1
    percentage = "Cached data for " + str((movies_added/len(movies))*100) + "% of movies"
    save_cache(cache, cache_file)

    print(percentage)
    return percentage
  

def get_highest_box_office_movie_by_country(country_name, cache_file): 
    '''
    ARGUMENTS: 
        country_name: the name of the country to find the highest grossing film for 
        cache_file: the file that has cached data 

    RETURNS:
        EITHER a tuple with the title and box office amount of the highest grossing film in the specified country
        OR "No films found for [country_name]"
    '''
    movie_title = None
    highest_price  = 0

    cache = get_json_content(cache_file) #gives me a dictionary 
    for movie_data in cache: #movie data is key for cache dict
        if country_name in cache[movie_data]["Country"]:
            if "BoxOffice" not in cache[movie_data]:
                continue
            box_office_str = cache[movie_data]["BoxOffice"]
            box_office_value = int(box_office_str.replace("$", "").replace(",", "")) if box_office_str else 0
            
            if box_office_value > highest_price: 
                highest_price = box_office_value
                movie_title = cache[movie_data]["Title"]

    
    if movie_title is None:
        return f"No films found for {country_name}"
      
    return (movie_title,highest_price)  


def filter_movies_by_year(cutoff_year, cache_file):
    '''
    ARGUMENTS: 
        cutoff_year: the year to filter movies
        cache_file: the file that has cached data 

    RETURNS:
        a list of tuples with the movies and their years of release
    '''
    #int(data_dict[Released[-4:]]) >=  cutoff_year 
    #((movie,year),(movie2, year2)

    filtered_movies = []

    cache = get_json_content(cache_file) #gives me a dictionary 
    for movie_data in cache.values():
        if "Year" in movie_data and int(movie_data["Year"]) >= cutoff_year:
            filtered_movies.append((movie_data["Title"], int(movie_data["Year"])))
            #how do i keep adding a new one of these tuple combinations every time i find a match do i use append?

    return filtered_movies
        

#EXTRA CREDIT
def get_api_key(file):
    '''
    ARGUMENTS:  
        file: file that contains your API key
    
    RETURNS:
        your API key
    '''

    with open(file, 'r', encoding = "utf-8") as f:
        line = f.readline().strip()
        api_key = line.split("=")[1].strip().strip('"')
        return api_key


API_KEY = get_api_key("api_key.txt")    
    
#EXTRA CREDIT
def get_movie_rating(title, cache_file):
    '''
    ARGUMENTS: 
        title: the title of the movie we're searching for 
        cache_file: the file that has cached data 

    RETURNS:
        the rating OR 'No rating found'
    '''

    cache = get_json_content(cache_file) #gives me a dictionary 
    for movie_data in cache: #movie data is key for cache dict
        if title in cache[movie_data]["Title"]:
            rating_list = cache[movie_data]["Ratings"]
            for item in rating_list:
                source = item["Source"]
                value = item["Value"]

                if source == "Rotten Tomatoes":
                    return value

            # if "Ratings" not in movie_data.items():
            #     continue

            # ratings = cache[movie_data]["Ratings"]
            # if "Rotten Tomatoes" in ratings:


            #     return ratings[1][]
    
      
    return "No rating found"


class TestHomework6(unittest.TestCase):
    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.filename = dir_path + '/' + "cache.json"

        with open('movies.txt', 'r') as f: 
            movies = f.readlines()
            
        for i in range(len(movies)): 
            movies[i] = movies[i].strip()
        self.movies = movies

        # NOTE: if you already have a cache file, setUp will open it
        # otherwise, it will cache all movies to use that in the test cases 
        if not os.path.isfile(self.filename):
            self.cache = update_cache(self.movies, 'cache.json')
        else:
            self.cache = get_json_content(self.filename)

        self.url = "http://www.omdbapi.com/"


    def test_load_and_save_cache(self):
        test_dict = {'test': [1, 2, 3]}
        save_cache(test_dict, 'test_cache_get_json_content.json')

        test_dict_cache = get_json_content('test_cache_get_json_content.json')
        self.assertEqual(test_dict_cache, test_dict)
        os.remove('test_cache_get_json_content.json')

        test_dict_2 = {'test_2': {'test_3': ['a', 'b', 'c']}}
        save_cache(test_dict_2, 'test_cache_get_json_content_2.json')
        
        test_dict_2_cache = get_json_content('test_cache_get_json_content_2.json')
        self.assertEqual(test_dict_2_cache, test_dict_2)
        os.remove('test_cache_get_json_content_2.json')


    def test_search_movie(self):
        # testing valid movies
        for movie in ['Mean Girls', 'Pulp Fiction', 'Forrest Gump']:
            movie_data = search_movie(movie) 
            movie = movie.replace(" ", "+")
            #print(movie_data[0])
            self.assertEqual(type(movie_data[0]), dict)
            self.assertTrue(movie in movie_data[1])

        # testing invalid movie 
        invalid_movie_data = search_movie('fake movie 123')
        self.assertEqual(invalid_movie_data, None)


    def test_update_cache(self):
        test_movies = ['Mean Girls', 'Pulp Fiction', 'Forrest Gump']
        test_resp = update_cache(test_movies, 'test_cache_movies.json')
        self.assertTrue(test_resp == "Cached data for 100% of movies" or test_resp == "Cached data for 100.0% of movies")
        test_cache = get_json_content('test_cache_movies.json')
        self.assertIsInstance(test_cache, dict)
        self.assertEqual(len(list(test_cache.keys())), 3)

        for _, data in test_cache.items():
            if data['Ratings']:
                self.assertEqual(type(data['Ratings']), list)
                self.assertEqual(type(data['Ratings'][0]), dict)

        # checking it won't cache duplicates
        test_resp_2 = update_cache(test_movies, 'test_cache_movies.json')
        self.assertTrue(test_resp_2 == "Cached data for 0% of movies" or test_resp_2 == "Cached data for 0.0% of movies")        
        self.assertEqual(len(list(test_cache.keys())), 3)
        os.remove('test_cache_movies.json')


    def test_get_highest_box_office_movie_by_country(self):
        test_1 = get_highest_box_office_movie_by_country("India", 'cache.json')
        self.assertEqual(test_1, ('The Help', 169708112))
        test_2 = get_highest_box_office_movie_by_country("United States", 'cache.json')
        self.assertEqual(test_2, ('Avatar', 785221649))
        test_3 = get_highest_box_office_movie_by_country("Mexico", 'cache.json')
        self.assertEqual(test_3, ('Titanic', 674292608))
        test_4 = get_highest_box_office_movie_by_country("Japan", 'cache.json')
        self.assertEqual(test_4, ('Brave',237283207))
        test_5 = get_highest_box_office_movie_by_country("Narnia", 'cache.json')
        self.assertEqual(test_5, "No films found for Narnia")


    def test_filter_movies_by_year(self):
        test_1 = filter_movies_by_year(1985, 'cache.json')
        test_1_list = [('Titanic', 1997), ('Into the Unknown: Making Frozen 2', 2020), ('Avatar', 2009), ('Toy Story', 1995), ('Little Women', 2019), ('Everything Everywhere All at Once', 2022), ('Top Gun', 1986), ('Barbie', 2023), ('La La Land', 2016), ('Whiplash', 2014), ('Brave', 2012), ('The Wolf of Wall Street', 2013), ('12 Years a Slave', 2013), ('Life of Pi', 2012), ('The Help', 2011), ('Killers of the Flower Moon', 2023), ('Oppenheimer', 2023), ('Jurassic World', 2015), ('The Avengers', 2012), ('Braveheart', 1995), ('The Princess Bride', 1987), ('Clueless', 1995), ('10 Things I Hate About You', 1999), ('Harry Potter and the Goblet of Fire', 2005), ('Shrek', 2001), ('Parasite', 2019), ('Ladybird', 2006)]
        self.assertEqual(len(test_1), 27)
        self.assertEqual(test_1, test_1_list)

        test_2 = filter_movies_by_year(1997, 'cache.json') 
        test_2_list = [('Titanic', 1997), ('Into the Unknown: Making Frozen 2', 2020), ('Avatar', 2009), ('Little Women', 2019), ('Everything Everywhere All at Once', 2022), ('Barbie', 2023), ('La La Land', 2016), ('Whiplash', 2014), ('Brave', 2012), ('The Wolf of Wall Street', 2013), ('12 Years a Slave', 2013), ('Life of Pi', 2012), ('The Help', 2011), ('Killers of the Flower Moon', 2023), ('Oppenheimer', 2023), ('Jurassic World', 2015), ('The Avengers', 2012), ('10 Things I Hate About You', 1999), ('Harry Potter and the Goblet of Fire', 2005), ('Shrek', 2001), ('Parasite', 2019), ('Ladybird', 2006)]
        self.assertEqual(len(test_2), 22) 
        self.assertEqual(test_2, test_2_list) 

        test_3 = filter_movies_by_year(2009, 'cache.json')
        test_3_list = [('Into the Unknown: Making Frozen 2', 2020), ('Avatar', 2009), ('Little Women', 2019), ('Everything Everywhere All at Once', 2022), ('Barbie', 2023), ('La La Land', 2016), ('Whiplash', 2014), ('Brave', 2012), ('The Wolf of Wall Street', 2013), ('12 Years a Slave', 2013), ('Life of Pi', 2012), ('The Help', 2011), ('Killers of the Flower Moon', 2023), ('Oppenheimer', 2023), ('Jurassic World', 2015), ('The Avengers', 2012), ('Parasite', 2019)]
        self.assertEqual(len(test_3), 17)
        self.assertEqual(test_3, test_3_list)

        test_4 = filter_movies_by_year(2021, 'cache.json')
        test_4_list = [('Everything Everywhere All at Once', 2022), ('Barbie', 2023), ('Killers of the Flower Moon', 2023), ('Oppenheimer', 2023)]
        self.assertEqual(len(test_4), 4)
        self.assertEqual(test_4, test_4_list)


    # UNCOMMENT TO TEST EXTRA CREDIT ### 
    
    def test_get_api_key(self):                     
        hidden_key = get_api_key('api_key.txt')
        self.assertEqual(API_KEY, hidden_key)

    def test_get_movie_rating(self):
        test_titanic = get_movie_rating('Titanic', self.filename)
        self.assertEqual(test_titanic, '88%')
        test_avatar = get_movie_rating('Avatar', self.filename)
        self.assertEqual(test_avatar, '81%')
        test_topgun = get_movie_rating('Top Gun', self.filename)
        self.assertEqual(test_topgun, '58%')
        test_frozen = get_movie_rating('Frozen 2', self.cache)
        self.assertEqual(test_frozen, 'No rating found')

    
def main():
    '''
    Note that your cache file will be called 
    cache.json and will be created in your current directory

    Make sure you are in the directory you want to be work in 
    prior to running
    '''
    #######################################
    # DO NOT CHANGE THIS 
    # this code loads in the list of movies and 
    # removes whitespace for you!
    with open('movies.txt', 'r') as f: 
        movies = f.readlines()
        
    for i in range(len(movies)): 
        movies[i] = movies[i].strip()
    #resp = update_cache(movies, 'cache.json')
        
    # DO NOT CHANGE THIS 
    #######################################



if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)
