import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
    text = text.replace('.', ' *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _:True))

key = 'AIzaSyAwKzzuSj6uBTq1DOGzLULScbZSmMnLSZM'

genai.configure(api_key=key)

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

model = genai.GenerativeModel('gemini-pro')


response = model.generate_content('What does this translate to in english? Es gibt verschiedene Verfahren der Statistik und\n        Klassifikation um den Wetter zu bestimmen. Hier werden wir die\n        Verwendung von Fuzzy-Systemen für diesen Zweck erklären. Wir\n        werden zunächst die notwendigen Grundkonzepte der Fuzzy-Systeme\n        beschreiben. Anschließend werden mehrere Beispiele angeführt.')


print(response.text)