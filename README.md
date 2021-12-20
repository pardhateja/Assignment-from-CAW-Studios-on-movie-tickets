# Assignment-from-CAW-Studios-on-movie-tickets

This project consists of API's which are used to get the functionalities to
1) Signup for a new user.
2) login for the existing user.
3) Create screen details for the respective cinema and show them in it.
4) Get the info regarding ticket availability in all shows on a particular screen.
5) Get the info regarding the availability of required tickets at particular showtime along with the row.
6) Get the info regarding all the movies playing in the city.
7) Get the info regarding particular movies playing at all the shows and screens.
8) Booking a ticket/tickets for a particular screen, show, and the row we needed.

# Signup for a new user.

Here we will be taking the details of the user name, email id of the user, and the password for the account.

![image](https://user-images.githubusercontent.com/37372052/146724646-ed241185-b2ef-448f-a8f1-d58068c1f867.png)

Like in the above picture if we provide the details the user will get created.
Here in the backend the email will go through basic email validations and check whether there is already an account with the same email id.
The password is hashed using the sha_256 method and stored in the DB.
We have generated a unique user id that will be used for the generation of token

# Login for the existing user.

Once we have signed up we need to login into the account to fetch the token which can be used in authentication required calls.
For signup, we will be taking the email id and the password for that mail id.

![image](https://user-images.githubusercontent.com/37372052/146726004-b1e6b8a6-ca41-4cff-8aa7-6a94367f50e2.png)

Like in the screenshot if we provide the details the token will get generated.
In the backend, we will be validating the email whether there is already an account or not.
We will be validating the password given with the has function stored in the DB.
Here we will be using the JWT encode method. This will generate a token with a validity of 30 mins. After its expiry, the user needs to log in again to get the token.

# Create screen details for the respective cinema and show them in it.

We need to create the data initially into the DB to test the code which we have written.

The JSON in the request body will look like this:

 {
    "name": "sfs",
    "shows": {
        "show1": {
            "cinema": "pushpa2",
            "seatInfo": {
                "A": {
                    "numberOfSeats": 10,
                    "aisleSeats": [
                        0,
                        5,
                        6,
                        9
                    ]
                },
                "B": {
                    "numberOfSeats": 15,
                    "aisleSeats": [
                        0,
                        7,
                        8,
                        14
                    ]
                },
                "C": {
                    "numberOfSeats": 20,
                    "aisleSeats": [
                        0,
                        9,
                        10,
                        19
                    ]
                }
            }
        },
        "show2": {
            "cinema": "julay",
            "seatInfo": {
                "A": {
                    "numberOfSeats": 10,
                    "aisleSeats": [
                        0,
                        5,
                        6,
                        9
                    ]
                },
                "B": {
                    "numberOfSeats": 15,
                    "aisleSeats": [
                        0,
                        7,
                        8,
                        14
                    ]
                },
                "C": {
                    "numberOfSeats": 20,
                    "aisleSeats": [
                        0,
                        9,
                        10,
                        19
                    ]
                }
            }
        }
    }
}

![image](https://user-images.githubusercontent.com/37372052/146728671-997832db-4499-4b18-963d-b65779a17b5a.png)

Here we will be taking all the details like the show, movie name which is being played, aisle seats, row info & number of seats.
In the backend, we will be storing the details of the show in the screen and row accordingly.
If the cinema is new we will be storing a new row on the cinema table.
In the Cinema_row table, we will be having an association between the cinema table and the row table.

# Get the info regarding ticket availability in all shows on a particular screen.

Here in this, we will be providing the details as if in the screenshot. The unreserved tickets in a particular hall in all shows will be returned as an output.

![image](https://user-images.githubusercontent.com/37372052/146729779-87d8cc1e-4314-4262-ad69-bcb9fd628b01.png)

# Get the info regarding the availability of required tickets in particular showtime along with the row.

Here we will be providing the screen name, showtime, the number of seats, and the choice which are needed for the user.

![image](https://user-images.githubusercontent.com/37372052/146730649-6da3624f-4e96-4b3f-b686-e861a894cef8.png)

As in the above screenshot, we will be providing the user with the best seat available for the selections user has made.

# Get the info regarding all the movies playing in the city.

Here we will be returning all the movies which are being played. Also, the screens and timings would be written.

![image](https://user-images.githubusercontent.com/37372052/146731417-141ae99c-2a64-400d-9cb6-1dad7f021345.png)

# Get the info regarding particular movies playing at all the shows and screens.

By providing the name of the movie, we will be returning all the screens and timings in which the movie is played.

![image](https://user-images.githubusercontent.com/37372052/146731749-a07cf81f-513c-4ee5-852a-b287b75efc8a.png)

# Booking a ticket/tickets for a particular screen, show, and the row we needed.

Here we will be providing the screen name, show timings, and the number of tickets in the row.

![image](https://user-images.githubusercontent.com/37372052/146731950-2596c3a2-215b-4644-a736-bd71245daad7.png)

As in the screenshot if the ticket was available we will be returning the booked status.
