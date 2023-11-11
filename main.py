from dash import dcc, html, Dash
import dash
import dash_bootstrap_components as dbc
import os
from sqlalchemy import (
    Table,
    create_engine,
    MetaData,
    insert,
    Column,
    String,
    Integer,
    Float,
    Boolean,
    select,
    DateTime,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin
from dash.dash import no_update
from dash.dependencies import Input, Output, State
from datetime import datetime
import numpy as np

app = dash.Dash(
    __name__,
    title="logindemo",
    # external_stylesheets=[dbc.themes.QUARTZ,dbc.icons.FONT_AWESOME],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
)

server = app.server
app.config.suppress_callback_exceptions = True
# config
server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI="sqlite:///data.sqlite",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db = SQLAlchemy()
engines = create_engine("sqlite:///data.sqlite")

db.init_app(server)
# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "login"
login_manager.login_message = "ログインしてください"


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=False)
    password = db.Column(db.String(80))

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


metadata = MetaData()
Users_tbl = Table("users", Users.metadata)
Users.metadata.create_all(engines)


def login_manager_init(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))


class User(UserMixin, Users):
    pass


login_manager_init(login_manager)
enginet = create_engine("sqlite:///test8.sqlite", echo=False)
logins = Table(
    "logins",
    metadata,
    Column("line_items_id", Integer(), primary_key=True),
    Column("userID", String(255)),
    Column("login", DateTime(), default=datetime.now),
)
metadata.create_all(enginet)

failed = html.Div(
    [
        dcc.Location(id="url_login_df", refresh=True),
        html.Div(
            [
                html.H5("エラーが起こりました. ログイン画面に戻ります"),
                html.Br(),
                html.Br(),
                html.Button(id="back-button", children="ログアウト", n_clicks=0),
            ]
        ),  # end div
    ]
)  # end div

create = html.Div(
    [
        html.Hr(),
        html.Div("アカウントを作成し全ての機能を使う"),
        dcc.Location(id="create_user", refresh=True),
        #         html.Audio(src="assets/toujyo.mp3",id="audio1",controls=False,autoPlay=True),
        html.Div(id="dummy"),
        dcc.Input(id="uname", type="text", placeholder="user name", maxLength=15),
        html.Div(dcc.Input(id="passwd", type="password", placeholder="password")),
        html.Div(
            dbc.Button(
                "アカウント作成",
                id="submit-val",
                n_clicks=0,
                outline=True,
                color="dark",
                size="sm",
            )
        ),
        html.Hr(),
        html.Div("お試しの場合はこちら"),
        dbc.Button(
            "ゲストログイン",
            id="guest_login",
            n_clicks=0,
            outline=True,
            color="dark",
            size="sm",
        ),
        html.Hr(),
        html.Div(
            [
                dcc.Location(id="url_login", refresh=True),
                dcc.Location(id="url_login2", refresh=True),
                dcc.Location(id="url_login3", refresh=True),
                html.Div("""登録済みのかた:""", id="h1"),
                html.Div(dcc.Input(placeholder="ユーザー名", type="text", id="username")),
                html.Div(
                    dcc.Input(placeholder="パスワード", type="password", id="password")
                ),
                html.Div(
                    dbc.Button(
                        children="ログイン",
                        n_clicks=0,
                        # href="/login",
                        type="submit",
                        id="login-button",
                        outline=True,
                        color="dark",
                        size="sm",
                    )
                ),
                html.Div(children="", id="output-state"),
                html.Div(id="container-button-basic"),
            ]
        ),
    ]
)

logout = html.Div(
    [
        dcc.Location(id="url_logout", refresh=True),
        html.Br(),
        html.Div(html.H2("ログアウトしました")),
        html.Br(),
        dbc.Button("戻る", href="/", n_clicks=0, outline=True, color="dark", size="sm"),
    ]
)

