import re
import os
import math
import logging
import asyncio
import aiohttp
import requests
import time
from pyrogram import Client,filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import xml.etree.ElementTree as ET 
import numpy as np
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip
from PIL import Image
import base64, requests, sys, xmltodict
import headers
from pywidevine.L3.cdm import cdm, deviceconfig
from base64 import b64encode
from pywidevine.L3.getPSSH import get_pssh
from pywidevine.L3.decrypt.wvdecryptcustom import WvDecrypt

api_id = '17810412'
api_hash = 'bd9cd7df354fb74e2f9ec88f6ee4de48'
bot_token = '6722338594:AAHEycYEJWffASKS-qlhdKqCqeUBIgDAHMg'
allowed_chats = [-1001974911212,5441346943,-1001562024039,6204387702,5877917640,-1001862375832,6365172445] 
log_channel_id = -1001767473604
admins = [5441346943,5877917640,1174588770,6365172445]

app = Client('my_bot', api_id=api_id, api_hash=api_hash, bot_token=bot_token)


UPLOAD_START = "Uploading"
AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = "Downloaded in {} seconds.\nUploaded in {} seconds."

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_allowed(chat_id):
    return chat_id in allowed_chats
def is_bot_owner(user_id):
    bot_owner_id = 5441346943
    return user_id == bot_owner_id
@app.on_message(filters.command("start") )
async def handle_command(client,message):
    await message.reply("I'm alive")

@app.on_message(filters.command("allow"))
async def handle_command(client,message):
  if is_bot_owner(message.chat.id):  
    try:
        chat_id_to_allow = int(message.text.split(" ")[1])
        allowed_chats.append(chat_id_to_allow)
        await message.reply(f"Chat ID {chat_id_to_allow} has been allowed.")
    except (ValueError, IndexError):
        await message.reply(f"Invalid command. \n\nUsage: /allow id")


@app.on_message(filters.command("methods"))
async def handle_command(client,message):
    if is_allowed(message.chat.id):
        await message.reply(f"<b><u>Edumix Method</u></b>\n\nâˆŽ <b>With Headers</b>\n\n<code>mpd_link*https://drm-bot.herokuapp.com/xxxxxxxx.txt*name</code>\n\nâˆŽ <b>With Keys</b>\n\nâ‹„ <p><u>Edumix </u>: -\n<code>mpd_link*--key xxxxxxxxx:xxxxxxxxxx*name</code></p>\n\n<b><u>Vimeo / m3u8 Links Method</u></b>\n<code>link*name</code>\n\n<b><u>BunnyDrm Method</u></b>\n\nfirst_link*second_link*name")  
        return
    else:
        await message.reply("you are not allowed to use me ðŸ™…ðŸ»â€â™€ï¸")


@app.on_message(filters.command("remove"))
async def handle_command(client,message):
  if is_bot_owner(message.chat.id): 
    try:
        chat_id_to_remove = int(message.text.split(" ")[1])
        if chat_id_to_remove in allowed_chats:
            allowed_chats.remove(chat_id_to_remove)
            await message.reply(f"Chat ID {chat_id_to_remove} has been removed from the allowed list.")
        else:
            await message.reply(f"Chat ID {chat_id_to_remove} is not in the allowed list.")
    except (ValueError, IndexError):
        await message.reply("Invalid command. \n\nUsage: /remove id")


@app.on_message(filters.regex(pattern="https://iframe.mediadelivery.net")) 
async def handle_text_message(client, message ):
  if is_allowed(message.chat.id):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    mention = message.from_user.mention
    command_args = message.text.split('*')
    mpd_url = command_args[0]
    if len(command_args) >= 1:
            custom_name = ' '.join(command_args[1:]) if len(command_args) > 1 else "default_custom_name"
            text = message.text
            mpd_url = None
            custom_name = None
            if "*" in text:
                mpd_url,*name_parts = text.split("*")
                custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                link_type = 'databoxtech'
                await download_worker_b(client,message,link_type,user_id,first_name,mention,mpd_url,custom_name)
            else:
                error = 'Please check /methods and send link in correct format'
                await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)

    else:
            error = 'Please check /methods and send link in correct format'
            await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)
  else:
      await app.send_message(chat_id=message.chat.id,text="you are not allowed to use me ðŸ™…ðŸ»â€â™€ï¸",reply_to_message_id=message.id)


