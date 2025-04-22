# 🎬 M3Cleaner

**M3Cleaner** is a Python script that lets you **manage `.m3u` IPTV playlists**: enable/disable channels, select the preferred stream for each one, and save your preferences in a local database for future use.

> Ideal for keeping your IPTV playlists clean, organized, and personalized.

---

## 📌 Features

- ✅ **Load M3U playlists** from a local file or a remote URL.
- 🧠 **Store your preferences** (channel status and selected stream) in SQLite.
- 🧪 **Automatically add new channels** as inactive when new `tvg-id`s are detected.
- 🔄 **Enable or disable channels**, individually or in bulk.
- 🔁 **Switch stream sources** for each channel when multiple are available.
- 🎯 **Only one source per active channel** is included in the generated list.
- 🎨 **Visual terminal interface** using colors for active/inactive channels.
- 💾 **Generate a new `.m3u` file** filtered based on your saved preferences.

---

## 📂 Project Structure

```
.
├── m3cleaner.py           # Main script
├── preferencias_canales.db # SQLite database (auto-created)
├── README.md               # This file
└── filtrado.m3u            # Output file (filtered playlist)
```

---

## 🚀 Requirements

- Python 3.7 or higher
- No external dependencies required (only standard Python libraries)

---

## ⚙️ Usage

```bash
python m3cleaner.py playlist.m3u
# or
python m3cleaner.py https://example.com/playlist.m3u
```

After loading the file (from disk or URL), you'll see an interactive menu:

```
🎛️ Main Menu:
1. Enable/disable individual channels
2. Enable all channels
3. Disable all channels
4. Change stream source (only for enabled channels)
5. Generate filtered m3u file
q. Quit
```

---

## 🧠 How the database works

The script creates and uses `preferencias_canales.db` with two tables:

### Table `channels`
- `tvg_id`: unique channel identifier
- `activo`: whether the channel is enabled (1) or not (0)

### Table `sources`
- `tvg_id`: associated channel ID
- `nombre`: name of the stream variant
- `url`: stream URL
- `activo`: only one active source per channel

---

## 📝 Example Input (`.m3u`)

```m3u
#EXTM3U
#EXTINF:-1 tvg-id="ExampleChannel1",Example HD
http://localhost:8000/stream1
#EXTINF:-1 tvg-id="ExampleChannel1",Example SD
http://localhost:8000/stream2
#EXTINF:-1 tvg-id="ExampleChannel2",Sports Channel
http://localhost:8000/stream3
```

---

## ✅ Example Output (`filtered.m3u`)

```m3u
#EXTM3U
#EXTINF:-1 tvg-id="ExampleChannel1",ExampleChannel1
http://localhost:8000/stream1
#EXTINF:-1 tvg-id="ExampleChannel2",ExampleChannel2
http://localhost:8000/stream3
```

Only **enabled channels** with **one active stream source** are included.

---

## 📌 Notes

- New `tvg-id`s are added as **inactive by default**.
- You can select **one active source per channel**, stored persistently.
- All preferences are reused automatically on future runs.
- You can load new playlists at any time without restarting the program.

---

## 🧪 To-Do & Future Improvements

- [ ] GUI using Tkinter or PyQt
- [ ] Export to other formats (`.json`, `.xml`, `.csv`)
- [ ] Cross-device favorites sync
- [ ] EPG and custom logo support

---

## 🧑‍💻 Author

GitHub: [@daviddelrom](https://github.com/daviddelrom)

---

## 📜 License

MIT License – Feel free to use it, with love and respect for open source! 💛

---

Thanks for using this project!  
Want to suggest improvements or found a bug? Open an issue or send a PR! 🚀

