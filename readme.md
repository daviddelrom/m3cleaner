# 🎬 M3Cleaner

This is a Python script that lets you **filter, enable/disable, and switch stream sources for IPTV channels** in `.m3u` playlists, while storing your preferences in a local database for future use.

> Perfect for managing custom IPTV playlists and keeping a clean, persistent channel setup!

---

## 📌 Features

- ✅ **Load an M3U playlist** and analyze all unique channels (`tvg-id`).
- 🧠 **Store your preferences** (active status and selected stream) in a local SQLite database.
- 🔄 **Enable or disable channels** individually or in bulk.
- 🧬 **Switch between different stream sources** for the same channel.
- 💾 **Generate a new filtered `.m3u` file** based on your preferences.
- ♻️ **Automatically reuse saved preferences** the next time a matching playlist is loaded.

---

## 📂 Project Structure

```
.
├── m3u_filter.py           # Main script
├── preferencias_canales.db # SQLite database (auto-created)
├── README.md               # This file
└── filtrado.m3u            # Output file (filtered playlist)
```

---

## 🚀 Requirements

- Python 3.7 or higher
- No external dependencies required (uses Python's standard library)

---

## ⚙️ Usage

```bash
python m3u_filter.py original_playlist.m3u
```

Once loaded, you'll see an interactive menu:

```
Menu:
1. Enable/disable individual channels
2. Enable all channels
3. Disable all channels
4. Change stream source (only for enabled channels)
5. Generate filtered m3u file
q. Quit
```

---

## 🧠 Preference Database

The script automatically creates a `preferencias_canales.db` file (SQLite) that stores:

- The `tvg-id` of the channel
- The selected variant (name + URL)
- Whether the channel is **enabled or disabled**

These preferences will be reused automatically the next time you analyze a playlist containing the same channels.

---

## 📝 Example Input (`.m3u`)

```m3u
#EXTM3U
#EXTINF:-1 tvg-id="ExampleChannel1" group-title="News",Example Channel 1 HD
http://192.168.1.100:8080/stream1
#EXTINF:-1 tvg-id="ExampleChannel1" group-title="News",Example Channel 1 SD
http://192.168.1.100:8080/stream2
#EXTINF:-1 tvg-id="ExampleChannel2" group-title="Sports",Sports Channel
http://192.168.1.100:8080/stream3
```

---

## ✅ Example Output (`filtered.m3u`)

```m3u
#EXTM3U
#EXTINF:-1 tvg-id="ExampleChannel1" group-title="News",Example Channel 1 HD
http://192.168.1.100:8080/stream1
#EXTINF:-1 tvg-id="ExampleChannel2" group-title="Sports",Sports Channel
http://192.168.1.100:8080/stream3
```

---

## 📌 Notes

- If a channel has multiple variants (`tvg-id` matches), you can choose your preferred one.
- Only **enabled** channels will be included in the final output.
- All your selections (stream and status) are saved for future sessions.

---

## 🧪 To-Do & Future Improvements

- [ ] GUI using Tkinter or PyQT
- [ ] Export to other formats: `.json`, `.xml`, `.csv`
- [ ] Cross-device channel favorite sync
- [ ] Support for `EPG` and custom logos

---

## 🧑‍💻 Author

GitHub: [@daviddelrom](https://github.com/daviddelrom)

---

## 📜 License

MIT License – Feel free to use it, with love and respect for open source! 💛

---

Thanks for using this project!  
Want to see improvements? Found a bug? Open an issue or send a PR! 🚀
