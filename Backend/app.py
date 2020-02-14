# python libraries
import base64
import io
import pickle
import time
from os import path as p
from os import remove as rm
# python web framework
from flask import Flask, jsonify, render_template, request, send_file
from flask_mysqldb import MySQL
# google libraries for api
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
# Flask configuration
app = Flask(__name__)
app.secret_key = "mySecretKey"
app_root = p.dirname(p.abspath(__file__))
app_credRoute = p.join(app_root, "credentials/")
app_token = p.join(app_credRoute, "token.pickle")
app_credentials = p.join(app_credRoute, "credentials.json")
app_files = p.join(app_root, "files/")
# mysql configuration
app.config['MYSQL_HOST'] = 'remotemysql.com'  # 'database'  # 'remotemysql.com'
app.config['MYSQL_USER'] = 'EZJ3dWJQGl'
app.config['MYSQL_PASSWORD'] = 'LtZuP4CBdl'
app.config['MYSQL_DB'] = 'EZJ3dWJQGl'
mysql = MySQL(app)
# google api configurations
SCOPES = ["https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/drive.appdata",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata",
          "https://www.googleapis.com/auth/drive.scripts"]

creds = None

if p.exists(app_token):
    with open(app_token, "rb") as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            app_credentials, SCOPES)
        creds = flow.run_local_server(port=0)

    with open(app_token, "wb") as token:
        pickle.dump(creds, token, protocol=2)

service = build("drive", "v3", credentials=creds)

# webpage renders
@app.route("/", methods=["GET"])
def Index():
    return render_template("Index.html")


@app.route("/Documents", methods=["GET"])
def Documents():
    return render_template("Documents.html")


@app.route("/Download", methods=["GET"])
def Download():
    return render_template("Download.html")


@app.route("/Upload", methods=["GET"])
def Upload():
    return render_template("Upload.html")


@app.route('/Files', methods=['GET'])
def Files():
    return render_template("files.html")
# auxiliar def


def encodeFile(file):
    openFile = open(file, "rb")
    return base64.encodestring(openFile.read())


def decodeFile(fileName, myFile):
    myPath = p.join(app_files, fileName)
    openFile = open(myPath, "wb")
    openFile.write(base64.decodestring(myFile))
    openFile.close()
    return myPath


def uploadFile(fileId, fileName, newFile):
    Archivo = encodeFile(newFile)
    Fecha = time.strftime("%c")
    cur = mysql.connection.cursor()
    cur.execute('''INSERT INTO versiones
                (fileId,
                 Nombre_Archivo,
                 Archivo,
                 Fecha)
                VALUES
                (%s,
                 %s,
                 %s,
                 %s)''',
                (fileId,
                 fileName,
                 Archivo,
                 Fecha))
    mysql.connection.commit()
    cur.close()

# web api defs
@app.route("/API/Documents/DB", methods=["GET"])
def getRecords():
    cur = mysql.connection.cursor()
    cur.execute('SELECT Id, fileId, Nombre_Archivo, Fecha FROM versiones')
    data = cur.fetchall()
    cur.close()
    payload = []
    content = {}
    for element in data:
        content = {
            'Id': element[0],
            'fileId': element[1],
            'Nombre_Archivo': element[2],
            "Fecha": element[3]}
        payload.append(content)
        content = {}
    return jsonify(payload)


@app.route("/API/Documents", methods=["GET"])
def getDocuments():
    try:
        # ,version,createdTime,modifiedTime,lastModifyingUser(displayName,emailAddress))'
        customFiles = 'nextPageToken,files(id,name,mimeType)'
        results = service.files().list(
            pageSize=1000,
            fields=customFiles).execute()

        items = results.get("files", [])

        if not items:
            return jsonify({"message": "No files found."})
        else:
            payload = []
            content = {}
            for item in items:
                content = {
                    "Id": item["id"],
                    "Name": item["name"],
                    # "mimeType": item["mimeType"],
                    #    "version": item["version"],
                    #    "createdTime": item["createdTime"],
                    #    "modifiedTime": item["modifiedTime"]
                }
                # for values in item.keys():
                #    if values == 'lastModifyingUser':
                #        content.update(
                #            {"lastModifyingUser": item["lastModifyingUser"]})

                payload.append(content)

                content = {}
            return jsonify(payload)
    except errors.HttpError as error:

        return jsonify({'message': 'An error occurred: %s' % error})


