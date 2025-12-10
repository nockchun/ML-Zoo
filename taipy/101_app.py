from taipy import Gui

page = "# Hello Taipy !"

Gui(page).run(port=5050, debug=True, use_reloader=True, title="step 101")