setting2 = (
    dbc.Container(
        [
            dcc.Location(id="url_setting", refresh=True),
            dbc.Row(
                [
                    dbc.Col([html.Span("username:"), html.Span(id="username")]),
                    dbc.Col(
                        dbc.Button("logout", href="/logout", outline=True, color="dark")
                    ),
                ]
            ),
            html.Div(id="user_item"),
        ]
    ),
)

app.layout = dbc.Container(
    [
        html.Div(id="page-content", className="content"),
        dcc.Location(id="url_app1", refresh=True),
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="store_data", storage_type="session", data={"test": "test"}),
        html.Div(id="user_name", children="", hidden=True),
        html.Div("2023 AKKDiS all rights reserved"),
    ]
)


@app.callback(
    Output("page-content", "children"),
    Output("store_data", "data"),
    Input("url", "pathname"),
    State("store_data", "data"),
)
def display_page(pathname, data1):
    data1 = data1 or {}
    if pathname == "/":
        return (create, data1)

    elif "start" == pathname.split("/")[-2]:
        if current_user.is_authenticated:
            sp = pathname.split("/")[-1]
            return (
                dcc.Location(id="url_login", pathname=f"/{sp}", refresh=True),
                data1,
            )

    if pathname == "/setting1":
        if current_user.is_authenticated:
            return (setting2, data1)
    if pathname == "/logout":
        if current_user.is_authenticated:
            return (logout, data1)
    return (failed, data1)


def login_log(username):
    with enginet.connect() as con:
        stmt = insert(logins).values(userID=username)
        result_proxy = con.execute(stmt)
        return result_proxy


@app.callback(Output("url_app1", "pathname"), Input("back-button", "n_clicks"))
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return "/"
    else:
        raise dash.exceptions.PreventUpdate


@app.callback(
    Output("url_login", "pathname"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True,
)
def successful(n_clicks, input1, input2):
    user = Users.query.filter_by(username=input1).first()
    if user:
        if check_password_hash(user.password, input2):
            login_user(user)
            login_log(user.username)
            return "/setting1"
        else:
            pass
    else:
        pass


@app.callback(
    Output("username", "children"),
    Input("user_item", "children"),
)
def return_123(user_item):
    username = "{}".format(current_user.username)
    return username


@app.callback(Output("create_user", "pathname"), [Input("guest_login", "n_clicks")])
def logout_dashboard2(n_clicks):
    if n_clicks > 0:
        num = np.random.randint(10000, 99999)
        un = "Guest10" + str(num)
        hashed_password = generate_password_hash("password", method="sha256")
        ins = Users_tbl.insert().values(
            username=un,
            password=hashed_password,
            email=un,
        )
        conn = engines.connect()
        conn.execute(ins)
        conn.close()
        user = Users.query.filter_by(username=un).first()
        login_user(user)
        return "/setting1"


@app.callback(
    Output("url_login3", "pathname"),
    Output("container-button-basic", "children"),
    Input("submit-val", "n_clicks"),
    State("uname", "value"),
    State("passwd", "value"),
    prevent_initial_call=True,
)
def insert_users(n_clicks, un, pw):
    em = None
    hashed_password = generate_password_hash(pw, method="sha256")
    user = Users.query.filter_by(username=un).first()
    if user:
        return (
            no_update,
            [
                html.Div(
                    [
                        html.H2("そのユーザー名はすでに使用されています"),
                        dbc.Button("他のユーザー名を設定してください", href="/"),
                    ]
                )
            ],
        )
    if un is not None and pw is not None:
        ins = Users_tbl.insert().values(
            username=un,
            password=hashed_password,
            email=em,
        )
        conn = engines.connect()
        conn.execute(ins)
        conn.close()
        user = Users.query.filter_by(username=un).first()
        if user:
            if check_password_hash(user.password, pw):
                login_user(user)
                login_log(user.username)
                return ("/setting1", html.Div())
    else:
        return ("/", html.Div())


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050, use_reloader=False)
