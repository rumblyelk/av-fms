# Notes on the Design and Approach to this project

This is the first project I've ever done in Flask, so the first thing I did was research a different approaches to building a Flask project. Flask turned out to be a very dynamic and loosely structured framework, unlike the framework which I'm more familiar with: Rails. Rails could be described almost as an prebuilt structure in which you write your code, but Flask is infinitely more dynamic. It could be a single file and not require any overhead.

Because I'd never built a Flask app before and I wasn't familiar with the best practices in doing so, I decided to follow a basic Tutorial on Flask's website on setting up a simple website with some simple views. I followed th tutorial only in so far as I learned the reccommended project structure and basic features like "blueprints," but then I broke from the tutorial when I wanted to add the SQLAlchemy ORM and build an API separate from the frontend.

Based off of what I learned form Flask's own direction, I structured the project loosely after the following template:

        /home/user/.../project
        ├── project-name/
        │   ├── __init__.py
        │   ├── [files similar to a controller in an MVC]
        │   ├── templates/
        │   └── static/
        │       └── style.css
        └── [assorted files such as .gitignore, requeriments.txt, etc]

## The Frontend

Ideally, I would have created a decoupled API and frontend. I chose not to do this for 2 reasons.
1. Coming from a a background in Rails, this is not usually done
2. Developing a tighhtly coupled frontend allows for more rapid development and quicker change implementation, so it's arguably better for a prototype frontend anyway
Therefore, I decided to go ahead and use Flask's builtin system of "templates" and develop some simple frontend pages. What this resulted in was unfortunate, however, is code that's not very DRY. There is a lot of reproduced functionality between the frontend templates and routes on the one hand and the API section that I created afterward. If I were to continue to develop this project, I would reproduce a frontend in another framework such as React.js and then merely have that use the same API that's exposed anyway. I don't regret developing it the way I did, however, because it produced something useable and working. And, as Donald Knuth once said, "Premature optimization is the root of all evil (or at least most of it) in programming."

## The API