async def download_worker_b(client,message,link_type,user_id,first_name,mention,mpd_url,custom_name):
    try:
        status_message = await message.reply(f"Checking Link.. Please Wait !") 
        async with aiohttp.ClientSession() as session:
                
                await status_message.edit_text("Recieved Valid Mpd link âœ…")
                await status_message.edit_text(f"Engine : <b>Bunny Drm Downloader</b>\n\nDownloading video : {custom_name}\n\nUser: {mention}\nID : <code>{user_id}</code>\n\n<b>ðŸš€ @Drm_Downloaderx_Bot</b>")
                custom_name = f"{custom_name}.ts"
                caption_name = custom_name
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                command_to_exec = [
                        'hlsdl',
                        '-b',
                        '-f',
                        '-F',
                        '-c',
                        '-v',
                        '-u',f"{user_agent}",
                        '-h',"Referer:https://iframe.mediadelivery.net",
                        '-o',custom_name,
                        f"{mpd_url}",
                    ]
                    
                logger.info(command_to_exec)
                process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                e_response = stderr.decode().strip()
                t_response = stdout.decode().strip()
                logger.info(e_response)
                logger.info(t_response)
                final_video_path = custom_name
                final_video_path1 = custom_name
                if os.path.exists(final_video_path):
                    output_mp4_path = f"{custom_name}.mp4"
                    ffmpeg_command = [
                    'ffmpeg',
                    '-i', final_video_path,
                    '-c:v', 'copy',
                    '-c:a', 'copy',
                    output_mp4_path,
                    ]
                    logger.info(ffmpeg_command)
                    start = datetime.now()
                    process = await asyncio.create_subprocess_exec(
                   *ffmpeg_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, stderr = await process.communicate()
                    e_response = stderr.decode().strip()
                    t_response = stdout.decode().strip()
                    logger.info(e_response)
                    logger.info(t_response)
                    video_clip = VideoFileClip(output_mp4_path)
                    video_duration = int(video_clip.duration)
                    await status_message.edit_text(f"Download Completed . Uploading video...")
                    await send_video_b(
                    message.chat.id,
                    output_mp4_path,
                    video_duration,
                    caption_name,
                    user_id,
                    mention,
                    status_message
                    )
                    os.remove(final_video_path)
                else:
                    os.remove(final_video_path1)
                    await status_message.edit_text("Oops... something went wrong! Maybe try again?")
                    return
    except Exception as e:
        await message.reply(f"Something went wrong\n\nâŒ Error : {str(e)}")
        return


async def send_video_b(chat_id, output_mp4_path, duration, caption_name,user_id,mention,status_message):
    try:
        thumbnail_path = generate_thumbnail_b(output_mp4_path)
        width = 320
        height = 180
        if user_id == 5877917640 or user_id == 5441346943 :
            name = 'Downloaded By Science Edu'
        else:
            name = str(user_id) + ' Downloaded By Science Edu'
        start_time = time.time()
        video_up = await app.send_video(
            chat_id=user_id,
            video=output_mp4_path,
            thumb=thumbnail_path,
            duration=duration,
            width=width,
            height=height,
            caption=caption_name,
            file_name=name,
            supports_streaming=True,
            )
        video_up = video_up.id
        cap=f"Name : {caption_name}\n\nUser: {mention}\n#ID_{user_id}"
        await app.copy_message(log_channel_id,user_id,message_id=video_up,caption=cap)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("ðŸ“¤ View in Bot PM", url='https://t.me/Drm_Downloaderx_Bot')]])
        await status_message.edit_text(
            f"File have been Sent to Bot PM (Private).\n\nName : <b>{caption_name}</b>\n\nUser : {mention}",
            reply_markup=keyboard,
            )
        os.remove(output_mp4_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    except Exception as e:
        logger.error(f"An error occurred while sending the video: {str(e)}")


def generate_thumbnail_b(final_video_path, time_offset=5):
    thumbnail_path = final_video_path.replace(".mp4", ".jpg")
    try:
        video_clip = VideoFileClip(final_video_path)
        thumbnail_frame = video_clip.get_frame(time_offset)
        thumbnail_image = Image.fromarray(np.uint8(thumbnail_frame))
        thumbnail_image.save(thumbnail_path, format="JPEG")
        return thumbnail_path
    except Exception as e:
        logger.error(f"Error generating thumbnail: {str(e)}")
        return None


@app.on_message(filters.regex(pattern="https://d2148dkxdf27z.cloudfront.net")) 
async def handle_text_message(client, message ):
  if is_allowed(message.chat.id):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    mention = message.from_user.mention
    command_args = message.text.split('*')
    mpd_url = command_args[0]
    key1 = command_args[1]
    key2 = command_args[2]
    key3 = command_args[3]
    key4 = command_args[4]
    custom_name = command_args[5]
    key1_match = re.search(r"https://drm-bot.herokuapp.com",key1)
    if key1_match:
        if len(command_args) >= 5:
            custom_name = ' '.join(command_args[2:]) if len(command_args) > 1 else "default_custom_name"
            text = message.text
            mpd_url = None
            key1 = None
            key2 = None
            key3 = None
            key4 = None
            custom_name = None
            if "*" in text:
                mpd_url, key1, key2, key3, key4, *name_parts = text.split("*")
                custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                link_type = 'databoxtech'
                await app.send_message(chat_id=message.chat.id,text="not supported yet",reply_to_message_id=message.id)
            else:
                error = 'Please check /methods and send link in correct format'
                await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)

        else:
            error = 'Please check /methods and send link in correct format'
            await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)
    else:
        if len(command_args) >= 5:
            custom_name = ' '.join(command_args[5:]) if len(command_args) > 4 else "default_custom_name"
            text = message.text
            mpd_url = None
            key1 = None
            key2 = None
            key3 = None
            key4 = None
            custom_name = None
            if "*" in text:
                mpd_url, key1, key2, key3, key4, *name_parts = text.split("*")
                custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                await download_worker_v(client,message,user_id,first_name,mention,mpd_url,key1, key2, key3, key4,custom_name)
            else:
                error = 'Please check /methods and send link in correct format'
                await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)

        else:
            error = 'Please check /methods and send link in correct format'
            await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)
  else:
      await app.send_message(chat_id=message.chat.id,text="you are not allowed to use me ðŸ™…ðŸ»â€â™€ï¸",reply_to_message_id=message.id)


