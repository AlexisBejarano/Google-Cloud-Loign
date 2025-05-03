from flask import Flask, redirect, url_for, session, request, render_template
from models import db, Usuario
from config import client, get_google_provider_cfg, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
import os, json, requests
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    config = get_google_provider_cfg()
    redirect_uri = request.base_url.replace("/login", "") + "/callback"
    print("Redirect URI usada:", redirect_uri)

    auth_uri = client.prepare_request_uri(
        config["authorization_endpoint"],
        redirect_uri=redirect_uri,
        scope=["openid","https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/userinfo.profile"]
    )
    return redirect(auth_uri)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    config = get_google_provider_cfg()

    token_url, headers, body = client.prepare_token_request(
        config["token_endpoint"],
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    access_token = token_response.json()["access_token"]

    uri, headers, body = client.add_token(config["userinfo_endpoint"])
    userinfo = requests.get(uri, headers=headers, data=body).json()

    usuario = Usuario.query.filter_by(email=userinfo["email"]).first()
    if not usuario:
        usuario = Usuario(
            email=userinfo["email"],
            name=userinfo["name"],
            picture=userinfo["picture"],
            token=access_token
        )
        db.session.add(usuario)
        db.session.commit()

    session["email"] = userinfo["email"]
    session["name"] = userinfo["name"]
    session["picture"] = userinfo["picture"]
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

