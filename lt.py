# !pip install libtorrent
# !pip install python-telegram-bot

import libtorrent as lt
from telegram.ext import *
from telegram import ParseMode
import time, os
from concurrent.futures import ThreadPoolExecutor

# import datetime

links = []


def torrent(links, context, update, id):
    # link = input("Paste your Torrent / Magnet link here: ")
    
    ses = lt.session()
    ses.listen_on(6881, 6891)
    params = {
        'save_path': '',
        }

    handle = lt.add_magnet_uri(ses, links, params)
    ses.start_dht()

    begin = time.time()

    context.bot.send_message(chat_id=update.message.chat_id,
                                text='*⬇️ Downloading Metadata... ⬇️*', parse_mode=ParseMode.MARKDOWN)


    while (not handle.has_metadata()):
        end = time.time()
        tt = end-begin
        time.sleep(1)
        if tt > float(120):
            break
    end = time.time()
    tt = end-begin

    if tt < float(120):
        context.bot.editMessageText(chat_id=update.message.chat_id,
                                    message_id=update.message.message_id+int(id), 
                                    text='*🤩 Got Metadata 🤩*\n\n*Starting Torrent Download...*', parse_mode=ParseMode.MARKDOWN)
        
        time.sleep(3)

        context.bot.editMessageText(chat_id=update.message.chat_id,
                                    message_id=update.message.message_id+int(id), 
                                    text="*Starting.............* \n"+'*'+handle.name()+'*', parse_mode=ParseMode.MARKDOWN)
        
        time.sleep(3)

        size = 0
        s = handle.get_torrent_info() 
        nf =  s.files().num_files()
        for x in range(s.files().num_files()):
            size = size+s.files().file_size(x)
        size = round(size/1000000000, 3)
        # print(size, 'Gb')

        while (handle.status().state != lt.torrent_status.seeding):
            s = handle.status()
            state_str = ['queued', 'checking', 'downloading metadata', \
                    'downloading', 'finished', 'seeding', 'allocating']
                    
            # context.bot.editMessageText(chat_id=update.message.chat_id,
            #                         message_id=update.message.message_id+int(id), 
            #                         text='*⬇️ Downloading.... ⬇️\n\n %.2f%% complete\n down: %.1f kb/s\n up: %.1f kB/s\n peers: %d\n %s *' % \
            #                         (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
            #                         s.num_peers, state_str[s.state]), parse_mode=ParseMode.MARKDOWN)

            context.bot.editMessageText(chat_id=update.message.chat_id,
                                    message_id=update.message.message_id+int(id), 
                                    text='*⬇️ Downloading.... ⬇️\n\nName:-  *'+'*'+str(handle.name())+'*'+'*\n\nSize:-  *'+'*'+str(size)+' GB*\n'+'*Tottle Files:-  '+str(nf)+'*'+'*\n\n Complete:-  %.2f%% \n Download Speed:-  %.1f mb/s\n Upload Speed:-  %.1f mb/s\n Peers:-  %d\n\n %s *' % \
                                    (s.progress * 100, s.download_rate / 1000000, s.upload_rate / 1000000, \
                                    s.num_peers, state_str[s.state]), parse_mode=ParseMode.MARKDOWN)


            time.sleep(5)


        context.bot.editMessageText(chat_id=update.message.chat_id,
                                    message_id=update.message.message_id+int(id), 
                                    text="*"+handle.name()+"\nn UPLOADING TO DRIVE*", parse_mode=ParseMode.MARKDOWN)


        # print('1 uploading...')
        os.system('rclone copy "'+str(handle.name())+'" gdm:')
        os.remove(handle.name())
        context.bot.editMessageText(chat_id=update.message.chat_id,
                                    message_id=update.message.message_id+int(id), 
                                    text="*"+handle.name()+"\nn UPLOAD COMPLETED*", parse_mode=ParseMode.MARKDOWN)



    else:
        context.bot.editMessageText(chat_id=update.message.chat_id,message_id=update.message.message_id+int(id),
                                text='*Download Failed Due to Dead Torrent Link\nPlease Send Working Torrent Link*', parse_mode=ParseMode.MARKDOWN)

def threding(context, update):
    with ThreadPoolExecutor(max_workers=50) as executor:
        for l in range(len(links)):
                arguments = [links[l], context, update, (l+1)]
                executor.submit(torrent, *arguments)
        executor.shutdown(wait=True)


def handle_message(update,context):
    message = update.message.text
    # print(u)
    if str(message).split('?xt=')[0] == 'magnet:':
        links.append(message)
        update.message.reply_text('*Send Another Magnet Link\n\n                         OR\n\nSend /start to Start Downloading*', parse_mode=ParseMode.MARKDOWN)
    elif message.lower() == '/start':
        if len(links) != 0:
            threding(context, update)
            links.clear()
        else:
            update.message.reply_text('🧲 🧲 *Please Send Magnet Link..* 🧲 🧲', parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text('🧲 🧲 *Please Send Magnet Link..* 🧲 🧲', parse_mode=ParseMode.MARKDOWN)

def error(update, context):
    print(f"Update {update} caused error {context.error}")        
       

def main():
    updater = Updater('5953512922:AAEy--1-Ukhlx9GWiMEcYcieIYqzKA0o2zo', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main() 
# torrent()