@app.on_message(filters.regex(pattern="https://video.lk.databoxtech.com/playlist")) 
async def handle_text_message(client, message ):
  if is_allowed(message.chat.id):

    user_id = message.from_user.id
    first_name = message.from_user.first_name
    mention = message.from_user.mention
    command_args = message.text.split('*')
    mpd_url = command_args[0]

    if len(command_args) >= 0:
            custom_name = ' '.join(command_args[2:]) if len(command_args) > 1 else "default_custom_name"
            text = message.text
            mpd_url = None
            custom_name = None
            if "*" in text:
                mpd_url, *name_parts = text.split("*")
                custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                link_type = 'databoxtech'
                await download_worker_M3U8_Drm(client,message,user_id,first_name,mention,mpd_url,custom_name)
            else:
                error = 'Please check /methods and send link in correct format'
                await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)

    else:
            error = 'Please check /methods and send link in correct format'
            await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)
  else:
      await app.send_message(chat_id=message.chat.id,text="you are not allowed to use me ðŸ™…ðŸ»â€â™€ï¸",reply_to_message_id=message.id)


async def download_worker_M3U8_Drm(client,message,user_id,first_name,mention,mpd_url,custom_name):
    try:
        status_message = await message.reply("Checking m3u8 Link.. Please Wait !")
        new_link = reformat_url(mpd_url)
        key_message = f'<b>Downloading video : {custom_name}\n\nEngine : <b>M3U8 Downloader</b>\n\nUser: {mention}\n#ID_{user_id}\n\n</b>'
        await status_message.edit_text(key_message)
        command_to_exec = [
            './N_m3u8DL-RE',
            new_link,
            '--save-name', custom_name,
            '-sv', 'best',
            '-sa', 'best',
            '--mux-after-done', 'mkv',
            '--thread-count', '100'
        ]
        logger.info(command_to_exec)
        start = datetime.now()
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        logger.info(e_response)
        logger.info(t_response)
        if t_response:
            end_one = datetime.now()
            time_taken_for_download = (end_one - start).seconds
            await status_message.edit_text(UPLOAD_START)

        final_video_path = f"{custom_name}.mkv"

        if os.path.exists(final_video_path):
            video_clip = VideoFileClip(final_video_path)
            video_duration = int(video_clip.duration)
            await status_message.edit_text(f"Download Completed . Uploading video...")
            await send_video(
                message.chat.id,
                final_video_path,
                video_duration,
                custom_name,
                user_id,
                mention,
                end_one,
                time_taken_for_download,
                status_message
            )
            os.remove(final_video_path)
        else:
            await status_message.edit_text("Oops... something went wrong! Maybe try again?")
    except Exception as e:
        await status_message.edit_text(f"Something went wrong\n\nâŒ Error : {str(e)}")

