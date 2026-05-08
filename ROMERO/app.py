from flask import Flask, redirect, url_for, session, jsonify, request
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = "DEVELOPMENT_ONLY_KEY_123"

oauth = OAuth(app)

# GitHub OAuth Configuration
github = oauth.register(
    name='github',
    client_id='Ov23liEl9MPnGgykqqKK',
    client_secret='adfa813a83f1eb115ab9eaa4f420f120060d4119',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

@app.route('/')
@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('profile'))
    
    if request.args.get('auth') == 'true':
        redirect_uri = url_for('callback', _external=True)
        return github.authorize_redirect(redirect_uri)

    # Check if we just came from the logout route
    logged_out = request.args.get('logout')
    logout_banner = ""
    if logged_out:
        logout_banner = '''
            <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #c3e6cb;">
                <strong>Success!</strong> You have been logged out safely.
            </div>
        '''

    return f'''
        <html>
            <head><title>Login Page</title></head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px; background-color: #f0f2f5;">
                <div style="max-width: 400px; margin: auto;">
                    {logout_banner}
                    <div style="border: 1px solid #ccc; padding: 50px; border-radius: 15px; background: white; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
                        <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="80">
                        <h1>OAuth Login</h1>
                        <p style="color: #666;">Please login to continue</p>
                        <br>
                        <a href="/login?auth=true">
                            <button style="padding: 15px 30px; font-size: 18px; cursor: pointer; background-color: #24292e; color: white; border: none; border-radius: 8px; font-weight: bold;">
                                Login with GitHub
                            </button>
                        </a>
                    </div>
                </div>
            </body>
        </html>
    '''

@app.route('/callback')
def callback():
    token = github.authorize_access_token()
    resp = github.get('user')
    user_info = resp.json()
    session['user'] = user_info
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return "<h1>401 Unauthorized</h1><p>Please <a href='/login'>Login</a>.</p>", 401
    return jsonify(user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    # Redirect to login with the logout flag set to true
    return redirect(url_for('login', logout='true'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)