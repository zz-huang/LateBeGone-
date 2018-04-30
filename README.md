# LateBeGone!
#### Authors: Zoe Huang, Nathan Weinberg, Charlene Yu

LateBeGone! is a web app designed to help simplify transit in the Greater Boston Area. Once logged in, users can enter their location and destination to find out how much it would cost for them to Uber/Lyft there. Alternatively, users can select an MBTA stop near them adn be given official predictions of when their bus or train will arrive. To ensure they don't miss the T, LateBeGone! will send a text notification to their phone when their bus or train is 5 minutes away from their selected stop.

Should the T be late or early, Twitter is also integrated within the app so users can complain to the MBTA directly.

## Technologies Used
LateBeGone! uses HTML, CSS, AJAX, and Javascipt on the Front-End and runs on the Back-End with the Python Flask framework and MongoDB as the database system. Third-party authentication with Twitter is done with OAuth. Text messages are handled with Twilio (an account is requried).

#### APIs

LateBeGone! uses the MBTA, Twitter, Google Maps, Uber, Lyft, and Twilio APIs.

Independent API keys will be required, stored in a Python file titled `apikeys.py`

### Libraries

Several libraries are used; many are built-in but you may need to download the following:

- Flask
- Flask-OAuth
- Pymongo
- Twilio

## Database Usage
### (Ensure you have MongoDB installed on your machine)

Open a command prompt and run `mongod`. This must be running before you launch the app.

To access the database manually open a second command prompt and run `mongo`.

Some useful links:

https://docs.mongodb.com/getting-started/shell/introduction/

https://docs.mongodb.com/getting-started/python/introduction/