@app.on_message(filters.regex(pattern="https://video.lk.databoxtech.com")) 
async def handle_text_message(client, message ):
  if is_allowed(message.chat.id):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    mention = message.from_user.mention
    command_args = message.text.split('*')
    mpd_url = command_args[0]
    xdrm = command_args[1]
    xdrm_match = re.search(r"https://drm-bot.herokuapp.com",xdrm)
    if xdrm_match:
        if len(command_args) >= 2:
            custom_name = ' '.join(command_args[2:]) if len(command_args) > 1 else "default_custom_name"
            text = message.text
            mpd_url = None
            xdrm = None
            custom_name = None
            if "*" in text:
                mpd_url, xdrm, *name_parts = text.split("*")
                custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                link_type = 'databoxtech'
                await download_worker(client,message,link_type,user_id,first_name,mention,mpd_url,xdrm,custom_name)
            else:
                error = 'Please check /methods and send link in correct format'
                await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)

        else:
            error = 'Please check /methods and send link in correct format'
            await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)
    else:
        if len(command_args) >= 2:
            custom_name = ' '.join(command_args[2:]) if len(command_args) > 1 else "default_custom_name"
            text = message.text
            mpd_url = None
            xdrm = None
            custom_name = None
            if "*" in text:
                mpd_url, xdrm, *name_parts = text.split("*")
                custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                link_type = 'datay'
                await download_worker(client,message,link_type,user_id,first_name,mention,mpd_url,xdrm,custom_name)
            else:
                error = 'Please check /methods and send link in correct format'
                await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)

        else:
            error = 'Please check /methods and send link in correct format'
            await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)
  else:
      await app.send_message(chat_id=message.chat.id,text="you are not allowed to use me ðŸ™…ðŸ»â€â™€ï¸",reply_to_message_id=message.id)


@app.on_message(filters.regex(pattern=".m3u8")) 
async def handle_text_message(client, message ):
  if is_allowed(message.chat.id):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    mention = message.from_user.mention
    command_args = message.text.split('*')
    mpd_url = command_args[0]
    xdrm = command_args[1]
    if len(command_args) >= 1:
            custom_name = ' '.join(command_args[2:]) if len(command_args) > 1 else "default_custom_name"
            text = message.text
            mpd_url = None
            custom_name = None
            if "*" in text:
                mpd_url, *name_parts = text.split("*")
                custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                await download_worker_M3U8(client,message,user_id,first_name,mention,mpd_url,custom_name)
            else:
                error = 'Please check /methods and send link in correct format'
                await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)

    else:
            error = 'Please check /methods and send link in correct format'
            await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)

async def download_worker_M3U8(client,message,user_id,first_name,mention,mpd_url,custom_name):
    try:
        status_message = await message.reply("Checking m3u8 Link.. Please Wait !")
        key_message = f'<b>Downloading video : {custom_name}\n\nEngine : <b>M3U8 Downloader</b>\n\nUser: {mention}\n#ID_{user_id}\n\n</b>'
        await status_message.edit_text(key_message)
        command_to_exec = [
            './N_m3u8DL-RE',
            mpd_url,
            '--save-name', custom_name,
            '-sv', 'best',
            '-sa', 'best',
            '--mux-after-done', 'mkv',
            '--thread-count', '100'
        ]
        logger.info(command_to_exec)
        start = datetime.now()
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        logger.info(e_response)
        logger.info(t_response)
        if t_response:
            end_one = datetime.now()
            time_taken_for_download = (end_one - start).seconds
            await status_message.edit_text(UPLOAD_START)

        final_video_path = f"{custom_name}.mkv"

        if os.path.exists(final_video_path):
            video_clip = VideoFileClip(final_video_path)
            video_duration = int(video_clip.duration)
            await status_message.edit_text(f"Download Completed . Uploading video...")
            await send_video(
                message.chat.id,
                final_video_path,
                video_duration,
                custom_name,
                user_id,
                mention,
                end_one,
                time_taken_for_download,
                status_message
            )
            os.remove(final_video_path)
        else:
            await status_message.edit_text("Oops... something went wrong! Maybe try again?")
    except Exception as e:
        await status_message.edit_text(f"Something went wrong\n\nâŒ Error : {str(e)}")


@app.on_message(filters.regex(pattern="https://cdn.dyntube.net") )
async def handle_text_message(client, message ):
  if is_allowed(message.chat.id):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    mention = message.from_user.mention
    command_args = message.text.split('*')
    mpd_url = command_args[0]
    if len(command_args) >= 1:
            custom_name = ' '.join(command_args[1:]) if len(command_args) > 1 else "default_custom_name"
            text = message.text
            mpd_url = None
            custom_name = None
            if "*" in text:
                mpd_url,*name_parts = text.split("*")
                custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                link_type = 'databoxtech'
                await download_worker_d(client,message,link_type,user_id,first_name,mention,mpd_url,custom_name)
            else:
                error = 'Please check /methods and send link in correct format'
                await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)

    else:
            error = 'Please check /methods and send link in correct format'
            await app.send_message(chat_id=message.chat.id,text=error,reply_to_message_id=message.id)
  else:
      await app.send_message(chat_id=message.chat.id,text="you are not allowed to use me ðŸ™…ðŸ»â€â™€ï¸",reply_to_message_id=message.id)


