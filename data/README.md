# Data pack goes here

The course data pack is **not** stored in this repo. Before running the app, copy it into this
folder so it looks like this:

```
data/
  campus_customs.db      SQLite database: catalogue, inventory, users, chat_messages
  products/              product photos (102 .jpg files), served at /images/<file>.jpg
  README.md              this file
```

Both are git-ignored. The app reads and writes `campus_customs.db` in place: new accounts go into
`users`, and logged-in chats go into `chat_messages`.
