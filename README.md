<p align="center">
  <b>~ Visits ~</b><br><br>
  <img src="https://profile-counter.glitch.me/pdf-pixy/count.svg">
</p>

<p align="center">
<a href="https://github.com/SirDank/PDF-Pixy"><img width="800" alt="image" src="static/pdf-pixy.png"></a><br>
</p>

# 💎 PDF Pixy 💎

- A simple pdf storage & collaboration website built with python!

# 💠Preview💠

## 🔹Sign-In🔹

<br><p align="center"><img width="800" alt="image" src="https://github.com/SirDank/PDF-Pixy/assets/52797753/67e36236-da00-4c28-a45f-937d0aaf3fa5"></p><br>

## 🔹Sign-Up🔹

<br><p align="center"><img width="800" alt="image" src="https://github.com/SirDank/PDF-Pixy/assets/52797753/a0b0e59f-ef4a-4590-b7b0-806684ca857f"></p><br>

## 🔹Dashboard🔹

<br><p align="center"><img width="800" alt="image" src="https://github.com/SirDank/PDF-Pixy/assets/52797753/62440cb7-b4d3-4e80-8713-7607d84756f6"></p><br>

## 🔹Share🔹

<br><p align="center"><img width="800" alt="image" src="https://github.com/SirDank/PDF-Pixy/assets/52797753/7f595d2d-45e6-478a-88b3-b054fdfdb105"></p><br>

# 💠Information💠

- The website is built using python and flask.
- The website uses a simple file sharing system with token based authentication ( for downloads ) and password hashing ( for storing passwords ).
- The website uses a simple ip based authentication system for login.
- A user is automatically logged in on other devices if he/she is already logged in on one device.
- A user remains authenticated for a maximum of one day.
- Users can share pdf files owned by them to other registered users.
- Users can comment on both uploaded and shared pdf files.
- User data is stored in json format in the following files under the asset folder: `registered_users.json`, `signed_in_users.json`, `shared_files.json`, `tokens.json`
- `registered_users.json`: every login ip associated with its email is logged here along with the hashed password and the name of the user.
```json
{
    "admin@gmail.com": {
        "name": "admin",
        "hash": "pbkdf2:sha256:600000$clfDlZm1RxDkzJ0I$4a27fd931369e2fb295fbe5885dc02c59081b53e8e78c71075739462b6a5dd9e",
        "ips": []
    }
}
```
- `signed_in_users.json`: every signed in ip along with its email and the valid time of the session is stored here.
```json
{
    "127.0.0.1": {
        "valid_time": 99999999999999999,
        "email": "admin@gmail.com"
    }
}
```
- `shared_files.json`: every file uploaded by a user is stored here along with the token associated with the file.
```json
{
    "admin@gmail.com": {
        "sample.pdf": "VhRHZuohDMFBowef",
        "dummy.pdf": "yaVhCkDbStSPDFIF"
    }
}
```
- `tokens.json`: every token created is stored here along with the path of the file and the comments associated with the file.
```json
{
    "VhRHZuohDMFBowef": {
        "path": "admin@gmail.com/sample.pdf",
        "comments": [
            {
                "file": "sample.pdf",
                "text": "very cool pdf",
                "user": "tmp-user1",
                "date": "3/Jul/23"
            }
        ]
    },
    "yaVhCkDbStSPDFIF": {
        "path": "admin@gmail.com/dummy.pdf",
        "comments": [
            {
                "file": "dummy.pdf",
                "text": "hope you get recruited X)",
                "user": "tmp-user1",
                "date": "3/Jul/23"
            },
            {
                "file": "dummy.pdf",
                "text": "all the best!",
                "user": "tmp-user2",
                "date": "3/Jul/23"
            }
        ]
    }
}
```