async def download_worker_d(client,message,link_type,user_id,first_name,mention,mpd_url,custom_name):
    try:
        status_message = await message.reply(f"Checking Link.. Please Wait !") 
        async with aiohttp.ClientSession() as session:
                await status_message.edit_text("Recieved Valid Mpd link âœ…")
                await status_message.edit_text(f"Website : Apni.lk\n\nEngine : <b>🚫Bunny Drm Downloader Test Version</b>\n\nDownloading video : {custom_name}\n\nUser: {mention}\nID : <code>{user_id}</code>\n\n<b>ðŸš€ @Drm_Downloaderx_Bot</b>")
                custom_name = f"{custom_name}"
                caption_name = custom_name
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                command_to_exec = [
                        'hlsdl',
                        '-b',
                        '-f',
                        '-F',
                        '-c',
                        '-v',
                        '-u',f"{user_agent}",
                        '-h',"Referer:https://videos.dyntube.com/",
                        '-o',f"{custom_name}.ts",
                        f"{mpd_url}",
                    ]
                    
                logger.info(command_to_exec)
                process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                e_response = stderr.decode().strip()
                t_response = stdout.decode().strip()
                logger.info(e_response)
                logger.info(t_response)
                final_video_path = f"{custom_name}.ts"
                final_video_path1 = custom_name
                if os.path.exists(final_video_path):
                    output_mp4_path = f"{custom_name}.mp4"
                    ffmpeg_command = [
                    'ffmpeg',
                    '-i', final_video_path,
                    '-c:v', 'copy',
                    '-c:a', 'copy',
                    output_mp4_path,
                    ]
                    logger.info(ffmpeg_command)
                    start = datetime.now()
                    process = await asyncio.create_subprocess_exec(
                   *ffmpeg_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    )
                    stdout, stderr = await process.communicate()
                    e_response = stderr.decode().strip()
                    t_response = stdout.decode().strip()
                    logger.info(e_response)
                    logger.info(t_response)
                    video_clip = VideoFileClip(output_mp4_path)
                    video_duration = int(video_clip.duration)
                    await status_message.edit_text(f"Download Completed . Uploading video...")
                    await send_video_b(
                    message.chat.id,
                    output_mp4_path,
                    video_duration,
                    caption_name,
                    user_id,
                    mention,
                    status_message
                    )
                    os.remove(final_video_path)
                else:
                    os.remove(final_video_path1)
                    await status_message.edit_text("Oops... something went wrong! Maybe try again?")
                    return
    except Exception as e:
        await message.reply(f"Something went wrong\n\nâŒ Error : {str(e)}")
        return


