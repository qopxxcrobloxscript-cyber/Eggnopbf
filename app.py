from flask import Flask, request, render_template_string
from obfuscator import obfuscate

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Lua Obfuscator</title>
<style>
body{background:#0f0f0f;color:white;font-family:monospace;padding:40px}
textarea{width:100%;height:300px;background:#1a1a1a;color:#0f0;border:none;padding:10px}
button{padding:10px 20px;margin-top:10px;background:#00ff88;border:none}
</style>
</head>
<body>

<h1>Lua Obfuscator</h1>

<form method="post">
<textarea name="code" placeholder="paste lua code here"></textarea>
<br>
<button>Obfuscate</button>
</form>

{% if result %}
<h2>Result</h2>
<textarea>{{result}}</textarea>
{% endif %}

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def home():
    result = None
    if request.method == "POST":
        code = request.form["code"]
        result = obfuscate(code)
    return render_template_string(HTML,result=result)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
