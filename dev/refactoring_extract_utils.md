
Idea:  
Extract methods like self.send_safe and all the other utils into a separate class   
they don't need to be in the base class, and the only reason they were
is that I wanted a consistent way to configure them

So now instead we keep them in a separate class, and pass that class using the Deps collection class
And we bind Deps to the Handler with BotManager