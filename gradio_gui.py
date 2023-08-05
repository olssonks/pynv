import gradio as gr
import tomli


def experiment(file_obj):
    
    with open(file_obj.name, "rb") as file:
        configs = tomli.load(file)
    return configs['name']


demo = gr.Interface(experiment, "file", "text")

if __name__ == "__main__":
    demo.launch()
