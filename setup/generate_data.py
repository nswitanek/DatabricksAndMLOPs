import configparser
import csv
import math
import random
import os

years = [str(i) for i in range(1920, 2020)]
bedrooms = [1, 2, 3, 4]
bathrooms = [1, 1.5, 2, 2.5, 3]
N = 100000

if __name__ == "__main__":
    # Columns
    # Year Built
    # Bedrooms
    # Bathrooms
    # Square Footage
    # AvgSchoolRanking
    # LastSalePrice
    data = []
    for i in range(N):
        year = random.choice(years)
        bathroom = random.choice(bathrooms)
        bedroom = random.choice([b for b in bedrooms if b > bathroom])
        sqft = int(
            bedroom * math.pow(10, 2) # Assuming bedrooms are 10 x 10
            + bedroom * random.randint(100, 750) # Assuming a bedroom has a related impact on sqft
            + 500 # Minimum bar will be 500 sq ft
        )
        ranking = random.choices(
            population=range(1,11),
            weights= [0.05, 0.1, 0.1, 0.1, 0.15, 0.2, 0.15, 0.1, 0.05, 0.05],
            k = 1
        )[0]
        price = (
            bathroom * 1050 +
            bedroom * 2125 + 
            sqft * 123 +
            ranking * 400 +
            random.normalvariate(4000, 600) # error term
        )
        if year <= '1939':
            price = price * 1.05
        elif year <= '1969':
            price = price * 0.90
        elif year <= '2000':
            price = price
        elif year <= '2020':
            price = price * 1.01
        
        price = round(price, 2)
        
        output = [year, bedroom, bathroom, sqft, ranking, price]
        data.append(output)

    
    training_start = 0
    training_end = int(N*0.9)
    
    with open('./data/training.csv', 'w', newline='') as fp:
        csv_file = csv.writer(fp)
        csv_file.writerows(data[training_start:training_end])
    
    with open('./data/validation.csv', 'w', newline='') as fp:
        validation_file = csv.writer(fp)
        validation_file.writerows( data[training_end:])