@app.on_message(filters.regex(pattern=".json"))
async def handle_text_message(client, message ):
  if is_allowed(message.chat.id):
    global user_id
    global first_name
    global mention
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    mention = message.from_user.mention
    global mpd_url
    global custom_name
    command_args = message.text.split('*')
    mpd = command_args[0]
    custom_name = command_args[1]
    if len(command_args) > 1:
        custom_name = ' '.join(command_args[1:]) if len(command_args) > 0 else "default_custom_name"
        text = message.text
        if "*" in text:
            mpd, *name_parts = text.split("*")
            custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
            mpd_url = mpd.replace(".json", ".m3u8")
        keyboard = [
            [InlineKeyboardButton("Best Quality",callback_data="best")],
            [InlineKeyboardButton("Medium Quality", callback_data="360")],
            [InlineKeyboardButton("Low Quality", callback_data="worst")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply(
            text=f"Recieved Valid link âœ…\n\nSelect video quality for download:",
            reply_markup=reply_markup
        )
    else:
        await message.reply("Please check /methods and send link in correct format")
  else:
    await app.send_message(chat_id=message.chat.id,text="you are not allowed to use me ðŸ™…ðŸ»â€â™€ï¸",reply_to_message_id=message.id)



@app.on_callback_query()
async def callback_handler(client, query):
    try:
        global user_id, first_name, mention, mpd_url, custom_name
        select = query.data
        message = query.message
        await message.delete()
        await download_worker_vimeo(client, message, select)

    except Exception as e:
        await query.message.reply(f"An error occurred: {str(e)}")

async def download_worker_vimeo(client, message, select):
    try:
        status_message = await message.reply("Checking m3u8 Link.. Please Wait !")
        if select == "medium":
            select = str('res="360*"')
        elif select == "best":
            select = "best"
        elif select == "worst":
            select = "worst"
        key_message = f'<b>Downloading video : {custom_name}\n\nEngine : <b>M3U8 Downloader</b>\n\nUser: {mention}\n#ID_{user_id}\n\n</b>'
        await status_message.edit_text(key_message)
        command_to_exec = [
            './N_m3u8DL-RE',
            mpd_url,
            '--save-name', custom_name,
            '-sv', select,
            '-sa', 'best',
            '--mux-after-done', 'mkv',
            '--thread-count', '100'
        ]
        logger.info(command_to_exec)
        start = datetime.now()
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        logger.info(e_response)
        logger.info(t_response)
        if t_response:
            end_one = datetime.now()
            time_taken_for_download = (end_one - start).seconds
            await status_message.edit_text(UPLOAD_START)

        final_video_path = f"{custom_name}.mkv"

        if os.path.exists(final_video_path):
            video_clip = VideoFileClip(final_video_path)
            video_duration = int(video_clip.duration)
            await status_message.edit_text(f"Download Completed . Uploading video...")
            await send_video(
                message.chat.id,
                final_video_path,
                video_duration,
                custom_name,
                user_id,
                mention,
                end_one,
                time_taken_for_download,
                status_message
            )
            os.remove(final_video_path)
        else:
            await status_message.edit_text("Oops... something went wrong! Maybe try again?")
    except Exception as e:
        await status_message.edit_text(f"Something went wrong\n\nâŒ Error : {str(e)}")


async def download_worker(client,message,link_type,user_id,first_name,mention,mpd_url,xdrm,custom_name):
    try:
        site_check = re.search(r'\/([^/]+)\/[^/]+$', mpd_url)
        site = site_check.group(1) 
        status_message = await message.reply(f"website : {site}.lk\n\nChecking Mpd Link.. Please Wait !") 
        async with aiohttp.ClientSession() as session:
            mpd_response = await session.get(mpd_url)
            if mpd_response.status == 200:
                await status_message.edit_text("Recieved Valid Mpd link âœ…")
                if link_type == 'databoxtech':
                    lic_url = 'https://licensing.eduvid.lk/acquireLicense/widevine'
                    mpd_content = await mpd_response.text()
                    pssh = extract_pssh_from_mpd(mpd_content)
                    header = extract_headers_from_curl(xdrm)
                    headers = {hkey: value for hkey, value in header.items()}
                    def WV_Function(pssh_data, lic_url, cert_b64=None):
                        wvdecrypt = WvDecrypt(init_data_b64=pssh, cert_data_b64=cert_b64, device=deviceconfig.device_android_generic) 
                        widevine_license = requests.post(url=lic_url, data=wvdecrypt.get_challenge(), headers=headers)
                        license_b64 = b64encode(widevine_license.content)
                        wvdecrypt.update_license(license_b64)
                        Correct, keyswvdecrypt = wvdecrypt.start_process()
                        if Correct:
                            return Correct, keyswvdecrypt 
                    correct, keys = WV_Function(pssh, lic_url) 
                    for key in keys:  
                        fkeys = key 
                        await status_message.edit_text(f"<b>Successfully Retrieved Keys âœ…\n\n<code><b>--key</b> {fkeys}</code>\n\nWebsite : {site}.lk\n\nEngine : <b>Databoxtech Downloader</b>\n\nDownloading video : {custom_name}\n\nUser: {mention}\nID : <code>{user_id}</code>\n\n<b>ðŸš€ @Drm_Downloaderx_Bot</b>")
                    command_to_exec = [
                        './N_m3u8DL-RE',
                        mpd_url,
                        '--save-name', custom_name,
                        '-sv', 'best',
                        '-sa', 'best',
                        '--mux-after-done', 'mkv',
                        '--key', fkeys ,
                        '--thread-count', '100'
                    ]
                    
                elif link_type == 'datay':
                    fkeys = xdrm
                    await status_message.edit_text(f"<b>Trying to Download video with recieved keys âœ…\n\n<code><b>--key</b> {fkeys}</code>\n\nWebsite : {site}.lk\n\nEngine : <b>Databoxtech Downloader</b>\n\nDownloading video : {custom_name}\n\nUser: {mention}\n#ID : <code>{user_id}</code>\n\n<b>ðŸš€ @Drm_Downloaderx_Bot</b>")
                    command_to_exec = [
                        './N_m3u8DL-RE',
                        mpd_url,
                        '--save-name', custom_name,
                        '-sv', 'best',
                        '-sa', 'best',
                        '--mux-after-done', 'mkv',
                        '--key',fkeys,
                        '--thread-count', '100'
                    ]
                logger.info(command_to_exec)
                start = datetime.now()
                process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                e_response = stderr.decode().strip()
                t_response = stdout.decode().strip()
                logger.info(e_response)
                logger.info(t_response)
                if t_response:
                    end_one = datetime.now()
                    time_taken_for_download = (end_one -start).seconds
                    await status_message.edit_text(UPLOAD_START)
                final_video_path = f"{custom_name}.mkv"
                final_video_path1 = custom_name
                if os.path.exists(final_video_path):
                    video_clip = VideoFileClip(final_video_path)
                    video_duration = int(video_clip.duration)
                    await status_message.edit_text(f"Download Completed . Uploading video...")
                    await send_video(
                    message.chat.id,
                    final_video_path,
                    video_duration,
                    custom_name,
                    user_id,
                    mention,
                    end_one,
                    time_taken_for_download,
                    status_message
                    )
                    os.remove(final_video_path)
                else:
                    os.remove(final_video_path1)
                    await status_message.edit_text("Oops... something went wrong! Maybe try again?")
                    return
            else:
                await message.reply("âŒ Link Expired âŒ. Please send me a fresh link ")
                return
    except Exception as e:
        await message.reply(f"Something went wrong\n\nâŒ Error : {str(e)}")
        return

async def download_worker_v(client,message,user_id,first_name,mention,mpd_url,key1, key2, key3, key4,custom_name):
    
    try:
        
        status_message = await message.reply(f"Checking Mpd Link.. Please Wait !") 
        async with aiohttp.ClientSession() as session:
            mpd_response = await session.get(mpd_url)
            if mpd_response.status == 200:
                await status_message.edit_text("Recieved Valid Mpd link âœ…")
                await status_message.edit_text(f"<b>Trying to Download video with recieved keys âœ…\n\nEngine : <b>Vdociper Downloader</b>\n\nDownloading video : {custom_name}\n\nUser: {mention}\n#ID : <code>{user_id}</code>\n\n<b>ðŸš€ @Drm_Downloaderx_Bot</b>")
                command_to_exec = [
                        './N_m3u8DL-RE',
                        mpd_url,
                        '--save-name', custom_name,
                        '-sv', 'best',
                        '-sa', 'best',
                        '--mux-after-done', 'mkv',
                        '--key',key1,
                        '--key',key2,
                        '--key',key3,
                        '--key',key4,
                        '--thread-count', '100'
                    ]
                logger.info(command_to_exec)
                start = datetime.now()
                process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                e_response = stderr.decode().strip()
                t_response = stdout.decode().strip()
                logger.info(e_response)
                logger.info(t_response)
                if t_response:
                    end_one = datetime.now()
                    time_taken_for_download = (end_one -start).seconds
                    await status_message.edit_text(UPLOAD_START)
                final_video_path = f"{custom_name}.mkv"
                final_video_path1 = custom_name
                if os.path.exists(final_video_path):
                    video_clip = VideoFileClip(final_video_path)
                    video_duration = int(video_clip.duration)
                    await status_message.edit_text(f"Download Completed . Uploading video...")
                    await send_video(
                    message.chat.id,
                    final_video_path,
                    video_duration,
                    custom_name,
                    user_id,
                    mention,
                    end_one,
                    time_taken_for_download,
                    status_message
                    )
                    os.remove(final_video_path)
                else:
                    os.remove(final_video_path1)
                    await status_message.edit_text("Oops... something went wrong! Maybe try again?")
                    return
            else:
                await message.reply("âŒ Link Expired âŒ. Please send me a fresh link ")
                return
    except Exception as e:
        await message.reply(f"Something went wrong\n\nâŒ Error : {str(e)}")
        return


async def send_video(chat_id, video_path, duration, caption,user_id,mention,end_one,time_taken_for_download,status_message):
    try:
        thumbnail_path = generate_thumbnail(video_path)
        width = 320
        height = 180
        if user_id == 5877917640 or user_id == 5441346943 or user_id == {admins}:
            name = 'Downloaded By Science Edu'
        else:
            name = str(user_id) + ' Downloaded By Science Edu'
        start_time = time.time()
        video_up = await app.send_video(
            chat_id=user_id,
            video=video_path,
            thumb=thumbnail_path,
            duration=duration,
            width=width,
            height=height,
            caption=caption,
            file_name=name,
            supports_streaming=True,
            progress=progress_for_pyrogram,
            progress_args=(
                UPLOAD_START,
                start_time,
                status_message,
            )
        )
        end_two = datetime.now()
        time_taken_for_upload = (end_two - end_one).seconds
        await status_message.edit_text(AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload))
        video_up = video_up.id
        cap=f"Name : {caption}\n\nUser: {mention}\n#ID_{user_id}"
        await app.copy_message(log_channel_id,user_id,message_id=video_up,caption=cap)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("ðŸ“¤ View in Bot PM", url='https://t.me/Drm_Downloaderx_Bot')]])
        await status_message.edit_text(
            f"File have been Sent to Bot PM (Private)\n\nDownloaded in <b>{time_taken_for_download}</b> seconds.\n\nUploaded in <b>{time_taken_for_upload}</b> seconds.\n\nName : <b>{caption}</b>\n\nUser : {mention}",
            reply_markup=keyboard,
            )
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    except Exception as e:
        logger.error(f"An error occurred while sending the video: {str(e)}")


