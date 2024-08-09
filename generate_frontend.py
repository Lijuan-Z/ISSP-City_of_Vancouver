import os
# update index.html,lazer.html, 404.html
file_list = ["index.html", "404.html", "lazer.html"]

for html_doc in file_list:
    with open(f"backend/templates/{html_doc}", "r+") as file:
        print(f"modifying url of file {html_doc}...")
        content = file.read()
        content = content.replace('src="/_next/static/', 'src=" {{ url_for(\'static\', filename=\'')
        content = content.replace('href="/_next/static/', 'href="{{ url_for(\'static\', filename=\'')
        content = content.replace('.css"', '.css\') }}"')
        content = content.replace('.js"', '.js\') }}"')
        content = content.replace("/_next/", "")

        file.seek(0)
        file.write(content)
        file.truncate()

        print(f"modify completed of file {html_doc}...")

#update webpack-xxx.js file
for root, dirs, files in os.walk("backend/static/chunks"):
    js_name = list(filter(lambda f: "webpack" in f, files))
    if len(js_name) > 0:
        js_name = js_name[0]
        break

with open(f"backend/static/chunks/{js_name}", "r+") as file:
    print(f"modifying next path of file {js_name}...")
    content = file.read()
    content = content.replace("/_next/", "")

    file.seek(0)
    file.write(content)
    file.truncate()
    file_list.append(js_name)



print(f"Files {file_list} are all updated.")