@app.route("/API/Documents", methods=["POST"])
def postDocuments():
    if request.method == "POST":
        newFile = request.files["file"]

        myPath = p.join(app_files, newFile.filename)

        newFile.save(myPath)

        folder_id = '1dGf7BNpSHxdA2TafIqGywkQPqWDipAUc'

        file_metadata = {
            'name': newFile.filename,
            'parents': [folder_id]

        }

        media = MediaFileUpload(myPath, mimetype="application/msword")

        response = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        if not response:
            return jsonify({"message": "No file created."})
        else:
            uploadFile(response.get('id'), newFile.filename, myPath)
            return jsonify({"message": "File created successfully"})
            rm(myPath)


@app.route("/API/Documents/<string:ID>", methods=["GET"])
def getDocument(ID):
    item = service.files().get(fileId=ID).execute()

    fileName = item['name'] + ".docx"

    if not item:

        return jsonify({"message": "No file found."})

    else:

        request = service.files().get_media(fileId=ID)

        myPath = p.join(app_files, fileName)

        myFile = io.FileIO(myPath, 'wb')

        fileRequest = MediaIoBaseDownload(myFile, request)

        while True:

            try:

                download_progress, done = fileRequest.next_chunk()

            except errors.HttpError as error:

                return jsonify({'message': 'An error occurred: %s' % error})

            if done:

                return send_file(
                    myPath,
                    as_attachment=True,
                    mimetype=item['mimeType'])
                time.sleep(120)
                rm(myPath)


@app.route("/API/Documents/<string:ID>", methods=["PUT"])
def putDocument(ID):
    if request.method == "PUT":
        try:
            file = service.files().get(fileId=ID).execute()
            file2Update = request.files['file']
            myPath = p.join(app_files, file2Update.filename)
            media_body = MediaFileUpload(
                myPath,
                filename=file['name'],
                mimetype=file['mimeType'],
                resumable=True)  # ,
            # modifiedTime='')
            updatedFile = service.files().update(
                fileId=ID,
                body=file,
                media_body=media_body
            ).execute()
            uploadFile(ID, file['name'], myPath)
            return jsonify({"message": {'file updated %s', updatedFile}})
        except errors.HttpError as error:
            return jsonify({'message': ('file not updated %s', error)})


@app.route("/API/Documents/<string:ID>", methods=["DELETE"])
def deleteDocument(ID):
    if request.method == "DELETE":
        try:
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM versiones WHERE fileId=%s', [ID])
            data = cur.fetchall()
            cur.close()
            response = service.files().delete(fileId=ID)
            return jsonify({"message": "File deleted successfully!!!!"})
        except errors.HttpError as error:
            return jsonify({'message': error})


@app.route("/API/Documents/Version/<string:ID>", methods=["GET"])
def getVersion(ID):
    cur = mysql.connection.cursor()
    cur.execute(
        'SELECT Id,Nombre_Archivo,Fecha FROM versiones WHERE fileId =%s', [ID])
    data = cur.fetchall()
    cur.close()
    payload = []
    content = {}
    for element in data:
        content = {
            'Id': element[0],
            'Nombre_Archivo': element[1],
            "Fecha": element[2]}
        payload.append(content)
        content = {}
    return jsonify(payload)
    # return jsonify({"document": })


@app.route('/API/Documents/VersionDB/<string:ID>', methods=['GET'])
def getVersionDB(ID):
    cur = mysql.connection.cursor()
    cur.execute(
        'SELECT Archivo,Nombre_Archivo FROM versiones WHERE fileId =%s', [ID])
    data = cur.fetchall()
    cur.close()
    return send_file(decodeFile(data[0][1], data[0][0]), as_attachment=True)


# server configuration
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
