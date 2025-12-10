from taipy import Gui

# 1) State variables to bind to the UI
sales = 100
base_sales = 100

# 2) Augmented Markdown page
# Taipy GUI uses augmented Markdown for visual elements, with the basic syntax <|{variable}|visual_element_type|...|>.
# Buttons execute functions when clicked and can have attributes like label and on_action.
# The on_action attribute specifies the callback (or callback name) to be called when pressed.
# The callback receives the State object as its first argument, which is used to read/modify values per user session.
# In Taipy, each user's session is managed independently, so the State object ensures that changes made by one user do not affect others.
page = """
# Step 2 - State & Button

현재 매출: <|{sales}|text|>

<|+10|button|on_action=add_sales|>
<|Reset|button|on_action=reset_sales|>
"""

# 3) Button callbacks
def add_sales(state):
    state.sales += 10

def reset_sales(state):
    state.sales = state.base_sales


Gui(page).run(port=5050, debug=True, use_reloader=True, title="step 102")


# Understanding how state variables work in a Taipy application : Server-side state management and user sessions.
# 1) Initialization: 
#    When the application first starts, the Python code sales = 100 is executed.
#    This value is stored on the server as the default for all users.

# 2) User connection:
#    When a new user accesses the application through a web browser, Taipy creates a unique session for that user
#    on the server. It then stores an independent copy of the state information for that session, including the sales variable.
#    The State object described in the code comments is responsible for managing this session state.

# 3) Interaction (button click):
#    When the user clicks the +10 button in the browser, this event is sent to the server.

# 4) Server handling:
#    The server calls the add_sales(state) function specified by on_action=add_sales.
#    At this time, the state parameter receives the current user's session state. When state.sales += 10 is executed,
#    only the current user's sales value increases by 10 on the server, not other users'.

# 5) UI update:
#    When the sales value changes on the server, Taipy automatically detects the change and sends the new value
#    to that user’s web browser.
#    Then the "Current sales: <|{sales}|text|>" section is updated, and the new value is displayed on screen.
