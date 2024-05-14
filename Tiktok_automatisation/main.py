import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pytube import YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
import re
import subprocess
import platform
import psutil
import GPUtil
from humanize import naturalsize
import shutil

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents)
cookies_path = 'cookies.txt'

def clear_folders():
    extracts_folder = 'extraits'
    videos_folder = 'Vidéos'

    if os.path.exists(extracts_folder):
        shutil.rmtree(extracts_folder)
    os.makedirs(extracts_folder)

    if os.path.exists(videos_folder):
        shutil.rmtree(videos_folder)
    os.makedirs(videos_folder)

clear_folders()

def clean_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '', title)

def download_youtube_video(url, output_path):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        video_title = clean_filename(yt.title).replace(' ', '_')

        print(f"Téléchargement : {video_title}")
        video_stream.download(output_path, filename=f'{video_title}.mp4')

        print("\nTéléchargement terminé!")
        return f'{video_title}.mp4', yt.author

    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        return None, None

def split_video(input_file, output_directory, youtube_channel):
    try:
        video_clip = VideoFileClip(input_file)
        duration = video_clip.duration
        num_clips = int(duration / 65) + 1

        video_name = clean_filename(os.path.basename(input_file)[:-4]).replace(' ', '_')
        output_folder = os.path.join(output_directory, video_name)
        os.makedirs(output_folder, exist_ok=True)

        for i in range(num_clips):
            start_time = i * 65
            end_time = min((i + 1) * 65, duration)
            clip = video_clip.subclip(start_time, end_time)
            temp_filename = f'partie_{i + 1}t.mp4'
            final_filename = f'partie_{i + 1}f.mp4'
            clip.write_videofile(os.path.join(output_folder, temp_filename),
                                 codec="libx264", audio_codec="aac", verbose=False)

            input_filepath = os.path.join(output_folder, temp_filename)
            output_filepath = os.path.join(output_folder, final_filename)

            cmd = f'ffmpeg -i {input_filepath} -lavfi "[0:v]scale=256/81*iw:256/81*ih,' \
                  f'boxblur=luma_radius=min(h\\,w)/40:luma_power=3:chroma_radius=min(cw\\,ch)/40:chroma_power=1[bg];' \
                  f'[bg][0:v]overlay=(W-w)/2:(H-h)/2,setsar=1,crop=w=iw*81/256" {output_filepath}'

            subprocess.run(cmd, shell=True)

            text_top_cmd = f'ffmpeg -i {output_filepath} -vf "drawtext=text=\'PARTIE {i + 1}\': fontfile=Montserrat-Regular.ttf: fontsize=128: fontcolor=white: x=(w-text_w)/2: y=h/10,drawtext=text=\'YOUTUBEUR : {youtube_channel}\': fontfile=Montserrat-Regular.ttf: fontsize=64: fontcolor=white: x=(w-text_w)/2: y=h-h/10" -codec:a copy {output_filepath.replace(".mp4", "_text.mp4")}'

            subprocess.run(text_top_cmd, shell=True)

            os.remove(input_filepath)

            print(f"Progression : {((i + 1) / num_clips) * 100:.2f}% | Temps estimé : {(num_clips - i - 1) * 2} sec")
            print(f"Building video {final_filename}")
            print(f"Writing audio {final_filename}")
            print("Done.")
            print(f"Writing video {final_filename}\n")

        print(f"Vidéo divisée en {num_clips} parties.")

    except Exception as e:
        print(f"Erreur de découpage : {e}")

def cleanup_files(videos_dir, extracts_dir):
    for filename in os.listdir(videos_dir):
        file_path = os.path.join(videos_dir, filename)
        try:
            if os.path.isfile(file_path) and filename.endswith(".mp4"):
                os.unlink(file_path)
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier : {e}")

    for root, dirs, files in os.walk(extracts_dir):
        for filename in files:
            if filename.endswith("f.mp4"):
                final_filepath = os.path.join(root, filename)
                os.unlink(final_filepath)

                text_filepath = final_filepath.replace("f.mp4", "f_text.mp4")
                os.rename(text_filepath, final_filepath)

                temp_filepath = final_filepath.replace("f.mp4", "t.mp4")
                if os.path.exists(temp_filepath):
                    os.unlink(temp_filepath)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='pc')
