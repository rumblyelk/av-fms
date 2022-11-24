# Notes on the Design and Approach to this project

This is the first project I've ever done in Flask, so the first thing I did was research different approaches and conventions when building a Flask project. Flask turned out to be a very dynamic and loosely structured framework, unlike the framework which I'm more familiar with: Rails. Rails could be described almost as a prebuilt structure in which you write your code, but Flask is infinitely more flexible. It could be a single file and not require any overhead.

Because I'd never built a Flask app before and I wasn't familiar with the best practices in doing so, I decided to follow a basic tutorial on Flask's website on setting up a simple website with some simple views. I followed the tutorial only in so far as I learned the reccommended project structure and basic features like "blueprints," but then I broke from the tutorial when I wanted to add the SQLAlchemy ORM and build an API separate from the frontend.

Based off of what I learned form Flask's own directions, I structured the project loosely after the following template:

        /home/user/.../project
        ├── project-name/
        │   ├── __init__.py
        │   ├── [files similar to a controller in an MVC]
        │   ├── templates/
        │   └── static/
        │       └── style.css
        └── [assorted files such as .gitignore, requirements.txt, etc]

## The Frontend

Ideally, I would have created a decoupled API and frontend. I chose not to do this for 2 reasons.

1. Coming from a a background in Rails, this is not usually done
2. Developing a tightly coupled frontend allows for more rapid development and quicker change implementation, so it's arguably better for a prototype frontend anyway

Therefore, I decided to go ahead and use Flask's builtin system of "templates" and develop some simple frontend pages. What this resulted in was unfortunate, however, and that is code that's not very DRY. There is a lot of reproduced functionality between the frontend templates and routes on the one hand and the API section that I created on the other. If I were to continue to develop this project, I would reproduce a frontend in another framework such as React.js and then merely have that use the same API that's exposed anyway. I don't regret developing it the way I did, however, because it produced something useable and working. And, as Donald Knuth once said, "Premature optimization is the root of all evil (or at least most of it) in programming."

## The API

I built the API in a very simple RESTful way, trying to stick to making endpoints in the form of `noun/id/verb` where possible. Where I felt it wasn't possible for whatever reason, I left a note either in the code or in the README.

For authentication, I used a basic token system. A user logs in and receives an API token which is an encoded form of their user ID and the server's secret. The token is then decoded and verified upon each subsequent request to the server.

On a side note, the "server secret" is currently a hardcoded string "hello". Obviously in prod I would never do this, instead using secure environment variables and a longer more secure key, but in this context I felt transparancy was preferable.

I tried to respond with appropriate error codes when an error would arise, and tried to provide some useful information in the response that may help the user.

## The Database

I decided to use SQLite3 for the database because it is ligthweight, requires almost no boilerplate, and is merely saved as a file in the working directory. A lot of my experience in the past has been with PostgresQL, but I felt that that was a bit overkill here.

When I started working on the project, I did not realize that Flask does not come with an ORM built in. Again, Rails is the full package. Either way, this wasn't a problem since SQLAlchemy was easy enough to install and I got right to work replacing the hardcoded SQL queries that I'd written with some proper SQLAlchemy.

## Conclusion

I enjoyed learning Flask and building this project very much. There are some things I mentioned above that I would do differently now that I'm more familiar with Flask, but overall I'm happy with my work.
