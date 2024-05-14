# Discord Bot for YouTube Video Transcription to TikTok

This Discord bot allows you to transcribe YouTube videos into clips and automatically download them to TikTok.

## Features

- Download YouTube videos
- Split videos into 65-second clips
- Add text to video clips
- Automatically upload clips to TikTok

## Configuration

1. **Install Dependencies:** Use `pip install -r requirements.txt` to install all necessary dependencies.

2. **Discord Token Configuration:** Create a `.env` file at the root of the project and add your Discord token:
    ```
    DISCORD_TOKEN=your_discord_token
    ```

3. **TikTok Cookies Configuration:** Make sure you have a `cookies.txt` file containing your TikTok cookies to download videos to TikTok.

## Usage

1. Invite the bot to your Discord server.

2. Use the `+up [youtube_video_link]` command to start transcribing a YouTube video into clips.

3. Wait for the bot to finish transcribing and downloading the clips to TikTok.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, feel free to create a pull request.

## Author

This project was created by Lex in December 2023.

## Notes

The bot is designed to work with most YouTube videos, but it may encounter issues with certain types of content or formats. Additionally, please note that as of its creation date in December 2023, the bot may not be fully functional or bug-free. If you encounter any issues or have any feedback, feel free to open an issue on GitHub.
