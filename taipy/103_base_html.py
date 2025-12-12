###############################################################################
# Separate execution settings for development/production.
###############################################################################
from taipy.gui import Gui, Html

# State variables
sales = 100
base_sales = 100

# HTML 기반 Taipy 페이지
page = Html("ui.html")
# page = Html("""
# <div class="container">
#   <h1>State &amp; Button</h1>

#   <p>
#     현재 매출:
#     <taipy:text>{sales}</taipy:text>
#   </p>

#   <div class="buttons">
#     <taipy:button label="+10" on_action="add_sales"></taipy:button>
#     <taipy:button label="Reset" on_action="reset_sales"></taipy:button>
#   </div>
# </div>
# """)

# 버튼 콜백
def add_sales(state):
    state.sales += 10

def reset_sales(state):
    state.sales = state.base_sales


if __name__ == "__main__":
    gui = Gui(page=page, env_filename="dev.env")
    gui.run(title="103: HTML Page")
