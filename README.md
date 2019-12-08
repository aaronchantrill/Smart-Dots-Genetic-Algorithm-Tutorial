# Smart-Dots-Genetic-Algorithm-Tutorial
This is a re-implementation of the code accompanying Code Bullet's tutorial, "How AIs learn part 2" but in Python instead of Processing. The YouTube video is here: https://www.youtube.com/watch?v=BOZfhUcNiqk

I've been wanting to do some visual machine learning examples, so this is my first attempt. I ended up having to change the fitness function because sometimes if a dot ended up really close to the goal without hitting the goal, it would beat a dot that does hit the goal. Which is odd, since anything within 5 units of the goal should register as a hit. So I probably screwed that up. Oh well.

It at least introduced me to tkinter and allowed me to create a simple "game" (next time I will use pygame to simplify the collision detection code). Anyway, I tried to basically retain the same structure and function names. Unfortunately, there is no license attached to that project, so Code Bullet, if you come across this, please don't sue me.