def generate_thumbnail(video_path, time_offset=5):
    thumbnail_path = video_path.replace(".mkv", ".jpg")
    try:
        video_clip = VideoFileClip(video_path)
        thumbnail_frame = video_clip.get_frame(time_offset)
        thumbnail_image = Image.fromarray(np.uint8(thumbnail_frame))
        thumbnail_image.save(thumbnail_path, format="JPEG")
        return thumbnail_path
    except Exception as e:
        logger.error(f"Error generating thumbnail: {str(e)}")
        return None
    
def extract_pssh_from_mpd(mpd_content):
    ns = {"mpd": "urn:mpeg:dash:schema:mpd:2011", "cenc": "urn:mpeg:cenc:2013"}
    root = ET.fromstring(mpd_content)
    content_protection_elements = root.findall(".//mpd:ContentProtection", namespaces=ns)

    for content_protection in content_protection_elements:
        pssh_element = content_protection.find("cenc:pssh", namespaces=ns)
        if pssh_element is not None:
            pssh_data = pssh_element.text.strip()
            return pssh_data

    return None

def extract_headers_from_curl(xdrm):
    response = requests.get(xdrm)
    soup = BeautifulSoup(response.content, 'html.parser')
    curl_command = soup.get_text()

    n01_match = re.search(r"-H 'sec-ch-ua: (.*?)'", curl_command)
    n02_match = re.search(r"-H 'eu: (.*?)'", curl_command)
    n03_match = re.search(r"-H 'sec-ch-ua-mobile: (.*?)'", curl_command)
    n04_match = re.search(r"-H 'user-agent: (.*?)'", curl_command)
    n05_match = re.search(r"-H 'et: (.*?)'", curl_command)
    n06_match = re.search(r"-H 'origin: (.*?)'", curl_command)
    n07_match = re.search(r"-H 'referer: (.*?)'", curl_command)
    n08_match = re.search(r"-H 'accept-language: (.*?)'", curl_command)
    n09_match = re.search(r"-H 'x-forwarded-for: (.*?)'", curl_command)

    if n01_match and n02_match and n03_match and n04_match and n05_match and n06_match and n06_match and n07_match and n08_match and n09_match:
       n01_value = n01_match.group(1)
       n02_value = n02_match.group(1)
       n03_value = n03_match.group(1)
       n04_value = n04_match.group(1)
       n05_value = n05_match.group(1)
       n06_value = n06_match.group(1)
       n07_value = n07_match.group(1)
       n08_value = n08_match.group(1)
       n09_value = n09_match.group(1)

       headers = {'sec-ch-ua': n01_value,
               'eu': n02_value, 
               'sec-ch-ua-mobile': n03_value, 
               'user-agent':n04_value,
               'et':n05_value,
               'origin':n06_value,
               'referer':n07_value,
               'accept-language':n08_value,
               'x-forwarded-for':n09_value,
               }

       return headers




async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    start,
    status_message,
):
    now = time.time()
    diff = now - start
    if round(diff % 30.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \nP: {2}%\n\n".format(
            ''.join(["â–ˆ" for i in range(math.floor(percentage / 5))]),
            ''.join(["â–‘" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await status_message.edit_text(
                text="{}\n {}".format(
                    ud_type,
                    tmp
                )
            )
        except:
            pass


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

def reformat_url(input_url):
    # Split the URL by "/"
    parts = input_url.split("/")

    # Find the index of "playlist" in the parts
    playlist_index = parts.index("playlist")

    # Extract the playlist ID
    playlist_id = parts[playlist_index + 1]

    # Construct the output URL format
    output_url = f"https://cdn2.video.lk.databoxtech.com/segments/{playlist_id}/_unsec/playlist.m3u8"

    return output_url


print("Bot Started")
if __name__ == "__main__":
    app.run()