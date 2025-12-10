from taipy.gui import Gui, Markdown, notify

# 1) State variables
price = 10000
discount = 10
currency = "KRW"
final_price = 0
summary = ""


page = Markdown("""
# 할인 계산기

<|layout|columns=1 1|gap=1rem|
<|
## 입력

가격  
<|{price}|number|min=0|step=100|>

할인율  
<|{discount}|slider|min=0|max=100|step=1|>

통화  
<|{currency}|selector|lov=KRW;USD;JPY;EUR|dropdown|>

<|Calculate|button|on_action=calculate|>
<|Reset|button|on_action=reset|>
|>

<|
## 결과

할인가  
<|{final_price}|text|>

요약  
<|{summary}|text|>
|>
|>
""")


if __name__ == "__main__":
    gui = Gui(page, env_filename="103.env")
    gui.run(title="step 104")


# Extremely important structural point : Why run it inside the __main__ block?
# Taipy provides various service execution structures such as GUI/REST/Orchestrator,
# and you can also bundle and run multiple services with tp.run(...).
# The documentation also recommends placing service startup code inside if __name__ == "__main__":.
# This is also a standard pattern that prevents unintended re-execution during Taipy's process spawning.