import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_path = './model/finalmodel'


model = AutoModelForCausalLM.from_pretrained(model_path, device_map='auto')
tokenizer = AutoTokenizer.from_pretrained(model_path)

text_generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map='auto',
    pad_token_id=tokenizer.eos_token_id,
    max_new_tokens=50
)

def format_input(instruction, prompt_input=None):
    if prompt_input:
        return f"""
        ### Instruction:
        {instruction}

        ### Input:
        {prompt_input}

        ### Response:
        """.strip()
    else:
        return f"""
        ### Instruction:
        {instruction}

        ### Response:
        """.strip()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Text Generation App", style={'textAlign': 'center'}),
    dcc.Textarea(id='user_instruction', style={'width': '50%', 'height': 50}, placeholder='Enter instruction...'),
    dcc.Textarea(id='user_input', style={'width': '50%', 'height': 50}, placeholder='Enter additional input if needed...'),
    html.Button('Generate', id='submit_button', n_clicks=0, style={'margin': 10}),
    html.Div(id='response', style={'whiteSpace': 'pre-line', 'marginTop': 20, 'padding': 10, 'border': '1px solid #ddd'})
])

@app.callback(
    Output('response', 'children'),
    [Input('submit_button', 'n_clicks')],
    [State('user_instruction', 'value'),
     State('user_input', 'value')]
)
def generate_text(n_clicks, user_instruction, user_input):
    if n_clicks > 0:
        if user_instruction:
            formatted_input = format_input(user_instruction, user_input)
            output = text_generator(formatted_input)
            response = output[0]['generated_text'].split("### Response:\n")[-1]
            return html.Pre(response)
        else:
            return html.Pre("Please enter an instruction before submitting.")
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)
