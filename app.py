from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv('OPENROUTER_API_KEY')
PROMPT_DIR = "./prompts"

def load_prompt(level):
    with open(os.path.join(PROMPT_DIR, f"level_{level}_prompt.txt"), 'r') as file:
        return file.read().strip()

def load_translation_prompt():
    with open(os.path.join(PROMPT_DIR, "translation_prompt.txt"), 'r') as file:
        return file.read().strip()

def call_nous_hermes(level, gender):
    system_prompt = load_prompt(level)
    user_prompt = f"Write task for {'men' if gender == 'MEN' else 'women'}"
    payload = {
        "model": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    response = requests.post("https://api.openrouter.ai/v1/ask", json=payload, headers={"Authorization": f"Bearer {API_KEY}"})
    return response.json()

def call_grok(nous_response):
    translation_prompt = load_translation_prompt()
    payload = {
        "model": "x-ai/grok-2-vision-1212",
        "messages": [
            {"role": "system", "content": translation_prompt},
            {"role": "user", "content": nous_response}
        ]
    }
    response = requests.post("https://api.openrouter.ai/v1/ask", json=payload, headers={"Authorization": f"Bearer {API_KEY}"})
    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit():
    level = request.json.get('level')
    gender = request.json.get('gender')
    nous_response = call_nous_hermes(level, gender)
    grok_response = call_grok(nous_response['content'])
    return jsonify({
        'nous_response': nous_response['content'],
        'grok_response': grok_response['content']
    })

@app.route('/edit_prompts', methods=['GET', 'POST'])
def edit_prompts():
    if request.method == 'POST':
        for level in range(1, 5):
            prompt_content = request.form.get(f'level_{level}')
            with open(os.path.join(PROMPT_DIR, f'level_{level}_prompt.txt'), 'w') as file:
                file.write(prompt_content)
        translation_content = request.form.get('translation_prompt')
        with open(os.path.join(PROMPT_DIR, 'translation_prompt.txt'), 'w') as file:
            file.write(translation_content)
    prompts = {f"level_{i}": load_prompt(i) for i in range(1, 5)}
    prompts['translation_prompt'] = load_translation_prompt()
    return render_template('edit_prompts.html', prompts=prompts)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render provides a PORT variable
    app.run(host="0.0.0.0", port=port, debug=True)
