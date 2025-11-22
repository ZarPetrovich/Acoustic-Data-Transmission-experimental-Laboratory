This is a Student Project.
Data Transmission via Signals in audible frequency range!
Learn about "how to Transmit Data" with this application.



Notices

Datclass Object are holding the actual data. They are menant as Container with Data and Metadata too.

Data Flow

create Pulse

Create Data--> Store in Container --> pass over the whole Object to a combobox for Baseband Creation

The Combobox can hold items with name and actual data. So the Name is from the object, and the object itself is the data. Python does the job here. instead of copying the whole object, Python creates pointers automatically.
To get the data from a combobox, you can access that without any Getter Workaroung. Clean and Simple