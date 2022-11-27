# Welcome to the Autonomous Vehicle Fleet Management System (AV-FMS)

## Versioning

    Ubuntu 20.04.5 LTS
    Python 3.9.15
    Flask 2.2.2
    Werkzeug 2.2.2

## Setting Up and Starting the App
From within the project directory, run the following line:

    $ pip install -r requirements.txt

Once dependancies are installed (which may require adding `--no-deps`), run the following to start the server:
    
    $ flask --app av-fms --debug run
    
The DB will be initialized automatically.

## Logging in and Staff Privileges

Once the server is running, navigate to `localhost:5000/register` to create an account. After the account has been created, login with the credentials that you just created.

Once one login has been performed, the server will automatically generate a staff user for testing purposes. The staff user is able to add or delete vehicles. The login info for the staff user is:
    
    username: staffUser
    password: staffpass
    

## API Login, Authentication, and Docs

Before sending any requests to the API, a toekn must be obtained. This is done with the `api/login` endpoint. All requests must contain the `"Content-Type": "application/json"` header. After obtaining an API token, it should be put in the header as `"x-access-token": token`.

#### > `/api/login`
Included in the body should be one's username and password as follows:
```json
{
    "username": string,
    "password": string
}
```
if authenticated, the server will return an API token for future authentication.

#### > `/api/vehicles`
This will return a list of all vehicle objects, each one serialized in JSON as:
```json
{
    "id": int,
    "manufacturer": string,
    "license_plate_number": string,
    "available": bool,
}
```
An optional filter parameter is allowed in the request body as well, in the form of:
```json
{
    "filter": {
        "param": string,
        "value": appropriate value for the param
    }
}
```
For example, if a user wished to see only Mercedes vehicles, the following filter could be used:
```json
{
    "filter": {
        "param": "manufacturer",
        "value": "Mercedes"
    }
}
```
If no filter is provided, an unfiltered list of vehicles will be returned.

#### > `/api/vehicles/id/take`
This will register a vehicle as having been taken by a user and will not be available for use by other users until it is returned.

#### > `/api/vehicles/id/return`
This will register a vehicle as having been returned by a user and will then be available once more to other users.

#### > `/api/vehicles/create`
This is only available to a user with staff privileges. This will create a new vehicle record in the DB using the information provided in the request body as follows:
```json
{
    "manufacturer": string,
    "license_plate_number": string
}
```

#### > `/api/vehicles/id/delete`
This is only available to a user with staff privileges. This will delete a vehicle from the DB.

#### > `/api/vehicles/task_history`
This will return the task history of a vehicle in a list of JSON objects of the form:
```json
{
    "task_id": int,
    "taken_by": string,
    "start_time": string,
    "end_time": string,
}
```
If a vehicle is still in the middle of a task and has not been returned yet, the `end_time` will show as a null value.
A vehicle is looked up by checking for a particular license plate value, carried in the request body as:
```json
{
    "license_plate_number": string
}
```
I should note that this is not the way I would have preferred to do this. I would have preferred to have an endpoint of the structure:
`/vehicles/<int:id>/task_history` However, the task requirements were: "The API should get a vehicle's license and return its history of availability (tasks)
that includes the date and time and the user who caught it." Putting the license plate number in the URL would have too
clunky for my liking, so I decided to put it in the request body instead.