async def pc(ctx):
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    gpu_info = ""
    try:
        gpus = GPUtil.getGPUs()
        for i, gpu in enumerate(gpus):
            gpu_info += f"GPU {i + 1}:\n"
            gpu_info += f" - Model: {gpu.name}\n"
            gpu_info += f" - Utilisation: {gpu.load * 100:.2f}%\n"
            gpu_info += f" - Mémoire utilisée: {gpu.memoryUsed} MB\n"
            gpu_info += f" - Mémoire totale: {gpu.memoryTotal} MB\n\n"
    except Exception as e:
        gpu_info = "Impossible de récupérer les informations GPU."

    system_info = f"Plateforme: {platform.system()}\n"
    system_info += f"Version: {platform.version()}\n"
    system_info += f"Architecture: {platform.architecture()}\n"
    system_info += f"Processeur: {platform.processor()}\n"
    system_info += f"CPU Usage: {cpu_usage}%\n"
    system_info += f"RAM:\n - Total: {naturalsize(ram.total)}\n - Disponible: {naturalsize(ram.available)}\n - Usage: {ram.percent}%\n"
    system_info += f"Disk:\n - Total: {naturalsize(disk.total)}\n - Disponible: {naturalsize(disk.free)}\n - Usage: {disk.percent}%\n"
    system_info += gpu_info

    embed = discord.Embed(title='Informations système', description=system_info, color=discord.Color.red())
    embed.set_footer(text='Made with ❤️ by LE𝕏')
    await ctx.send(embed=embed)

@bot.command(name='h')
async def help_command(ctx):
    help_message = "Commandes disponibles:\n"
    help_message += "+up [lien] : Transcrit une vidéo YouTube en extraits.\n"
    help_message += "+pc : Affiche des informations sur le PC hébergeant le bot."

    await ctx.send(embed=discord.Embed(description=help_message, color=discord.Color.red()).set_footer(text='Made with ❤️ by LE𝕏'))

def upload_to_tiktok(video_path, description, cookies_path):
    try:
        cmd = f'tiktok-uploader -v "{video_path}" -d "{description}" -c "{cookies_path}"'
        subprocess.run(cmd, shell=True)
        print(f'Upload réussi : {video_path}')
    except Exception as e:
        print(f'Erreur lors de l\'upload : {e}')
        return str(e)

def upload_all_parts(cookies_path):
    extracts_folder = 'extraits'
    description = 'Abonne-toi! #viral #replay # youtube #youtubeclips #fyp #prt #foryou'

    for root, dirs, files in os.walk(extracts_folder):
        for file in files:
            if file.endswith("_text.mp4"):
                video_path = os.path.join(root, file)
                upload_to_tiktok(video_path, description, cookies_path)

    clear_folders()

    return None

def run_upload():
    upload_all_parts(cookies_path)

@bot.command(name='up')
async def up(ctx, url):
    await ctx.send(embed=discord.Embed(description=f'Début de la transcription en extraits de la vidéo.', color=discord.Color.red()).set_footer(text='Made with ❤️ by LE𝕏'))

    downloaded_file, youtube_channel = download_youtube_video(url, 'Vidéos')

    if downloaded_file:
        split_video(os.path.join('Vidéos', downloaded_file), 'extraits', youtube_channel)
        
        run_upload()

        await ctx.send(embed=discord.Embed(description=f'Transcription de la vidéo de {youtube_channel} terminée. Tous les extraits ont été téléchargés sur TikTok avec succès.', color=discord.Color.red()).set_footer(text='Made with ❤️ by LE𝕏'))

if __name__ == "__main__":
    run_upload()
    bot.run(TOKEN)