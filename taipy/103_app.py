from taipy import Gui

# Separate execution settings for development/production.
sales = 100
base_sales = 100

page = """
# Step 3 - State & Button

현재 매출: <|{sales}|text|>

<|+10|button|on_action=add_sales|>
<|Reset|button|on_action=reset_sales|>
"""

# 3) Button callbacks
def add_sales(state):
    state.sales += 10

def reset_sales(state):
    state.sales = state.base_sales

if __name__ == "__main__":
    gui = Gui(page, env_filename="103.env")
    gui.run(title="step 103")


# Extremely important structural point : Why run it inside the __main__ block?
# Taipy provides various service execution structures such as GUI/REST/Orchestrator,
# and you can also bundle and run multiple services with tp.run(...).
# The documentation also recommends placing service startup code inside if __name__ == "__main__":.
# This is also a standard pattern that prevents unintended re-execution during Taipy's process spawning.