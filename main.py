# This is a sample Python script.

# Press Ctrl+Shift+R to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import gradio


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
from Post import *
from Query import *
from ui import gradio_ui
#
# q = Query()
# tags = ['feet','ass']
# q = Query_Yandere(tags)
# q.query_page(5)
# print(len(q.posts))

gradio.close_all()
u = gradio_ui()
u.interface()


